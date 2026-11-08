from django.urls import path
from . import views


urlpatterns = [
    path('singleobj/<int:pk>/', views.SingleObjectGenericView.as_view(), name='single_object_view'),
    path('multipleobj/', views.MultipleObjectsGenericView.as_view(), name='multiple_objects_view'),
]
