# urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DamageRepairReportViewSet, RepairImageViewSet,NotificationViewSet

router = DefaultRouter()
router.register(r'damage-reports', DamageRepairReportViewSet)
router.register(r'repair-images', RepairImageViewSet)
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),  # Add the API routes
]
