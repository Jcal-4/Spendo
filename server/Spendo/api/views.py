from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser
from .serializer import CustomUserSerializer
from .services.user_service import (
    get_users_by_email,
    get_user_by_username,
    create_user,
    get_accounts_by_userid,
)
# from .services.OpenAI_service import analyze_user_message
from django.views.generic import View
from django.http import FileResponse, StreamingHttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
import os
import asyncio
from openai import OpenAI
from .chatkit_server import get_chatkit_server
from chatkit.server import StreamingResult

# Store mapping of ChatKit username to Django user ID in database
# We'll use the ChatKitThread model to store this persistently


async def _collect_streaming_result(streaming_result):
    """Collect all items from a StreamingResult async iterator."""
    items = []
    # Check if it's an async iterator
    if hasattr(streaming_result, '__aiter__'):
        async_iter = streaming_result.__aiter__()
        try:
            while True:
                item = await async_iter.__anext__()
                items.append(item)
        except StopAsyncIteration:
            pass
    # Check if it's a regular iterator
    elif hasattr(streaming_result, '__iter__'):
        for item in streaming_result:
            items.append(item)
    else:
        # Try to iterate it directly
        try:
            async for item in streaming_result:
                items.append(item)
        except TypeError:
            # Not iterable, return as single item
            items = [streaming_result]
    return items


@csrf_exempt
async def chatkit_endpoint(request):
    """ChatKit SDK endpoint for handling chat requests."""
    # Allow both GET (for health checks) and POST (for chat requests)
    if request.method not in ["GET", "POST"]:
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    # Handle GET requests (health check)
    if request.method == "GET":
        return JsonResponse({"status": "ok"})
    
    try:
        server = get_chatkit_server()
        payload = request.body
        
        if not payload:
            return JsonResponse({"error": "Empty payload"}, status=400)
        
        # Try to get user_id from Django session (set when getClientSecret was called)
        django_user_id = None
        if hasattr(request, 'session'):
            django_user_id = request.session.get('chatkit_user_id')
            if django_user_id:
                print(f"DEBUG: Got user_id from session: {django_user_id}")
        
        # Pass user information in context
        context = {
            "request": request,
            "user_id": django_user_id,
        }
        result = await server.process(payload, context)
        
        if isinstance(result, StreamingResult):
            # Collect all items from the async iterator first
            items = await _collect_streaming_result(result)
            
            # Create a synchronous generator from collected items
            def sync_iterator():
                for item in items:
                    yield item
            
            # Return streaming response
            response = StreamingHttpResponse(
                sync_iterator(),
                content_type="text/event-stream"
            )
            response['Cache-Control'] = 'no-cache'
            response['X-Accel-Buffering'] = 'no'
            return response
        
        if hasattr(result, "json"):
            return JsonResponse(json.loads(result.json), safe=False)
        
        return JsonResponse(result, safe=False)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"ChatKit endpoint error: {e}")
        print(f"Traceback: {error_details}")
        return JsonResponse(
            {"error": str(e), "details": error_details},
            status=500,
            safe=False
        )

@api_view(["POST"])
def create_chatkit_session(request):
    import requests

    openai_api_key = os.getenv("OPENAI_API_KEY")
    workflow_id = "wf_68ee92d551ac819096e06e9789e4accf05c17f1103e9f72d"
    url = "https://api.openai.com/v1/chatkit/sessions"
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "chatkit_beta=v1",
    }
    
    # Get user ID from request body (passed from frontend) or from authenticated user
    user_id_from_body = request.data.get("user_id") if hasattr(request, 'data') else None
    django_user_id = None
    
    if user_id_from_body:
        # Look up user by ID to get username
        try:
            from .models import CustomUser
            user = CustomUser.objects.get(pk=user_id_from_body)
            chatkit_user_id = user.username
            django_user_id = user_id_from_body
        except CustomUser.DoesNotExist:
            chatkit_user_id = "anonymous"
    elif request.user and request.user.is_authenticated:
        chatkit_user_id = request.user.username
        django_user_id = request.user.id
    else:
        chatkit_user_id = "anonymous"

    data = {
        "workflow": {"id": workflow_id},
        "user": chatkit_user_id
        # Add other required parameters here
    }
    response = requests.post(url, headers=headers, json=data)
    print("response: ", response)
    if response.status_code == 200:
        response_data = response.json()
        client_secret = response_data.get("client_secret")
        
        # Store mapping of ChatKit username to Django user ID in database
        # This will be used to identify users when ChatKit makes requests
        if chatkit_user_id and django_user_id:
            try:
                from .models import CustomUser, ChatKitThread
                user = CustomUser.objects.get(pk=django_user_id)
                # Store username -> user mapping (we'll use this when we can get the username from requests)
                # For now, we'll rely on thread_id lookups in chatkit_server.py
                print(f"DEBUG: Created ChatKit session for username {chatkit_user_id} -> Django user ID {django_user_id}")
            except Exception as e:
                print(f"DEBUG: Error storing user mapping: {e}")
        
        return Response({"client_secret": client_secret})
    else:
        print("ChatKit session creation error:", response.text)
        return Response({"error": response.text}, status=response.status_code)

# TODO: Uncomment the code below when analyze_user_message is restored
# @api_view(["POST"])
# def trigger_openAI_request(request):
#     user_message = request.data.get("user_message")
#     user_accounts_data = request.data.get("user_balance")
#     result = analyze_user_message(user_message)
#     output_content = result.output[1].content[0].text
#     # output_content = output_content.strip().lstrip('\ufeff')
#     print(
#         "\033[92moutput_content repr:\033[0m", output_content
#     )  # Debug: see invisible chars
#     try:
#         parsed = json.loads(output_content)
#     except Exception as e:
#         print("JSON decode error:", e)
#         return Response("Error parsing OpenAI response.")
#     if not parsed.get("Finance_Question"):
#         return Response(
#             "Question does not pertain to finances please ask another question."
#         )
#     if not parsed.get("Valid_Prompt_Message"):
#         return Response(parsed.get("Tentative_Response"))
#     return Response(parsed.get("Monetary_Balance_Query"))


@api_view(["GET"])
def get_user_accounts(request, user_id):
    data = get_accounts_by_userid(user_id)
    if not data:
        return Response("No accounts found for logged in User")
    return Response(data)


@api_view(["GET"])
def get_customusers(request):
    email = request.data.get("email")
    print(email)
    data = get_users_by_email(email)
    if not data:
        return Response("No users found")
    return Response(data)


@api_view(["GET"])
def get_customuser_by_username(request, username):
    data = get_user_by_username(username)
    if not data:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    return Response(data)


@api_view(["POST"])
def create_customuser(request):
    username = request.data.get("username")
    email = request.data.get("email")
    password = request.data.get("password")
    first_name = request.data.get("first_name")
    last_name = request.data.get("last_name")
    result = create_user(username, email, password, first_name, last_name)
    if not result:
        return Response("User creation failed")
    return Response(
        {"detail": "User created successfully"}, status=status.HTTP_201_CREATED
    )


class FrontendAppView(View):
    def get(self, request):
        index_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../client_dist/index.html"
        )
        return FileResponse(open(index_path, "rb"))


class UserMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
                "role": "admin" if user.is_staff or user.is_superuser else "user",
            }
        )


class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        print(username, " ", password)
        user = authenticate(request, username=username, password=password)
        print(user)
        if user is not None:
            login(request, user)
            # Store user session for ChatKit
            try:
                from .models import ChatKitUserSession
                ChatKitUserSession.objects.update_or_create(
                    user=user,
                    defaults={}  # Just update the updated_at timestamp
                )
                print(f"DEBUG: Stored ChatKit session for user {user.id}")
            except Exception as e:
                print(f"DEBUG: Error storing ChatKit session: {e}")
            return Response({"detail": "Logged in"})
        return Response(
            {"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )


class LogoutView(APIView):
    def post(self, request):
        # Delete ChatKit session before logging out
        if request.user.is_authenticated:
            try:
                from .models import ChatKitUserSession
                ChatKitUserSession.objects.filter(user=request.user).delete()
                print(f"DEBUG: Deleted ChatKit session for user {request.user.id}")
            except Exception as e:
                print(f"DEBUG: Error deleting ChatKit session: {e}")
        logout(request)
        return Response({"detail": "Logged out"})
