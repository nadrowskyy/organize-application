from .forms import CreateUserForm, UserFullnameChoiceField
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm
from .forms import CreateEvent
from .forms import SubjectForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from datetime import datetime, date
from django.contrib.auth.models import Group
from .decorators import unauthenticated_user, allowed_users
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from .models import Event, Subject, Lead, User
from django.utils import timezone
import pytz
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from .tasks import sent_event_notification


# @login_required(login_url='login') # nie pozwala na wejscie uzytkownika na strone glowna jesli nie jest zarejestrowany
def home_page(request):
    now = timezone.now()
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

        # Sprawdzanie parametru next, by móc przekierować niezalogowanego użytkownika
        # w miejsce do którego chciał się dostać po poprawnym logowaniu
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
                    user = form.save()
                    username = form.cleaned_data.get('username')
                    raw_password = form.cleaned_data.get('password1')
                    group = Group.objects.get(name='employee')
                    user.groups.add(group)
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


# Tylko zalogowany użytkownik może wejśc w listę eventów. Niezalogowany zostanie przeniesiony
# do strony odpowiedzialnej za logowanie
@login_required(login_url="/login")
def events_list(request):
    all_events_list = Event.objects.all()

    pa = Paginator(all_events_list, 12)

    page_num = request.GET.get('page', 1)
    try:
        page = pa.page(page_num)
    except EmptyPage:
        page = pa.page(1)

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


@allowed_users(allowed_roles=['admin'])
def users_list(request):
    if request.method == 'POST':
        delete_id = request.POST.get('delete')
        user = get_user_model()
        selected_user = user.objects.filter(id=delete_id)
        selected_user.delete()

    user = get_user_model()
    users = user.objects.all()

    lead_cnt = []
    subjects_cnt = []

    for i in users:
        lead_cnt.append(Event.objects.filter(organizer=i.id).count())
        subjects_cnt.append(Subject.objects.filter(proposer=i.id).count())

    context = {'users': users, 'lead_cnt': lead_cnt, 'subjects_cnt': subjects_cnt}

    return render(request, 'schedule/users_list.html', context)


@allowed_users(allowed_roles=['admin'])
def user_details(request, index):
    if request.method == 'GET':
        user = get_user_model()
        selected_user = user.objects.filter(id=index)

        subjects = Subject.objects.filter(proposer=index)
        events = Event.objects.filter(organizer=index)

        subjects_cnt = subjects.count()
        events_cnt = events.count()

        context = {'selected_user': selected_user, 'subjects': subjects, 'events': events, 'subjects_cnt': subjects_cnt, 'events_cnt': events_cnt}
        return render(request, 'schedule/user_details.html', context)


@allowed_users(allowed_roles=['admin'])
def user_edit(request, index):


    if request.method == 'GET':
        user = get_user_model()
        selected_user = user.objects.filter(id=index)
        context = {'selected_user': selected_user}

    if request.method == 'POST':
        user = get_user_model()
        selected_user = user.objects.filter(id=index)

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        if_admin = request.POST.get('if_admin')

        if if_admin:
            employee_group = Group.objects.get(name='employee')
            admin_group = Group.objects.get(name='admin')
            employee_group.user_set.remove(index)
            admin_group.user_set.add(index)
        else:
            employee_group = Group.objects.get(name='employee')
            admin_group = Group.objects.get(name='admin')
            admin_group.user_set.remove(index)
            employee_group.user_set.add(index)

        update_user = user.objects.filter(id=index).update(first_name=first_name, last_name=last_name, username=username, email=email)

        return redirect('users_list')

    return render(request, 'schedule/user_edit.html', context)

@allowed_users(allowed_roles=['admin'])
def delete_user(request, index):
    try:
        user = get_user_model()
        selected_user = user.objects.filter(id=index)
        selected_user.delete()
        return redirect('users_list')

    except:
        return redirect('users_list')

    return render(request, 'schedule/users_list.html')

@allowed_users(allowed_roles=['admin'])
def subject_edit(request, index):

    if request.method == 'GET':
        subject = Subject.objects.filter(id=index)
        context = {'subject': subject}
        return render(request, 'schedule/subject_edit.html', context)

    if request.method == 'POST':

        title = request.POST.get('title')
        description = request.POST.get('description')

        update_subject = Subject.objects.filter(id=index).update(title=title, description=description)

        return redirect('subjects_list')

    return render(request, 'schedule/subject_edit.html', context)

@allowed_users(allowed_roles=['admin'])
def delete_subject(request, index):
    try:
        selected_subject = Subject.objects.filter(id=index)
        selected_subject.delete()

        return redirect('subjects_list')

    except:
        return redirect('subjects_list')


    return render(request, 'schedule/subjects_list.html')


@allowed_users(allowed_roles=['admin'])
def email_settings(request):

    '''
    Do wysłania maila potrzeba:
        - host,
        - port,
        - username,
        - password,
        - user_tls(bool)
    '''

    m_host = ''
    m_port = 0
    m_username = ''
    m_password = ''
    m_use_tls = True




    return render(request, 'schedule/email_settings.html')
