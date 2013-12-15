from django.test import TestCase
from django.test.client import Client
import simplejson as json
from webapi import models

def get_people_url(user_id):
    return "/webapi/people/"+user_id

def get_friends_url(user_id, scope):
    return "/webapi/people/"+user_id+"/friends/"+scope

def get_activities_url(user_id):
    return "/webapi/people/"+user_id+"/activities"

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
        
class friendsTest(TestCase):
    
    fixtures = ['TestFixtures.json']
    authentication = "1 hepengzhangAT"
    
    def setUp(self):
        self.c = Client()
        pass
    
    def test_getMyFriends(self):
        url = get_friends_url("1", "friends")
        response = self.c.get(url, HTTP_AUTHORIZATION=self.authentication)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertTrue(len(response)==1,"There should be only one friend")
        pass

    def test_getMyRequest(self):
        url = get_friends_url("1", "requests")
        response = self.c.get(url, HTTP_AUTHORIZATION=self.authentication)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertTrue(len(response)==1,"There should be only one request")
        
    def test_getAll(self):
        url = get_friends_url("1", "all")
        response = self.c.get(url, HTTP_AUTHORIZATION=self.authentication)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertTrue(len(response)==2,"There should be two objects in response")
            
    def test_getOthersFriends(self):
        url = get_friends_url("2", "all")
        response = self.c.get(url, HTTP_AUTHORIZATION=self.authentication)
        self.assertEqual(response.status_code, 403)
        
class peopleActivitiesTest(TestCase):
    
    fixtures = ['TestFixtures.json']
    authentication = "1 hepengzhangAT"
    
    def expect(self, user_id, numOfActivities):
        url = get_activities_url(user_id)
        response = self.c.get(url, HTTP_AUTHORIZATION=self.authentication)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(len(response), numOfActivities)

    def setUp(self):
        self.c = Client()
    
    def test_getMyActivities(self):
        self.expect("1", 1)
    
    def test_getMyFriendActivities(self):
        self.expect("3", 2)
        
    def test_getOthersActivities(self):
        url = get_activities_url("2")
        response = self.c.get(url, HTTP_AUTHORIZATION=self.authentication)
        self.assertEqual(response.status_code, 403)

    
    