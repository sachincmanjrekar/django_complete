from django.shortcuts import render
from rest_framework.views import APIView, Response
from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer
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


class RegisterView(APIView):
    permission_classes = []  # Overrides the global IsAuthenticated: anyone can register
    authentication_classes = []  # No token needed to register

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # 400 if username is taken / fields are missing
        user = serializer.save()  # Calls RegisterSerializer.create() -> create_user()
        token = Token.objects.create(user=user)  # New user, so a new token
        return Response({'token': token.key}, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    # No overrides: the global TokenAuthentication + IsAuthenticated apply,
    # so only a request with a valid token gets here (no token -> 401)

    def post(self, request):
        request.user.auth_token.delete()  # Delete this user's token; it stops working at once
        return Response({'message': 'Logged out'}, status=status.HTTP_200_OK)
