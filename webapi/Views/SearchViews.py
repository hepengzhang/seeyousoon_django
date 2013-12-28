from rest_framework import generics
from rest_framework.response import Response
from rest_framework import exceptions

from webapi import models
from webapi.Utils import Serializers


class SearchPeopleView(generics.GenericAPIView):
    queryset = models.activities.objects.all()
    serializer_class = Serializers.UserSerializer
    lookup_field = 'user_id'

    def get(self, request, *args, **kwargs):
        if not 'keywords' in self.request.QUERY_PARAMS:
            raise exceptions.ParseError("Missing parameter 'keywords'")
        keywords = u" ".join([u"+" + k + u"*" for k in self.request.QUERY_PARAMS['keywords'].split()])
        users = models.user_search.objects.select_related().filter(search_index__search=keywords)
        users = [u.user for u in users]
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)

