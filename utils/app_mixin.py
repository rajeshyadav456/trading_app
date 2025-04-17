
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