from django.shortcuts import render
from django.http import HttpResponseRedirect

from .forms import ReviewForm


# Create your views here.
def review(request):
    # if request.method == "POST":
    #     username = request.POST.get("username")
    #     print(username)

    #     if username == "":
    #         return render(request, "reviews/review.html", {"has_error":True})
    #     return HttpResponseRedirect("/thank-you")


    form = ReviewForm()
    return render(request, "reviews/review.html", {"form":form})



def thank_you(request):
    return render(request, "reviews/thank_you.html", {"has_error":False})


