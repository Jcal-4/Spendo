from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser
from .serializer import CustomUserSerializer
from .services.user_service import get_users_by_email, get_user_by_username, create_user, get_accounts_by_userid
from django.views.generic import View
from django.http import FileResponse
from openai import OpenAI
import os

from dotenv import load_dotenv
load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=openai_api_key)

# Define type of request with api_view

@api_view(['POST'])
def trigger_opanAI_request(request):
    user_message = request.data.get('user_message')
    # user_accounts_data = get_accounts_by_userid(request.data.get('user_id'))
    user_accounts_data = request.data.get('user_balance')
    # Combine user data and question into a message
    system_message = (
        f"You are a well-versed financial advisor. Limit the response to under 150 words.\n"
        f"If the question is pertaining to anything about how they can manage their money then make sure to respond with a brief description of their current balances. Only do this if it benefits the response."
        f"Here is the user's financial data:\n"
        f"Cash balance: {user_accounts_data['cash_balance']}\n"
        f"Savings balance: {user_accounts_data['savings_balance']}\n"
        f"Investing/Retirement: {user_accounts_data['investing_retirement']}"
    )

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]

    response = client.chat.completions.create(
        model="gpt-5-nano",
        messages=messages
    )
    
    if not response:
        return Response('No response from openAI')
    return Response({"result": response.choices[0].message.content})
    # return Response({"result": "fake return"})

@api_view(['GET'])
def get_user_accounts(request, user_id):
    data = get_accounts_by_userid(user_id)
    if not data:
        return Response('No accounts found for logged in User')
    return Response(data)
    

@api_view(['GET'])
def get_customusers(request):
    email = request.data.get('email')
    print(email)
    data = get_users_by_email(email)
    if not data:
        return Response('No users found')
    return Response(data)


@api_view(['GET'])
def get_customuser_by_username(request, username):
    data = get_user_by_username(username)
    if not data:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    return Response(data)

@api_view(['POST'])
def create_customuser(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    first_name = request.data.get('first_name')
    last_name = request.data.get("last_name")
    result = create_user(username, email, password, first_name, last_name)
    if not result:
        return Response("User creation failed")
    return Response({"detail": "User created successfully"}, status=status.HTTP_201_CREATED)

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
    
class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'detail': 'Logged out'})