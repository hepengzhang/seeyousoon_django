from rest_framework import mixins, generics
from rest_framework.views import APIView
from rest_framework.response import Response

from webapi import models
from webapi.Utils import Serializers, Permissions

class UserView(mixins.RetrieveModelMixin,
               generics.GenericAPIView):

    queryset = models.user_info.objects.all()
    serializer_class = Serializers.UserSerializer
    lookup_field = 'user_id'
    permission_classes = (Permissions.PeoplePermission, )

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
class AuthView(APIView):
    def get(self, request):
        content = {"status":"request was permitted"}
        return Response(content)
    
    def post(self, request):
        content = {"status":"request was permitted"}
        return Response(content)