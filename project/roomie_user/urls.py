# urls.py
from django.urls import path
from .views import CustomUserProfileView, DefaultUserView

urlpatterns = [
    
    path('me/', CustomUserProfileView.as_view(), name='user-profile'),
    path('default-user/', DefaultUserView.as_view(), name='default-user'),
]
