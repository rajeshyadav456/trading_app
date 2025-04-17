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
# Create your views here.

class GenerateOtpAPIView(APIView):
    """
    Generate OTP for user registration
    """
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

            # Send email
            send_otp_email(
                subject=subject,
                recipient_email_list=recipient_list,
                html_content=html_content
            )

            return generic_response(status.HTTP_201_CREATED, 'OTP sent successfully', data=data)

        except Exception as e:
            return generic_response(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Error while creating: {str(e)}')
