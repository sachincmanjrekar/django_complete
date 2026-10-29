from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views import View
from .forms import ReviewForm
# from django.views.generic.base import TemplateView

class ReviewView(View):
    def get(self, request):
        form = ReviewForm()
        return render(request, "reviews/review.html", {"form":form})
    
    def post(self, request):
        data = request.POST.copy()                              # request.POST can't be edited, so copy it
        data["user_name"] = data.get("user_name", "").strip()   # "   " -> ""
        form = ReviewForm(data)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/thank-you")
        else:
            print("clean data not received")
            return render(request, "reviews/review.html", {"form":form})

class ThankYouView(View):

    def get(self, request):
        return render(request, "reviews/thank_you.html")



