from django_celery_beat.models import PeriodicTask, IntervalSchedule

def start_competition_tasks():
    """
    Enable periodic contest tasks such as event execution and leaderboard updates.
    """
    schedule, _ = IntervalSchedule.objects.get_or_create(
        every=5,
        period=IntervalSchedule.SECONDS,
    )
    
    PeriodicTask.objects.update_or_create(
        name="event-apply",
        defaults={
            "interval": schedule,
            "task": "timer.tasks.event_apply",
            "enabled": True,
        },
    )
    
    PeriodicTask.objects.update_or_create(
        name="update-leaderboard",
        defaults={
            "interval": schedule,
            "task": "leaderboard.tasks.update_leaderboard",
            "enabled": True,
        },
    )

def disable_competition_tasks():
    PeriodicTask.objects.filter(
        name__in=[
            "event-apply",
            "update-leaderboard",
        ]
    ).delete()