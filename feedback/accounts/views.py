from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView


# Create your views here.
class SignUpView(CreateView):
    form_class = UserCreationForm               # Built-in: username + password1 + password2, validated and hashed
    template_name = "registration/signup.html"
    success_url = reverse_lazy("review-list")   # reverse_lazy: the URLs aren't loaded yet when the class is defined

    def form_valid(self, form):
        response = super().form_valid(form)     # Saves the new User (self.object), redirect to success_url
        login(self.request, self.object)        # Log the new user in right away (puts their id in the session)
        return response
