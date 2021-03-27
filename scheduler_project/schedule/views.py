from .forms import CreateUserForm
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
import calendar
from calendar import HTMLCalendar
from datetime import datetime
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user, allowed_users
from django.http import HttpResponseRedirect
from .models import Event


# @login_required(login_url='login') # nie pozwala na wejscie uzytkownika na strone glowna jesli nie jest zarejestrowany
def home_page(request):
    all_events_list = Event.objects.all()

    return render(request, 'schedule/home.html',
                  {
                      'all_events_list': all_events_list,
                  })


@unauthenticated_user
def login_page(request):

    if request.method == 'POST':
        username = request.POST.get('username')  # html name="username"
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Username or password is incorrect')

    context = {}
    return render(request, 'schedule/login.html', context)


# do zakladki rejestracji moga przejsc tylko niezalogowani uzytkownicy
@unauthenticated_user
def register_page(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')

            group = Group.objects.get(name='employee')
            user.groups.add(group)

            messages.success(request, f'Account was created for {username}')

            return redirect('login')

    context = {'form': form}
    return render(request, 'schedule/register.html', context)


def events_list(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
    month = month.capitalize()
    month_number = list(calendar.month_name).index(month)
    month_number = int(month_number)

    cal = HTMLCalendar().formatmonth(year, month_number)

    present = datetime.now()
    present_year = present.year
    present_month = present.month
    present_time = present.strftime('%H:%M:%S')

    all_events_list = Event.objects.all()

    return render(request, 'schedule/events_list.html',
                  {
                      "year": year,
                      "month": month,
                      "month_number": month_number,
                      "cal": cal,
                      "present_year": present_year,
                      "present_month": present_month,
                      "present_time": present_time,
                      'all_events_list': all_events_list,
                  })


# pozwala wejsc na strone tworzenia eventów tylko adminom
@allowed_users(allowed_roles=['admin'])
def create_event(request):

    if request.method == 'POST':
        subject = request.POST.get('subject')
        print(subject)
        description = request.POST.get('description')
        print(description)
        organizer = request.POST.get('organizer')
        print(organizer)
        start_date = request.POST.get('startdate')
        print(start_date)
        duration = request.POST.get('duration')
        print(duration)

    return render(request, 'schedule/create_event.html')

def suggest_event(request):
    return render(request, 'schedule/suggest_event.html')


def logout_user(request):
    logout(request)
    return redirect('home')


def about(request):

    return render(request, 'schedule/about.html')


def user_page(request):
    context = {}
    return render(request, 'schedule/user.html', context)



