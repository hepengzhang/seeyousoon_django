from rest_framework import permissions
from django.contrib.auth.models import AnonymousUser
from webapi import models
import rest_framework

def isFriend(current_user_id, requested_user_id):
    if current_user_id == requested_user_id : return True
    friendRelation = models.friends.objects.filter(user=requested_user_id, friend=current_user_id, status__gt=0).count()
    return friendRelation > 0

class AuthPermission(permissions.BasePermission):
    
    def safe_method(self):
        return ('OPTION', 'HEAD')

    """
    Basic perrmission requires at least user_id and auth_token
    """
    def has_permission(self, request, view):
        return type(request.user) != AnonymousUser

class ActivityFriendReadOwnerModify(AuthPermission):
    
    def has_permission(self, request, view):
        if request.method in self.safe_method(): 
            return True
        if not AuthPermission.has_permission(self, request, view) :
            return False
        filter_kwargs = {'activity_id': view.kwargs['activity_id']}
        activity = rest_framework.generics.get_object_or_404(models.activities.objects.all(), **filter_kwargs)
        current_user_id = request.user.user_id
        creator_id = activity.creator_id
        return (activity.access < 1 
                or isFriend(current_user_id, creator_id))
        
    def has_object_permission(self, request, view, obj):
        
        if request.method in self.safe_method(): 
            return True

        current_user_id = request.user.user_id
        creator_id = obj.creator_id
        if request.method == 'GET':
            return (obj.access < 1 or isFriend(current_user_id, creator_id))
        else :
            return current_user_id == creator_id

class PeopleAllReadOwnerModify(AuthPermission):
    
    def safe_method(self):
        return ('OPTION', 'HEAD', 'GET')
    
    def has_object_permission(self, request, view, obj):
        
        if request.method in self.safe_method(): 
            return True

        current_user_id = request.user.user_id
        requested_id = obj.user_id
        return current_user_id == requested_id
    
class PeopleFriendReadOwnerModify(AuthPermission):
    
    def safe_method(self):
        return ('OPTION', 'HEAD')
    
    def has_permission(self, request, view):
        if not AuthPermission.has_permission(self, request, view): return False
        requested_user_id = long(view.kwargs["user_id"])
        current_user_id = request.user.user_id
        return isFriend(current_user_id, requested_user_id)
    
    def has_object_permission(self, request, view, obj):
        
        if request.method in self.safe_method(): 
            return True
        
        requested_user_id = long(view.kwargs["user_id"])
        current_user_id = request.user.user_id
        if requested_user_id == current_user_id : return True
        elif request.method == 'GET':
            return isFriend(current_user_id, requested_user_id)
        else :
            return False
        
        