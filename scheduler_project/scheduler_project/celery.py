from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scheduler_project.settings')

app = Celery('scheduler_project')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.timezone = 'Europe/Warsaw'
app.conf.beat_schedule = {
    'send-email-notifications-for-all': {
        'task': 'schedule.tasks.send_notification_all',
        'schedule': 10
    },
    'send-email-notifications-for-organizer': {
        'task': 'schedule.tasks.send_notification_organizer',
        'schedule': 10
    }
}
app.autodiscover_tasks()