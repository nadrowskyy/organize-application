from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user, allowed_users


# @login_required(login_url='login') # nie pozwala na wejscie uzytkownika na strone glowna jesli nie jest zarejestrowany
def home_page(request):
    return render(request, 'schedule/home.html')


# do zakladki logowania moga przejsc tylko niezalogowani uzytkownicy
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


# pozwala wejsc na strone tworzenia eventów tylko adminom
@allowed_users(allowed_roles=['admin'])
def create_event(request):

    if request.method == 'POST':
        subject = request.POST.get('subject')
        print(subject)
        description = request.POST.get('description')
        print(description)
        organizer = request.POST.get('organizer')
        start_date = request.POST.get('startdate')
        print(start_date)
        duration = request.POST.get('duration')
        print(duration)

    return render(request, 'schedule/create_event.html')


def logout_user(request):
    logout(request)
    return redirect('login')


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


def user_page(request):
    context = {}
    return render(request, 'schedule/user.html', context)

