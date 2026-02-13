"""
Authentication Views for Prolean API
"""
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import authenticate
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from ..serializers.auth import (
    StudentRegistrationSerializer,
    LoginSerializer,
    LoginResponseSerializer,
    ProfileSerializer
)


@method_decorator(ratelimit(key='ip', rate='5/h', method='POST'), name='dispatch')
class StudentRegistrationView(generics.CreateAPIView):
    """
    POST /api/v1/auth/register/
    Register a new student account
    Creates user with PENDING status - requires admin activation
    Rate limited: 5 requests per hour per IP
    """
    permission_classes = [AllowAny]
    serializer_class = StudentRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
            'profile': ProfileSerializer(user.profile).data,
            'message': 'Account created successfully. Your account is pending approval by our staff. You will be notified once activated.'
        }, status=status.HTTP_201_CREATED)


@method_decorator(ratelimit(key='ip', rate='10/h', method='POST'), name='dispatch')
class StudentLoginView(APIView):
    """
    POST /api/v1/auth/login/
    Login with username and password
    Returns JWT access and refresh tokens
    Rate limited: 10 requests per hour per IP
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        # Authenticate user
        user = authenticate(username=username, password=password)
        
        if user is None:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Check if user has profile
        if not hasattr(user, 'profile'):
            return Response({
                'error': 'User profile not found'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if student account is active
        if user.profile.role == 'STUDENT' and user.profile.status != 'ACTIVE':
            return Response({
                'error': 'Your account is pending approval. Please wait for staff activation.',
                'status': user.profile.status
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.profile.full_name,
                'role': user.profile.role,
                'status': user.profile.status
            }
        }, status=status.HTTP_200_OK)


class StudentLogoutView(APIView):
    """
    POST /api/v1/auth/logout/
    Logout and blacklist refresh token
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Token refresh view (provided by simplejwt)
class CustomTokenRefreshView(TokenRefreshView):
    """
    POST /api/v1/auth/refresh/
    Refresh access token using refresh token
    """
    pass
