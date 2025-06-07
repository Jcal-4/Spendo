from django.urls import path
from .views import get_customusers

urlpatterns = [
    path('customusers/', get_customusers, name='get_customusers')
]
