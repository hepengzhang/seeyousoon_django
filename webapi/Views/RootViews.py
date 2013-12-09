from rest_framework.views import APIView
from rest_framework.response import Response

class RootView(APIView):
    def get(self, request):
        paraDict = {'a':'a',
            'b':True,
            'c':False,
            'd':1,
            'e':None,
            'g':[1,2,3,4]}
        return Response(paraDict)
