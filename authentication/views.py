from django.shortcuts import get_object_or_404
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from django.db import transaction
from rest_framework import status, permissions, parsers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import User, EmailOtp
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import UserSerializer, RequestNewOTPSerializer, LoginSerializer, LogoutSerializer, PasswordResetRequestSerializer, PasswordResetSerializer
from .utils import send_otp




class UserRegistrationView(GenericAPIView):
    """"
    View to handle user registration.
    """
    
    serializer_class = UserSerializer
    
    @swagger_auto_schema(
        operation_summary="User Registration",
        operation_description="Register a new user.",
        request_body=UserSerializer,
        responses={
            201: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    "message": openapi.Schema(type=openapi.TYPE_STRING),
                    "data": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "email": openapi.Schema(type=openapi.TYPE_STRING),
                            "first_name": openapi.Schema(type=openapi.TYPE_STRING),
                            "last_name": openapi.Schema(type=openapi.TYPE_STRING),
                        },
                    ),
                }
            ),
            200: openapi.Response(
                "Resent OTP",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: openapi.Response(
                "Error Response",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "error": openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
        }
    )
    @transaction.atomic
    def post(self, request):
        """"
        Handle user registration.
        """
        
        email = request.data.get("email")
        existing_user = User.objects.filter(email=email).first()
        
        if existing_user:
            if not existing_user.is_active:
                otp, _ = EmailOtp.objects.get_or_create(user=existing_user)
                otp.generate_otp()
                return Response({
                    "success": True,
                    "message": "User already registered but not active. OTP sent."
                }, status=status.HTTP_200_OK)
            return Response({
                "success": False,
                "error": "User already registered."
            }, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "success": True,
                "message": "User registered successfully. Check email for OTP.",
                "data": {
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name
                }
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": False,
            "error": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(GenericAPIView):
    """"
    View to handle email verification.
    """
    
    @swagger_auto_schema(
        operation_summary="Verify Email",
        operation_description="Verify email using OTP.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "otp": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="One-time password sent to the email."
                ),
            },
            required=["otp"]
        ),
        responses={
            200:openapi.Response(
                "Account Verified",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: openapi.Response(
                "Error Response",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "error": openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            404: openapi.Response(
                "Not Found - Invalid OTP",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "error": openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            500: openapi.Response(
                "Server Error",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "error": openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    @transaction.atomic
    def post(self, request):
        """
        Handle email verification.
        """
        otp_code = request.data.get("otp")
        if not otp_code:
            return Response({
                "success": False,
                "error": "OTP is required."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user_obj_otp = EmailOtp.objects.filter(otp=otp_code).first()
            
            if not user_obj_otp:
                return Response({
                    "success": False,
                    "message": "Invalid OTP."
                }, status=status.HTTP_404_NOT_FOUND)
            
            if not user_obj_otp.is_valid():
                return Response({
                    "success": False,
                    "message": "OTP expired."
                }, status=status.HTTP_400_BAD_REQUEST)
                
            user = user_obj_otp.user
            if not user.is_active:
                user.is_active = True
                user.save()
                user_obj_otp.delete()
                return Response({
                    "success": True,
                    "message": "Account verified successfully."
                }, status=status.HTTP_200_OK)
            return Response({
                "success": False,
                "error": "Account already verified."
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "success": False,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RequestNewOTPView(GenericAPIView):
    """
    View to handle requesting a new OTP.
    """
    serializer_class = RequestNewOTPSerializer
    
    @swagger_auto_schema(
        operation_summary="Request New OTP",
        operation_description="Request a new OTP for email verification.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_EMAIL,
                    description="Email address of the user."
                )
            },
            required=["email"]
        ),
        responses={
            200: openapi.Response(
                "OTP Sent",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: openapi.Response(
                "Error Response",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "error": openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            404: openapi.Response(
                "Not Found - Email Not Registered",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "error": openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            500: openapi.Response(
                "Server Error",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "error": openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    @transaction.atomic
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        
        try:
            user = User.objects.get(email=email)
            otp, _ = EmailOtp.objects.get_or_create(user=user)
            otp.generate_otp()
            send_otp(user.email, otp.otp)
            return Response({
                "success": True,
                "message": "OTP sent to email."
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({
                "success": False,
                "message": "Email not registered."
            }, status=status.HTTP_404_NOT_FOUND)


class LoginView(GenericAPIView):
    """"
    View to handle user login.
    """
    serializer_class = LoginSerializer
    
    @swagger_auto_schema(
        operation_summary="User Login",
        operation_description="Login a user using email and password.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_EMAIL,
                    description="Email address of the user."
                ),
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_PASSWORD,
                    description="Password of the user."
                )
            },
            required=["email", "password"]
        ),
        responses={
            200: openapi.Response(
                "Login Successful",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_STRING),
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "email": openapi.Schema(type=openapi.TYPE_STRING),
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "full_name": openapi.Schema(type=openapi.TYPE_STRING),
                                "access_token": openapi.Schema(type=openapi.TYPE_STRING),
                                "refresh_token": openapi.Schema(type=openapi.TYPE_STRING)
                            }
                        )
                    }
                )
            ),
            400: openapi.Response(
                "Error Response",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "error": openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            401: openapi.Response(
                "Unauthorized - Account Not Verified",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "error": openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            500: openapi.Response(
                "Server Error",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "error": openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    @transaction.atomic
    def post(self, request):
        """"
        Handle user login.
        """
        context = {"request": request}
        
        serializer = self.serializer_class(data=request.data, context=context)
        if serializer.is_valid():
            return Response({
                "success": True,
                "message": "Login successful.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            "success": False,
            "error": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)



class LogoutView(GenericAPIView):
    """""
    Logout view for the user.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LogoutSerializer
    
    @swagger_auto_schema(
        operation_summary="User Logout",
        operation_description="Logout a user using refresh token.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "refresh": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Refresh token of the user."
                )
            },
            required=["refresh"]
        ),
        responses={
            200: openapi.Response(
                "Logout Successful",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: openapi.Response(
                "Bad Request - Missing or Invalid Refresh Token",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "error": openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
        }
    )
    def post(self, request):
        """""
        Handle user logout.
        """
        
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            refresh = request.data.get("refresh")
            if not refresh:
                return Response({
                    "success": False,
                    "error": "Refresh token is required."
                }, status=status.HTTP_400_BAD_REQUEST)
            token = RefreshToken(refresh)
            token.blacklist()
            
            return Response({
                "success": True,
                "message": "Logout successful."
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False,
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)



class PasswordResetRequestView(GenericAPIView):
    """"
    View to handle password reset request.
    """
    
    serializer_class = PasswordResetRequestSerializer
    
    @swagger_auto_schema(
        operation_summary="Password Reset Request",
        operation_description="Request a password reset link.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_EMAIL,
                    description="Email address of the user."
                )
            },
            required=["email"]
        ),
        responses={
            200: openapi.Response(
                "Password Reset Link Sent",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: openapi.Response(
                "Error Response",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "error": openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            404: openapi.Response(
                "Not Found - Email Not Registered",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "error": openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            500: openapi.Response(
                "Server Error",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "error": openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    @transaction.atomic
    def post(self, request):
        """""
        Handle password reset request.
        """
        
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save creates PasswordResetToken
            return Response({
                "success": True,
                "message": "Password reset link has been sent if the email exists."
            }, status=status.HTTP_200_OK)

        return Response({
            "success": False,
            "error": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)



class PasswordResetView(GenericAPIView):
    """""
    Reset password view for the user.
    """
    
    serializer_class = PasswordResetSerializer
    
    @swagger_auto_schema(
        operation_summary="Reset Password",
        operation_description="User can reset their password using a token.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "token": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Password reset token."
                ),
                "new_password": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_PASSWORD,
                    description="New password for the user."
                ),
                "confirm_password": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_PASSWORD,
                    description="Confirm new password."
                )
            },
            required=["token", "new_password", "confirm_password"]
        ),
        responses={
            200: openapi.Response(
                "Password Reset Successful",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: openapi.Response(
                "Error Response",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "error": openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            404: openapi.Response(
                "Not Found - Invalid Token",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "error": openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            500: openapi.Response(
                "Server Error",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "error": openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    
    def post(self, request):
        """""
        Handle password reset.
        """
        
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Password reset successful."
            }, status=status.HTTP_200_OK)
        return Response({
            "success": False,
            "error": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)