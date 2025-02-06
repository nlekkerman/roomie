# roomie_property/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PropertyViewSet, OwnerDashboardView,PropertyCreateView,PropertyUpdateTextFieldsView

router = DefaultRouter()
router.register(r'properties', PropertyViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('owner-dashboard/', OwnerDashboardView.as_view(), name='owner-dashboard'),
    path('properties/create/', PropertyCreateView.as_view(), name='property-create'),
    path('properties/<int:pk>/update-text-fields/', PropertyUpdateTextFieldsView.as_view(), name='update_text_fields'),

]
