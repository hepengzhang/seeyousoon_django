from rest_framework import mixins
from rest_framework import generics

from webapi import models
from webapi.Utils import Serializers

class TimelineView(generics.GenericAPIView,
                   mixins.ListModelMixin):

    serializer_class = Serializers.TimelineSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        all_friends_queryset = models.friends.objects.filter(user=user, status__gt=0)
        return models.user_timeline.objects.exclude(related_user=user).filter(user__in=all_friends_queryset).order_by('-createdDate')[:50]