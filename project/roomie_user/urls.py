# roomie_user/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet

router = DefaultRouter()
router.register(r'roomie_user', CustomUserViewSet)

urlpatterns = [
    path('', include(router.urls)),  # Include the router-generated URLs
]
