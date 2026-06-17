from celery import shared_task
from .services import leaderboard_data
from realtime.services import update_leaderboard as send_leaderboard_ws

@shared_task
def update_leaderboard():
    leaderboard = leaderboard_data.get_leaderboard()
    send_leaderboard_ws(leaderboard)