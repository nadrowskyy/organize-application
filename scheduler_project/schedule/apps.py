from django.apps import AppConfig


class ScheduleConfig(AppConfig):
    name = 'schedule'
    verbose_name = 'schedule'

    def ready(self):
        import schedule.signals
