
from rest_framework import status
from rest_framework.response import Response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def generic_response(status_code=status.HTTP_200_OK, message=None, data=None, common_data={}):
    response_data = {'statusCode': status_code, 'message': message, 'data': data}
    if common_data:
        for key, value in common_data.items():
            response_data[key] = value

    response = Response(response_data, status=status_code)
    return response


def validate_field_not_request_body(request_body_fields={}):
    for field, value in request_body_fields.items():
        if value is None or not value:
            return (True, generic_response(status.HTTP_400_BAD_REQUEST,
                                           'Missing {} in body parameter which is required field!'.format(field)))
    return False, None


def get_pure_paginated_response(serialized_data, request, common_data={}):
    """
        This function is used to create a pagination for the API responses, need to pass list of dict data
    """
    per_page = int(request.GET.get('per_page', 10))
    page = int(request.GET.get('page', 1))

    if int(per_page) == -1:
        return generic_response(data=serialized_data)

    paginator = Paginator(serialized_data, per_page)

    try:
        paginated_data = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        paginated_data = paginator.page(1)

    serialized_paginated_data = serialized_data[paginated_data.start_index() - 1:paginated_data.end_index()]

    has_next_page = paginated_data.has_next()
    base_url = request.build_absolute_uri().split('?')[0]
    
    next_link = f'{base_url}?per_page={per_page}&page={paginated_data.next_page_number()}' if paginated_data.has_next() else None
    previous_link = f'{base_url}?per_page={per_page}&page={paginated_data.previous_page_number()}' if paginated_data.has_previous() else None

    response_data = {
        'statusCode': status.HTTP_200_OK,
        'hasNextPage': has_next_page,
        'next': next_link,
        'previous': previous_link,
        'count': paginator.count,
        'message': None,
        'data': serialized_paginated_data,
    }

    if common_data:
        for key, value in common_data.items():
            response_data[key] = value

    return Response(response_data, status=status.HTTP_200_OK)



def send_email_common_method(subject, recipient_email_list, html_content, cc=[], bcc=[]):
    dev_admin_emails = DEV_ADMIN_EMAIL.split(',')
    BCC = bcc + dev_admin_emails

    msg = EmailMultiAlternatives(subject=subject, from_email=EMAIL_FROM, to=recipient_email_list, bcc=BCC, cc=cc)#, bcc=[bcc], cc=get_sales_users_emails())
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def convert_utc_to_timezone(utc_datetime, target_timezone):
    # Define the UTC timezone
    utc = pytz.utc

    # Localize the UTC datetime
    utc_datetime = utc.localize(utc_datetime)

    # Define the target timezone
    target_tz = pytz.timezone(target_timezone)

    # Convert UTC datetime to the target timezone
    target_timezone_datetime = utc_datetime.astimezone(target_tz)

    return target_timezone_datetime


def create_homework_stripe_subscription(user, customer_id, payment_method_id, amount, currency_code, subscription_plan_id, added_credits, intent_id, is_free_trial=False, number_of_days_of_free_trial=None):
    """
    Create a Stripe subscription for homework-related purposes.

    Args:
        user: The user object representing the customer.
        customer_id: The Stripe customer ID.
        payment_method_id: The Stripe payment method ID.
        amount: The amount to be charged for the subscription.
        currency_code: The currency code (e.g., 'usd').
        subscription_plan_id: The ID of the subscription plan (in your database).
        added_credits: Additional credits to be added to the user.
        number_of_days_of_free_trial if more than zero  will be free trial 

    Returns:
        stripe_subscription: The created StudentSubscriptionPlan object after the Stripe subscription is successfully created.
    """
    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY

        today = datetime.now()
        HOMEWORK_SUBSCRIPTIONS_DAYS = settings.HOMEWORK_SUBSCRIPTIONS_DAYS
        HOMEWORK_SUBSCRIPTIONS_DAYS = int(HOMEWORK_SUBSCRIPTIONS_DAYS)

        # subscription_start_date = get_stripe_subscription_next_billing_date()
        subscription_start_date = today + timedelta(days=HOMEWORK_SUBSCRIPTIONS_DAYS)

        timestamp_subscription = int(round(subscription_start_date.timestamp()))

        customer = stripe.Customer.retrieve(customer_id)

        payment_method_obj = stripe.PaymentMethod.retrieve(payment_method_id)

        subscription_plan = SubscriptionPlan.objects.filter(id=int(subscription_plan_id)).first()
     
        # amount_to_charge = int(round(subscription_plan.credit.amount, 2) * 100)
        amount_to_charge = int(round(subscription_plan, 2) *100)

        # subscription_added_credits = int(subscription_plan.credit.credit)
        
        stripe.Customer.modify(
            customer_id,
            invoice_settings={
                'default_payment_method': payment_method_obj.id
            },
        )

        if is_free_trial:
            # NOTE: This is for the free trial subscription.
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[
                    {
                        "price_data": {
                            "unit_amount": amount_to_charge,
                            "currency": currency_code,
                            "product": settings.STRIPE_HOMEWORK_PRODUCT_KEY,
                            "recurring": {"interval": "month", "interval_count":1},
                        },
                    },
                ], 

                trial_period_days = trial_period_days,
                proration_behavior='none',
            )

        else:
            # NOTE: This is for the paid subscription.
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[
                    {
                        "price_data": {
                            "unit_amount": int(round(amount, 2) * 100),
                            "currency": currency_code,
                            "product": settings.STRIPE_HOMEWORK_PRODUCT_KEY,
                            "recurring": {"interval": "month", "interval_count":1},
                        },
                    },
                ],
                billing_cycle_anchor=timestamp_subscription,
                proration_behavior='none',
            )

        # Reteiving the latest charge id in order to fetch the invoice url.

      
        # Paid subscription: Retrieve PaymentIntent
        intent = stripe.PaymentIntent.retrieve(intent_id)
        charge = stripe.Charge.retrieve(intent.latest_charge)

        logger.debug(f'Subscription created for the user: {user} -- {subscription}')
        subscription_plan = SubscriptionPlan.objects.filter(id=subscription_plan_id).first()
        stripe_subscription = None 

        if subscription and subscription.status in ['active', 'trialing']:
            # Get the user's timezone and Convert the period start and end times from UTC to the user's timezone
            user_timezone = user.timezone
            logger.debug(f'User timezone: -- {user_timezone}')

            utc_period_start = datetime.utcfromtimestamp(subscription.current_period_start)
            logger.debug(f'UTC period start: -- {utc_period_start}')

            utc_period_end = datetime.utcfromtimestamp(subscription.current_period_end + 3900)
            logger.debug(f'UTC period end: -- {utc_period_end}')
            
            stripe_subscription = StudentSubscriptionPlan.objects.create(
                user=user, 
                customer_stripe_id=subscription.customer, 
                subscription_id=subscription.id, 
                payment_order_id=payment_method_obj.id, 
                subscription_start_date=datetime.now(), 
                from_date=utc_period_start,
                to_date=utc_period_end, 
                amount_paid=amount,
                currency_code=subscription.currency, 
                is_paid=True, 
                invoice_id=charge.id if charge else None, 
                subscription_plan=subscription_plan,
                invoice_url=charge.receipt_url if charge else None,
                subscription_end_date = utc_period_end,
                )
        return stripe_subscription
    except Exception as ex:
        logger.debug(f'Error while creating the stripe subscription object in the database -- {ex}')
        return generic_response(status_code=status.HTTP_400_BAD_REQUEST,
                                    message="Error while creating the stripe subscription object in the database")
    

