from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
# Create your views here.


monthly_challenges = {
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


def index(request):
    return HttpResponse("Hello, World!")


def monthly_challenge_by_number(request, month):

    months = list(monthly_challenges.keys())
    if month > len(months):
        return HttpResponseNotFound("Invalid month")
    else:
        month = months[month - 1]
        return HttpResponseRedirect(f"/challenges/{month}")


def monthly_challenge(request, month):
    challenge_text = monthly_challenges.get(month)
    if challenge_text:
        return HttpResponse(f"Monthly Challenge for {month}: {challenge_text}")
    else:
        return HttpResponseNotFound(f"No challenge found for {month}")