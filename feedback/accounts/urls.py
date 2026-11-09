from django.urls import path, include
from . import views

urlpatterns = [
    path("signup/", views.SignUpView.as_view(), name="signup"),
    # Django's built-in auth views: login/, logout/, password_change/, password_reset/, ...
    path("", include("django.contrib.auth.urls")),
]
