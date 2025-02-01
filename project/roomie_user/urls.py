# urls.py
from django.urls import path
from .views import CustomUserListView, CustomUserDetailView, CustomUserProfileView

urlpatterns = [
    path('customusers/', CustomUserListView.as_view(), name='customuser-list'),
    path('customusers/<int:pk>/', CustomUserDetailView.as_view(), name='customuser-detail'),
    path('me/', CustomUserProfileView.as_view(), name='user-profile'),
]
