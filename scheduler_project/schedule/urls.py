import django.contrib.auth.views
from django.contrib import admin
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView

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
    # AJAX
    path('ajax_like/', views.ajax_like, name='ajax_like'),
    path('ajax_lead/', views.ajax_lead, name='ajax_lead'),
    # PASSWORD RESET
    path('password_reset/', views.password_reset_request, name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(template_name=
        'schedule/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name=
        'schedule/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(template_name=
        'schedule/password_reset_complete.html'), name='password_reset_complete'),

    path('subjects_list/', views.subjects_list, name='subjects_list'),
    path('users_list/', views.users_list, name='users_list'),
    path('user_details/<int:index>', views.user_details, name='user_details'),
    path('user_edit/<int:index>', views.user_edit, name='user_edit'),
    path('delete_user/<int:index>', views.delete_user, name='delete_user'),
    path('subject_edit/<int:index>', views.subject_edit, name='subject_edit'),
    path('delete_subject/<int:index>', views.delete_subject, name='delete_subject'),
    path('email_client', views.email_client, name='email_client'),
    path('email_notification', views.email_notification, name='email_notification'),
    path('event_edit/<int:index>', views.event_edit, name='event_edit'),
    path('delete_event/<int:index>', views.delete_event, name='delete_event'),
    path('my_profile/', views.my_profile, name='my_profile'),
    # path('change_password/', views.change_password, name='change_password'),
    path('event_details/<int:index>', views.event_details, name='event_details'),
    path('drafts_list', views.drafts_list, name='drafts_list'),
    path('draft_edit/<int:index>', views.draft_edit, name='draft_edit')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
