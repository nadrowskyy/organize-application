from .forms import CreateUserForm, UserFullnameChoiceField
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm, CreateEvent, SubjectForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
import calendar
from calendar import HTMLCalendar
from datetime import datetime
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user, allowed_users
from django.http import HttpResponseRedirect
from .models import Event
from django.core.files.storage import FileSystemStorage
from django.utils import timezone
import pytz



# @login_required(login_url='login') # nie pozwala na wejscie uzytkownika na strone glowna jesli nie jest zarejestrowany
def home_page(request):
    now = timezone.now()
    print(now)
    upcoming_events_list = Event.objects.filter(planning_date__gte=now)

    context = {'upcoming_events_list': upcoming_events_list}

    return render(request, 'schedule/home.html', context)


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

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():

# sprawdzanie prefixu i suffixu maila
            email = form.cleaned_data.get('email')
            suffix = (email.rsplit('@'))[1]
            prefix = (email.split('@'))[0]

            User = get_user_model()
            emails = User.objects.all().values_list('email')
            prefixes = []
            for i in emails:
                prefixes.append((str(i).rsplit('\'')[1].split('@')[0]))

            is_unique = True

            for i in prefixes:
                if i == prefix:
                    is_unique = False

            if suffix == 'gmail.com' or suffix == 'comarch.pl' or suffix == 'comarch.com':
                if is_unique:
                    form.save()
                    username = form.cleaned_data.get('username')
                    raw_password = form.cleaned_data.get('password1')
                    user = authenticate(username=username, password=raw_password)
                    login(request, user)
                    return redirect('home')
                else:
                    messages.error(request, "Błąd: adres e-mail znajduje się już w bazie")
            else:
                messages.error(request, "Błąd: adres e-mail powinien posiadać suffix comarch.pl lub comarch.com")
    else:
        form = CreateUserForm()

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

    User = get_user_model()
    fullnames = User.objects.all()

    if request.method == 'POST':
        form = CreateEvent(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('events_list')
    else:
        form = CreateEvent()

    context = {'form': form, 'fullnames': fullnames}

    return render(request, 'schedule/create_event.html', context)


def suggest_event(request):

    User = get_user_model()

    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            print(request.POST.get('if_lead'))
            print('valid form')
            tit = form.cleaned_data.get('title')
            print(tit)
            #form.save()
            return redirect('home')
    else:
        print('gettt')
        form = SubjectForm()

    context = {'form': form}

    return render(request, 'schedule/suggest_event.html', context)


def logout_user(request):
    logout(request)
    return redirect('home')


def about(request):

    return render(request, 'schedule/about.html')


def user_page(request):
    context = {}
    return render(request, 'schedule/user.html', context)



