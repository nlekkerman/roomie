# urls.py
from django.urls import path
from .views import CustomUserProfileView

urlpatterns = [
    
    path('me/', CustomUserProfileView.as_view(), name='user-profile'),
]
