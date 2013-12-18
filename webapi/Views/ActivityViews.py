from rest_framework import mixins, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from webapi import models, SYSMessages
from webapi.Utils import Serializers, PushNotification, Permissions, Mixins

from datetime import datetime

class ActivitiesView(generics.GenericAPIView,
                     mixins.RetrieveModelMixin,
                     mixins.DestroyModelMixin,
                     mixins.UpdateModelMixin):
    
    permission_classes = (Permissions.ActivityFriendReadOwnerModify, )
    queryset = models.activities.objects.all()
    serializer_class = Serializers.ActivitySerializer
    lookup_field = 'activity_id'
    
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
    
class ActivityCommentsView(generics.GenericAPIView,
                          mixins.ListModelMixin,
                          Mixins.OverrideCreateModelMixin,
                          mixins.DestroyModelMixin):
    
    permission_classes = (Permissions.ActivityFriendReadOwnerModify, )
    serializer_class = Serializers.CommentSerializer
    lookup_field = "comment_id"
    createScope = ['contents', 'activity']
    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    """
    Required parameters:
    contents, unicode
    """
    def post(self, request, *args, **kwargs):
        override = {"activity":self.kwargs['activity_id'], "creator":request.user.user_id}
        return self.create(request, override, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    
    def get_queryset(self):
        activity_id = self.kwargs["activity_id"]
        commentsQuerySet = models.comments.objects.filter(activity_id=activity_id)
        return commentsQuerySet
    
class ParticipantsView(generics.GenericAPIView,
                       mixins.ListModelMixin):
    
    permission_classes = (Permissions.ActivityFriendReadOwnerModify, )
    serializer_class = Serializers.ParticipantSerializer
    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def get_queryset(self):
        activity_id = self.kwargs['activity_id']
        peopleQuerySet = models.participants.objects.filter(activity_id=activity_id)
        return peopleQuerySet


class SearchAcitivityView(APIView):
    def get(self, request):
        if request.QUERY_PARAMS['type']=='nearby':#return all nearby public activities
            return Response(SYSMessages.SYSMESSAGE_ERROR_NOTIMPLEMENTED, status.HTTP_501_NOT_IMPLEMENTED)
        if request.QUERY_PARAMS['type']=='friends':#return all friends's visible activities
            uid = request.QUERY_PARAMS['user_id']
            timeMin = request.QUERY_PARAMS['min_date'];
            timeMax = request.QUERY_PARAMS['max_date'];
            
            user_self = models.user_info.objects.get(pk=uid)
            friendsList = models.friends.objects.filter(user=user_self, status__gt=0).values_list('friend_id',flat=True)
            friendsList = [uid] + list(friendsList)
            queryset = models.activities.objects.select_related().filter(creator__in=friendsList,
                                                          activity_created_date__gt=timeMin,
                                                          activity_created_date__lt=timeMax,
                                                          access__lt=2)
            activities = queryset.order_by('-activity_created_date')[:50]
            activities = [a for a in activities]
            serializer = Serializers.ActivitySerializer(activities, many=True)
            result = {"activities":serializer.data}
            return Response(result)
        
    def post(self, request):
        paraDict = request.DATA
        activity = models.activities(keyword=paraDict['keyword'], creator_id=paraDict['user_id'],access=paraDict['access'])
        
        #add to database
        if 'type' in paraDict: activity.type=paraDict['type']
        if 'status' in paraDict: activity.status=paraDict['status']
        if 'description' in paraDict: activity.description=paraDict['description']
        
        dtformat = "%Y-%m-%dT%H:%M:%S"
        if 'start_date' in paraDict: activity.start_date=datetime.strptime(paraDict['start_date'], dtformat)
        if 'end_date' in paraDict: activity.end_date=datetime.strptime(paraDict['end_date'], dtformat)
        if 'latitude' in paraDict: activity.latitude=paraDict['latitude']
        if 'longitude' in paraDict: activity.longitude=paraDict['longitude']
        if 'destination' in paraDict: activity.destination=paraDict['destination']

        activity.save()
        
        activity_id = activity.activity_id
        if paraDict['access']=='2':
            #get the invited friends list
            friends_list = paraDict['invited_list']
            for user_id in friends_list:
                models.participants.objects.create(activity=activity_id,participant=user_id)
                PushNotification.SYSNotify(user_id, u"You are invited to a new event")
            models.participants.objects.create(activity=activity_id,participant=paraDict['user_id'],status=1)
        
        serializer = Serializers.ActivitySerializer(activity)
        result = {"activity":serializer.data}
        return Response(result)
    
    def delete(self, request):
        pass

class ActivityComments(APIView):
    
    def get(self, request):
        offset = int(request.QUERY_PARAMS['offset'])
        number = int(request.QUERY_PARAMS['number'])
        activity_id = request.QUERY_PARAMS['activity_id']
        results = models.comments.objects.filter(activity_id=activity_id)
        results = results.order_by('-created_date')[offset:offset+number]
        results = [a for a in results]
        
        serializer = Serializers.CommentSerializer(results, many=True)
        
        results = {"comments":serializer.data,
                   "offset":offset,
                   "number":len(results)}
        
        return Response(results)
    
    def post(self, request):
        
        paraDict = request.DATA
        user_id = paraDict['user_id']
        contents = paraDict['contents']
        activity_id = paraDict['activity_id']
        
        models.comments.objects.create(creator_id=user_id, activity_id=activity_id,contents=contents)
        activity = models.activities.objects.get(pk=activity_id)
        activity.num_of_comments += 1
        activity.save()
        
        return Response({'message':'success'})
    
    def delete(self, request):
        user_id = request.DATA['user_id']
        comment_id = request.DATA['comment_id']
        activity_id = request.DATA['activity_id']
        
        models.comments.objects.filter(creator_id=user_id, comment_id=comment_id, activity_id=activity_id).delete()
        activity = models.activities.objects.get(pk=activity_id)
        activity.num_of_comments -= 1
        activity.save()
        
        return Response({'message':'success'})