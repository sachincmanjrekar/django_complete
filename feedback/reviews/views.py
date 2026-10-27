from django.shortcuts import render
from django.http import HttpResponseRedirect

from .forms import ReviewForm
from .models import Review



# Create your views here.
def review(request):
    if request.method == "POST":
        data = request.POST.copy()                              # request.POST can't be edited, so copy it
        data["user_name"] = data.get("user_name", "").strip()   # "   " -> ""
        form = ReviewForm(data)

        if form.is_valid():
            review = Review(user_name=form.cleaned_data['user_name'],
                            review_text=form.cleaned_data['review_text'],
                            rating=form.cleaned_data['rating'])
            review.save()
            return HttpResponseRedirect("/thank-you")
        else:
            print("clean data not received")
    else:
        form = ReviewForm()
    return render(request, "reviews/review.html", {"form":form})


def thank_you(request):
    return render(request, "reviews/thank_you.html", {"has_error":False})


