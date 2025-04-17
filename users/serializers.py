from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from  django.conf import settings
from .models import *
import pyotp
import time


class RegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    mobile = serializers.CharField(max_length=13, validators=[MinLengthValidator(4), MaxLengthValidator(12)])
    email = serializers.EmailField()
    password = serializers.CharField(max_length=100, write_only=True)
    confirm_password = serializers.CharField(max_length=100, write_only=True)

    def is_valid_otp(self, otp, mobile):
        totp = pyotp.TOTP(settings.OTP_SECRET, interval=300, digits=4)
        if totp.verify(otp):
            return PhoneModel.objects.filter(mobile=mobile, otp=otp).exists()
        return False

    def validate(self, attrs):
        mobile = attrs.get('mobile')
        otp = attrs.pop('otp')
        user = UserProfile.objects.filter(mobile=mobile).exists()
        agent_user = SignalProviderProfile.objects.filter(mobile=mobile).exists()
        if user or agent_user:
            raise ValidationError('user already exists')
        if not self.is_valid_otp(otp, mobile):
            raise ValidationError('Invalid OTP')
        return super().validate(attrs)

    def create(self, validated_data):
        user = UserProfile.objects.create_user(**validated_data)
        signal_provider = SignalProviderProfile.objects.create_user(**validated_data)
        PhoneModel.objects.filter(mobile=user.mobile).delete()
        PhoneModel.objects.filter(mobile=signal_provider.mobile).delete()
        return user, signal_provider

# we want to register using usertype we want to create user_type  like if take user_type as user then user will be created if user_type is agent then agent will be created
# and we take mobile then email is not required and if email is taken then mobile is not required similarly for both agent and user. and we take mobile then show only mobile otp
# and if email is taken then show only email otp. for both user and agent. and we take mobile then show only mobile otp and if email is taken then show only email otp. for both user and agent.
# and we take mobile then show only mobile otp and if email is taken then show only email otp. for both user and agent.
# and we take mobile then show only mobile otp and if email is taken then show only email otp. for both user and agent. 
  

class PhoneModelSerializer(serializers.ModelSerializer):
    class Meta:
        model=PhoneModel
        fields=['mobile']

    def create(self,validated_data):
        totp=pyotp.TOTP(settings.OTP_SECRET,interval=30,digits=4)
        otp=totp.now()
        instance, _=self.Meta.model.objects.get_or_create(**validated_data)
        instance.otp=otp
        instance.save()
        return instance



class EmailModelSerializer(serializers.ModelSerializer):
    class Meta:
        model=EmailModel
        fields=['email']

    def create(self,validated_data):
        totp=pyotp.TOTP(settings.OTP_SECRET,interval=30,digits=6)
        otp=totp.now()
        instance, _=self.Meta.model.objects.get_or_create(**validated_data)
        instance.otp=otp
        instance.save()
        return instance












































































































































