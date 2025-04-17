from django.db import models
from django.conf import settings
#data
# Create your models here.

class CommonTimeStamp(models.Model):
    """
        Use this model reference for all Models
    """
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=u"Created By", null=True, blank=True, related_name="created_by_%(class)s")
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=u"Updated By", null=True, blank=True, related_name="updated_by_%(class)s")

    class Meta:
        abstract = True



