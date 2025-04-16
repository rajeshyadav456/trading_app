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
# from django.utils.translation import gettext_lazy as _
# # Create your models here.
class MyUserManager(BaseUserManager):
    def _create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The email field must be set')
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_user(self,email,**extra_fields):
        extra_fields.setdefault('is_staff',False)
        extra_fields.setdefault('is_superuser',False)
        extra_fields.setdefault('is_active',True)
        return self._create_user(email,**extra_fields)
    
    def create_admin(self,email,password,**extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',False)
        extra_fields.setdefault('is_active',True)
        return self._create_user(email,password,**extra_fields)
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active',True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)
        
    
class User(AbstractBaseUser,PermissionsMixin): 
  ADMIN_MANAGER = 'ADMIN_MANAGER'
  CLEANING_MANAGER = 'CLEANING_MANAGER'
  CLIENT  = 'CLIENT'

  CLEANER = 'CLEANER'
  USER_TYPE = (
    (CLIENT ,'Client'),
    (CLEANING_MANAGER,'Cleaning Manager'),
    (CLEANER,'Cleaner')
  )
  email = models.EmailField(null=True,blank=True,default="",unique=True)
  username = models.CharField(max_length=150,null=True,blank=True ,unique=True)
  first_name = models.CharField(max_length=150,null=True,blank=True)
  last_name = models.CharField(max_length=150,null=True,blank=True)
  date_of_birth = models.DateField(default=date.today,null=True,blank=True)
  mobile = models.CharField(verbose_name="Mobile Number",max_length=13,null=True,unique=True, validators=[MinLengthValidator(4), MaxLengthValidator(12)], blank=True, db_index=True,)
  is_active = models.BooleanField(default=False)
  is_superuser = models.BooleanField(default=False)
  is_staff = models.BooleanField(default=False)
  date_joined = models.DateTimeField(auto_now=True)
  user_type = models.CharField(choices=USER_TYPE,max_length=250,default=ADMIN_MANAGER)
  profile_image = models.ImageField(verbose_name="Profile Image",default='/dummy.png')
  objects = MyUserManager()
  USERNAME_FIELD = 'username'
  REQUIRED_FIELDS = ['email']
  country_code = models.CharField(max_length=5 ,default='+91')

   class Meta:
    verbose_name = "User"
    verbose_name_plural = "Users"
 

  def __str__(self):
    return f"{self.username}"





