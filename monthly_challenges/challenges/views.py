from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.urls import reverse
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
    list_items = ""
    months = list(monthly_challenges.keys())

    return render(request, "challenges/index.html", {"months": months})


def monthly_challenge_by_number(request, month):

    months = list(monthly_challenges.keys())
    if month > len(months):
        return HttpResponseNotFound("Invalid month")
    else:
        month = months[month - 1]
        redirect_path = reverse("month-challenge", args=[month])
        return HttpResponseRedirect(redirect_path)


def monthly_challenge(request, month):

    try:
        challenge_text = monthly_challenges.get(month)
        return render(request, "challenges/challenge.html", {
                "text": challenge_text,
                "month_name": month,})

    except:
        return HttpResponseNotFound(f"No challenge found for {month}")