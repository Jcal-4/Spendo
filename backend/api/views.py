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
from django.views.generic import View
from django.http import FileResponse, StreamingHttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
import json
import os
import asyncio
from openai import OpenAI
from .chatkit_server import get_chatkit_server
from chatkit.server import StreamingResult



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
        
        # Note: We don't access request.session here because:
        # 1. It requires sync_to_async (sessions use database queries)
        # 2. We use database-backed user identification instead (ChatKitThread/ChatKitUserSession)
        # 3. ChatKit doesn't send cookies anyway, so sessions won't work
        
        # Pass request in context (user identification happens in chatkit_server.py)
        context = {
            "request": request,
        }
        result = await server.process(payload, context)
        
        if isinstance(result, StreamingResult):
            # Collect all items from the async iterator first
            print(f"DEBUG: Processing StreamingResult, type: {type(result)}")
            try:
                items = await _collect_streaming_result(result)
                print(f"DEBUG: Collected {len(items)} items from StreamingResult")
                
                # Create a synchronous generator from collected items
                def sync_iterator():
                    try:
                        for idx, item in enumerate(items):
                            print(f"DEBUG: Yielding item {idx}, type: {type(item)}")
                            # StreamingResult items should already be in the correct format
                            # ChatKit SDK handles serialization internally
                            if isinstance(item, bytes):
                                yield item
                            elif isinstance(item, str):
                                yield item.encode('utf-8')
                            else:
                                # If it's a Pydantic model or similar, try to serialize
                                if hasattr(item, 'model_dump_json'):
                                    yield item.model_dump_json().encode('utf-8')
                                elif hasattr(item, 'json'):
                                    yield item.json().encode('utf-8')
                                else:
                                    # Default: yield as-is (ChatKit SDK should handle it)
                                    yield item
                    except Exception as yield_error:
                        print(f"DEBUG: Error in sync_iterator: {yield_error}")
                        import traceback
                        print(f"DEBUG: Yield error traceback: {traceback.format_exc()}")
                        raise
                
                # Return streaming response
                response = StreamingHttpResponse(
                    sync_iterator(),
                    content_type="text/event-stream"
                )
                response['Cache-Control'] = 'no-cache'
                response['X-Accel-Buffering'] = 'no'
                # Note: Don't set 'Connection: keep-alive' - it's a hop-by-hop header
                # that causes errors with Django's development server (wsgiref)
                # SSE connections are kept alive by default
                print("DEBUG: Returning StreamingHttpResponse")
                return response
            except Exception as stream_error:
                print(f"DEBUG: Error processing StreamingResult: {stream_error}")
                import traceback
                error_trace = traceback.format_exc()
                print(f"DEBUG: StreamingResult error traceback: {error_trace}")
                # Return error as JSON so ChatKit can display it
                return JsonResponse(
                    {"error": f"Streaming error: {str(stream_error)}", "traceback": error_trace},
                    status=500,
                    safe=False
                )
        
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
    }
    response = requests.post(url, headers=headers, json=data)
    print("response: ", response)
    if response.status_code == 200:
        response_data = response.json()
        client_secret = response_data.get("client_secret")
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
            os.path.dirname(os.path.abspath(__file__)), "../spendo/client_dist/index.html"
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
