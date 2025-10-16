from django.urls import path
from django.contrib.auth import views as auth_views
from .views import create_chatkit_session, trigger_openAI_request, get_user_accounts, get_customusers, get_customuser_by_username, create_customuser, FrontendAppView, UserMeView, LoginView, LogoutView
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse

@ensure_csrf_cookie
def get_csrf(request):
    return JsonResponse({'detail': 'CSRF cookie set'})

urlpatterns = [
    path('api/csrf/', get_csrf),
    path('chatkit/session/', create_chatkit_session, name='create_chatkit_session'),
    path('', FrontendAppView.as_view(), name='frontend'),
    path('me/', UserMeView.as_view(), name='user-me'),
    # Session-based login/logout
    path('login/', LoginView.as_view(), name='api-login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    # User management
    path('customusers/', get_customusers, name='get_customusers'),
    path('createuser/', create_customuser, name='create_customuser'),
    path('customuser/<username>/', get_customuser_by_username, name='get_customuser_by_username' ),
    # Users accounts and transactions
    path('customuser/<int:user_id>/accounts/', get_user_accounts, name='get_user_accounts'),
    path('openai/chatbot/', trigger_openAI_request, name ='trigger_openAI_request')
]
