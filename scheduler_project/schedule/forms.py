from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.db import models
from .models import Event, Subject
import datetime


class UserFullnameChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        fullname = obj.get_full_name()
        return fullname


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')


class CreateEvent(ModelForm):
    organizer = UserFullnameChoiceField(queryset=User.objects.all())
    planning_date = forms.DateTimeField(initial=datetime.date.today)
    icon = forms.FileField()
    attachment = forms.FileField()

    class Meta:
        model = Event
        fields = ('title', 'description', 'organizer', 'planning_date', 'duration', 'icon', 'attachment')


class SubjectForm(ModelForm):
    #if_lead = forms.CheckboxInput()
    planning_date = forms.DateTimeField(initial=datetime.date.today)

    class Meta:
        model = Subject
        fields = ('title', 'description', 'planning_date', 'duration')
