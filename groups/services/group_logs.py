from ..models import GroupActivity

def log_group_activity(group, action, message):
    GroupActivity.objects.create(
        group=group,
        action=action,
        message=message,
    )