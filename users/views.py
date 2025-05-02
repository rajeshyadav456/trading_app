from django.shortcuts import render
from .serializers import *
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.conf import settings
from django.contrib.auth.models import User
from utils.app_mixin import generic_response, validate_field_not_request_body, get_pure_paginated_response
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
User = get_user_model()
from .tokens import CustomAccessToken

# Create your views here.

class LoginAPIView(APIView):
    authentication_classes = []  
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            email = request.data.get('email', None)
            mobile = request.data.get('mobile', None)
            password = request.data.get('password', None)

            if email:
                user = authenticate(email=email, password=password)
                user = User.objects.filter(email=email).first()
                

            if mobile:
                user = authenticate(mobile=mobile, password=password)
                user = User.objects.filter(mobile=mobile).first()
              

            if user is None:
                return generic_response(status.HTTP_400_BAD_REQUEST, 'User not found')

            login(request,user)
            jwt_token = CustomAccessToken.for_user(user)

            return Response({'message':'Login Successfully', 'user_type':user.user_type if user else None, 'token':str(jwt_token)})

        except Exception as ex:
            return generic_response(status.HTTP_404_NOT_FOUND, f'Error while creating: {str(ex)}')


class SuperuserLoginAPIView(APIView):
    def post(self, request):
        try:
            data = request.data
            email = data.get('email')
            password = data.get('password')

            user = authenticate(email=email, password=password)
            
        except Exception as ex:
            return generic_response(status.HTTP_404_NOT_FOUND, f'Error while login: {str(ex)}')

class RegisterAPIView(APIView):
    """
    User Registration API View
    """
    authentication_classes = []  
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            data = request.data
            serializer = RegisterSerializer(data=data)
            
            if not serializer.is_valid():
                return generic_response(status.HTTP_400_BAD_REQUEST, f'{serializer.errors}')  

            serializer.save()

            return generic_response(status.HTTP_201_CREATED, 'User created successfully', data=data)
            
        except Exception as e:
            return generic_response(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Error while creating: {str(e)}')



class GenerateOtpAPIView(APIView):
    """
    Generate OTP for user registration
    """
    authentication_classes = []  
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            serializer = PhoneModelSerializer(data=data)

            if not serializer.is_valid():
                return generic_response(status.HTTP_400_BAD_REQUEST, serializer.errors)

            instance = serializer.save()
            data = {'mobile':instance.mobile, 'otp': instance.otp}
            return generic_response(status.HTTP_201_CREATED, 'OTP sent successfully', data=data)

        except Exception as e:
            return generic_response(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Error while creating: {str(e)}')
        
from django.core.mail import send_mail
from django.conf import settings

# Utility function to send email


from django.core.mail import EmailMessage
from django.conf import settings
from rest_framework.views import APIView
from rest_framework import status
from django.conf import settings
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives

# def send_otp_email(subject, message, recipient_list):
#     try:
#         email_from = settings.DEFAULT_FROM_EMAIL
#         email = EmailMessage(subject, message, email_from, recipient_list)
#         email.content_subtype = "html"  # Support HTML content
#         print(email, 'email')
#         email.send()
#     except Exception as e:
#         print(f"Error sending OTP email: {e}")

def send_otp_email(subject, recipient_email_list, html_content):
    EMAIL_FROM = settings.DEFAULT_FROM_EMAIL
    msg = EmailMultiAlternatives(
        subject=subject,
        from_email=EMAIL_FROM,
        to=recipient_email_list,
    )
    msg.attach_alternative(html_content, "text/html")
    print(msg, 'msg')
    msg.send()


class GenerateOtpUsingEmailAPIView(APIView):
    """
    Generate OTP for user registration using email
    """
    authentication_classes = []  
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            serializer = EmailModelSerializer(data=data)

            if not serializer.is_valid():
                return generic_response(status.HTTP_400_BAD_REQUEST, serializer.errors)

            instance = serializer.save()
            data = {'email': instance.email, 'otp': instance.otp}

            # Prepare email content
            subject = 'Your OTP Code for Verification'
            html_content = f"""
                <html>
                  <body>
                    <h2>Hello!</h2>
                    <p>Your OTP code for email verification is:</p>
                    <h1 style="color:#2b6cb0;">{instance.otp}</h1>
                    <p>This code is valid for 10 minutes. Please do not share it with anyone.</p>
                    <br>
                    <p>Thanks,<br>Your App Team</p>
                  </body>
                </html>
            """
            recipient_list = [instance.email]
            try:
                # Send email
                send_otp_email(
                    subject=subject,
                    recipient_email_list=recipient_list,
                    html_content=html_content
                )
                print(send_otp_email, 'send_otp_email')
            except Exception as ex:
                return generic_response(status.HTTP_400_BAD_REQUEST, f'Email not working {str(ex)}')

            return generic_response(status.HTTP_201_CREATED, 'OTP sent successfully', data=data)

        except Exception as e:
            return generic_response(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Error while creating: {str(e)}')


class UserProfileAPIView(APIView):
    """
    User Profile API View
    """
    permission_classes = (IsAuthenticated, )

    def patch(self, request):
        try:
            user = request.user
            data = request.data
            if not user.user_type == 'USER':
                return generic_response(status.HTTP_403_FORBIDDEN, 'User is not a normal user')

            user_profile = User.objects.filter(id=user.id).first()
            print(user_profile, 'user_profile')
            if not user_profile:
                return generic_response(status.HTTP_404_NOT_FOUND, 'User profile not found')

            serializer = UserProfileSerializer(user_profile, data=data, partial=True)

            if not serializer.is_valid():
                return generic_response(status.HTTP_400_BAD_REQUEST, f'{serializer.errors}')

            serializer.save()
            return generic_response(status.HTTP_200_OK, 'User profile updated successfully', data=data)

        except Exception as e:
            return generic_response(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Error while updating: {str(e)}')

    def get(self, request):
        try:
            user = request.user
            print(user.user_type, 'user_type')
            if not user.user_type == 'USER':
                return generic_response(status.HTTP_403_FORBIDDEN, 'User is not a normal user')

            user_profile = User.objects.filter(id=user.id, user_type='USER').first()
            if not user_profile:
                return generic_response(status.HTTP_404_NOT_FOUND, 'User profile not found')

            serialized_data = GetUserProfileSerializer(user_profile).data
            return generic_response(status.HTTP_200_OK, 'User profile fetched successfully', data=serialized_data)

        except Exception as e:
            return generic_response(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Error while fetching: {str(e)}')


class SignalProviderProfileAPIView(APIView):
    """
    Signal Provider Profile API View
    """

    def patch(self, request, *args, **kwargs):
        try:
            user = request.user
            data = request.data
            if not user.user_type == 'SIGNAL_PROVIDER':
                return generic_response(status.HTTP_403_FORBIDDEN, 'User is not a signal provider')

            signal_provider_profile = User.objects.filter(id=user.id).first()
            if not signal_provider_profile:
                return generic_response(status.HTTP_404_NOT_FOUND, 'Signal provider profile not found')

            serializer = SignalProviderProfileSerializer(signal_provider_profile, data=data, partial=True)

            if not serializer.is_valid():
                return generic_response(status.HTTP_400_BAD_REQUEST, serializer.errors)

            instance = serializer.save()
            return generic_response(status.HTTP_200_OK, 'Signal provider profile updated successfully')

        except Exception as e:
            return generic_response(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Error while updating: {str(e)}')

    def get(self, request):
        try:
            user = request.user
            if not user.user_type == 'SIGNAL_PROVIDER':
                return generic_response(status.HTTP_403_FORBIDDEN, 'User is not a signal provider')

            signal_provider_profile = User.objects.filter(id=user.id).first()
            if not signal_provider_profile:
                return generic_response(status.HTTP_404_NOT_FOUND, 'Signal provider profile not found')

            serialized_data = SignalProviderProfileSerializer(signal_provider_profile).data
            return generic_response(status.HTTP_200_OK, data=serialized_data)

        except Exception as e:
            return generic_response(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Error while fetching: {str(e)}')


class AssestAPIView(APIView):
    """
    Asset API View
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            if not user.is_superuser:
                return generic_response(status.HTTP_400_BAD_REQUEST, 'User is not Superuser')

            data = request.data
            serializer = AssetSerializer(data=data)

            if not serializer.is_valid():
                return generic_response(status.HTTP_400_BAD_REQUEST, serializer.errors)

            serializer.save()
            return generic_response(status.HTTP_201_CREATED, 'Asset created successfully', data=serializer.data)

        except Exception as ex:
            return generic_response(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Error while creating: {str(ex)}')

    def patch(self, request, *args, **kwargs):
        try:
            data = request.data
            user = request.user
            if not user.is_superuser:
                return generic_response(status.HTTP_404_NOT_FOUND, 'User is not superuser')

            asset_id = Assest.objects.filter(id=kwargs['id']).first()
            if not asset_id:
                return generic_response(status.HTTP_404_NOT_FOUND, 'Asset not found')

            serialized_data = AssetSerializer(asset_id, data=data, partial=True)

            if not serialized_data.is_valid():
                return generic_response(status.HTTP_400_BAD_REQUEST, serialized_data.errors)

            serialized_data.save()
            return generic_response(status.HTTP_200_OK, 'Asset updated successfully', data=serialized_data.data)    

        except Exception as e:
            return generic_response(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Error while updating: {str(e)}')

    def get(self, request):
        try:
            user = request.user
            if not user.is_superuser:
                return generic_response(status.HTTP_404_NOT_FOUND, 'User not Superuser')

            assets = Asset.objects.all()
            serialized_data = AssetSerializer(assets, many=True).data
            return get_pure_paginated_response(serialized_data, request)

        except Exception as e:
            return generic_response(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Error while fetching: {str(e)}')


class SingnalProviderPostAPIView(APIView):
    """
    Signal Provider Post API View
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            posts = SingnalProviderPost.objects.all(is_premium=False)
            serialized_data = SingnalProviderPostSerializer(posts, many=True).data
            return get_pure_paginated_response(serialized_data, request)

        except Exception as e:
            return generic_response(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Error while fetching: {str(e)}')

    def post(self, request):
        try:
            data = request.data
            user = request.user
            if not user.user_type == 'SignalProvider':
                return generic_response(status.HTTP_403_FORBIDDEN, 'User is not a signal provider')

            serializer = SignalProviderPostSerializer(data=data)

            if not serializer.is_valid():
                return generic_response(status.HTTP_400_BAD_REQUEST, serializer.errors)

            serializer.save()
            return generic_response(status.HTTP_201_CREATED, 'Signal provider post created successfully')

        except Exception as e:
            return generic_response(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Error while creating: {str(e)}')

   
    def delete(self, request):
        try:
            user  = request.user
            if not user.is_superuer:
                return generic_response(status.HTTP_403_FORBIDDEN, 'User is not a superuser')

            signal_provider = SignalProviderProfile.objects.filter(id=signal_provider_id).first()
            if not signal_provider:
                return generic_response(status.HTTP_404_NOT_FOUND, 'Signal provider not found')

            signal_provider.delete()
            return generic_response(status.HTTP_200_OK, 'Signal provider deleted successfully')

        except Exception as e:
            return generic_response(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Error while deleting: {str(e)}')


class AssetBasedSignalProviderPostAPIView(APIView):
    permission_classes = (IsAuthenticated, )
    def get(self, request):
        try:

            assest = request.GET.get('assest')
            signal_provider_post = SingnalProviderPost.objects.filter(assest=asset)

            if not signal_provider_post:
                return generic_response(status.HTTP_404_NOT_FOUND, f'Signal provider post not found for this {assest}')

            serialized_data = AssetBasedSignalProviderSerializer(signal_provider_post, many=True).data

            return generic_response(status.HTTP_200_OK, data=serialized_data)

        except Exception as ex:
            return generic_response(status.HTTP_404_NOT_FOUND, f'Error while getting: {str(ex)}')


class FollowRequestAPIView(APIView):
    def post(self, request):
        """
        Follow Request API View
        """
        try:
            data = request.data
            user = request.user
            if not user.user_type == 'User':
                return generic_response(status.HTTP_403_FORBIDDEN, 'User is not a normal user')

            user = User.objects.filter(id=user.id).first()
            if not user:
                return generic_response(status.HTTP_404_NOT_FOUND, 'User not found')

            data['user'] = user.id if user else None

            follow_request_serializer = FollowRequestSerializer(data=data)

            if not follow_request_serializer.is_valid():
                return generic_response(status.HTTP_400_BAD_REQUEST, follow_request_serializer.errors)

            follow_request_serializer.save()
            return generic_response(status.HTTP_201_CREATED, 'Follow request created successfully')

        except Exception as e:
            return generic_response(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Error while sending follow request: {str(e)}')


class FollowingAPIView(APIView):
    """
    Following API View
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            if not user.user_type == 'User':
                return generic_response(status.HTTP_403_FORBIDDEN, 'User is not a normal user')

            following = UserFollewRequest.objects.filter(user=user.id).first()
            if not following:
                return generic_response(status.HTTP_404_NOT_FOUND, 'Following not found')

            serialized_data = FollowingSerializer(following).data
            return generic_response(status.HTTP_200_OK, 'Following fetched successfully', data=serialized_data)

        except Exception as e:
            return generic_response(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Error while fetching: {str(e)}')


class FollwersAPIView(APIView):
    """
    Followers API View
    """
    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            if not user.user_type == 'SignalProvider':
                return generic_response(status.HTTP_403_FORBIDDEN, 'User is not a normal user')

            followers = UserFollewRequest.objects.filter(signal_provider=user.id).first()
            if not followers:
                return generic_response(status.HTTP_404_NOT_FOUND, 'Followers not found')

            serialized_data = FollowersSerializer(followers).data
            return generic_response(status.HTTP_200_OK, 'Followers fetched successfully', data=serialized_data)

        except Exception as e:
            return generic_response(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Error while fetching: {str(e)}')


class LikedPostAPIView(APIView):
    """"
    Liked Post API View
    """
    def post(self, request):
        try:
            user = request.user
            if not user.user_type == 'User':
                return generic_response(status.HTTP_403_FORBIDDEN, 'User is not a normal user')

            serialized_data = LikeSingalProviderPostSerializer(data=request.data)

            if not serialized_data.is_valid():
                return generic_response(status.HTTP_400_BAD_REQUEST, serializer.errors)

            serialized_data.save()
            return generic_response(status.HTTP_201_CREATED, 'Post liked successfully', data=serialized_data.data)

        except Exception as e:
            return generic_response(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Error while creating: {str(e)}')

    def get(self, request):
        try:

            data = request.data
            user = request.user
            if not user.user_type == 'User':
                return generic_response(status.HTTP_403_FORBIDDEN, 'User is not a normal user')

            like = LikeSingalProviderPost.objects.filter(user=user.id).first()

            if not like:
                return generic_response(status.HTTP_404_NOT_FOUND, 'Like not found')

            liked_serializer = LikeSingalProviderPostSerializer(like).data
            return generic_response(status.HTTP_200_OK, 'Liked post fetched successfully', data=liked_serializer)

        except Exception as e:
            return generic_response(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Error while fetching: {str(e)}')


class CommentSignalProviderPostAPIView(APIView):
    """
    Comment API View
    """
    def post(self, request):
        try:
            user = request.user
            if not user.user_type == 'User':
                return generic_response(status.HTTP_403_FORBIDDEN, 'User is not a normal user')

            serialized_data = CommentSignalProviderPostSerializer(data=request.data)

            if not serialized_data.is_valid():
                return generic_response(status.HTTP_400_BAD_REQUEST, serializer.errors)

            serialized_data.save()
            return generic_response(status.HTTP_201_CREATED, 'Comment created successfully', data=serialized_data.data)

        except Exception as e:
            return generic_response(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Error while creating: {str(e)}')

    def get(self, request):
        try:
            user = request.user
            if not user.user_type =='User':
                return generic_response(status.HTTP_403_FORBIDDEN, 'User is not a normal user')

            comment = ComentSignalProviderPost.objects.filter(user=user.id)
            if not comment:
                return generic_response(status.HTTP_404_NOT_FOUND, 'Comment not found')

            serialized_data = CommentSignalProviderPostSerializer(comment, many=True).data
            return generic_response(status.HTTP_200_OK, 'Comment fetched successfully', data=serialized_data)
        except Exception as e:
            return generic_response(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Error while fetching: {str(e)}')

    
class LikeCommentAPIView(APIView):
    """"
    Like Comment API View
    """
    def post(self, request):
        try:
            data = request.data
            user = request.user

            if not user.user_type == 'User':
                return generic_response(status.HTTP_403_FORBIDDEN, 'User is not a normal user')

            data['user'] = user.id if user else None
            serialized_data = LikeCommentSerializer(data=data)

            if not serialized_data.is_valid():
                return generic_response(status.HTTP_400_BAD_REQUEST, serialized_data.errors)

            serialized_data.save()
            return generic_response(status.HTTP_201_CREATED, 'Comment liked successfully', data=serialized_data.data)

        except Exception as e:
            return generic_response(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Error while creating: {str(e)}')


class BlockUserAPIView(APIView):
    """
    Block User API View
    """
    def post(self, request):
        try:
            data = request.data
            user = request.user

            if not user.user_type == 'SignalProvider':
                return generic_response(status.HTTP_403_FORBIDDEN, 'User is not a normal user')

            data['singal_provider'] = user.id if user else None
            serialized_data = BlockUserSerializer(data=data)

            if not serialized_data.is_valid():
                return generic_response(status.HTTP_400_BAD_REQUEST, serialized_data.errors)

            serialized_data.save()
            return generic_response(status.HTTP_201_CREATED, 'User blocked successfully', data=serialized_data.data)

        except Exception as e:
            return generic_response(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Error while creating: {str(e)}')

    def get(self, request):
        try:
            user = request.user
            if not user.user_type == 'SignalProvider':
                return generic_response(status.HTTP_403_FORBIDDEN, 'User is not a normal user')

            block_user = BlockUser.objects.filter(user=user.id)
            if not block_user:
                return generic_response(status.HTTP_404_NOT_FOUND, 'Block user not found')

            serialized_data = BlockUserSerializer(block_user, many=True).data
            return generic_response(status.HTTP_200_OK, 'Blocked user fetched successfully', data=serialized_data)

        except Exception as ex:
            return generic_response(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Error while fetching: {str(ex)}')

class UserFollewRequestAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        try:
            data = request.data
            user = request.user.id

            data['user'] = user

            serialized_data = UserFollewRequestSerializer(data=data)

            if not serialized_data.is_valid():
                return generic_response(status.HTTP_404_NOT_FOUND, f'{serialized_data.errors}')

            serialized_data.save()
            return generic_response(status.HTTP_201_CREATED, 'User Follow request created')

        except Exception as ex:
            return generic_response(status.HTTP_404_NOT_FOUND, f'Error while geting: {str(ex)}')

    def get(self, request):
        try:
            user = request.user.id
            user = UserFollewRequest.objects.filter(user=user)
            if not user:
                return generic_response(status.HTTP_200_OK, 'User not found')

            serialized_data = UserFollewRequestSerializer(user, many=True).data

            return generic_response(status.HTTP_200_OK, data=serialized_data)

        except Exception as ex:
            return generic_response(status.HTTP_404_NOT_FOUND, f'Error while getting: {str(ex)}')

class PlanTypeAPIView(APIView):

    permission_classes = (IsAuthenticated, )

    def get(self, request):
        try:
            plan_types = PlanType.objects.all()
            serialized_data = PlanTypeSerializer(plan_types, many=True).data
            return get_pure_paginated_response(serialized_data, request)

        except Exception as e:
            return generic_response(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Error while fetching: {str(e)}')


class SubscriptionPlan(APIView):
    permission_classes = (IsAuthenticated, )
    def get(self, request):
        try:
            subscription_plans = SubscriptionPlan.objects.all()
            serialized_data = SubscriptionPlanSerializer(subscription_plans, many=True).data
            return get_pure_paginated_response(serialized_data, request)

        except Exception as e:
            return generic_response(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Error while fetching: {str(e)}')


class SubscriptionPlanDetailAPIView(APIView):
    permission_classes = (IsAuthenticated, )
    def get(self, request, subscription_id):
        try:
            subscription_plan = SubscriptionPlan.objects.filter(id=subscription_id).first()
            if not subscription_plan:
                return generic_response(status.HTTP_404_NOT_FOUND, 'Subscription plan not found')

            serialized_data = SubscriptionPlanSerializer(subscription_plan).data
            return generic_response(status.HTTP_200_OK, 'Subscription plan fetched successfully', data=serialized_data)

        except Exception as e:
            return generic_response(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Error while fetching: {str(e)}')





