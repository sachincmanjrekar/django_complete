from rest_framework import serializers
from .models import Todo


class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = ['id', 'title', 'description', 'completed', 'created_at']
        read_only_fields = ['created_at']  # Shown in responses, can't be sent by the client
        # 'user' is not a field: the view sets it from request.user, so nobody can create a todo for someone else
