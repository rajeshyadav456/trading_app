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
from trading_app.models import *
from .enums import *

# # Create your models here.


class MyUserManager(BaseUserManager):
    def _create_user(self, email=None, mobile=None, password=None, **extra_fields):
        # if not email:
        #     raise ValueError('The email field must be set')
        if email:
            user = self.model(email=email, **extra_fields)

        if mobile:
            user = self.model(mobile=mobile, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self,email=None, mobile=None,**extra_fields):
        extra_fields.setdefault('is_staff',False)
        extra_fields.setdefault('is_superuser',False)
        extra_fields.setdefault('is_active',True)
        return self._create_user(email, mobile, **extra_fields)
    
    def create_admin(self,email,mobile, password,**extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',False)
        extra_fields.setdefault('is_active',True)
        return self._create_user(email,mobile, password,**extra_fields)
    
    def create_superuser(self, email, mobile, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active',True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, mobile, password, **extra_fields)
        
    
class User(CommonTimeStamp, AbstractBaseUser,PermissionsMixin): 
    email = models.EmailField(null=True,blank=True,default="",unique=True)
    username = models.CharField(max_length=150,null=True,blank=True ,unique=True)
    first_name = models.CharField(max_length=150,null=True,blank=True)
    last_name = models.CharField(max_length=150,null=True,blank=True)
    date_of_birth = models.DateField(null=True,blank=True)
    mobile = models.CharField(verbose_name="Mobile Number",max_length=13,null=True,unique=True, validators=[MinLengthValidator(4), MaxLengthValidator(12)], blank=True, db_index=True,)
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now=True)
    user_type = models.CharField(max_length=100,choices=UserType.choices())
    profile_image = models.ImageField(verbose_name="Profile Image",default='/dummy.png')
    country_code = models.CharField(max_length=5 ,default='+91')
    postal_code = models.CharField(max_length=5, blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    address2 = models.TextField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=100, choices=GENDERCHOICE.choices(), blank=True, null=True)
    is_suspended = models.BooleanField(default=False)
    document = models.FileField(upload_to='user_document', blank=True, null=True)
    objects = MyUserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    country_code = models.CharField(max_length=5 ,default='+91')
    

    def __str__(self):
        return f"{self.username}"


class Asset(CommonTimeStamp):
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = u"Asset"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return str(self.name)

    def __str__(self):
        return str(self.name)
        


class SingnalProviderPost(CommonTimeStamp):
    CATEGORY_CHOICES = (
        ('BUY', 'BUY'), 
        ('SELL', 'SELL'),
    )
    SIGNAL_CHOICES =(
        ('Scalping', 'Scalping'),
        ('Swing', 'Swing'),
        ('Long_Term', 'Long_Term')
    )
    signal_provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='signal_provider_post')
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='signal_provider_post_assess', blank=True, null=True)
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
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    direction = models.CharField(max_length=100, choices=CATEGORY_CHOICES, blank=True,null=True)
    signal_type = models.CharField(max_length=100, choices=SIGNAL_CHOICES, blank=True,null=True)


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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='like_signal_provider_post')
    post = models.ForeignKey(SingnalProviderPost, on_delete=models.CASCADE, related_name='like_signal_provider_post')

    class Meta:
        verbose_name = u"Like Signal Provider Post"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return str(self.user.email)

    def __str__(self):
        return str(self.user.email)
    

class ComentSignalProviderPost(CommonTimeStamp):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_coment_signal_provider_post')
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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='like_comment_signal_provider_post')
    comment = models.ForeignKey(ComentSignalProviderPost, on_delete=models.CASCADE, related_name='like_comment_signal_provider_post')

    class Meta:
        verbose_name = u"Like Comment Signal Provider Post"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return str(self.user.email)

    def __str__(self):
        return str(self.user.email)
    
class BlockUser(CommonTimeStamp):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='block_user')
    signal_provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='signal_provider_block_user')

    class Meta:
        verbose_name = u"Block User"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return str(self.user.email)

    def __str__(self):
        return str(self.user.email)


class UserFollewRequest(CommonTimeStamp):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_follow_request')
    signal_provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='signal_provider_follow_request')

    class Meta:
        verbose_name = u"User Follow Request"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return str(self.user.email)

    def __str__(self):
        return str(self.email)
    
   
class ReportCommentAbuse(CommonTimeStamp):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='report_comment_abuse')
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
        


