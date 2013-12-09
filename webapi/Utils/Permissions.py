from rest_framework import permissions
from django.contrib.auth.models import AnonymousUser
from webapi import models

class AuthPermission(permissions.BasePermission):
    """
    Basic perrmission requires at least user_id and auth_token
    """
    def has_permission(self, request, view):
        return type(request.user) != AnonymousUser
    
class PeoplePermission(AuthPermission):
    """
    Object-level permission that determines if given user is visible to current user
    """
    
    def has_object_permission(self, request, view, obj):
        requested_user_id = obj.user_id
        current_user_id = request.user.user_id 
        if requested_user_id == current_user_id:
            return True
        if request.method in permissions.SAFE_METHODS:
            isFriend = models.friends.objects.filter(user_id=requested_user_id, friend_id=current_user_id, status__gt=0).count()
            return isFriend == 1

class ActivityPermission(AuthPermission):
    
    def has_object_permission(self, request, view, obj):
        return True; 
        
        