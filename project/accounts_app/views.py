from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .serializers import UserSerializer

# ✅ User Registration View (Sign-Up)
class RegisterUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]  # Anyone can register

# ✅ JWT Authentication View (Login)
class ObtainTokenPairWithPassword(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # Get username and password from the request
        username = request.data.get('username')
        password = request.data.get('password')

        # Authenticate user
        user = authenticate(username=username, password=password)

        if user is not None:
            # Generate JWT tokens (refresh and access)
            refresh = RefreshToken.for_user(user)

            # Generate the access token and refresh token
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            # Optionally, return user info in response (you can remove if not needed)
            response_data = {
                'refresh': refresh_token,
                'access': access_token,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }

            return Response(response_data, status=status.HTTP_200_OK)
        
        # If authentication fails, return an error response
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

# ✅ JWT Token Refresh View
class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # Extract the refresh token from the request
        refresh_token = request.data.get('refresh')

        if refresh_token is None:
            return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Validate and refresh the token
            refresh = RefreshToken(refresh_token)
            new_access_token = str(refresh.access_token)

            return Response({'access': new_access_token}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
