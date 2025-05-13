from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrReadOnly(BasePermission):
    """
    Custom permission to only allow admins to edit objects.
    """
    
    def has_permission(self, request, view):
        # Allow read-only access for all users
        if request.method in SAFE_METHODS:
            return True
        
        # Allow write access only for admin users
        return request.user and request.user.is_staff


class IsOwner(BasePermission):
    """
    Custom permission to only allow owners of an object to edit or delete it.
    """
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user