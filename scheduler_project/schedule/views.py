from .forms import CreateUserForm
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
import calendar
from calendar import HTMLCalendar
from datetime import datetime, date
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user, allowed_users
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from .models import Event
from django.core.paginator import Paginator, EmptyPage


# @login_required(login_url='login') # nie pozwala na wejscie uzytkownika na strone glowna jesli nie jest zarejestrowany
def home_page(request):
    today = datetime.today()
    upcoming_events_list = Event.objects.filter(planning_date__gte=today)

    return render(request, 'schedule/home.html',
                  {
                      'upcoming_events_list': upcoming_events_list,
                  })


@unauthenticated_user
def login_page(request):

    if request.method == 'POST':
        username = request.POST.get('username')  # html name="username"
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        #Sprawdzanie parametru next, by móc przekierować niezalogowanego użytkownika
        #w miejsce do którego chciał się dostać po poprawnym logowaniu
        if user is not None:
            login(request, user)
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            else:
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

#Tylko zalogowany użytkownik może wejśc w listę eventów. Niezalogowany zostanie przeniesiony
#do strony odpowiedzialnej za logowanie
@login_required(login_url="/login")
def events_list(request):

    all_events_list = Event.objects.all()

    p = Paginator(all_events_list, 4)

    page_num = request.GET.get('page', 1)
    try:
        page = p.page(page_num)
    except EmptyPage:
        page =p.page(1)

    today_date = datetime.today()

    context = {'list': page, 'today_date': today_date}

    return render(request, 'schedule/events_list.html', context)

    # return render(request, 'schedule/events_list.html',
    #               {
    #                   'all_events_list': all_events_list,
    #               })


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



