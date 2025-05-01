from django.contrib import admin
from .models import PlanType, SubscriptionPlan, UserSubscriptionPlan, UpgradeCreditPlan
# Register your models here.
admin.site.register(PlanType)
admin.site.register(SubscriptionPlan)
admin.site.register(UserSubscriptionPlan)
admin.site.register(UpgradeCreditPlan)


