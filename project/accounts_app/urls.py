from django.urls import path
from .views import RegisterUserView, ObtainTokenPairWithPassword, RefreshTokenView

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', ObtainTokenPairWithPassword.as_view(), name='login'),
    path('token/refresh/', RefreshTokenView.as_view(), name='token_refresh'),
]
