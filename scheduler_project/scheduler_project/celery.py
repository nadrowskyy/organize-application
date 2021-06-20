from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scheduler_project.settings')

if os.environ.get('DOCKERIZE') == "1":
    app = Celery('scheduler_project', broker="amqp://rabbitmq")
else:
    app = Celery('scheduler_project')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.timezone = 'Europe/Warsaw'
app.conf.beat_schedule = {
    'send-email-notifications-for-all': {
        'task': 'schedule.tasks.send_notification_all',
        'schedule': crontab(minute='*/5')
    },
    'send-email-notifications-for-organizer': {
        'task': 'schedule.tasks.send_notification_organizer',
        'schedule': crontab(minute='*/5')
    },
    'send-poll-notification-cron': {
        'task': 'schedule.tasks.send_poll_notification_cron',
        'schedule': crontab(minute='*/10')
    },
    'deactive-poll': {
        'task': 'schedule.tasks.deactive_poll',
        'schedule': crontab(minute=55, hour=23)
    }
}

app.autodiscover_tasks()
