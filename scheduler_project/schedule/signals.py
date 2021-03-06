from django.dispatch import receiver
from django.db.models.signals import post_save, pre_migrate, post_migrate
from .models import Event, EventNotification
from django.contrib.auth.models import User, Group
from django.contrib.auth import get_user_model


@receiver(post_migrate)
def populate_models(sender, **kwargs):
    group, created = Group.objects.get_or_create(name='admin')
    group.save()
    group, created = Group.objects.get_or_create(name='employee')
    group.save()

    User = get_user_model()
    if not User.objects.filter(username='superuser').exists():
        User.objects.create_superuser(username='superuser',
                                      email='super@email.com',
                                      password='super')
        suser = User.objects.get(username='superuser')
        admin = Group.objects.get(name='admin')
        suser.groups.add(admin)



@receiver(post_migrate)
def email_setter(sender, **kwargs):
    from .models import EmailSet
    email, created = EmailSet.objects.get_or_create(pk=1)
    email.save()


@receiver(post_save, sender=Event)
def create_notification(sender, instance, created, **kwargs):
    if created:
        tmp = Event.objects.filter(title=instance.title)[0]
        EventNotification.objects.create(event=instance, leader=tmp.organizer)
