from django.shortcuts import render

def show_leaderboard(request):
    return render(request, "leaderboard/mobile_leaderboard.html")