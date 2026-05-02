from celery import shared_task
from django.conf import settings
from django.db import transaction

from .models import ProgramSubscription, SmsDeliveryLog
from .services import due_meal_logs
from .sms import get_sms_client


def meal_reminder_body(log):
    return (
        f'Hi {log.subscription.subscriber.username}! '
        f'Time for {log.get_meal_display().lower()}. '
        'Do not forget to eat it.'
    )


def program_confirmation_body(subscription):
    return (
        f'Hello {subscription.subscriber.username}! '
        f'You subscribed to {subscription.meal_plan.title}.\n'
        f'Breakfast at {subscription.breakfast_time}\n'
        f'Lunch at {subscription.lunch_time}\n'
        f'Dinner at {subscription.dinner_time}\n'
    )


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_sms_delivery_log(self, log_id):
    if not settings.SMS_REMINDERS_ENABLED:
        return {'status': 'disabled'}

    log = SmsDeliveryLog.objects.select_related(
        'subscription__subscriber__profile',
        'subscription__meal_plan',
    ).get(id=log_id)
    try:
        provider_sid = get_sms_client().send(
            to=log.subscription.subscriber.profile.phone,
            body=meal_reminder_body(log),
        )
    except Exception as exc:
        SmsDeliveryLog.objects.filter(id=log.id).update(
            status=SmsDeliveryLog.FAILED,
            error=str(exc),
        )
        raise self.retry(exc=exc) from exc

    SmsDeliveryLog.objects.filter(id=log.id).update(
        status=SmsDeliveryLog.SENT,
        provider_sid=provider_sid,
        error='',
    )
    return {'status': SmsDeliveryLog.SENT, 'provider_sid': provider_sid}


@shared_task
def send_due_meal_reminders():
    if not settings.SMS_REMINDERS_ENABLED:
        return {'scheduled': 0, 'status': 'disabled'}

    logs = due_meal_logs()
    for log in logs:
        transaction.on_commit(lambda log_id=log.id: send_sms_delivery_log.delay(log_id))
    return {'scheduled': len(logs)}


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_program_confirmation(self, subscription_id):
    if not settings.SMS_REMINDERS_ENABLED:
        return {'status': 'disabled'}

    subscription = ProgramSubscription.objects.select_related(
        'subscriber__profile',
        'meal_plan',
    ).get(id=subscription_id)
    try:
        provider_sid = get_sms_client().send(
            to=subscription.subscriber.profile.phone,
            body=program_confirmation_body(subscription),
        )
    except Exception as exc:
        raise self.retry(exc=exc) from exc
    return {'status': SmsDeliveryLog.SENT, 'provider_sid': provider_sid}
