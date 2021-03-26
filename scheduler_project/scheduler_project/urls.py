"""scheduler_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from schedule.views import register_page, login_page, home_page, logout_user, user_page, create_event

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_page, name='home'),
    path('register/', register_page),
    path('login/', login_page, name='login'),
    path('logout/', logout_user, name='logout'),
    path('user/', user_page, name='user_page'),
    path('create-event/', create_event, name='create_event'),
]
