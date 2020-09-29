import os
from celery import Celery
from celery.schedules import crontab
import schedule
from diets.models import Diet
from django.contrib.auth.models import User

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barbershop.settings')

app = Celery('barbershop')
app.config_from_object('django.conf:settings')

# Registration tasks

# schedule.every().day.at().do()

users = User.objects.all()
diets = Diet.objects.all()
breakfast_time = []
lunch_time = []
for i in diets:
    if i.subscriber:
        breakfast_time.append(i.breakfast_time)

app.conf.beat_schedule = {

    'send-notification-every-day-breakfast': {
        'task': 'diets.tasks.send_sms_breakfast',
        'schedule': crontab(minute='*/30', hour='8'),
    },
    'send-notification-every-day-lunch': {
        'task': 'diets.tasks.send_sms_lunch',
        'schedule': crontab(minute='*/20',
                            hour=14
                            ),
    },
    'send-notification-every-day-dinner': {
        'task': 'diets.tasks.send_sms_lunch',
        'schedule': crontab(minute='*/30',
                            hour=21
                            ),
    }
}

app.autodiscover_tasks()
