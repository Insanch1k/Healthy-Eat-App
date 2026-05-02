from .base import *  # noqa: F401,F403
from .base import env_bool, env_list

DEBUG = env_bool("DJANGO_DEBUG", True)
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", ["localhost", "127.0.0.1", "0.0.0.0"])
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
SMS_REMINDERS_ENABLED = env_bool("SMS_REMINDERS_ENABLED", False)
