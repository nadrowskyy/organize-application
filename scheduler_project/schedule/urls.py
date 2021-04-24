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
    path('like/', views.like, name='like'),
    path('want_to_lead/', views.want_to_lead, name='want_to_lead'),
    path('subjects_list/', views.subjects_list, name='subjects_list'),
    path('users_list/', views.users_list, name='users_list'),
    path('user_details/<int:index>', views.user_details, name='user_details'),
    path('user_edit/<int:index>', views.user_edit, name='user_edit'),
    path('delete_user/<int:index>', views.delete_user, name='delete_user'),
    path('subject_edit/<int:index>', views.subject_edit, name='subject_edit'),
    path('delete_subject/<int:index>', views.delete_subject, name='delete_subject'),
    path('event_edit/<int:index>', views.event_edit, name='event_edit'),
    path('delete_event/<int:index>', views.delete_event, name='delete_event'),
    path('my_profile/', views.my_profile, name='my_profile')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
