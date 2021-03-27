from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_page, name='home'),
    path('events_list/', views.events_list, name='events_list'),
    path('register/', views.register_page, name='register'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('create-event/', views.create_event, name='create_event'),
    path('suggest_event/', views.suggest_event, name='suggest_event'),
    path('about/', views.about, name='about'),
]
