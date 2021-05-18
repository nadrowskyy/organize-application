from django.contrib import admin
from .models import Event, Subject, Polls, Dates


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'organizer', 'planning_date')
    list_filter = ('title', 'created', 'publish', 'organizer')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('organizer',)
    date_hierarchy = 'publish'
    ordering = ('status', 'publish')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'proposer', 'created', 'like_count', 'lead_count')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('proposer',)

@admin.register(Polls)
class PolesAdmin(admin.ModelAdmin):
    pass
@admin.register(Dates)
class DatesAdmin(admin.ModelAdmin):
    pass
