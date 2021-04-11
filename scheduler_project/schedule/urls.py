from django.contrib import admin
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_page, name='home'),
    path('events_list/', views.events_list, name='events_list'),
    path('register/', views.register_page, name='register'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('create_event/', views.create_event, name='create_event'),
    path('suggest_event/', views.suggest_event, name='suggest_event'),
    path('about/', views.about, name='about'),
    path('subjects_list/', views.subjects_list, name='subjects_list'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
