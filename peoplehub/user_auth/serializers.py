from django.contrib.auth.models import User
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  # Accepted on input, never sent back in a response

    class Meta:
        model = User
        fields = ['username', 'password']

    def create(self, validated_data):
        # create_user() hashes the password; User.objects.create() would store it as plain text
        return User.objects.create_user(**validated_data)
