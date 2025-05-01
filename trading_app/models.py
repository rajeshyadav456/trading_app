from django.db import models
from users.models import User
from utils.models import CommonTimeStamp, CURRENCY_CODE
# Create your models here.

class PlanType(CommonTimeStamp):
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=False)


    class Meta:                                                                                                                                                           
        verbose_name = u"Plan Type"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return str(self.name)

    def __str__(self):
        return str(self.name)
        

class SubscriptionPlan(models.Model):
    plan_type = models.ForeignKey(PlanType, on_delete=models.CASCADE, related_name='subscription_plan')
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        verbose_name = u"Subscription Plan"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return str(self.name)

    def __str__(self):
        return str(self.name)


class UserSubscriptionPlan(CommonTimeStamp):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, null=True, blank=True)
    is_paid = models.BooleanField(default=False, verbose_name=u"Is_Paid_Subscription", blank=True, null=True)
    due_date = models.DateTimeField(null=True, blank=True, verbose_name=u"Due Date")
    payment_order_id = models.CharField('Payment ORDER ID', max_length=50, null=True, blank=True)
    customer_stripe_id = models.CharField('Customer Stripe ID', max_length=50, null=True, blank=True)
    subscription_id = models.CharField(max_length=500, verbose_name="Subscription Id", null=True, blank=True)
    is_notified = models.BooleanField(default=False, verbose_name=u"Is Notified")
    is_notified_by_whatsapp = models.BooleanField(default=False, verbose_name=u"Is Notified By WhatsApp")
    subscription_start_date = models.DateTimeField(verbose_name=u"Subscription start date", null=True, blank=True)
    subscription_end_date = models.DateTimeField(verbose_name=u"Subscription end date", null=True, blank=True)
    from_date = models.DateTimeField(verbose_name=u"From date", null=True, blank=True)
    to_date = models.DateTimeField(verbose_name=u"To date", null=True, blank=True)
    last_subscription_date = models.DateTimeField(verbose_name=u"last subscription date", blank=True, null=True)
    next_billing_date = models.DateTimeField(verbose_name=u"Next Subscription Billing Date", blank=True, null=True)
    amount_paid = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=u"Amount Paid", blank=True,
                                      null=True)
    currency_code = models.CharField(choices=CURRENCY_CODE, default='USD', max_length=10)
    cancelled_subscription_date = models.DateTimeField(verbose_name=u"Cancelled Subscription Date", blank=True,
                                                       null=True)
    is_subscription_cancelled = models.BooleanField(default=False, verbose_name=u"Is Subscription Cancelled",
                                                    blank=True, null=True)
    invoice_id = models.CharField(max_length=50, verbose_name=u'Invoice id', null=True, blank=True)
    invoice_url = models.CharField(max_length=300, verbose_name=u'Invoice Url', null=True, blank=True)

    class Meta:
        verbose_name = u"Student Subscription Plan"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return '%s' % (self.user,)

    def __str__(self):
        return f'{self.user}'


class UpgradeCreditPlan(CommonTimeStamp):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    user_subscription_plan = models.ForeignKey(UserSubscriptionPlan, on_delete=models.CASCADE, null=True, blank=True)
    currency_code = models.CharField(choices=CURRENCY_CODE, default='USD', max_length=10)
    discount_percentage = models.IntegerField(null=True, blank=True, verbose_name=u"Discount")
    amount_paid = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=u"Amount Paid")
    is_notified = models.BooleanField(default=False, verbose_name=u"Is Notified")
    is_notified_by_whatsapp = models.BooleanField(default=False, verbose_name=u"Is Notified By WhatsApp")
    paid_date = models.DateTimeField(verbose_name=u"Paid date", null=True, blank=True)
    payment_order_id = models.CharField('Payment ORDER ID', max_length=50, null=True, blank=True)
    customer_stripe_id = models.CharField('Customer Stripe ID', max_length=50, null=True, blank=True)
    invoice_id = models.CharField(max_length=50, verbose_name=u'Invoice id', null=True, blank=True)
    invoice_url = models.CharField(max_length=300, verbose_name=u'Invoice Url', null=True, blank=True)

    class Meta:
        verbose_name = u"Upgrade Credit Plan"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return '%s' % (self.user,)

    def __str__(self):
        return self.user.email

