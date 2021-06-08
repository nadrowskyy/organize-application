from django.db import models
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from django.db.models.signals import post_migrate
from django.contrib.auth import get_user_model


class Event(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Szkic'),
        ('publish', 'Opublikowano')
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250,
                            unique_for_date='planning_date', default=None)
    description = models.TextField(verbose_name='opis wydarzenia', blank=True, max_length=1000)
    created = models.DateTimeField(auto_now_add=True)
    planning_date = models.DateTimeField(blank=True, null=True)
    publish = models.DateTimeField(default=timezone.now)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)
    want_to_listen = models.ManyToManyField(User, related_name='want_to_listen', default=None, blank=True, null=True)
    status = models.CharField(max_length=15,
                              choices=STATUS_CHOICES,
                              default='publish')
    duration = models.IntegerField(blank=True, null=True)
    icon = models.FileField(upload_to='icons/', default='icons/default.png', null=True)
    attachment = models.FileField(upload_to='attachments/', blank=True, null=True)
    link = models.CharField(max_length=1000, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Event, self).save(*args, **kwargs)

    # topics

    class Meta:
        ordering = ('planning_date',)

    def __str__ (self):
        return self.title


class Polls(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, default=None, blank=True)
    if_active = models.BooleanField(default=False, blank=True)
    since_active = models.DateField(blank=True, null=True, default=None)
    till_active = models.DateField(blank=True, null=True, default=None)
    if_sent_notification = models.BooleanField(blank=True, null=True, default=False)


class Dates(models.Model):
    poll = models.ForeignKey(Polls, on_delete=models.CASCADE)
    date = models.DateTimeField(blank=True, null=True)
    count = models.IntegerField(null=True, blank=True, default=0)
    users = models.ManyToManyField(User, related_name='users', default=None, blank=True)


class Subject(models.Model):
    proposer = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique_for_date='created', default=None)
    description = models.TextField(verbose_name='opis tematu', max_length=400)
    created = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='like', default=None, blank=True)
    like_count = models.IntegerField(default='0')
    want_to_lead = models.ManyToManyField(User, related_name='want_to_lead', default=None, blank=True)
    lead_count = models.IntegerField(default='0')

    def save (self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Subject, self).save(*args, **kwargs)

    def __str__ (self):
        return self.title

    class Meta:
        ordering = ('-created',)


class EmailSet(models.Model):
    delay_leader = models.IntegerField(default=3)
    delay_all = models.IntegerField(default=2)
    # USTAWIENIA SERWERA POCZTY
    EMAIL_BACKEND = models.CharField(max_length=50)
    EMAIL_HOST = models.CharField(max_length=30)
    EMAIL_PORT = models.IntegerField(default=587)
    EMAIL_HOST_USER = models.CharField(max_length=50)
    EMAIL_HOST_PASSWORD = models.CharField(max_length=100)
    EMAIL_USE_TLS = models.BooleanField(default=True)
    DEFAULT_FROM_EMAIL = models.CharField(max_length=50)
    EMAIL_HEADER = models.CharField(max_length=50)


class EventNotification(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    leader = models.ForeignKey(User, on_delete=models.CASCADE)
    if_sent_leader = models.BooleanField(default=False)
    if_sent_all = models.BooleanField(default=False)
    settings = models.ForeignKey(EmailSet, on_delete=models.CASCADE, default=1)


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    content = models.TextField(max_length=1000)
    if_edited = models.BooleanField(default=False)
    if_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ('-created',)
