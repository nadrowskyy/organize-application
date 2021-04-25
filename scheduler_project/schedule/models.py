from django.db import models
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.utils.text import slugify
from vote.models import VoteModel, Vote
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
    description = models.TextField(verbose_name='opis wydarzenia')
    created = models.DateTimeField(auto_now_add=True)
    planning_date = models.DateTimeField()
    publish = models.DateTimeField(default=timezone.now)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)
    want_to_listen = models.ManyToManyField(User, related_name='want_to_listen', default=None, blank=True)
    status = models.CharField(max_length=15,
                              choices=STATUS_CHOICES,
                              default='publish')
    duration = models.IntegerField()
    icon = models.FileField(upload_to='icons/', default='icons/default.png')
    attachment = models.FileField(upload_to='attachments/', blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Event, self).save(*args, **kwargs)

    # topics

    class Meta:
        ordering = ('planning_date',)

    def __str__(self):
        return self.title


class Subject(VoteModel, models.Model):
    proposer = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique_for_date='created', default=None)
    description = models.TextField(verbose_name='opis tematu', max_length=400)
    created = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='like', default=None, blank=True)
    like_count = models.IntegerField(default='0')
    want_to_lead = models.ManyToManyField(User, related_name='want_to_lead', default=None, blank=True)
    lead_count = models.IntegerField(default='0')


    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Subject, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class Lead(models.Model):
    #vote = models.OneToOneField('vote.vote', on_delete=models.CASCADE, default=None)
    leader = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    if_lead = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


    # def save(self, *args, **kwargs):
    #     self.slug = slugify(self.title)
    #     super(Lead, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.leader.username} {self.if_lead} {self.subject.title}'


class EmailSet(models.Model):
    delay_leader = models.IntegerField(default=3)
    delay_all = models.IntegerField(default=2)
    # USTAWIENIA SERWERA POCZTY
    EMAIL_BACKEND = models.CharField(default='django.core.mail.backends.smtp.EmailBackend', max_length=50)
    EMAIL_HOST = models.CharField(default='smtp.gmail.com', max_length=30)
    EMAIL_PORT = models.IntegerField(default=587)
    EMAIL_HOST_USER = models.CharField(default='carnetdjango@gmail.com', max_length=50)
    EMAIL_HOST_PASSWORD = models.CharField(default='ozebijqmlwhlahqw', max_length=100)
    EMAIL_USE_TLS = models.BooleanField(default=True)
    DEFAULT_FROM_EMAIL = models.CharField(default='carnetdjango@gmail.com', max_length=50)
    EMAIL_HEADER = models.CharField(default='"FFT - Food For Thought" <fft@comarch.pl>', max_length=50)


class EventNotification(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    leader = models.ForeignKey(User, on_delete=models.CASCADE)
    if_sent_leader = models.BooleanField(default=False)
    if_sent_all = models.BooleanField(default=False)
    settings = models.ForeignKey(EmailSet, on_delete=models.CASCADE, default=1)
