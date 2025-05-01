from django.contrib import admin
from django.urls import path, include
from .views import UserProfileAPIView, GenerateOtpAPIView, GenerateOtpUsingEmailAPIView,\
RegisterAPIView, SignalProviderProfileAPIView, AssestAPIView, AssetBasedSignalProviderPostAPIView


urlpatterns = [
    path('generate_otp/', GenerateOtpAPIView.as_view(), name='generate_otp'),
    path('generate_otp_using_email/', GenerateOtpUsingEmailAPIView.as_view(), name='generate_otp_using_email'),
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('update_user_profile/', UserProfileAPIView.as_view(), name='user_profile'),
    path('update_signal_provider_profile/', SignalProviderProfileAPIView.as_view(), name='signal_provider_profile'),
    path('get_user_profile/', UserProfileAPIView.as_view(), name='get_user_profile'),
    path('get_signal_provider_profile/', SignalProviderProfileAPIView.as_view(), name='get_signal_provider_profile'),
    path('create_asset/', AssestAPIView.as_view(), name='create_asset'),
    path('udpate_asset/', AssestAPIView.as_view(), name='udpate_asset'),
    path('get_asset/', AssestAPIView.as_view(), name='get_asset'),
    path('asset_based_signal_provider_post_api/', AssetBasedSignalProviderPostAPIView.as_view(), name='asset_based_signal_provider_post_api')

]



































