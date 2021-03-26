from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
import calendar
from calendar import HTMLCalendar
from datetime import datetime

def home_page(request):
    return render(request, 'schedule/home.html', {})

def login_page(request):

    if request.method == 'POST':
        username = request.POST.get('username')  # html name="username"
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')

    context = {}
    return render(request, 'schedule/login.html')

def register_page(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, f'Account was created for {user}')

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

    return render(request, 'schedule/events_list.html',
                  {
                      "year": year,
                      "month": month,
                      "month_number": month_number,
                      "cal": cal,
                      "present_year": present_year,
                      "present_month": present_month,
                      "present_time": present_time,
                  })