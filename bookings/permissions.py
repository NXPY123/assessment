# bookings/permissions.py
from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users to access it.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin()

class IsBookingOwner(permissions.BasePermission):
    """
    Custom permission to only allow booking owners to view/edit their bookings.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user