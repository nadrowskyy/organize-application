from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.db import models
from .models import Event, Subject
import datetime
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm


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
    icon = forms.FileField(required=False)
    attachment = forms.FileField(required=False)

    class Meta:
        model = Event
        fields = ('title', 'description', 'organizer', 'planning_date', 'duration', 'icon', 'attachment')


class SubjectForm(ModelForm):
    class Meta:
        model = Subject
        fields = ('title', 'description')


class ChangePassword(PasswordChangeForm):
    error_messages = dict(PasswordChangeForm.error_messages, **{
        'passwords_match': ("Nowe hasło jest takie same jak poprzednie hasło."
                             "Wprowadź jeszcze raz"),
    })


    def clean_new_password1(self):
        old_pass = self.cleaned_data.get('old_password')
        new_pass = self.cleaned_data.get('new_password1')
        if old_pass and new_pass:
            if old_pass == new_pass:
                raise forms.ValidationError(
                    self.error_messages['passwords_match'], code='passwords_match'
                )
        return new_pass
