from django.urls import path

from . import views

urlpatterns = [
    path("", views.CreateProfileView.as_view()),
    path("lists", views.ProfilesView.as_view())
]

