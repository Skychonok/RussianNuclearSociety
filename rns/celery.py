from celery import Celery
import os

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "rns.settings"
)

app = Celery("rns")

app.config_from_object(
    "django.conf:settings",
    namespace="CELERY"
)

app.autodiscover_tasks()