from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date


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
                              default='draft')
    duration = models.IntegerField()
    # topics

    class Meta:
        ordering = ('planning_date',)

    def __str__(self):
        return self.title


@property
def is_past_due(self):
    return date.today() > self.date