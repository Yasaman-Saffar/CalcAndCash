from celery import shared_task
from .celery_schedules import disable_competition_tasks
from .models import TimeControl
from bank.models import Event
from .services import execute_event
from realtime.services import force_refresh_all

def check_timer_status(current_time, timer):
    if current_time >= timer.duration:
        timer.finish()
        force_refresh_all()
        disable_competition_tasks()
        

@shared_task
def event_apply():
    """
    Apply due contest events and finish the contest when time is over.
    """
    
    timer = TimeControl.objects.first()
    if not timer or timer.status != "running":
        return
    
    current_time = timer.passed_time()
    
    events = Event.objects.filter(
        executed=False,
        apply_time__lte=current_time
    )
    
    for e in events:
        execute_event(e)
        e.executed = True
        e.save(update_fields=['executed'])
        
    check_timer_status(current_time, timer)