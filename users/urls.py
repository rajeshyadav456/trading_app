from django.contrib import admin
from django.urls import path, include
from .views import GenerateOtpAPIView, GenerateOtpUsingEmailAPIView


urlpatterns = [
    path('generate_otp/', GenerateOtpAPIView.as_view(), name='generate_otp'),
    path('generate_otp_using_email/', GenerateOtpUsingEmailAPIView.as_view(), name='generate_otp_using_email'),
]






