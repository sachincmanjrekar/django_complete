from django.urls import path
from . import views


urlpatterns = [
    path('singleobj/<int:id>/', views.single_object_view, name='single_object_view'),
    path('multipleobj/', views.multiple_objects_view, name='multiple_objects_view'),
]
