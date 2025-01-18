# roomie_users/urls.py

from django.urls import path
from .views import ProfileCreateView, ProfileRetrieveView, ProfileUpdateView, ProfileDeleteView, ProfileListView

urlpatterns = [
    path('profile/<int:pk>/', ProfileRetrieveView.as_view(), name='profile-retrieve'),
    path('profile/update/<int:pk>/', ProfileUpdateView.as_view(), name='profile-update'),
    path('profile/delete/<int:pk>/', ProfileDeleteView.as_view(), name='profile-delete'),
    path('profile/create/', ProfileCreateView.as_view(), name='profile-create'),
    path('api/profile/', ProfileListView.as_view(), name='profile-list'),
]
