from django.urls import path
from . import views


urlpatterns = [
    path('singleobj/<int:id>/', views.SingleObjectView.as_view(), name='single_object_view'),
    path('multipleobj/', views.MultipleObjectsView.as_view(), name='multiple_objects_view'),
]
