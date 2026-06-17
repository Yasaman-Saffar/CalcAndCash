from .models import TimeControl

def contest_status(request):
    timer = TimeControl.objects.first()
    if timer:
        return {
            "contest_state": timer.get_status_display(),
        }
    return {}

def event_status(request):
    timer = TimeControl.objects.first()
    if timer and timer.current_inflation:
        return {
            "current_inflation": str(timer.current_inflation.get_event_rate()),
        }
    return {}