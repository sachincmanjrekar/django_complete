from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .models import Todo
from .serializers import TodoSerializer


# Create your views here.
class TodoListCreateView(ListCreateAPIView):
    # GET: the logged-in user's todos, POST: a new todo for the logged-in user
    serializer_class = TodoSerializer

    def get_queryset(self):
        return Todo.objects.filter(user=self.request.user)  # Only this user's todos, never anyone else's

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)  # The owner is whoever sent the request


class TodoRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    # GET / PUT / PATCH / DELETE one todo
    serializer_class = TodoSerializer

    def get_queryset(self):
        return Todo.objects.filter(user=self.request.user)  # Another user's todo id -> 404


class RootAPIView(APIView):
    # Entry point: links to the API's endpoints
    def get(self, request):
        return Response({
            'list': reverse('list', request=request),  # Full URL of the URL named 'list'
        })
