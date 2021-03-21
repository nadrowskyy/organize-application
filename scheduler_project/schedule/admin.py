from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'organizer', 'planning_date')
    list_filter = ('title', 'created', 'publish', 'organizer')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('organizer',)
    date_hierarchy = 'publish'
    ordering = ('status', 'publish')