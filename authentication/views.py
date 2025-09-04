from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import authenticate
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from accounts.models import CustomUser
from accounts.serializers import CustomUserSerializer, CustomUserCreateSerializer

import logging

logger = logging.getLogger(__name__)


@extend_schema(
    summary="User Registration",
    description="Register a new user account with JWT token generation.",
    request=CustomUserSerializer,
    responses={
        201: OpenApiTypes.OBJECT,
        400: OpenApiTypes.OBJECT,
    },
    examples=[
        OpenApiExample(
            'Registration Request',
            value={
                "mobile_no": "09088648123",
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "password": "securepassword123",
                "user_type": "buyer",
                "address1": "123 Main St",
                "city": "Manila",
                "province": "Metro Manila",
                "region": "NCR",
                "country": "Philippines"
            }
        ),
        OpenApiExample(
            'Registration Response',
            value={
                "user": {
                    "user_id": "uuid-string",
                    "mobile_no": "09088648123",
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john@example.com",
                    "user_type": "buyer"
                },
                "tokens": {
                    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                },
                "message": "User registered successfully"
            }
        )
    ],
    tags=["Authentication"]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Register a new user and return JWT tokens.
    """
    try:
        serializer = CustomUserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            # Log successful registration
            logger.info(f"New user registered: {user.mobile_no} - {user.get_full_name()}")
            
            response_data = {
                "user": CustomUserSerializer(user).data,
                "tokens": {
                    "access": str(access_token),
                    "refresh": str(refresh)
                },
                "message": "User registered successfully"
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            logger.warning(f"User registration failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"User registration error: {str(e)}")
        return Response(
            {"error": "Registration failed. Please try again."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    summary="User Login",
    description="Authenticate user and return JWT tokens.",
    request=OpenApiTypes.OBJECT,
    responses={
        200: OpenApiTypes.OBJECT,
        401: OpenApiTypes.OBJECT,
    },
    examples=[
        OpenApiExample(
            'Login Request',
            value={
                "mobile_no": "09088648123",
                "password": "securepassword123"
            }
        ),
        OpenApiExample(
            'Login Response',
            value={
                "user": {
                    "user_id": "uuid-string",
                    "mobile_no": "09088648123",
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john@example.com",
                    "user_type": "buyer"
                },
                "tokens": {
                    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                },
                "message": "Login successful"
            }
        )
    ],
    tags=["Authentication"]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """
    Authenticate user and return JWT tokens.
    """
    try:
        mobile_no = request.data.get('mobile_no')
        password = request.data.get('password')
        
        if not mobile_no or not password:
            return Response(
                {"error": "Mobile number and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Authenticate user
        user = authenticate(mobile_no=mobile_no, password=password)
        
        if user is not None:
            if user.is_active:
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                access_token = refresh.access_token
                
                # Log successful login
                logger.info(f"User logged in: {user.mobile_no} - {user.get_full_name()}")
                
                response_data = {
                    "user": CustomUserSerializer(user).data,
                    "tokens": {
                        "access": str(access_token),
                        "refresh": str(refresh)
                    },
                    "message": "Login successful"
                }
                
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                logger.warning(f"Login attempt for inactive user: {mobile_no}")
                return Response(
                    {"error": "Account is deactivated"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        else:
            logger.warning(f"Failed login attempt for mobile: {mobile_no}")
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return Response(
            {"error": "Login failed. Please try again."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    summary="User Logout",
    description="Logout user and blacklist refresh token.",
    request=OpenApiTypes.OBJECT,
    responses={
        200: OpenApiTypes.OBJECT,
        401: OpenApiTypes.OBJECT,
    },
    examples=[
        OpenApiExample(
            'Logout Request',
            value={
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
            }
        ),
        OpenApiExample(
            'Logout Response',
            value={
                "message": "Logout successful"
            }
        )
    ],
    tags=["Authentication"]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """
    Logout user and blacklist refresh token.
    """
    try:
        refresh_token = request.data.get('refresh_token')
        
        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            # Log successful logout
            logger.info(f"User logged out: {request.user.mobile_no} - {request.user.get_full_name()}")
            
            return Response(
                {"message": "Logout successful"},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.warning(f"Invalid refresh token during logout: {str(e)}")
            return Response(
                {"error": "Invalid refresh token"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return Response(
            {"error": "Logout failed. Please try again."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    summary="Get User Profile",
    description="Retrieve the authenticated user's profile information.",
    responses={
        200: CustomUserSerializer,
        401: OpenApiTypes.OBJECT,
    },
    tags=["Authentication"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """
    Get the authenticated user's profile.
    """
    try:
        serializer = CustomUserSerializer(request.user)
        logger.info(f"Profile retrieved for user: {request.user.mobile_no}")
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Profile retrieval error: {str(e)}")
        return Response(
            {"error": "Failed to retrieve profile"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    summary="Update User Profile",
    description="Update the authenticated user's profile information.",
    request=CustomUserSerializer,
    responses={
        200: CustomUserSerializer,
        400: OpenApiTypes.OBJECT,
        401: OpenApiTypes.OBJECT,
    },
    tags=["Authentication"]
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    """
    Update the authenticated user's profile.
    """
    try:
        serializer = CustomUserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            user = serializer.save()
            logger.info(f"Profile updated for user: {user.mobile_no}")
            return Response(CustomUserSerializer(user).data, status=status.HTTP_200_OK)
        else:
            logger.warning(f"Profile update failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        return Response(
            {"error": "Failed to update profile"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    summary="Change Password",
    description="Change the authenticated user's password.",
    request=OpenApiTypes.OBJECT,
    responses={
        200: OpenApiTypes.OBJECT,
        400: OpenApiTypes.OBJECT,
        401: OpenApiTypes.OBJECT,
    },
    examples=[
        OpenApiExample(
            'Change Password Request',
            value={
                "old_password": "currentpassword",
                "new_password": "newsecurepassword123"
            }
        ),
        OpenApiExample(
            'Change Password Response',
            value={
                "message": "Password changed successfully"
            }
        )
    ],
    tags=["Authentication"]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Change the authenticated user's password.
    """
    try:
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not old_password or not new_password:
            return Response(
                {"error": "Old password and new password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify old password
        if not request.user.check_password(old_password):
            logger.warning(f"Password change failed - incorrect old password for user: {request.user.mobile_no}")
            return Response(
                {"error": "Current password is incorrect"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Set new password
        request.user.set_password(new_password)
        request.user.save()
        
        logger.info(f"Password changed for user: {request.user.mobile_no}")
        
        return Response(
            {"message": "Password changed successfully"},
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Password change error: {str(e)}")
        return Response(
            {"error": "Failed to change password"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Custom JWT Token Views with enhanced documentation
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token obtain view with enhanced documentation.
    """
    
    @extend_schema(
        summary="Obtain JWT Tokens",
        description="Obtain JWT access and refresh tokens using mobile number and password.",
        request=OpenApiTypes.OBJECT,
        responses={
            200: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                'Token Request',
                value={
                    "mobile_no": "09088648123",
                    "password": "securepassword123"
                }
            ),
            OpenApiExample(
                'Token Response',
                value={
                    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                }
            )
        ],
        tags=["Authentication"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom JWT token refresh view with enhanced documentation.
    """
    
    @extend_schema(
        summary="Refresh JWT Token",
        description="Refresh JWT access token using refresh token.",
        request=OpenApiTypes.OBJECT,
        responses={
            200: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                'Refresh Request',
                value={
                    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                }
            ),
            OpenApiExample(
                'Refresh Response',
                value={
                    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                }
            )
        ],
        tags=["Authentication"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
