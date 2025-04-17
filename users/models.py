from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
from django.contrib.auth import get_user_model
from datetime import date, time, datetime
from django.utils import timezone
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings
from django.db.models import JSONField
import pdb
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from utils.models import CommonTimeStamp
from django.contrib.auth.models import User
# from django.utils.translation import gettext_lazy as _
# # Create your models here.

class UserProfile(CommonTimeStamp):
    CATEGORY_CHOICES =(
        ('MALE', 'MALE'),
        ('FEMALE', 'FEMALE'),
        ('OTHER', 'OTHER'),
        ('Prefer not to say', 'Prefer not to say'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='user_profile')
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True,null=True)
    email = models.EmailField(null=True,blank=True, unique=True)
    profile_image = models.ImageField(verbose_name="Profile Image",default='/dummy.png', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    mobile = models.CharField(verbose_name="User Mobile Number",max_length=13,null=True,unique=True, validators=[MinLengthValidator(4), MaxLengthValidator(12)], blank=True, db_index=True,)
    gender = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    address = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    country_code = models.CharField(max_length=5 ,default='+91', blank=True, null=True)
    is_suspended = models.BooleanField(default=False)



    class Meta:
        verbose_name = u"User Profile"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return str(self.email)

    def __str__(self):
        return str(self.email)
    


class SignalProviderProfile(CommonTimeStamp):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='signal_provider_profile')
    name = models.CharField(max_length=150,null=True,blank=True)
    email = models.EmailField(null=True,blank=True,default="",unique=True)
    mobile = models.CharField(verbose_name="Signal Provider Mobile Number",max_length=13,null=True,unique=True, validators=[MinLengthValidator(4), MaxLengthValidator(12)], blank=True, db_index=True,)
    country_code = models.CharField(max_length=5 ,default='+91', blank=True, null=True)
    profile_image = models.ImageField(verbose_name="Profile Image",default='/dummy.png', blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    class Meta:
        verbose_name = u"Signal Provider Profile"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return str(self.email)

    def __str__(self):
        return str(self.email)
    

class SingnalProviderPost(CommonTimeStamp):
    signal_provider = models.ForeignKey(SignalProviderProfile, on_delete=models.CASCADE, related_name='signal_provider_post')
    entry = models.IntegerField(blank=True, null=True)
    tp1time = models.TimeField(blank=True, null=True)
    tp1 = models.IntegerField(blank=True, null=True)
    tp2time = models.TimeField(blank=True, null=True)
    tp2 = models.IntegerField(blank=True, null=True)
    tp3time = models.TimeField(blank=True, null=True)
    tp3 = models.IntegerField(blank=True, null=True)
    stop_loss_time = models.TimeField(blank=True, null=True)
    stop_loss = models.IntegerField(blank=True, null=True)
    caption = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_premium =models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)


    class Meta:
        verbose_name = u"Signal Provider Post"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return str(self.caption)

    def __str__(self):
        return str(self.caption)
    
class SignalProviderPostItem(CommonTimeStamp):
    post = models.ForeignKey(SingnalProviderPost, on_delete=models.CASCADE, related_name='signal_provider_post_item')
    image = models.ImageField(upload_to='signal_provider_post_item', blank=True, null=True)
    file = models.FileField(upload_to='signal_provider_post_item', blank=True, null=True)
    thumbnail = models.FileField(upload_to='signal_provider_post_item', blank=True, null=True)
    MimeType = models.CharField(max_length=100, blank=True, null=True)


    class Meta:
        verbose_name = u"Signal Provider Post Item"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return str(self.post.caption)

    def __str__(self):
        return str(self.post.caption)
    


class LikeSingalProviderPost(CommonTimeStamp):
    user = models.ForeignKey(SignalProviderProfile, on_delete=models.CASCADE, related_name='like_signal_provider_post')
    post = models.ForeignKey(SingnalProviderPost, on_delete=models.CASCADE, related_name='like_signal_provider_post')

    class Meta:
        verbose_name = u"Like Signal Provider Post"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return str(self.user.email)

    def __str__(self):
        return str(self.user.email)
    

class ComentSignalProviderPost(CommonTimeStamp):
    user = models.ForeignKey(SignalProviderProfile, on_delete=models.CASCADE, related_name='user_coment_signal_provider_post')
    post = models.ForeignKey(SingnalProviderPost, on_delete=models.CASCADE, related_name='coment_signal_provider_post')
    comment = models.TextField(blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    is_abused = models.BooleanField(default=False)

    class Meta:
        verbose_name = u"Comment Signal Provider Post"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return str(self.user.email)

    def __str__(self):
        return str(self.user.email)
    

class LikeCommentSignalProviderPost(CommonTimeStamp):
    user = models.ForeignKey(SignalProviderProfile, on_delete=models.CASCADE, related_name='like_comment_signal_provider_post')
    comment = models.ForeignKey(ComentSignalProviderPost, on_delete=models.CASCADE, related_name='like_comment_signal_provider_post')

    class Meta:
        verbose_name = u"Like Comment Signal Provider Post"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return str(self.user.email)

    def __str__(self):
        return str(self.user.email)
    
class BlockUser(CommonTimeStamp):
    user = models.ForeignKey(SignalProviderProfile, on_delete=models.CASCADE, related_name='block_user')
    signal_provider = models.ForeignKey(SignalProviderProfile, on_delete=models.CASCADE, related_name='signal_provider_block_user')

    class Meta:
        verbose_name = u"Block User"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return str(self.user.email)

    def __str__(self):
        return str(self.user.email)


class UserFollewRequest(CommonTimeStamp):
    CATEGORY_CHOICES = (
        ('PENDING', 'PENDING'),
        ('ACCEPTED', 'ACCEPTED'),
        ('REJECTED', 'REJECTED'),
    )
    user = models.ForeignKey(SignalProviderProfile, on_delete=models.CASCADE, related_name='user_follow_request')
    signal_provider = models.ForeignKey(SignalProviderProfile, on_delete=models.CASCADE, related_name='signal_provider_follow_request')
    status = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='PENDING')

    class Meta:
        verbose_name = u"User Follow Request"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return str(self.user.email)

    def __str__(self):
        return str(self.email)
    
   
class ReportCommentAbuse(CommonTimeStamp):
    user = models.ForeignKey(SignalProviderProfile, on_delete=models.CASCADE, related_name='report_comment_abuse')
    comment = models.ForeignKey(ComentSignalProviderPost, on_delete=models.CASCADE, related_name='report_comment_abuse')
    reason = models.TextField(blank=True, null=True)
    is_approved = models.BooleanField(default=False)

    class Meta:
        verbose_name = u"Report Comment Abuse"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return str(self.user.email)

    def __str__(self):
        return str(self.user.email)



class PhoneModel(models.Model):
    mobile = models.CharField(max_length=13, blank=True, null=True)
    otp = models.CharField(max_length=6, blank=True, null=True)


    class Meta:
        verbose_name = u"Phone Model"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return str(self.mobile)

    def __str__(self):
        return str(self.mobile)


class EmailModel(models.Model):
    email = models.EmailField(blank=True, null=True)
    otp = models.CharField(max_length=6, blank=True, null=True)

    class Meta:
        verbose_name = u"Email Model"
        verbose_name_plural = verbose_name
        