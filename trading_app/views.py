from django.shortcuts import render
from rest_framework import APIView, status
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.core.cache.backends.base import DEFAULT_TIMEOUT
# Create your views here.
