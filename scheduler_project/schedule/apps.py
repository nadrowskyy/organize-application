from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .models import populate_models


class ScheduleConfig(AppConfig):
    name = 'schedule'
    verbose_name = 'schedule'
