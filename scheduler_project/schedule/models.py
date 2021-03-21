from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Event(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Szkic'),
        ('published', 'Opublikowano')
    )
    title = models.CharField(max_length=200)
    description = models.TextField(verbose_name='opis wydarzenia')
    created = models.DateTimeField(auto_now_add=True)
    planning_date = models.DateTimeField()
    publish = models.DateTimeField(default=timezone.now)
    # participants
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)
    # topics
    status = models.CharField(max_length=15,
                              choices=STATUS_CHOICES,
                              default='draft')
    # comments
    duration = models.IntegerField()

    class Meta:
        ordering = ('-publish',)

    def __str__(self):
        return self.title
