from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions

from webapi import models, SYSMessages
from webapi.Utils import Serializers

from django.core.signing import Signer
from datetime import datetime

def generate_accessToken(userID):
    signer = Signer()
    return signer.sign(str(userID)+str(datetime.now()))[-27:]

class LoginView(APIView):
    """
    Login current user
    """
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request):
        paraDict = request.DATA
 
        info = None
        auth = None
        if 'fb_id' in paraDict:
            info = models.user_info.objects.filter(fb_id=paraDict['fb_id'])
            if len(info) != 1: return Response(u"Facebook id "+paraDict['fb_id']+" not linked.", status.HTTP_404_NOT_FOUND)
            info = info[0]
        elif 'wb_id' in paraDict:
            info = models.user_info.objects.filter(fb_id=paraDict['wb_id'])
            if len(info) != 1: return Response(u"Weibo id "+paraDict['wb_id']+" not linked.", status.HTTP_404_NOT_FOUND)
            info = info[0]
        elif 'username' in paraDict:
            auth = models.user_auth.objects.select_related().filter(username=paraDict['username'])
            if len(auth) != 1: return Response(SYSMessages.SYSMESSAGE_ERROR_AUTH_REGISTER_USERNAMENOTEXIST, status.HTTP_404_NOT_FOUND)
            auth = auth[0] 
            if auth.password != paraDict['password']: return Response(SYSMessages.SYSMESSAGE_ERROR_AUTH_REGISTER_WRONGPASSWORD, status.HTTP_406_NOT_ACCEPTABLE)
            info = auth.user
         
        ##update access_token
        auth.access_token = generate_accessToken(info.user_id)
        # performance blocker, about 20ms on localhost
        auth.save()
        #update user location
        if 'latitude' in paraDict:
            info.latitude = paraDict['latitude']
            info.longitude = paraDict['longitude']
        
        # performance blocker, about 20ms on localhost
        info.save()
        
        serializer = Serializers.UserSerializer(info)
        result = {"user_info":serializer.data,
                  "access_token":auth.access_token}
        
        return Response(result)
    
class SignupView(APIView):
    """
    Sign up a new account
    """
    permission_classes = (permissions.AllowAny,)
    def post(self, request):
        paraDict = request.DATA
        exist = models.user_auth.objects.filter(username=paraDict['username']).exists()
        if exist:
            return Response(SYSMessages.SYSMESSAGE_ERROR_AUTH_REGISTER_USERNAMEUNAVAILABLE, status.HTTP_406_NOT_ACCEPTABLE)
        
        ### user_info
        info = models.user_info(email=paraDict['email'],
                         username=paraDict['username'])
        if 'phone' in paraDict: info.phone=paraDict['phone']
        if 'name' in paraDict: info.name=paraDict['name']
        if 'primary_sns' in paraDict: info.primary_sns=paraDict['primary_sns']
        if 'wb' in paraDict: info.wb_id=paraDict['wb']
        if 'fb' in paraDict: info.fb_id=paraDict['fb']
        info.save()
        
        ### user_auth
        token = generate_accessToken(paraDict['username'])
        auth = models.user_auth(username=paraDict['username'],
                         password=paraDict['password'],
                         access_token=token,
                         user=info)
        auth.save()
        
        ### user search
        search = models.user_search(username=auth.username,
                             user=info)
        if 'name' in paraDict: search.name=paraDict['name']
        search.save()
        
        ### retrieve
        serializer = Serializers.UserSerializer(info)
        result = {"user_info":serializer.data,
                  "access_token":auth.access_token}
        return Response(result)

class LogoutView(APIView):
    """
    Login current user
    """
    def get(self, request):
        users = models.user_info.objects.all();
        serializer = Serializers.UserSerializer(users, many=True)
#         users = [u for u in users]
        return Response(serializer.data)
    
class CheckUsernameView(APIView):
    """
    check if username is available
    """
    permission_classes = (permissions.AllowAny,)
    def get(self, request):
        paraDict = request.QUERY_PARAMS
        user = models.user_auth.objects.filter(username=paraDict['username'])
        r = len(user)
        result = {'username':paraDict['username']}
        result['available'] = False if r>0 else True
        return Response(result)

