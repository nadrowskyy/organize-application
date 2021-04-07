from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
from vote.models import VoteModel, Vote
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType


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
    status = models.CharField(max_length=15,
                              choices=STATUS_CHOICES,
                              default='publish')
    duration = models.IntegerField()
    icon = models.FileField(upload_to='icons/', default='media/icons/default.jpg')
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

    def __str__(self):
        return f'{self.leader.username} {self.if_lead} {self.subject.title}'
