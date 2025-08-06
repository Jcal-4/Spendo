from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
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