from rest_framework import mixins, generics
from rest_framework.views import APIView
from rest_framework.response import Response

from webapi import models
from webapi.Utils import Serializers, Permissions

from django.db.models import Q

class mustBeFriendView(generics.GenericAPIView):
    
    def check_permissions(self, request):
        generics.GenericAPIView.check_permissions(self, request)
        requested_user_id = long(self.kwargs["user_id"])
        current_user_id = self.request.user.user_id
        isFriend = models.friends.objects.filter(user=requested_user_id, friend=current_user_id, status__gt=0).count()
        if requested_user_id != current_user_id and isFriend == 0:
            self.permission_denied(self.request)

class UserView(mixins.RetrieveModelMixin,
               mustBeFriendView):

    queryset = models.user_info.objects.all()
    serializer_class = Serializers.UserSerializer
    lookup_field = 'user_id'

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
class FriendsView(mixins.ListModelMixin,
                 mustBeFriendView):

    queryset = models.friends.objects.all()
    serializer_class = Serializers.FriendsSerializer

    def get(self, request, *args, **kwargs):
        if long(self.kwargs["user_id"]) != request.user.user_id:
            self.permission_denied(request)
        return self.list(request, *args, **kwargs)
    
    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        scope = self.kwargs["scope"]
        if scope == "requests":
            return models.friends.objects.filter(friend_id=user_id, status=0)
        elif scope == "friends":
            return models.friends.objects.filter(user_id=user_id, status__gt=0)
        else :
            request = Q(friend_id=user_id, status=0)
            friends = Q(user_id=user_id, status__gt=0)
            return models.friends.objects.filter(request | friends)

class ActivitiesView(mustBeFriendView,
                     mixins.ListModelMixin):
    
    serializer_class = Serializers.ActivitySerializer
    lookup_field = 'activity_id'
    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        return models.activities.objects.filter(creator=user_id)
