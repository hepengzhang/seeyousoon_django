from rest_framework.views import APIView
from rest_framework import generics, mixins
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.exceptions import AuthenticationFailed, ParseError

from webapi import models, SYSMessages
from webapi.Utils import Serializers

from django.core.signing import Signer
from datetime import datetime

from passlib.hash import ldap_salted_sha1 as password_hash

def generate_accessToken(userID):
    signer = Signer()
    return signer.sign(str(userID) + str(datetime.now()))[-27:]


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
            if len(info) != 1: return Response(u"Facebook id " + paraDict['fb_id'] + " not linked.",
                                               status.HTTP_404_NOT_FOUND)
            info = info[0]
        elif 'wb_id' in paraDict:
            info = models.user_info.objects.filter(fb_id=paraDict['wb_id'])
            if len(info) != 1: return Response(u"Weibo id " + paraDict['wb_id'] + " not linked.",
                                               status.HTTP_404_NOT_FOUND)
            info = info[0]
        elif 'username' in paraDict:
            auth = models.user_auth.objects.select_related().filter(username=paraDict['username'])
            if len(auth) != 1:
                raise AuthenticationFailed(SYSMessages.SYSMESSAGE_ERROR_AUTH_LOGIN_USERNAMENOTEXIST)
            auth = auth[0]
            if not password_hash.verify(paraDict['password'], auth.password):
                raise AuthenticationFailed(SYSMessages.SYSMESSAGE_ERROR_AUTH_LOGIN_WRONGPASSWORD)
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

        result = {"access_token": auth.access_token}
        serializer = Serializers.UserSerializer(info)
        result.update(serializer.data)

        return Response(result)


class SignupView(generics.GenericAPIView,
                 mixins.CreateModelMixin):
    """
    Sign up a new account
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = Serializers.UserSerializer

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=self.request.DATA)

        if serializer.is_valid():
            serializer.object.username = self.request.DATA['username']
            exist = models.user_auth.objects.filter(username=serializer.object.username).exists()
            if exist:
                raise AuthenticationFailed(SYSMessages.SYSMESSAGE_ERROR_AUTH_REGISTER_USERNAMEUNAVAILABLE)

            user_info = serializer.save(force_insert=True)

            ### user_auth
            token = generate_accessToken(user_info.username)
            password = password_hash.encrypt(self.request.DATA['password'])
            auth = models.user_auth(username=user_info.username, password=password,
                                    access_token=token, user=user_info)
            auth.save()

            ### user search
            search_index = "{} {}".format(user_info.username, user_info.name)
            models.user_search.objects.create(user=user_info, search_index=search_index)

            result = {"access_token": auth.access_token}
            result.update(serializer.data)

            return Response(result, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        result = {'username': paraDict['username'], 'available': False if r > 0 else True}
        return Response(result)

