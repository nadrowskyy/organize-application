from .forms import CreateUserForm, UserFullnameChoiceField
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm
from .forms import CreateEvent
from .forms import SubjectForm, AddComment
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from datetime import datetime, date
from django.contrib.auth.models import Group
from .decorators import unauthenticated_user, allowed_users
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from .models import Event, Subject, User, EmailSet, Comment, Polls, Dates
from django.core.mail import send_mail, get_connection, send_mass_mail
from django.core.mail import EmailMessage
from django.utils import timezone
import pytz
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from django.template.loader import get_template, render_to_string
import os
from .forms import ChangePassword
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import PasswordResetForm
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.http import HttpResponse
from django.db.models import Q
from django.core.mail import BadHeaderError, send_mail
from .tasks import send_mail_register


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
                    send_mail_register.delay(email)
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
#@login_required(login_url="/login")
def events_list(request):

    today = datetime.today()

    User = get_user_model()
    fullnames = User.objects.all()

    all_events_list = Event.objects.filter()

    sort_by = request.GET.get('sort_by')

    show_upcoming = request.GET.get('show_upcoming')
    show_historical = request.GET.get('show_historical')
    only_mine = request.GET.get('only_mine')
    drafts = request.GET.get('drafts')

    organizer = request.GET.get('organizer')
    title = request.GET.get('title')

    if show_historical and not show_upcoming:
        all_events_list = all_events_list.filter(planning_date__lte=today)

    elif not show_historical and show_upcoming:
        all_events_list = all_events_list.filter(planning_date__gte=today)

    if not drafts:
        all_events_list = all_events_list.filter(status='publish')

    if not request.user.groups.all()[0].name == 'admin' and drafts:
        all_events_list = all_events_list.filter(organizer=request.user)

    if organizer:
        all_events_list = all_events_list.filter(organizer=organizer)

    if only_mine:
        all_events_list = all_events_list.filter(organizer=request.user)

    if title and title != '':
        all_events_list = all_events_list.filter(title__icontains=title)

    # SORTOWANIE

    if sort_by == 'latest':
        all_events_list = all_events_list.order_by('planning_date')

    elif sort_by == 'oldest':
        all_events_list = all_events_list.order_by('-planning_date')

    elif sort_by == 'alphabetical':
        all_events_list = all_events_list.order_by('title')

    else:
        all_events_list = all_events_list.all()

    # FILTROWANIE







    pa = Paginator(all_events_list, 12)

    page_num = request.GET.get('page', 1)
    try:
        page = pa.page(page_num)
    except EmptyPage:
        page = pa.page(1)

    context = {'list': page, 'fullnames': fullnames}

    return render(request, 'schedule/events_list.html', context)

    # return render(request, 'schedule/events_list.html',
    #               {
    #                   'all_events_list': all_events_list,
    #               })


def drafts_list(request):
    all_events_list = Event.objects.filter(status='draft')
    # wyroznic wydarzenia ktore dla ktorych ankieta jest nieaktywna
    context = {'list': all_events_list}
    return render(request, 'schedule/drafts_list.html', context)


def draft_edit(request, index):

    if request.user.groups.all()[0].name == 'admin':

        if request.method == 'GET':
            event = Event.objects.filter(id=index)
            user = get_user_model()
            users = user.objects.all()
            poll = Polls.objects.filter(event=index).first()
            dates = Dates.objects.filter(poll=poll)

            if event[0].planning_date < datetime.today():
                past = True
            else:
                past = False

            context = {'event': event, 'users': users, 'permitted': True, 'past': past, 'poll': poll, 'dates': dates}
            return render(request, 'schedule/draft_edit.html', context)

        if request.method == 'POST':
            if request.POST.get('pub_button') == 'save':
                poll = Polls.objects.filter(event=index).first()
                dates = Dates.objects.filter(poll=poll)

                planning_dates = request.POST.getlist('planning_date_draft')

                if len(planning_dates) < 2 and request.POST.get('if_active') == 'True' or \
                        request.POST.get('poll_avaible_since') or request.POST.get('poll_avaible'):
                    messages.error(request, "Wypełnij wszystkie pola wymagane dla utworzenia aktywnej ankiety.")
                    return redirect('draft_edit', index)
                if request.POST.get('if_active') == 'True':
                    if_active = True
                else:
                    # daty beda zapisane w ankiecie ale sama ankieta bedzie nie aktywna
                    if_active = False

                since_active = request.POST.get('poll_avaible_since')
                till_active = request.POST.get('poll_avaible')

                update_poll = Polls.objects.filter(event=index).update(since_active=since_active,
                                                                       till_active=till_active, if_active=if_active)

                planning_dates_from_db = [x.date.strftime("%Y-%m-%dT%H:%M") for x in dates]

                if planning_dates != planning_dates_from_db:
                    dates_to_delete = []
                    for el in planning_dates_from_db:
                        if el not in planning_dates:
                            dates_to_delete.append(el)
                    dates_to_add = []
                    for el2 in planning_dates:
                        if el2 not in planning_dates_from_db:
                            dates_to_add.append(el2)

                    for el3 in dates_to_delete:
                        convert_to_date = datetime.strptime(el3, "%Y-%m-%dT%H:%M")
                        date_obj = Dates.objects.filter(poll=poll, date=convert_to_date).first()
                        date_obj.delete()

                    for el4 in dates_to_add:
                        convert_to_date = datetime.strptime(el4, "%Y-%m-%dT%H:%M")
                        date_obj = Dates.objects.create(poll=poll, date=convert_to_date)

                selected_event = Event.objects.get(id=index)
                title = request.POST.get('title')
                description = request.POST.get('description')
                organizer = request.POST.get('organizer')
                planning_date = request.POST.get('planning_date')
                duration = request.POST.get('duration')
                link = request.POST.get('link')
                update_event = Event.objects.filter(id=index).update(title=title, description=description,
                                                                         organizer=organizer,
                                                                         planning_date=planning_date,
                                                                         duration=duration, link=link)

                new_icon = request.FILES.get('icon')
                new_attachment = request.FILES.get('attachment')

                if new_icon:
                    selected_event.icon = new_icon
                    selected_event.save()

                if new_attachment:
                    selected_event.attachment = new_attachment
                    selected_event.save()

            if request.POST.get('pub_button') == 'publish':
                if request.POST.get('description') == '' or request.POST.get('planning_date') == '' or \
                        request.POST.get('duration') == '':
                    messages.error(request, "Wypełnij wszystkie pola wymagane dla opublikowania szkolenia.")
                    return redirect('draft_edit', index)
                else:
                    selected_event = Event.objects.get(id=index)
                    title = request.POST.get('title')
                    description = request.POST.get('description')
                    organizer = request.POST.get('organizer')
                    print('306')
                    print(organizer)
                    planning_date = request.POST.get('planning_date')
                    duration = request.POST.get('duration')
                    link = request.POST.get('link')

                    update_event = Event.objects.filter(id=index).update(title=title, description=description,
                                                        organizer=organizer, planning_date=planning_date,
                                                        duration=duration, link=link, status='publish',
                                                        publish=timezone.now())

                    new_icon = request.FILES.get('icon')
                    new_attachment = request.FILES.get('attachment')

                    if new_icon:
                        selected_event.icon = new_icon
                        selected_event.save()

                    if new_attachment:
                        selected_event.attachment = new_attachment
                        selected_event.save()

                    return redirect('events_list')

        return render(request, 'schedule/draft_edit.html')

    elif request.user.groups.all()[0].name == 'employee':

        try:
            event = Event.objects.filter(id=index)
        except:
            context = {'not_permitted': True}
            return render(request, 'schedule/draft_edit.html', context)

        if event[0].planning_date < datetime.today():
            past = True
        else:
            past = False

        for i in event:

            if i.organizer == request.user:

                if request.method == 'GET':
                    user = get_user_model()
                    users = user.objects.all()
                    poll = Polls.objects.filter(event=index).first()
                    dates = Dates.objects.filter(poll=poll)
                    context = {'event': event, 'users': users, 'permitted': True, 'past': past, 'poll': poll,
                               'dates': dates}
                    return render(request, 'schedule/draft_edit.html', context)

                if request.method == 'POST':
                    if request.POST.get('pub_button') == 'save':
                        poll = Polls.objects.filter(event=index).first()
                        dates = Dates.objects.filter(poll=poll)

                        planning_dates = request.POST.getlist('planning_date_draft')
                        if len(planning_dates) < 2 and request.POST.get('if_active') == 'True' or \
                                request.POST.get('poll_avaible_since') or request.POST.get('poll_avaible'):
                            messages.error(request, "Wypełnij wszystkie pola wymagane dla utworzenia aktywnej ankiety.")
                            return redirect('draft_edit', index)
                        if request.POST.get('if_active') == 'True':
                            if_active = True
                        else:
                            # daty beda zapisane w ankiecie ale sama ankieta bedzie nie aktywna
                            if_active = False

                        since_active = request.POST.get('poll_avaible_since')
                        till_active = request.POST.get('poll_avaible')

                        update_poll = Polls.objects.filter(event=index).update(since_active=since_active,
                                                                               till_active=till_active,
                                                                               if_active=if_active)

                        planning_dates_from_db = [x.date.strftime("%Y-%m-%dT%H:%M") for x in dates]

                        if planning_dates != planning_dates_from_db:
                            dates_to_delete = []
                            for el in planning_dates_from_db:
                                if el not in planning_dates:
                                    dates_to_delete.append(el)
                            dates_to_add = []
                            for el2 in planning_dates:
                                if el2 not in planning_dates_from_db:
                                    dates_to_add.append(el2)

                            for el3 in dates_to_delete:
                                convert_to_date = datetime.strptime(el3, "%Y-%m-%dT%H:%M")
                                date_obj = Dates.objects.filter(poll=poll, date=convert_to_date).first()
                                date_obj.delete()
                            for el4 in dates_to_add:
                                convert_to_date = datetime.strptime(el4, "%Y-%m-%dT%H:%M")
                                date_obj = Dates.objects.create(poll=poll, date=convert_to_date)
                        selected_event = Event.objects.get(id=index)
                        title = request.POST.get('title')
                        description = request.POST.get('description')
                        organizer = request.user.id
                        planning_date = request.POST.get('planning_date')
                        duration = request.POST.get('duration')
                        link = request.POST.get('link')
                        update_event = Event.objects.filter(id=index).update(title=title, description=description,
                                                                             organizer=organizer,
                                                                             planning_date=planning_date,
                                                                             duration=duration, link=link)

                        new_icon = request.FILES.get('icon')
                        new_attachment = request.FILES.get('attachment')

                        if new_icon:
                            selected_event.icon = new_icon
                            selected_event.save()

                        if new_attachment:
                            selected_event.attachment = new_attachment
                            selected_event.save()

                    if request.POST.get('pub_button') == 'publish':
                        if request.POST.get('description') == '' or request.POST.get('planning_date') == '' or \
                                request.POST.get('duration') == '':
                            messages.error(request, "Wypełnij wszystkie pola wymagane dla opublikowania szkolenia.")
                            return redirect('draft_edit', index)
                        else:
                            selected_event = Event.objects.get(id=index)
                            title = request.POST.get('title')
                            description = request.POST.get('description')
                            organizer = request.user.id
                            planning_date = request.POST.get('planning_date')
                            duration = request.POST.get('duration')
                            link = request.POST.get('link')

                            update_event = Event.objects.filter(id=index).update(title=title, description=description,
                                                                                 organizer=organizer,
                                                                                 planning_date=planning_date,
                                                                                 duration=duration, link=link,
                                                                                 status='publish',
                                                                                 publish=timezone.now())

                            new_icon = request.FILES.get('icon')
                            new_attachment = request.FILES.get('attachment')

                            if new_icon:
                                selected_event.icon = new_icon
                                selected_event.save()

                            if new_attachment:
                                selected_event.attachment = new_attachment
                                selected_event.save()

                            return redirect('events_list')

                return render(request, 'schedule/draft_edit.html')

            else:
                context = {'not_permitted': True}
                return render(request, 'schedule/draft_list.html', context)


# pozwala wejsc na strone tworzenia eventów tylko adminom
@allowed_users(allowed_roles=['admin'])
def create_event(request):
    User = get_user_model()
    fullnames = User.objects.all()
    if request.method == 'POST':
        print('312')
        print('publish')
        print(type(request.POST.get('publish')))
        if request.POST.get('publish') == 'True':
            print('publish')
            form = CreateEvent(request.POST, request.FILES)
            print('non valid')
            if form.is_valid():
                print('valid')
                form.save()
                return redirect('events_list')
        if request.POST.get('publish') == 'False':
            form = CreateEvent(request.POST, request.FILES)
            if form.is_valid():
                draft_form = form.save(commit=False)
                draft_form.status = 'draft'
                draft_form.save()

                event = get_object_or_404(Event, pk=draft_form.pk)
                since_active = request.POST.get('poll_avaible_since')
                till_active = request.POST.get('poll_avaible')
                if request.POST.get('if_active') == 'True':

                    planning_dates = request.POST.getlist('planning_date_draft')
                    if len(planning_dates) < 2:
                        messages.error(request, "Podaj co najmniej dwie proponowane daty w ankiecie")

                    if_active = True
                    poll_form = Polls(event=event, since_active=since_active, till_active=till_active,
                                      if_active=if_active)
                    poll_form.save()

                    poll = get_object_or_404(Polls, pk=poll_form.pk)

                    for el in planning_dates:
                        dates_form = Dates(poll=poll, date=el+':00')
                        dates_form.save()
                if request.POST.get('if_active') == 'False':

                    planning_dates = request.POST.getlist('planning_date_draft')
                    if_active = False
                    poll_form = Polls(event=event, since_active=since_active, till_active=till_active,
                                      if_active=if_active)
                    poll_form.save()

                    poll = get_object_or_404(Polls, pk=poll_form.pk)

                    for el in planning_dates:
                        dates_form = Dates(poll=poll, date=el + ':00')
                        dates_form = Dates(poll=poll, date=el)
                        dates_form.save()

    else:
        form = CreateEvent()
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
            if request.POST.get('if_lead') is not None:
                leader = Subject.objects.filter(proposer=me).last()
                leader.want_to_lead.add(me)
                leader.lead_count += 1
                leader.save()

            return redirect('subjects_list')
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

    title = request.GET.get('s_title')
    all_subjects_list = Subject.objects.all()

    cnt = []

    for i in all_subjects_list:
        for j in i.want_to_lead.all():

            e = Event.objects.filter(organizer=j).count()
            s = Subject.objects.filter(proposer=j).count()

            temp = {
                'user': j,
                'events': e,
                'subjects': s
            }
            cnt.append(temp)

    seen = set()
    new_l = []
    for d in cnt:
        t = tuple(d.items())
        if t not in seen:
            seen.add(t)
            new_l.append(d)

    if title and title != '':
        all_subjects_list = all_subjects_list.filter(title__icontains=title)

    sort_by = request.GET.get('s_sort_by')

    if sort_by == 'alphabetical':
        all_subjects_list = all_subjects_list.order_by('title')
    elif sort_by == 'create_date':
        all_subjects_list =all_subjects_list.order_by('-created')
    elif sort_by == 'like_count':
        all_subjects_list =all_subjects_list.order_by('like_count')
    elif sort_by == 'like_count-':
        all_subjects_list =all_subjects_list.order_by('-like_count')
    elif sort_by == 'lead_count':
        all_subjects_list =all_subjects_list.order_by('lead_count')
    elif sort_by == 'lead_count-':
        all_subjects_list =all_subjects_list.order_by('-lead_count')
    else:
        all_subjects_list = all_subjects_list.all()





    pa = Paginator(all_subjects_list, 5)

    page_num = request.GET.get('page', 1)
    try:
        page = pa.page(page_num)
    except EmptyPage:
        page = pa.page(1)

    context = {"list": page, "cnt": new_l}

    return render(request, 'schedule/subjects_list_ajax.html', context)


@login_required(login_url='login')
@require_POST
def ajax_like(request):
    subject_id = request.POST.get('postid')
    action = request.POST.get('action')

    if subject_id and action:
        subject = get_object_or_404(Subject, id=subject_id)
        if subject.likes.filter(id=request.user.id).exists():
            subject.likes.remove(request.user)
            subject.like_count -= 1
            subject.save()
            action = 'unlike'
        else:
            subject.likes.add(request.user)
            subject.like_count += 1
            subject.save()
            action = 'like'

        subject.refresh_from_db()
        like_count = subject.like_count

        return JsonResponse({'like_count': like_count, 'action': action, 'status': 'ok'})


@login_required(login_url='login')
@require_POST
def ajax_lead(request):

    subject_id = request.POST.get('postid')
    action = request.POST.get('action')

    if subject_id and action:

        leader = get_object_or_404(Subject, id=subject_id)
        if leader.want_to_lead.filter(id=request.user.id).exists():
            leader.want_to_lead.remove(request.user)
            leader.lead_count -= 1
            leader.save()
            action = 'unlead'
        else:
            leader.want_to_lead.add(request.user)
            leader.lead_count += 1
            leader.save()
            action = 'lead'

        leader.refresh_from_db()
        lead_count = leader.lead_count

        return JsonResponse({'lead_count': lead_count, 'action': action, 'status': 'ok'})


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
def email_client(request):

    if request.method == 'GET':
        settings = EmailSet.objects.filter(id=1)[0]
        context = {'settings': settings}

        return render(request, 'schedule/email_client.html', context=context)

    if request.method == 'POST':

        email_host = request.POST.get('email_host')
        username = request.POST.get('username')
        password = request.POST.get('password')
        port = request.POST.get('port')
        if_tls = request.POST.get('if_tls')
        delay_leader = request.POST.get('delay_leader')
        delay_all = request.POST.get('delay_all')
        from_email = request.POST.get('from_email')

        email_body = render_to_string('schedule/email_test_template.html')

        try:

            with get_connection(host=email_host, port=port, username=username, password=password, use_tls=if_tls) as conn:
                msg = EmailMessage(subject='FFT - Wiadomość testowa', from_email=from_email, body=email_body,
                                   to=[request.user.email], connection=conn)
                msg.send(fail_silently=True)

        except Exception as e:

            e = str(e)

            if "535" in e:
                error = 'Login i/lub hasło są nieprawidłowe'

            elif "10060" in e:
                error = 'Port jest nieprawidłowy'

            elif "11001" in e:
                error = 'Nazwa serwera jest nieprawidłowa'

            elif "Invalid address; only" in e:
                error = 'Błędna nazwa nadawcy. Powinna być w formie: nazwa <mail@serwer.domena> lub sama nazwa'

            else:
                error = e

            settings = EmailSet.objects.filter(id=1)[0]
            context = {'settings': settings, 'error': error}

            return render(request, 'schedule/email_client.html', context)

        EmailSet.objects.filter(id=1).update(delay_leader=delay_leader, delay_all=delay_all, EMAIL_HOST=email_host,
                                             EMAIL_PORT=port, EMAIL_HOST_USER=username, EMAIL_HOST_PASSWORD=password,
                                             EMAIL_USE_TLS=if_tls, EMAIL_HEADER=from_email)

        return redirect('email_client')


@allowed_users(allowed_roles=['admin'])
def email_notification(request):

    if request.method == 'GET':
        module_dir = os.path.dirname(__file__)
        file_path = os.path.join(module_dir, 'templates\schedule\email_template.html')
        data_file = open(file_path, 'r', encoding='utf-8')
        data = data_file.read()

        return render(request, 'schedule/email_notification.html', context={'notification': data})

    if request.method == 'POST':

        notification = request.POST.get('notification')
        module_dir = os.path.dirname(__file__)
        file_path = os.path.join(module_dir, 'templates\schedule\email_template.html')
        with open(file_path, 'w', encoding='utf-8') as output:
            for line in notification.splitlines():
                output.write(line)
                output.write('\n')

        return redirect('email_notification')


@allowed_users(allowed_roles=['admin', 'employee'])
def event_edit(request, index):

    if request.user.groups.all()[0].name == 'admin':

        if request.method == 'GET':
            event = Event.objects.filter(id=index)
            user = get_user_model()
            users = user.objects.all()

            if event[0].planning_date < datetime.today():
                past = True
            else:
                past = False

            context = {'event': event, 'users': users, 'permitted': True, 'past': past}
            return render(request, 'schedule/event_edit.html', context)

        if request.method == 'POST':

            selected_event = Event.objects.get(id=index)

            title = request.POST.get('title')
            description = request.POST.get('description')
            organizer = request.POST.get('organizer')
            planning_date = request.POST.get('planning_date')
            duration = request.POST.get('duration')
            link = request.POST.get('link')

            update_event = Event.objects.filter(id=index).update(title=title, description=description, organizer=organizer, planning_date=planning_date, duration=duration, link=link)

            new_icon = request.FILES.get('icon')
            new_attachment = request.FILES.get('attachment')

            if new_icon:
                selected_event.icon = new_icon
                selected_event.save()

            if new_attachment:
                selected_event.attachment = new_attachment
                selected_event.save()

            return redirect('events_list')

        return render(request, 'schedule/event_edit.html', context)

    elif request.user.groups.all()[0].name == 'employee':

        try:
            event = Event.objects.filter(id=index)
        except:
            context = {'not_permitted': True}
            return render(request, 'schedule/event_edit.html', context)

        if event[0].planning_date < datetime.today():
            past = True
        else:
            past = False

        for i in event:

            if i.organizer == request.user:

                if request.method == 'GET':

                    context = {'event': event, 'past': past}
                    return render(request, 'schedule/event_edit.html', context)

                if request.method == 'POST':

                    selected_event = Event.objects.get(id=index)

                    description = request.POST.get('description')
                    planning_date = request.POST.get('planning_date')
                    duration = request.POST.get('duration')
                    link = request.POST.get('link')

                    update_event = Event.objects.filter(id=index).update(description=description, planning_date=planning_date, duration=duration, link=link)

                    new_icon = request.FILES.get('icon')
                    new_attachment = request.FILES.get('attachment')

                    if new_icon:
                        selected_event.icon = new_icon
                        selected_event.save()

                    if new_attachment:
                        selected_event.attachment = new_attachment
                        selected_event.save()

                    return redirect('events_list')

            else:
                context = {'not_permitted': True}
                return render(request, 'schedule/event_edit.html', context)


@allowed_users(allowed_roles=['admin'])
def delete_event(request, index):
    try:
        selected_event = Event.objects.filter(id=index)
        selected_event.delete()

        return redirect('events_list')

    except:
        return redirect('events_list')


@allowed_users(allowed_roles=['admin', 'employee'])
def my_profile(request):

    my_events = Event.objects.filter(organizer=request.user)
    my_subjects = Subject.objects.filter(proposer=request.user)

    events_cnt = my_events.count()
    subjects_cnt = my_subjects.count()

    if request.method == 'POST' and request.POST.get('change_profile') == '1':

        user = get_user_model()

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')

        update_user = user.objects.filter(id=request.user.id).update(first_name=first_name, last_name=last_name, email=email)

        return redirect('my_profile')

    elif request.method == 'POST':
        form = ChangePassword(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            login(request, request.user)
            messages.success(request, 'Hasło zostało zmienione.')
            return redirect('my_profile')
    else:
        form = ChangePassword(user=request.user)

    for field in form.fields.values():
        field.help_text = None

    context = {'my_events': my_events, 'my_subjects': my_subjects, 'events_cnt': events_cnt, 'subjects_cnt': subjects_cnt, 'form': form }

    return render(request, 'schedule/my_profile.html', context)


#@allowed_users(allowed_roles=['admin', 'employee'])
def event_details(request, index):

    if request.method == 'GET':
        selected_event = Event.objects.filter(id=index)
        comments = Comment.objects.filter(event=index)
        comments_cnt = comments.count()
        form = AddComment()
        context = {'selected_event': selected_event, 'comments': comments, 'form': form, 'comments_cnt': comments_cnt}

        return render(request, 'schedule/event_details.html', context)

    if request.method == 'POST' and request.POST.get('new_content'):

        comment_id = request.POST.get('comment_id')
        new_content = request.POST.get('new_content')
        form = AddComment()
        update_comment = Comment.objects.filter(id=comment_id).update(content=new_content, if_edited=True)
        selected_event = Event.objects.filter(id=index)
        comments = Comment.objects.filter(event=index)
        comments_cnt = comments.count()

        context = {'selected_event': selected_event, 'comments': comments, 'form': form, 'myid': comment_id,
                   'comments_cnt': comments_cnt}

        return redirect('event_details', index)

    if request.method == 'POST' and request.POST.get('delete'):

        comment_id = request.POST.get('comment_id')

        delete_comment = Comment.objects.filter(id=comment_id).update(if_deleted=True)

        form = AddComment()
        selected_event = Event.objects.filter(id=index)
        comments = Comment.objects.filter(event=index)
        comments_cnt = comments.count()

        context = {'selected_event': selected_event, 'comments': comments, 'form': form, 'myid': comment_id,
                   'comments_cnt': comments_cnt}

        return render(request, 'schedule/event_details.html', context)


    if request.method == 'POST' and not request.POST.get('new_content') and request.POST.get('delete') != True:

        author = request.user
        event = Event.objects.filter(id=index)[0]
        created = datetime.now()
        content = request.POST.get('content')

        form = Comment(author=author, event=event, created=created, content=content)
        form.save()

        selected_event = Event.objects.filter(id=index)
        comments = Comment.objects.filter(event=index)
        comments_cnt = comments.count()
        mycmt = Comment.objects.filter(event=index).order_by('-id')[0]
        myid = mycmt.id

        context = {'selected_event': selected_event, 'comments': comments, 'form': form, 'myid': myid, 'comments_cnt': comments_cnt}

        return render(request, 'schedule/event_details.html', context)

    else:
        return redirect('events_list')


def password_reset_request(request):
    if request.method == "POST":
        domain = request.headers['Host']
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "schedule/password_reset_email.txt"
                    c = {
                        "email": user.email,
                        'domain': domain,
                        'site_name': 'Interface',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        mail_settings = EmailSet.objects.filter(pk=1)[0]
                        host = mail_settings.EMAIL_HOST
                        port = mail_settings.EMAIL_PORT
                        username = mail_settings.EMAIL_HOST_USER
                        password = mail_settings.EMAIL_HOST_PASSWORD
                        use_tls = bool(mail_settings.EMAIL_USE_TLS)
                        from_email = mail_settings.EMAIL_HEADER
                        with get_connection(host=host, port=port, username=username, password=password,
                                            use_tls=use_tls) as conn:
                            msg = EmailMessage(subject=subject, body=email,
                                               from_email=from_email,
                                               to=[user.email], connection=conn)
                            msg.send(fail_silently=True)

                        #send_mail(subject, email, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    return redirect("password_reset_done")
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="schedule/password_reset_form.html",
                  context={"password_reset_form": password_reset_form})
