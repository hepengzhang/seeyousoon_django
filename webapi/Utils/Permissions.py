from rest_framework import permissions
from django.contrib.auth.models import AnonymousUser

class AuthPermission(permissions.BasePermission):
    """
    Basic perrmission requires at least user_id and auth_token
    """
    def has_permission(self, request, view):
        return type(request.user) != AnonymousUser
        