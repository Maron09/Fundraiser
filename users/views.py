from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction

from .serializers import UserProfileSerializer
from .models import UserProfile


class UserProfileView(RetrieveUpdateAPIView):
    """
    Retrieve and update the authenticated user's profile.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(UserProfile, user=self.request.user)

    @swagger_auto_schema(
        operation_summary="User Profile",
        operation_description="Retrieve the authenticated user's profile.",
        responses={
            200: openapi.Response(
                "User Profile",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_STRING),
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "bio": openapi.Schema(type=openapi.TYPE_STRING),
                                "profile_picture": openapi.Schema(type=openapi.TYPE_STRING),
                                "address": openapi.Schema(type=openapi.TYPE_STRING),
                                "country": openapi.Schema(type=openapi.TYPE_STRING),
                                "state": openapi.Schema(type=openapi.TYPE_STRING),
                                "city": openapi.Schema(type=openapi.TYPE_STRING),
                            }
                        )
                    }
                )
            ),
            404: openapi.Response(
                "Not Found",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
        }
    )
    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "message": "User profile retrieved successfully.",
            "data": serializer.data
        })

    @swagger_auto_schema(
        operation_summary="Update User Profile",
        operation_description="Update the authenticated user profile.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "bio": openapi.Schema(type=openapi.TYPE_STRING),
                "profile_picture": openapi.Schema(type=openapi.TYPE_FILE),
                "address": openapi.Schema(type=openapi.TYPE_STRING),
                "country": openapi.Schema(type=openapi.TYPE_STRING),
                "state": openapi.Schema(type=openapi.TYPE_STRING),
                "city": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        consumes=["multipart/form-data"],
        responses={
            200: openapi.Response("Profile Updated", UserProfileSerializer),
            400: openapi.Response(
                "Bad Request",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_STRING),
                        "errors": openapi.Schema(type=openapi.TYPE_OBJECT),
                    }
                )
            ),
        }
    )
    @transaction.atomic
    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "User profile updated successfully.",
                "data": serializer.data
            })
        return Response({
            "success": False,
            "message": "Invalid data.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)



class UserDashboardView(GenericAPIView):
    pass