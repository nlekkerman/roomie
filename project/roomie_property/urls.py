# roomie_property/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PropertyViewSet, OwnerDashboardView

router = DefaultRouter()
router.register(r'properties', PropertyViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('owner-dashboard/', OwnerDashboardView.as_view(), name='owner-dashboard'),
]
