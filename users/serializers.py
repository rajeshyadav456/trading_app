from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from  django.conf import settings
from .models import *
from trading_app.models import *
import pyotp
import time
from django.contrib.auth.hashers import make_password


# class RegisterSerializer(serializers.Serializer):
#     first_name = serializers.CharField(max_length=100) #mandotry field
#     last_name = serializers.CharField(max_length=100) #mandotry field
#     username = serializers.CharField(max_length=100) #mandotry field
#     dob = serializers.CharField(max_length=100) #mandotry field
#     address = serializers.CharField(max_length=200) #optional field
#     address1 = serializers.CharField(max_length=200) #optional field
#     city = serializers.CharField(max_length=100) #optional field
#     postal_code = serializers.CharField(max_length=100) #optional field
#     country = serializers.CharField(max_length=100) #optional field
#     document = serializers.FileField() #mandotry field if user_type == SIGNAL_PROVIDER
#     mobile = serializers.CharField(max_length=13, validators=[MinLengthValidator(4), MaxLengthValidator(12)]) #if user and signalprovide signup with mobile than required if signup with email then mobile isn't mandory
#     email = serializers.EmailField() # if user and signal provide signup with email then required if signup with mobile then not required
#     password = serializers.CharField(max_length=100, write_only=True) #mandtory field
#     confirm_password = serializers.CharField(max_length=100, write_only=True) #mandtory field

#     def is_valid_otp(self, otp, mobile):
#         totp = pyotp.TOTP(settings.OTP_SECRET, interval=300, digits=4)
#         if totp.verify(otp):
#             return PhoneModel.objects.filter(mobile=mobile, otp=otp).exists()
#         return False

#     def validate(self, attrs):
#         mobile = attrs.get('mobile')
#         otp = attrs.pop('otp')
#         user = User.objects.filter(user_type='User', mobile=mobile).exists()
#         agent_user = User.objects.filter(user_type='SIGNAL_PROVIDER', mobile=mobile).exists()
#         if user or agent_user:
#             raise ValidationError('user already exists')
#         if not self.is_valid_otp(otp, mobile):
#             raise ValidationError('Invalid OTP')
#         return super().validate(attrs)

#     def create(self, validated_data):
#         validated_data['user_type'] = 'User'
#         user = User.objects.create_user(**validated_data)
#         validated_data['user_type'] = 'SIGNAL_PROVIDER'
#         signal_provider = User.objects.create_user(**validated_data)
#         PhoneModel.objects.filter(mobile=user.mobile).delete()
#         PhoneModel.objects.filter(mobile=signal_provider.mobile).delete()
#         return user, signal_provider



class RegisterSerializer(serializers.Serializer):
    user_type = serializers.ChoiceField(choices=UserType.choices())
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    username = serializers.CharField(max_length=100)
    date_of_birth = serializers.DateTimeField()
    gender = serializers.ChoiceField(choices=GENDERCHOICE.choices())
    address = serializers.CharField(max_length=200, required=False) 
    address1 = serializers.CharField(max_length=200, required=False)
    city = serializers.CharField(max_length=100, required=False)
    postal_code = serializers.CharField(max_length=100, required=False)
    country = serializers.CharField(max_length=100, required=False)
    document = serializers.FileField(required=False)
    mobile = serializers.CharField(max_length=13, required=False)
    email = serializers.EmailField(required=False)
    otp = serializers.CharField(max_length=6)
    password = serializers.CharField(max_length=100, write_only=True)
    confirm_password = serializers.CharField(max_length=100, write_only=True)

    def is_valid_mobile_otp(self, otp, mobile):
        totp = pyotp.TOTP(settings.OTP_SECRET, interval=30, digits=4)
        if totp.verify(otp):
            return PhoneModel.objects.filter(mobile=mobile, otp=otp).exists()
            
        return False
    
    def is_valid_email_otp(self, otp, email):
        totp = pyotp.TOTP(settings.OTP_SECRET, interval=30, digits=6)
        if totp.verify(otp):
            return EmailModel.objects.filter(email=email, otp=otp).exists()
        return False


    def validate(self, attrs):
        mobile = attrs.get('mobile')
        email = attrs.get('email')
        otp = attrs.get('otp')
        user_type = attrs.get('user_type')

        if not mobile and not email:
            raise serializers.ValidationError("Either mobile or email must be provided.")
        if mobile and email:
            raise serializers.ValidationError("Only one of mobile or email should be provided at a time.")

        if mobile:
            if not self.is_valid_mobile_otp(otp, mobile):
                raise serializers.ValidationError("Invalid OTP for mobile data.")
            if User.objects.filter(mobile=mobile).exists():
                raise serializers.ValidationError("User with this mobile already exists.")
        if email:
            if not self.is_valid_email_otp(otp, email):
                raise serializers.ValidationError("Invalid OTP for email.")
            if User.objects.filter(email=email).exists():
                raise serializers.ValidationError("User with this email already exists.")

        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")

        if user_type == 'SIGNAL_PROVIDER' and not attrs.get('document'):
            raise serializers.ValidationError("Document is required for SIGNAL_PROVIDER.")

        return attrs
       

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        validated_data.pop('otp')

        user_type = validated_data.pop('user_type')
        password = validated_data.pop('password')


        user = User.objects.create_user(**validated_data, user_type=user_type, password=make_password(password))

        if 'mobile' in validated_data:
            PhoneModel.objects.filter(mobile=validated_data['mobile']).delete()
        if 'email' in validated_data:
            EmailModel.objects.filter(email=validated_data['email']).delete()

        return user



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
        fields = ('id', 'user_type', 'first_name', 'last_name', 'username', 'email', 'gender', 'date_of_birth', 'profile_image', 'mobile', 'bio', 'address', 'address2', 'postal_code', 'country', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')

    def update(self, instance, validated_data):
        validated_data.pop('password', None)
        for attrs, value in validated_data.items():
            setattr(instance, attrs, value)
        instance.save()
        return instance

class GetUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'user_type', 'first_name', 'last_name', 'username', 'email', 'gender', 'date_of_birth', 'profile_image', 'mobile', 'bio', 'address', 'address2', 'postal_code', 'country', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')


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






























































































































