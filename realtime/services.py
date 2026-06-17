from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Personal
def notify(user_id, data):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        {
            "type": "notification",
            "data": data
        }
    )
    
# Group notify
def notify_all_players(data):
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        "contest_players_notifications",
        {
            "type": "notification",
            "data": data
        }
    )
    
def update_leaderboard(data):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "leaderboard_group",
        {
            "type": "update_leaderboard",
            "data": data
        }
    )
    
def force_refresh_all():
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "contest_users",
        {
            "type": "force_refresh",
        }
    )

def inflation_announcement(data):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "inflation_group",
        {
            "type": "inflation_announcement",
            "data": data
        }
    )