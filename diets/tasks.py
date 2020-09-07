from django.template import Template, Context
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from barbershop.celery import app
from diets.models import Diet
from twilio.rest import Client
from django.contrib.auth.models import User
from celery.task import periodic_task
from django.conf import settings

REPORT_TEMPLATE_BREAKFAST = """
MAKE BREAKFAST
"""
users = User.objects.all()


@app.task
def send_sms_breakfast():
    for user in users:
        '''program = Diet.objects.filter(subscriber=user)
        template = Template(REPORT_TEMPLATE_BREAKFAST)
        message_to_broadcast = f'{user.username}!Time for making breakfast. Dont forget eat it!'
        print(user.username)
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=message_to_broadcast,
            from_='+12526240484',
            to=user.profile.phone
        )'''
        print(user.profile.phone + ' BREAKFAST every 1 minute')


@app.task
def send_sms_dinner():
    for user in users:
        program = Diet.objects.filter(subscriber=user)
        template = Template(REPORT_TEMPLATE_BREAKFAST)
        message_to_broadcast = f'{user.username}!Time for making dinner. Dont forget eat it!'
        print(user.username)
        client = Client(settings.account_sid, settings.auth_token)
        message = client.messages.create(
            body=message_to_broadcast,
            from_='+12526240484',
            to=user.profile.phone
        )


@app.task
def send_sms_lunch():
    for user in users:
        program = Diet.objects.filter(subscriber=user)
        template = Template(REPORT_TEMPLATE_BREAKFAST)
        message_to_broadcast = f'{user.username}!Time for making lunch. Dont forget eat it!'
        print(user.username)
        client = Client(settings.account_sid, settings.auth_token)
        message = client.messages.create(
            body=message_to_broadcast,
            from_='+12526240484',
            to=user.profile.phone
        )
