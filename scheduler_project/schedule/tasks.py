# from celery import task
from django.core.mail import send_mail, send_mass_mail
from .models import Event


# @task
def sent_event_notification():

    pass
