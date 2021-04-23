from celery import shared_task
from django.core.mail import send_mail, get_connection, send_mass_mail
from django.core.mail import EmailMessage
from .models import EmailSet, Event, EventNotification
from django.contrib.auth.models import User
from datetime import datetime, timedelta


@shared_task
def send_notification_all():

    delay_all = EmailSet.objects.filter(pk=1)[0].delay_all
    to_sent_1 = EventNotification.objects.filter(if_sent_all=False)
    to_sent_list_1 = []
    for el in to_sent_1:
        to_sent_list_1.append((Event.objects.filter(id=el.event_id)[0].id))

    to_sent_2 = Event.objects.filter(planning_date__date__gte=datetime.now())
    to_sent_list_2 = []
    for el in to_sent_2:
        to_sent_list_2.append(el.id)

    intersection = list(set(to_sent_list_1).intersection(to_sent_list_2))

    mailing_list_all = []
    for el in intersection:
        event = Event.objects.filter(id=el)[0]
        if event.planning_date - datetime.now() <= timedelta(days=delay_all):
            email = User.objects.filter(id=event.organizer_id)[0].email
            mailing_list_all.append(email)

    if mailing_list_all:
        print('------------------------')
        print('WYSYLANIE')
        mail_settings = EmailSet.objects.filter(pk=1)[0]
        host = mail_settings.EMAIL_HOST
        port = mail_settings.EMAIL_PORT
        username = mail_settings.EMAIL_HOST_USER
        password = mail_settings.EMAIL_HOST_PASSWORD
        use_tls = bool(mail_settings.EMAIL_USE_TLS)

        with get_connection(host=host, port=port, username=username, password=password, use_tls=use_tls) as conn:
            msg = EmailMessage(subject='Tytuł', body='Treść maila', from_email='django', to=mailing_list_all,
                         connection=conn)
            msg.send(fail_silently=True)

        for el in to_sent_1:
            el.if_sent_all = True
            el.save()

    return None


@shared_task
def send_notification_organizer():

    delay_leader = EmailSet.objects.filter(pk=1)[0].delay_leader
    to_sent_1 = EventNotification.objects.filter(if_sent_leader=False)
    to_sent_list_1 = []
    for el in to_sent_1:
        to_sent_list_1.append((Event.objects.filter(id=el.event_id)[0].id))

    to_sent_2 = Event.objects.filter(planning_date__date__gte=datetime.now())
    to_sent_list_2 = []
    for el in to_sent_2:
        to_sent_list_2.append(el.id)

    intersection = list(set(to_sent_list_1).intersection(to_sent_list_2))

    mailing_list_leader = []
    for el in intersection:
        event = Event.objects.filter(id=el)[0]
        if event.planning_date - datetime.now() <= timedelta(days=delay_leader):
            email = User.objects.filter(id=event.organizer_id)[0].email
            mailing_list_leader.append(email)
    print(mailing_list_leader)
    if mailing_list_leader:
        print('------------------------')
        print('WYSYLANIE')
        mail_settings = EmailSet.objects.filter(pk=1)[0]
        host = mail_settings.EMAIL_HOST
        port = mail_settings.EMAIL_PORT
        username = mail_settings.EMAIL_HOST_USER
        password = mail_settings.EMAIL_HOST_PASSWORD
        use_tls = bool(mail_settings.EMAIL_USE_TLS)

        with get_connection(host=host, port=port, username=username, password=password, use_tls=use_tls) as conn:
            msg = EmailMessage(subject='Tytuł', body='Treść maila', from_email='django', to=mailing_list_leader,
                         connection=conn)
            msg.send(fail_silently=True)

        for el in to_sent_1:
            el.if_sent_leader = True
            el.save()

    return None
