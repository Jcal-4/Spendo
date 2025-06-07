from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser
from .serializer import CustomUserSerializer

# Define type of request with api_view
@api_view(['GET'])
def get_customusers(request):
    email = request.GET.get('email')
    if email:
        customusers = CustomUser.objects.filter(email=email)
    else:
        customusers = CustomUser.objects.all()
    serializedData = CustomUserSerializer(customusers, many=True).data
    return Response(serializedData)


# Use the views.py in our api app to set up the requests 
# I had to create the serializer.py file
# Attribtue of many=True because it can recieve many records (list)
# Create the urls.py file in the api (do not get this confused with the one already in the Spendo folder)
