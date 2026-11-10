from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views import View
from .forms import ReviewForm
from django.views.generic.base import TemplateView
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from .models import Review

class ReviewView(LoginRequiredMixin, CreateView):
    # Anonymous -> redirect to LOGIN_URL with ?next=/ (back here after login)
    model = Review
    form_class = ReviewForm
    template_name = "reviews/review.html"
    success_url = "/thank-you"

    def form_valid(self, form):
        form.instance.owner = self.request.user  # The logged-in user owns the new review
        return super().form_valid(form)


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
        session = self.request.session
        recent_ids = session.get("recent_reviews", [])
        reviews_by_id = Review.objects.in_bulk(recent_ids)       # {id: Review}, one query
        context["recent_reviews"] = [reviews_by_id[i] for i in recent_ids if i in reviews_by_id]  # Keep the newest-first order
        context["session_key"] = session.session_key          # The value of the sessionid cookie (None if no session yet)
        context["session_expires"] = session.get_expiry_date()
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

        recent = request.session.get("recent_reviews", [])  # A list of ids, [] the first time
        if self.object.id in recent:
            recent.remove(self.object.id)
        recent.insert(0, self.object.id)                     # Newest first
        request.session["recent_reviews"] = recent[:3]       # Assigning the key -> Django saves the session
        request.session.set_expiry(120)                      # This session ends 2 minutes after the LAST request (testing)
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


class ClearSessionView(View):
    # Ends the session: data deleted from the DB, new session key
    def get(self, request):
        request.session.flush()  # logout() does the same
        return HttpResponseRedirect("/reviews")


class ReviewUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    # Only the review's owner may edit it: anonymous -> login page, logged in but not the owner -> 403
    model = Review
    form_class = ReviewForm
    template_name = "reviews/review.html"

    def test_func(self):
        return self.get_object().owner == self.request.user  # True -> allowed, False -> 403 Forbidden

    def get_success_url(self):
        return f"/reviews/{self.object.id}"


class ReviewDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    # Only users with the delete_review permission (a moderator, or a superuser) may delete
    model = Review
    permission_required = "reviews.delete_review"  # "<app_label>.<action>_<model>", created by migrate
    template_name = "reviews/review_confirm_delete.html"
    success_url = "/reviews"

