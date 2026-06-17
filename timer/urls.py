from django.urls import path
from . import views

urlpatterns = [
    path("start/", views.start, name="contest-start"),
    path("pause/", views.pause, name="contest-pause"),
    path("resume/", views.resume, name="contest-resume"),
    path("reset/", views.reset_competition, name="contest-reset"),
    path("force-finish/", views.force_finish, name="contest-force-finish"),
    path("timer-data/", views.timer_data, name="timer-data"),
]
