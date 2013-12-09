from django.test import TestCase
from django.test.client import Client
import simplejson as json
from webapi import models

def get_people_url(user_id):
    return "/webapi/people/"+user_id

def get_friends_url(user_id, scope):
    return "webapi/people/"+user_id+"/friends/"+scope

class peopleTest(TestCase):
    
    fixtures = ['TestFixtures.json']
    authentication = "1 hepengzhangAT"
    
    def setUp(self):
        self.c = Client()
        pass
    
    def test_getMyself(self):
        url = get_people_url("1")
        response = self.c.get(url, HTTP_AUTHORIZATION=self.authentication)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertTrue('user_id' in response, "return doesn't contain user_id")
        self.assertEqual(response['user_id'], 1)
        pass
    
    def test_getFriend(self):
        url = get_people_url("3")
        response = self.c.get(url, HTTP_AUTHORIZATION=self.authentication)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertTrue('user_id' in response, "return doesn't contain user_id")
        self.assertEqual(response['user_id'], 3)
        
    def test_getNonFriend(self):
        url = get_people_url("2")
        response = self.c.get(url, HTTP_AUTHORIZATION=self.authentication)
        self.assertEqual(response.status_code, 403)

    