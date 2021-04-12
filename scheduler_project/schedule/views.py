from .forms import CreateUserForm, UserFullnameChoiceField
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm
from .forms import CreateEvent
from .forms import SubjectForm
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
from .models import Event, Subject, Lead
from django.core.paginator import Paginator, EmptyPage
from django.core.files.storage import FileSystemStorage
from django.utils import timezone
import pytz
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage



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
        remember_me = request.POST.get('remember_me')

        user = authenticate(request, username=username, password=password)

        #Sprawdzanie parametru next, by móc przekierować niezalogowanego użytkownika
        #w miejsce do którego chciał się dostać po poprawnym logowaniu
        if user is not None:
            login(request, user)
            if 'next' in request.POST:

                if not remember_me:
                    request.session.set_expiry(0)

                return redirect(request.POST.get('next'))
            else:
                return redirect('home')
        else:
            messages.info(request, 'Nazwa użytkownika lub hasło są nieprawidłowe')

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

    pa = Paginator(all_events_list, 12)

    page_num = request.GET.get('page', 1)
    try:
        page = pa.page(page_num)
    except EmptyPage:
        page =pa.page(1)

    today = datetime.today()
    upcoming_events_list = Event.objects.filter(planning_date__gte=today)

    context = {'list': page, 'upcoming_events': upcoming_events_list}

    return render(request, 'schedule/events_list.html', context)

    # return render(request, 'schedule/events_list.html',
    #               {
    #                   'all_events_list': all_events_list,
    #               })


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


@login_required(login_url='login')
def suggest_event(request):
    print('hereeee')
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            user = get_user_model()
            me = user.objects.get(username=request.user)
            subject = form.save(commit=False)
            subject.proposer_id = me.id
            subject.save()

            if request.POST.get('if_lead') != None:
                sub = ''
                try:
                    sub = Subject.objects.latest('id')
                except:
                    pass

                # tworzenie glosu jesli nie ma go juz w tabeli
                if not Lead.objects.filter(leader=me, subject=sub, if_lead=True):
                    Lead.objects.create(leader=me, subject=sub, if_lead=True, created=timezone.now())

            return redirect('home')
    else:
        form = SubjectForm()

    context = {'form': form}

    return render(request, 'schedule/suggest_event.html', context)

@login_required(login_url='login')
def logout_user(request):
    logout(request)
    return redirect('home')


def about(request):

    return render(request, 'schedule/about.html')


def user_page(request):
    context = {}
    return render(request, 'schedule/user.html', context)

def subjects_list(request):

    all_subjects_list = Subject.objects.all()
    return render(request, 'schedule/subjects_list.html', {"all_subjects_list": all_subjects_list})

@login_required(login_url='login')
def like(request):
    if request.method == 'POST':
        id2 = (request.POST.get('subject_id'))
        subject = get_object_or_404(Subject, id=id2)
        if subject.likes.filter(id=request.user.id).exists():
            subject.likes.remove(request.user)
            subject.like_count -= 1
            subject.save()
        else:
            subject.likes.add(request.user)
            subject.like_count += 1
            subject.save()

        return redirect('subjects_list')

@login_required(login_url='login')
def want_to_lead(request):
    if request.method == 'POST':
        leader = get_object_or_404(Subject, id=(request.POST.get('leader_id')))
        if leader.want_to_lead.filter(id=request.user.id).exists():
            messages.info(request, "Już zgłosiłeś się do prowadzenia tego tematu")
        else:
            leader.want_to_lead.add(request.user)
            leader.lead_count += 1
            leader.save()

        return redirect('subjects_list')



