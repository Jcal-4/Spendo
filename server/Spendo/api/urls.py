from django.urls import path
from django.contrib.auth import views as auth_views
from .views import get_customusers, get_customuser_by_username, FrontendAppView, UserMeView, LoginView
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse

@ensure_csrf_cookie
def get_csrf(request):
    return JsonResponse({'detail': 'CSRF cookie set'})

urlpatterns = [
    path('api/csrf/', get_csrf),
    # Session-based login/logout
    path('login/', LoginView.as_view(), name='api-login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', FrontendAppView.as_view(), name='frontend'),
    path('customusers/', get_customusers, name='get_customusers'),
    path('customuser/<username>/', get_customuser_by_username, name='get_customuser_by_username' ),
    path('me/', UserMeView.as_view(), name='user-me'),
]
