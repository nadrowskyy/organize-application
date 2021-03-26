from django.shortcuts import render
import calendar
from calendar import HTMLCalendar
from datetime import datetime

def home(request):
    return render(request, 'schedule/home.html', {})

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