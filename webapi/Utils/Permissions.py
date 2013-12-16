from rest_framework import permissions
from django.contrib.auth.models import AnonymousUser
from webapi import models
import rest_framework

class AuthPermission(permissions.BasePermission):
    """
    Basic perrmission requires at least user_id and auth_token
    """
    def has_permission(self, request, view):
        return type(request.user) != AnonymousUser

class ActivityFriendReadOwnerModify(AuthPermission):
    
    def safe_method(self):
        return ('OPTION', 'HEAD')
    
    def has_permission(self, request, view):
        if request.method in self.safe_method(): 
            return True
        if not AuthPermission.has_permission(self, request, view) :
            return False
        filter_kwargs = {'activity_id': view.kwargs['activity_id']}
        activity = rest_framework.generics.get_object_or_404(models.activities.objects.all(), **filter_kwargs)
        current_user_id = request.user.user_id
        creator_id = activity.creator_id
        isFriend = models.friends.objects.filter(user_id=creator_id, friend_id=current_user_id, status__gt=0).count()
        return (activity.access < 1 or isFriend > 0)
        
    def has_object_permission(self, request, view, obj):
        
        if request.method in self.safe_method(): 
            return True

        current_user_id = request.user.user_id
        creator_id = obj.creator_id
        if request.method == 'GET':
            isFriend = models.friends.objects.filter(user_id=creator_id, friend_id=current_user_id, status__gt=0).count()
            return (obj.access < 1 or isFriend > 0)
        else :
            return current_user_id == creator_id
        