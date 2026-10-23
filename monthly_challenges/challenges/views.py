from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
# Create your views here.


def index(request):
    return HttpResponse("Hello, World!")


def monthly_challenge_by_number(request, month):
    return HttpResponse(f"Monthly Challenge for month {month}")


def monthly_challenge(request, month):

    challenges = {
        "january": "Eat no meat for the entire month!",
        "february": "Walk for at least 20 minutes every day!",
        "march": "Learn Django for at least 20 minutes every day!",
        "april": "Eat no meat for the entire month!",
        "may": "Walk for at least 20 minutes every day!",
        "june": "Learn Django for at least 20 minutes every day!",
        "july": "Eat no meat for the entire month!",
        "august": "Walk for at least 20 minutes every day!",
        "september": "Learn Django for at least 20 minutes every day!",
        "october": "Eat no meat for the entire month!",
        "november": "Walk for at least 20 minutes every day!",
        "december": None,
    }
    challenge_text = challenges.get(month)
    if challenge_text:
        return HttpResponse(f"Monthly Challenge for {month}: {challenge_text}")
    else:
        return HttpResponseNotFound(f"No challenge found for {month}")