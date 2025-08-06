from django.urls import path
from .views import get_customusers, get_customuser_by_username, FrontendAppView

urlpatterns = [
    path('', FrontendAppView.as_view(), name='frontend'),
    path('customusers/', get_customusers, name='get_customusers'),
    path('customuser/<username>/', get_customuser_by_username, name='get_customuser_by_username' )
]
