from django.test import TestCase
from django.test.client import Client
import simplejson as json
from webapi import models

from rest_framework import status

API_LOGIN_URL = "/webapi/auth/login"
API_REGISTER_URL = "/webapi/auth/register"
API_CHECKUSERNAME_URL = "/webapi/auth/checkusername"

class registerTest(TestCase):

    fixtures = ['AuthTestFixtures.json']
    
    def setUp(self):
        self.c = Client()
        pass
    
    def test_NewUser(self):
        paraDict = {'email':'test@test.com', 'username':'hepengzhangNew', 'password':'testpassordAuthNew', "name":"Hepeng Zhang" }
        response = self.c.post(API_REGISTER_URL, data=json.dumps(paraDict), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        response = json.loads(response.content)
        
        self.assertIsNotNone(response['access_token'])
        self.assertEqual(response['username'], paraDict['username'], 'return wrong username')
        self.assertEqual(response['email'], paraDict['email'], 'return wrong email')
        
        info = models.user_info.objects.filter(username=paraDict['username'])
        self.assertEqual(len(info), 1, 'not inserted in database user_info')
        auth = models.user_auth.objects.filter(username=paraDict['username'])
        self.assertEqual(len(auth), 1, 'not inserted in database user_auth')
        search_keyword = "{0} {1}".format(paraDict['username'], paraDict['name'])
        search = models.user_search.objects.filter(search_index=search_keyword)
        self.assertEqual(len(search), 1, 'not inserted in database user_search')
        pass
    
    def test_alreadyExist(self):
        paraDict = {'email':'test@test.com', 'username':'hepengzhang', 'password':'testpassordAuthNew' }
        response = self.c.post(API_REGISTER_URL, data=json.dumps(paraDict), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
#         self.assertEqual(response.content, SYSMessages.SYSMESSAGE_ERROR_AUTH_REGISTER_USERNAMEUNAVAILABLE)
        pass

class loginTest(TestCase):
    
    fixtures = ['AuthTestFixtures.json']
    
    def setUp(self):
        self.c = Client()
        pass
    
    def test_correctLogin(self):
        params = {'email':'test@test.com', 'username':'hepengzhang', 'password':'testpasswordAuth' }
        response = self.c.post(API_LOGIN_URL, data=json.dumps(params), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertIsNotNone(response['access_token'], 'access_token should not be null')
        self.assertEqual(response['username'], params['username'], 'return wrong username')
        pass
    
    def test_userNotExist(self):
        params = {'email':'test@test.com', 'username':'hepengzhangNotExist', 'password':'testpasswordAuth' }
        response = self.c.post(API_LOGIN_URL, data=json.dumps(params), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
#         self.assertEqual(response.content, SYSMessages.SYSMESSAGE_ERROR_AUTH_REGISTER_USERNAMENOTEXIST)
        pass
    
    def test_wrongPassword(self):
        params = {'email':'test@test.com', 'username':'hepengzhang', 'password':'testpasswordAuthWrong' }
        response = self.c.post(API_LOGIN_URL, data=json.dumps(params), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
#         self.assertEqual(response.content, SYSMessages.SYSMESSAGE_ERROR_AUTH_REGISTER_WRONGPASSWORD)
        pass
    
class checkUsernameTest(TestCase):
    fixtures = ['AuthTestFixtures.json']
    def setUp(self):
        self.c = Client()
        pass
    
    def test_nonexistUser(self):
        params = {'username':'hepengzhangNotExist'}
        response = self.c.get(API_CHECKUSERNAME_URL, params)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['available'], True)
        pass
        
    def test_existUser(self):
        params = {'username':'hepengzhang'}
        self.c.post(API_REGISTER_URL, data=json.dumps(params), content_type='application/json')
        response = self.c.get(API_CHECKUSERNAME_URL, params)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['available'], False)
        pass