from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from  django.conf import settings
from .models import *
from trading_app.models import *
import pyotp
import time


class RegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100) #mandotry field
    last_name = serializers.CharField(max_length=100) #mandotry field
    username = serializers.CharField(max_length=100) #mandotry field
    dob = serializers.CharField(max_length=100) #mandotry field
    address = serializers.CharField(max_length=200)
    address1 = serializers.CharField(max_length=200)
    city = serializers.CharField(max_length=100)
    postal_code = serializers.CharField(max_length=100)
    country = serializers.CharField(max_length=100)
    document = serializers.FileField() #mandotry field if user_type == SIGNAL_PROVIDER
    mobile = serializers.CharField(max_length=13, validators=[MinLengthValidator(4), MaxLengthValidator(12)]) #if user and signalprovide signup with mobile than required if signup with email then mobile isn't mandory
    email = serializers.EmailField() # if user and signal provide signup with email then required if signup with mobile then not required
    password = serializers.CharField(max_length=100, write_only=True) #mandtory field
    confirm_password = serializers.CharField(max_length=100, write_only=True) #mandtory field

    def is_valid_otp(self, otp, mobile):
        totp = pyotp.TOTP(settings.OTP_SECRET, interval=300, digits=4)
        if totp.verify(otp):
            return PhoneModel.objects.filter(mobile=mobile, otp=otp).exists()
        return False

    def validate(self, attrs):
        mobile = attrs.get('mobile')
        otp = attrs.pop('otp')
        user = User.objects.filter(user_type='User', mobile=mobile).exists()
        agent_user = User.objects.filter(user_type='SIGNAL_PROVIDER', mobile=mobile).exists()
        if user or agent_user:
            raise ValidationError('user already exists')
        if not self.is_valid_otp(otp, mobile):
            raise ValidationError('Invalid OTP')
        return super().validate(attrs)

    def create(self, validated_data):
        validated_data['user_type'] = 'User'
        user = User.objects.create_user(**validated_data)
        validated_data['user_type'] = 'SIGNAL_PROVIDER'
        signal_provider = User.objects.create_user(**validated_data)
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

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'user_type', 'first_name', 'last_name', 'username', 'email', 'gender', 'date_of_birth', 'profile_image', 'mobile', 'bio', 'address')
        read_only_fields = ('id', 'first_name', 'last_name', 'email', 'profile_image', 'mobile', 'bio')


class SignalProviderProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'user_type', 'first_name', 'last_name', 'username', 'email', 'gender', 'date_of_birth', 'profile_image', 'mobile', 'bio', 'address')

class SingnalProviderPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'signal_type', 'signal_provider', 'asset', 'entry', 'tp1', 'tp2', 'tp3', 'stop_loss', 'caption', 'description', 'is_premium', 'direction')

class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = ('id', 'name', 'description', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')


class CommentSignalProviderPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComentSignalProviderPost
        fields = ('id', 'user', 'post', 'comment', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')

    def validate_data(self, attrs):
        post = attrs.get('post')
        if not post:
            raise serializers.ValidationError("Post is required")
        return super().validate_data(attrs)


class AssetBasedSignalProviderSerializer(serializers.ModelSerializer):
    signal_provider = serializers.SerializerMethodField()

    class Meta:
        model = SingnalProviderPost
        fields = ('id', 'signal_provider', 'asset')

    def get_signal_provider(self, instance):
        signal_provider = User.objects.filer(id=instance.signal_provider)
        serialized_data = SignalProviderProfileSerializer(signal_provider, many=True)
        return serialized_data.data if serialized_data else None

        

class LikeSingalProviderPostSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    class Meta:
        model = LikeSingalProviderPost
        fields = ('id', 'user', 'post', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')
 
    def create(self, validated_data):
        like = LikeSingalProviderPost.objects.filter(post=validated_data['post'], user=self.context.request.user)
        if like:
            like[0].delete()
            return like[0]
        return super().create(**validated_data)



class LikeCommentSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    class Meta:
        model = LikeCommentSignalProviderPost
        fields = ('id', 'user', 'comment', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')

    def create(self, validated_data):
        like = LikeCommentSignalProviderPost.objects.filter(comment=validated_data['comment'], user=self.context.request.user)
        if like:
            like[0].delete()
            return like[0]
        return super().create(**validated_data)

class UserFollewRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFollewRequest
        fields = ('id', 'user', 'signal_provider', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')


class BlockUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockUser
        fields = ('id', 'user', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')



class PlanTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanType
        fields = ('id', 'name', 'description', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')



class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ('id', 'plan_type', 'name', 'description', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')






























































































































