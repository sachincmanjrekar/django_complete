## Project: Multi User Todo REST API

    - Each user has their own todos: a user can only list, see, update and
      delete their own. The course's code is in Downloads\DRF\todo.
    - Created with the drf venv from peoplehub (it has Django + DRF):
        cd C:\Users\scman\django_complete
        .\peoplehub\drf\Scripts\activate
        django-admin startproject todo
        cd todo
        python manage.py startapp api
    - todo/settings.py, INSTALLED_APPS:
        'api',
        'rest_framework',

## Todo model

    - api/models.py:
        from django.db import models
        from django.contrib.auth.models import User

        class Todo(models.Model):
            title = models.CharField(max_length=200)
            description = models.TextField()
            completed = models.BooleanField(default=False)
            created_at = models.DateField(auto_now_add=True)  # Set once, when the todo is created
            user = models.ForeignKey(User, on_delete=models.CASCADE)  # Owner; deleting the user deletes their todos

            def __str__(self):
                return self.title
    - user = ForeignKey(User) -> many todos per user; this is what makes it
      "multi user".
    - python manage.py makemigrations api   -> api\migrations\0001_initial.py, Create model Todo
      python manage.py migrate
    - api/admin.py:
        @admin.register(Todo)
        class TodoAdmin(admin.ModelAdmin):
            list_display = ['title', 'completed', 'created_at', 'user']
      @admin.register(Todo) = the same as admin.site.register(Todo, TodoAdmin).

## TodoSerializer

    - api/serializers.py:
        class TodoSerializer(serializers.ModelSerializer):
            class Meta:
                model = Todo
                fields = ['id', 'title', 'description', 'completed', 'created_at']
                read_only_fields = ['created_at']  # Shown in responses, can't be sent by the client
    - read_only_fields: created_at is in the response, but a created_at
      sent by the client is ignored (auto_now_add sets it).
    - 'user' is not in fields: the view sets it from request.user, so nobody
      can create a todo for someone else.
    - 'id' added (the course's version has no id) so the client knows which
      URL /todo/<id>/ to use.

## Views: get_queryset() and perform_create()

    - api/views.py:
        class TodoListCreateView(ListCreateAPIView):
            serializer_class = TodoSerializer

            def get_queryset(self):
                return Todo.objects.filter(user=self.request.user)  # Only this user's todos, never anyone else's

            def perform_create(self, serializer):
                serializer.save(user=self.request.user)  # The owner is whoever sent the request


        class TodoRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
            serializer_class = TodoSerializer

            def get_queryset(self):
                return Todo.objects.filter(user=self.request.user)  # Another user's todo id -> 404


        class RootAPIView(APIView):
            def get(self, request):
                return Response({
                    'list': reverse('list', request=request),  # Full URL of the URL named 'list'
                })
    - get_queryset() instead of queryset = ...: the queryset depends on who
      sends the request, so it is built per request. The generic views use
      it for the list AND for get_object(), so another user's id is "not
      found" (404) for GET / PUT / PATCH / DELETE.
    - perform_create(serializer): CreateModelMixin calls it after
      is_valid(); serializer.save(user=...) adds the owner to the data
      before saving.
    - rest_framework.reverse.reverse(name, request=request) -> the full URL
      (http://127.0.0.1:8000/todo/) instead of just /todo/.
    - api/urls.py:
        urlpatterns = [
            path('', views.RootAPIView.as_view(), name='root'),
            path('todo/', views.TodoListCreateView.as_view(), name='list'),
            path('todo/<int:pk>/', views.TodoRetrieveUpdateDestroyView.as_view(), name='detail'),
        ]
    - todo/urls.py:
        path('', include('api.urls')),  # The todo API
        path('api-auth/', include('rest_framework.urls')),  # Log in / log out for the browsable API

## IsAuthenticated for every view

    - The course's code has no permission setting. An anonymous request
      makes request.user = AnonymousUser, and
      Todo.objects.filter(user=AnonymousUser) / save(user=AnonymousUser)
      fail.
    - todo/settings.py:
        REST_FRAMEWORK = {
            'DEFAULT_PERMISSION_CLASSES': [
                'rest_framework.permissions.IsAuthenticated',
            ],
        }
      Authentication stays DRF's default (SessionAuthentication +
      BasicAuthentication), so logging in at /api-auth/login/ works in the
      browser.
    - Not logged in -> 403 {"detail": "Authentication credentials were not provided."}
      (403, not 401: SessionAuthentication, the first class, sends no
      WWW-Authenticate header.)

## Checked: two users (test client, rolled back)

    - alice and bob, logged in:
        anonymous GET /todo/            -> 403
        GET /                           -> {"list": "http://127.0.0.1/todo/"}
        alice POST /todo/ {"title": "buy milk", "description": "2 litres"}
                                        -> 201 {"id": 1, "title": "buy milk", "description": "2 litres",
                                                "completed": false, "created_at": "2026-11-09"}
        POST with "created_at": "2000-01-01" -> saved as today (read only)
        bob POST "gym"                  -> 201
        alice GET /todo/                -> only alice's todos
        bob GET /todo/                  -> ["gym"] only
        bob GET /todo/1/ (alice's)      -> 404
        bob DELETE /todo/1/ (alice's)   -> 404
        alice PATCH /todo/1/ {"completed": true} -> 200
        alice DELETE /todo/1/           -> 204
        POST without title              -> 400 {"title": ["This field is required."]}

## Helpful resources

    - Django REST Framework (DRF) docs:
        https://www.django-rest-framework.org/
    - Generic views (get_queryset, perform_create):
        https://www.django-rest-framework.org/api-guide/generic-views/
