from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import User
from hairstyle.models import Recipe
import datetime
from django.core.mail import send_mail
from twilio.rest import Client


# Create your models here.


class Weight(models.Model):
    user = models.ForeignKey(User, related_name="user", on_delete=models.CASCADE)
    weight = models.DecimalField(decimal_places=2, max_digits=5)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created',)


class Diet(models.Model):
    title = models.CharField(blank=True, max_length=100)
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    subscriber = models.ForeignKey(User, related_name='subscriber', on_delete=models.CASCADE, blank=True, null=True)
    description_of_diet = models.TextField(blank=True)
    amount_of_breakfast = models.IntegerField(default=1)
    breakfast = models.ManyToManyField(Recipe, blank=True, related_name='breakfast')
    breakfast_time = models.TimeField(blank=True)
    amount_of_lunch = models.IntegerField(default=1)
    lunch = models.ManyToManyField(Recipe, blank=True, related_name='lunch')
    lunch_time = models.TimeField(blank=True)
    second_lunch_time = models.TimeField(blank=True, null=True)
    amount_of_dinner = models.IntegerField(default=1)
    dinner = models.ManyToManyField(Recipe, blank=True, related_name='dinner')
    dinner_time = models.TimeField(blank=True)
    is_active = models.BooleanField(default=True)
    date_subscribe = models.DateField(default=datetime.date.today)

    def __str__(self):
        return self.title

    '''def save(self, *args, **kwargs):
        message_to_broadcast = (f'Hello {self.subscriber.username}! You just subscribed on {self.title}.\n'
                                f'Breakfast at {self.breakfast_time}\n'
                                f'Lunch at {self.lunch_time}\n'
                                f'Dinner at {self.dinner_time}\n'
                                f'Time now: {datetime.datetime.today().time()}')
        
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=message_to_broadcast,
            from_='+12526240484',
            to=self.subscriber.profile.phone
        )
        print(message.sid)
        return super(Diet, self).save(*args, **kwargs)'''
