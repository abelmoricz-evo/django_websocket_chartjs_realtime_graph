from __future__ import absolute_import, unicode_literals
from celery import task
#imports needed for the functions
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from .models import *
from django.contrib.auth.models import User
from users.models import *

def sendEmail(email, subject, to_email):
    print(email)
    return 0

@task()
def scheduledTask():
    #Get Subscriptions

    subject = '[Careers Portal] Weekly Job Notifications'
    email_jobs = {
    "title": "Job Notifications from Careers Portal",
    "shortDescription": "Thank you for subscribing to Careers Portal, job notifications. For more jobs visit https://careers-portal.co.za",
    "subtitle": "Careers Portal - The latest job opportunities, updated weekly",
    }
    
    sendEmail(email_jobs, subject,)