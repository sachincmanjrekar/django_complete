from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views import View
from .forms import ReviewForm
from django.views.generic.base import TemplateView
from .models import Review

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

class ThankYouView(TemplateView):

    template_name = "reviews/thank_you.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["message"] = "Thank you for your feedback!"
        return context


class ReviewListView(TemplateView):

    template_name = "reviews/review_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reviews = Review.objects.all()
        context["reviews"] = reviews
        return context


