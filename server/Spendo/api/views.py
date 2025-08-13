from rest_framework.decorators import api_view
from django.contrib.auth import authenticate, login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser
from .serializer import CustomUserSerializer
from django.views.generic import View
from django.http import FileResponse
import os

# Define type of request with api_view
@api_view(['GET'])
def get_customusers(request):
    email = request.data.get('email')
    print(email)
    if email:
        customusers = CustomUser.objects.filter(email=email)
    else:
        customusers = CustomUser.objects.all()
    serializedData = CustomUserSerializer(customusers, many=True).data
    if not customusers:
        return Response(f'No users found')
    return Response(serializedData)

@api_view(['GET'])
def get_customuser_by_username(request, username):
    try:
        customuser = CustomUser.objects.get(username=username)
        serializedData = CustomUserSerializer(customuser, many=False).data
        return Response(serializedData)
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

class FrontendAppView(View):
    def get(self, request):
        index_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '../client_dist/index.html'
        )
        return FileResponse(open(index_path, 'rb'))
    
class UserMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            "role": "admin" if user.is_staff or user.is_superuser else "user",
        })
        
class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        print(username, ' ', password)
        user = authenticate(request, username=username, password=password)
        print(user)
        if user is not None:
            login(request, user)
            return Response({'detail': 'Logged in'})
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)