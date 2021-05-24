from django import template
from django.contrib.auth.models import Group
from datetime import datetime
from ..models import Event, Polls, Dates

register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return True if group in user.groups.all() else False


@register.filter(name='have_polls')
def have_polls(user):
    # trzeba odfiltrowac te ankiety gdzie user juz zaglosowal
    all_events_list = Event.objects.filter(polls__if_active=True, polls__since_active__lte=datetime.now(),
                                           polls__till_active__gte=datetime.now())
    # ankiety gdzie user juz zaglosowal
    curr_user_voted = set(all_events_list.filter(polls__dates__users=user))

    all_events_filtered = []
    if len(curr_user_voted) == 0:
        all_events_filtered = all_events_list
    else:
        for el in curr_user_voted:
            if el in all_events_list:
                pass
            else:
                all_events_filtered.append(el)
    if len(all_events_filtered) == 0:
        return False
    else:
        return True
