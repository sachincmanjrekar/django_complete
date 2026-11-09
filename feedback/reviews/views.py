from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views import View
from .forms import ReviewForm
from django.views.generic.base import TemplateView
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from .models import Review

class ReviewView(CreateView):

    model = Review
    form_class = ReviewForm
    template_name = "reviews/review.html"
    success_url = "/thank-you"


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["last_viewed_id"] = self.request.COOKIES.get("last_viewed_review")  # A string, or None
        context["visits"] = self.request.get_signed_cookie("review_visits", default=0)  # Tampered or missing -> 0
        return context

    # def get_queryset(self):
    #     base_query = super().get_queryset()
    #     data = base_query.filter(rating__gte=3)
    #     return data


class SingleReviewView(DetailView):
    template_name = "reviews/single_review.html"

    model = Review

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        loaded_review = self.object
        request = self.request
        favorite_id = request.session.get("favorite_review")
        context["is_favorite"] = str(loaded_review.id) == favorite_id
        return context

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)  # The normal DetailView response
        response.set_cookie(
            "last_viewed_review", self.object.id,
            max_age=60,                # 1 minute (for testing; was 60 * 60 * 24 * 7 = 1 week)
            httponly=True,             # JavaScript can't read it
            samesite="Lax",            # Not sent on requests coming from other sites
        )
        visits = request.get_signed_cookie("review_visits", default=0)  # Tampered or missing -> 0
        response.set_signed_cookie("review_visits", int(visits) + 1)    # No max_age: gone when the browser closes
        return response


class AddfavoriteView(View):

    def post(self, request):
        review_id = request.POST['review_id']
        request.session["favorite_review"] = review_id
        return HttpResponseRedirect("/reviews/" + review_id)


class ForgetCookiesView(View):
    # Deletes both cookies, then back to the list
    def get(self, request):
        response = HttpResponseRedirect("/reviews")
        response.delete_cookie("last_viewed_review")  # Sends the cookie again with Max-Age=0 -> the browser removes it
        response.delete_cookie("review_visits")
        return response

