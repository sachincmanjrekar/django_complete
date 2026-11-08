from django.urls import path
from . import views


urlpatterns = [
    path('singleobj/<int:pk>/', views.SingleObjectConcreteView.as_view(), name='single_object_view'),
    path('multipleobj/', views.MultipleObjectsConcreteView.as_view(), name='multiple_objects_view'),
]
