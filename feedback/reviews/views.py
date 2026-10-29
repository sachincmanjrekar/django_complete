from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views import View
from .forms import ReviewForm
from django.views.generic.base import TemplateView
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormView
from .models import Review

class ReviewView(FormView):

    form_class = ReviewForm
    template_name = "reviews/review.html"
    success_url = "/thank-you"

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    # def get(self, request):
    #     form = ReviewForm()
    #     return render(request, "reviews/review.html", {"form":form})
    
    # def post(self, request):
    #     data = request.POST.copy()                              # request.POST can't be edited, so copy it
    #     data["user_name"] = data.get("user_name", "").strip()   # "   " -> ""
    #     form = ReviewForm(data)

    #     if form.is_valid():
    #         form.save()
    #         return HttpResponseRedirect("/thank-you")
    #     else:
    #         print("clean data not received")
    #         return render(request, "reviews/review.html", {"form":form})

class ThankYouView(TemplateView):

    template_name = "reviews/thank_you.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["message"] = "Thank you for your feedback!"
        return context


class ReviewListView(ListView):

    template_name = "reviews/review_list.html"
    model = Review
    context_object_name = "reviews"

    # def get_queryset(self):
    #     base_query = super().get_queryset()
    #     data = base_query.filter(rating__gte=3)
    #     return data


class SingleReviewView(DetailView):
    template_name = "reviews/single_review.html"

    model = Review
    

