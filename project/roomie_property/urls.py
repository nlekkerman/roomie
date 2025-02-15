# roomie_property/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PropertyViewSet,RoomImageUploadView, OwnerDashboardView,PropertyUpdateTextFieldsView,AllCustomUsersView, TenancyRequestViewSet,TenantTenancyRequestViewSet

router = DefaultRouter()
router.register(r'properties', PropertyViewSet)
router.register(r'tenancy-requests', TenancyRequestViewSet)
router.register(r'tenant-tenancy-requests', TenantTenancyRequestViewSet, basename='tenant-tenancy-requests')


urlpatterns = [
    path('', include(router.urls)),
    path('owner-dashboard/', OwnerDashboardView.as_view(), name='owner-dashboard'),
    path('properties/<int:pk>/update-text-fields/', PropertyUpdateTextFieldsView.as_view(), name='update_text_fields'),
    path('upload-room-image/', RoomImageUploadView.as_view(), name='upload-room-image'),
    path("custom-users/", AllCustomUsersView.as_view(), name="custom-users"),


]
