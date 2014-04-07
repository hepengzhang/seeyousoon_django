from django.db.models import Q
from rest_framework import mixins, generics, status
from rest_framework.response import Response
from webapi import models
from webapi.Utils import Serializers, Permissions, PushNotification, \
    GeoCalculate




class UserView(generics.GenericAPIView,
               mixins.RetrieveModelMixin,
               mixins.UpdateModelMixin):
    permission_classes = (Permissions.PeopleAllReadOwnerModify, )
    queryset = models.user_info.objects.all()
    serializer_class = Serializers.UserSerializer
    lookup_field = 'user_id'

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        response = self.partial_update(request, *args, **kwargs)
        if 'longitude' in request.DATA and 'latitude' in request.DATA:
            obj = self.get_object_or_none()
            friends = models.friends.objects.filter(user_id=obj.user_id, status__gt=0)
            friends = [f.friend.user_id for f in friends]
            boundsLat = GeoCalculate.boundsOfLat(self.object.latitude, 500)
            boundsLong = GeoCalculate.boundsOfLong(self.object.longitude, 500)
            needNotify = models.user_info.objects.filter(user_id__in=friends, latitude__range=boundsLat, longitude__range=boundsLong)
            friends_ids = [u.user_id for u in needNotify]
            for uid in friends_ids:
                print "notified", uid
                PushNotification.SYSNotify(uid, obj.username + " is around you.")
        return response

class FriendsView(mixins.ListModelMixin,
                  mixins.DestroyModelMixin,
                  generics.GenericAPIView):
    permission_classes = (Permissions.AllAddFriendOwnerReadDeletePermission,)
    queryset = models.friends.objects.all()
    serializer_class = Serializers.FriendsSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        scope = self.kwargs["scope"]
        if scope == "requests":
            return models.friends.objects.filter(friend_id=user_id, status=0)
        elif scope == "friends":
            return models.friends.objects.filter(user_id=user_id, status__gt=0)
        else:
            request = Q(friend_id=user_id, status=0)
            friends = Q(user_id=user_id, status__gt=0)
            return models.friends.objects.filter(request | friends)


class AddFriendsView(mixins.ListModelMixin,
                     mixins.DestroyModelMixin,
                     generics.GenericAPIView):
    permission_classes = (Permissions.AllAddFriendOwnerReadDeletePermission,)
    queryset = models.friends.objects.all()
    serializer_class = Serializers.FriendsSerializer

    def post(self, request, *args, **kwargs):
        current_user_id = request.user.user_id
        requested_user_id = self.kwargs['user_id']
        approve = models.friends.objects.filter(user_id=requested_user_id, friend_id=current_user_id).count()
        if approve > 0:
            r1 = models.friends.objects.get_or_create(user_id=requested_user_id, friend_id=current_user_id)[0]
            r2 = models.friends.objects.get_or_create(friend_id=requested_user_id, user_id=current_user_id)[0]
            if r1.status == 0 or r2.status == 0:
                r1.status = 1
                r2.status = 1
                r1.save()
                r2.save()
                models.user_timeline.objects.create(user_id=current_user_id, related_user_id=requested_user_id,
                                                type=models.TIMELINE_BECOME_FRIENDS)
                models.user_timeline.objects.create(related_user_id=current_user_id, user_id=requested_user_id,
                                                type=models.TIMELINE_BECOME_FRIENDS)
            
            serializer = Serializers.FriendsSerializer(r2)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        
        requested = models.friends.objects.filter(user_id=current_user_id, friend_id=requested_user_id).count()
        if requested > 0:
            r2 = models.friends.objects.get(user_id=current_user_id, friend_id=requested_user_id)
            serializer = Serializers.FriendsSerializer(r2)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        
        r2 = models.friends.objects.create(user_id=current_user_id, friend_id=requested_user_id, status=0)
        serializer = Serializers.FriendsSerializer(r2)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

class FriendView(mixins.DestroyModelMixin,
                 generics.GenericAPIView):
    permission_classes = (Permissions.AllAddFriendOwnerReadDeletePermission,)
    queryset = models.friends.objects.all()
    serializer_class = Serializers.FriendsSerializer

    def delete(self, request, *args, **kwargs):
        current_user_id = request.user.user_id
        friend_user_id = self.kwargs['friend_id']
        models.friends.objects.filter(user_id=current_user_id, friend_id=friend_user_id).delete()
        models.friends.objects.filter(friend_id=current_user_id, user_id=friend_user_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ActivitiesView(generics.GenericAPIView,
                     mixins.ListModelMixin,
                     mixins.CreateModelMixin):
    permission_classes = (Permissions.PeopleFriendReadOwnerModify, )
    serializer_class = Serializers.ActivitySerializer
    lookup_field = 'activity_id'

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def pre_valid_model(self, serializer, model):
        model.creator_id = self.request.user.user_id

    def post_save(self, obj, created=False):
        if not created: return;
        models.user_timeline.objects.create(user=self.request.user, activity=obj, type=models.TIMELINE_CREATE_ACTIVITY)
        user = models.user_info.objects.get(user_id=self.request.user.user_id)
        user.numOfActivities += 1;
        user.save();

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        return models.activities.objects.filter(creator=user_id)


class TimelineView(generics.GenericAPIView,
                   mixins.ListModelMixin):
    permission_classes = (Permissions.PeopleFriendReadOwnerModify,)
    serializer_class = Serializers.TimelineSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        return models.user_timeline.objects.exclude(related_user_id=user_id).filter(user_id=user_id).order_by(
            '-created_date')[:50]
            
class PNSView(generics.GenericAPIView,
               mixins.UpdateModelMixin):
    
    permission_classes = (Permissions.PNSPermission, )
    serializer_class = Serializers.PushNotificationSerializer
    queryset = models.push_notification.objects.all()
    lookup_field = 'user_id'
    
    def pre_valid_model(self, serializer, model):
        model.user = self.request.user
    
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)