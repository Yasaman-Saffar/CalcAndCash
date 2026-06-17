from django.http import JsonResponse

from realtime.services import force_refresh_all
from .models import TimeControl
from .celery_schedules import start_competition_tasks, disable_competition_tasks
from bank.models import Item, Event
from timer.decorator import permission_required
from timer.permissions import HasAccessToTimer



def get_timer():
    return TimeControl.objects.first()

def timer_not_configured_response():
    return JsonResponse({"status": "timer_not_configured"}, status=404)

@permission_required([HasAccessToTimer])
def start(request):
    timer = get_timer()
    
    if timer is None:
        return timer_not_configured_response()
    
    if timer.status == "running":
        return JsonResponse({"status": "already_started"})
    
    timer.start()
    start_competition_tasks()
    force_refresh_all()
    
    return JsonResponse({"status": "started"})

@permission_required([HasAccessToTimer])
def pause(request):
    timer = get_timer()
    
    if timer is None:
        return timer_not_configured_response()
    
    if timer.status == "paused":
        return JsonResponse({"status": "already_paused"})
    
    timer.pause()
    force_refresh_all()
    
    return JsonResponse({"status": "paused",
                         "message": "Contest Paused",
                         "type": "warning"})

@permission_required([HasAccessToTimer])
def resume(request):
    timer = get_timer()

    if timer is None:
        return timer_not_configured_response()
    
    if timer.status == "running":
        return JsonResponse({"status": "already_running"})
    
    timer.resume()
    force_refresh_all()
    
    return JsonResponse({"status": "resumed",
                         "message": "Contest Resumed. Hurry up!",
                         "type": "info"})

@permission_required([HasAccessToTimer])
def force_finish(request):
    timer = get_timer()

    if timer is None:
        return timer_not_configured_response()
    
    if timer.status == "finished":
        return JsonResponse({"status": "already_finished"})
    
    timer.finish()
    force_refresh_all()
    disable_competition_tasks()
    
    return JsonResponse({"status": "finished"})

@permission_required([HasAccessToTimer])
def reset_competition(request):
    timer = get_timer()
    
    if timer is None:
        return timer_not_configured_response()
    
    if timer.status != "finished":
        return JsonResponse({"status": "Timer must get finished first."})
    
    timer.reset_timer()
    Event.reset_events()
    Item.reset_items()
    force_refresh_all()
    
    return JsonResponse({"status": "restarted"})
  
def timer_data(request):
    timer = get_timer()
    
    if timer is None:
        return timer_not_configured_response()
    
    return JsonResponse({
        "status": timer.status,
        "remaining": timer.remaining(),
    })