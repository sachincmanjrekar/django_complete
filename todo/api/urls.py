from django.urls import path
from . import views

urlpatterns = [
    path('', views.RootAPIView.as_view(), name='root'),
    path('todo/', views.TodoListCreateView.as_view(), name='list'),
    path('todo/<int:pk>/', views.TodoRetrieveUpdateDestroyView.as_view(), name='detail'),
]
