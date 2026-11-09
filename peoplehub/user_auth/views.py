from django.shortcuts import render
from rest_framework.views import APIView, Response
from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.permissions import AllowAny
# Create your views here.

class LoginView(APIView):
    permission_classes = []  # Overrides the global IsAuthenticated: anyone can try to log in
    authentication_classes = []  # No authentication required for login

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=200)

        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)