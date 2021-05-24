from celery import shared_task
from scheduler_project.celery import app
from django.core.mail import send_mail, get_connection, send_mass_mail
from django.core.mail import EmailMessage
from .models import EmailSet, Event, EventNotification, Polls
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.template.loader import render_to_string
from django.template import loader
from django.shortcuts import get_object_or_404


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

    events_list = []
    for el in intersection:
        event = Event.objects.filter(id=el)[0]
        if event.planning_date - datetime.now() <= timedelta(days=delay_all):
            events_list.append(event)

    mailing_list_all = []
    user_mails = User.objects.all()
    for el in user_mails:
        mailing_list_all.append(el.email)

    if events_list:
        mail_settings = EmailSet.objects.filter(pk=1)[0]
        host = mail_settings.EMAIL_HOST
        port = mail_settings.EMAIL_PORT
        username = mail_settings.EMAIL_HOST_USER
        password = mail_settings.EMAIL_HOST_PASSWORD
        use_tls = bool(mail_settings.EMAIL_USE_TLS)
        email_body = render_to_string('schedule/email_template.html', context={'events': events_list})
        from_email = mail_settings.EMAIL_HEADER

        with get_connection(host=host, port=port, username=username, password=password, use_tls=use_tls) as conn:
            msg = EmailMessage(subject='Sprawdź nadchodzące szkolenia!', body=email_body, from_email=from_email,
                               to=mailing_list_all, connection=conn)
            msg.send(fail_silently=True)

        for el in events_list:
            tmp_not = EventNotification.objects.filter(event_id=el.id)[0]
            tmp_not.if_sent_all = True
            tmp_not.save()

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

    events_list = []
    for el in intersection:
        event = Event.objects.filter(id=el)[0]
        if event.planning_date - datetime.now() <= timedelta(days=delay_leader):
            events_list.append(event)

    user_event_dict = dict()
    for el in events_list:
        tmp = EventNotification.objects.filter(event_id=el.id)[0]
        user = User.objects.filter(id=tmp.leader_id)[0]
        user_event_dict[user] = []

    # mailing_list_organizers = []
    for el in events_list:
        tmp = EventNotification.objects.filter(event_id=el.id)[0]
        event = Event.objects.filter(id=el.id)[0]
        user = User.objects.filter(id=tmp.leader_id)[0]
        # mailing_list_organizers.append(user.email)
        user_event_dict[user].append(event)

    if user_event_dict:
        for user, events in user_event_dict.items():
            mail_settings = EmailSet.objects.filter(pk=1)[0]
            host = mail_settings.EMAIL_HOST
            port = mail_settings.EMAIL_PORT
            username = mail_settings.EMAIL_HOST_USER
            password = mail_settings.EMAIL_HOST_PASSWORD
            use_tls = bool(mail_settings.EMAIL_USE_TLS)
            email_body = render_to_string('schedule/email_template.html', context={'user': user, 'events': events})
            from_email = mail_settings.EMAIL_HEADER

            with get_connection(host=host, port=port, username=username, password=password, use_tls=use_tls) as conn:
                msg = EmailMessage(subject='Twoje nadchodzące szkolenia!', body=email_body, from_email=from_email,
                                   to=[user.email], connection=conn)
                msg.send(fail_silently=True)

            for el in events:
                tmp_not = EventNotification.objects.filter(event_id=el.id)[0]
                tmp_not.if_sent_leader = True
                tmp_not.save()

    return None


@app.task
def send_mail_register(email):
    user = User.objects.filter(email=email)[0]
    mail_settings = EmailSet.objects.filter(pk=1)[0]
    host = mail_settings.EMAIL_HOST
    port = mail_settings.EMAIL_PORT
    username = mail_settings.EMAIL_HOST_USER
    password = mail_settings.EMAIL_HOST_PASSWORD
    use_tls = bool(mail_settings.EMAIL_USE_TLS)
    from_email = mail_settings.EMAIL_HEADER
    email_body = render_to_string('schedule/register_message.html', context={'user': user})

    with get_connection(host=host, port=port, username=username, password=password, use_tls=use_tls) as conn:
        msg = EmailMessage(subject='Witaj w serwisie FFT!', body=email_body, from_email=from_email,
                           to=[email], connection=conn)
        msg.send(fail_silently=True)

    return None


@app.task
def send_poll_notification(poll_pk, draft_pk):
    poll = get_object_or_404(Polls, pk=poll_pk)
    event = get_object_or_404(Event, pk=draft_pk)
    mailing_list_all = []
    user_mails = User.objects.all()
    for el in user_mails:
        mailing_list_all.append(el.email)
    rendered_body = loader.render_to_string('schedule/poll_notification.html',
                                            {'poll': poll, 'event': event})
    mail_settings = EmailSet.objects.filter(pk=1)[0]
    host = mail_settings.EMAIL_HOST
    port = mail_settings.EMAIL_PORT
    username = mail_settings.EMAIL_HOST_USER
    password = mail_settings.EMAIL_HOST_PASSWORD
    use_tls = bool(mail_settings.EMAIL_USE_TLS)
    from_email = mail_settings.EMAIL_HEADER
    with get_connection(host=host, port=port, username=username, password=password,
                        use_tls=use_tls) as conn:
        msg = EmailMessage(subject='Zagłosuj w ankiecie!', body=rendered_body,
                           from_email=from_email,
                           to=mailing_list_all, connection=conn)
        msg.content_subtype = "html"
        msg.send(fail_silently=True)
    poll.if_sent_notification = True
    poll.save()

    return None


@shared_task
def send_poll_notification_cron():
    pass