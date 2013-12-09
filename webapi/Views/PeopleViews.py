from rest_framework import mixins, generics
from rest_framework.views import APIView
from rest_framework.response import Response

from webapi import models
from webapi.Utils import Serializers, Permissions

from django.db.models import Q

class UserView(mixins.RetrieveModelMixin,
               generics.GenericAPIView):

    queryset = models.user_info.objects.all()
    serializer_class = Serializers.UserSerializer
    lookup_field = 'user_id'
    permission_classes = (Permissions.PeoplePermission, )

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
class FriendsView(mixins.ListModelMixin,
                 generics.GenericAPIView):

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
            
class AuthView(APIView):
    def get(self, request):
        content = {"status":"request was permitted"}
        return Response(content)
    
    def post(self, request):
        content = {"status":"request was permitted"}
        return Response(content)