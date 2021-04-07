from django.contrib import admin
from .models import Event, Subject, Vote, Lead


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
    list_display = ('title', 'proposer', 'created', 'vote_score')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('proposer',)


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    pass


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('leader', 'subject', 'if_lead', 'created', 'updated')
    list_filter = ('leader', 'subject', 'if_lead')
