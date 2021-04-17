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
