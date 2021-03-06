from django.template import Template, Context
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from health.celery import app
from diets.models import Diet
from twilio.rest import Client
from django.contrib.auth.models import User
from celery.task import periodic_task
from django.conf import settings


'''Module for define celery tasks'''

#sending sms at the same time every day for each user


REPORT_TEMPLATE_BREAKFAST = """
MAKE BREAKFAST
"""
users = User.objects.all()

diets = Diet.objects.all()

'''Take all programs and send sms for each user who has diet'''


@app.task
def send_sms_breakfast():
    for diet in diets:
        print(diet.subscriber.profile.phone)
        '''program = Diet.objects.filter(subscriber=user)
        template = Template(REPORT_TEMPLATE_BREAKFAST)
        message_to_broadcast = f'{diet.subscriber.profile.phone}!Time for making breakfast. Dont forget eat it!\n'
                               f'{diet.breakfast_time}\n'
        print(user.username)
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=message_to_broadcast,
            from_='+12526240484',
            to=diet.subscriber.profile.phone
        )'''
        print(diet.subscriber.profile.phone + ' BREAKFAST every 1 minute')


@app.task
def send_sms_dinner():
    for user in users:
        program = Diet.objects.filter(subscriber=user)
        template = Template(REPORT_TEMPLATE_BREAKFAST)
        message_to_broadcast = f'{user.username}!Time for making dinner. Dont forget eat it!\n'
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
