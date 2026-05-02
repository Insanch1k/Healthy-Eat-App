from django.conf import settings
from twilio.rest import Client


class SmsConfigurationError(RuntimeError):
    pass


class TwilioSmsClient:
    def __init__(self, account_sid=None, auth_token=None, from_number=None):
        self.account_sid = account_sid or settings.TWILIO_ACCOUNT_SID
        self.auth_token = auth_token or settings.TWILIO_AUTH_TOKEN
        self.from_number = from_number or settings.TWILIO_FROM_NUMBER
        if not all([self.account_sid, self.auth_token, self.from_number]):
            raise SmsConfigurationError('Twilio settings are incomplete.')
        self.client = Client(self.account_sid, self.auth_token)

    def send(self, to, body):
        message = self.client.messages.create(
            body=body,
            from_=self.from_number,
            to=to,
        )
        return message.sid


def get_sms_client():
    return TwilioSmsClient()
