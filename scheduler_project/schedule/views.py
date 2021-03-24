from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm


def login_page(request):
    context = {}
    return render(request, 'schedule/login.html')


def register_page(request):
    context = {}
    return render(request, 'schedule/register.html')

