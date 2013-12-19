from django.test import TestCase
from django.test.client import Client
import simplejson as json

from TestUtils import get_authorization_credential

from webapi import models

def get_people_url(user_id):
    return "/webapi/people/"+user_id

def get_friends_url(user_id, scope):
    return "/webapi/people/"+user_id+"/friends/"+scope

def get_friends_id_url(user_id, friend_id):
    return "/webapi/people/"+user_id+"/friends/"+friend_id

def add_friends_url(friend_id):
    return "/webapi/people/"+friend_id+"/friends"

def get_activities_url(user_id):
    return "/webapi/people/"+user_id+"/activities"

class peopleTest(TestCase):
    
    fixtures = ['TestFixtures.json']
    authentication = "1 hepengzhangAT"
    c = Client()
    
    def expectGet(self, user_id, return_code, expect_user_id):
        url = get_people_url(user_id)
        response = self.c.get(url)
        self.assertEqual(response.status_code, 403)
        response = self.c.get(url, HTTP_AUTHORIZATION=self.authentication)
        self.assertEqual(response.status_code, return_code)
        if return_code!=200: return
        response = json.loads(response.content)
        self.assertTrue('user_id' in response, "return doesn't contain user_id")
        self.assertEqual(long(response['user_id']), long(expect_user_id))
    
    def expectUpdate(self, user_id, return_code, update_contents, expected_contents):
        url = get_people_url(user_id)
        response = self.c.put(url, data=json.dumps(update_contents), content_type='application/json')
        self.assertEqual(response.status_code, 403)
        response = self.c.put(url, data=json.dumps(update_contents), content_type='application/json', HTTP_AUTHORIZATION=self.authentication)
        self.assertEqual(response.status_code, return_code, response)
        if return_code!=200:return
        response = json.loads(response.content)
        self.assertDictContainsSubset(expected_contents, response)
        
    def test_getMyself(self):
        self.expectGet("1", 200, "1")
    
    def test_getFriend(self):
        self.expectGet("3", 200, "3")
        
    def test_getNonFriend(self):
        self.expectGet("2", 200, "2")
    
    def test_udpateMyself(self):
        update_contents = {"name":"hepeng", "phone":"94291015"}
        self.expectUpdate("1", 200, update_contents, update_contents)
        
    def test_updateMyselfUnmodifiable(self):
        update_contents = {"user_id":2, "username":"newusername"}
        expected_contents = {"user_id":1, "username":"hepengzhang"}
        self.expectUpdate("1", 200, update_contents, expected_contents)
        pass
    
    def test_updateOther(self):
        self.expectUpdate("2", 403, {}, {})
        
class friendsTest(TestCase):
    
    fixtures = ['TestFixtures.json']
    c = Client()
    
    def setUp(self):
        self.authorization = get_authorization_credential(self.fixtures, 1)
        
    def expectGetFriends(self, user_id, return_code, scope, expectedFriendsNum):
        url = get_friends_url(user_id, scope)
        response = self.c.get(url, HTTP_AUTHORIZATION=self.authorization)
        self.assertEqual(response.status_code, return_code)
        if return_code!=200:return
        response = json.loads(response.content)
        self.assertEqual(len(response), expectedFriendsNum)

    def test_getMyFriends(self):
        self.expectGetFriends("1", 200, "friends", 1)

    def test_getMyRequest(self):
        self.expectGetFriends("1", 200, "requests", 1)
        
    def test_getAll(self):
        self.expectGetFriends("1", 200, "all", 2)
            
    def test_getOthersFriends(self):
        self.expectGetFriends("2", 403, "all", 0)
        self.expectGetFriends("2", 403, "requests", 0)
        self.expectGetFriends("2", 403, "friends", 0)
    
    def expectDelete(self, user_id, friend_id, return_code):
        url = get_friends_id_url(user_id, friend_id)
        response = self.c.delete(url, HTTP_AUTHORIZATION=self.authorization)
        self.assertEqual(response.status_code, return_code)
    
    def test_deleteMyFriend(self):
        self.expectDelete("1", "3", 204)
    
    def test_deleteOtherFriend(self):
        self.expectDelete("2", "1", 403)
        
    def expectAddFriend(self, user_id, friend_id, return_code, friend_status):
        url = add_friends_url(friend_id)
        self.authorization = get_authorization_credential(self.fixtures, user_id)
        response = self.c.post(url, {}, HTTP_AUTHORIZATION=self.authorization)
        self.assertEqual(response.status_code, return_code)
        if response.status_code != return_code: return
        exist = models.friends.objects.filter(user_id=user_id, friend_id=friend_id, status=friend_status).count()
        self.assertTrue(exist==1)
        
    def test_postFriendRequest(self):
        self.expectAddFriend('1', '2', 201, 0)
    
    def test_approveFriendRequest(self):
        self.expectAddFriend('1', '2', 201, 0)
        self.expectAddFriend('2', '1', 201, 1)
    
class peopleActivitiesTest(TestCase):
    
    fixtures = ['TestFixtures.json']
    authentication = "1 hepengzhangAT"
    
    def expect(self, user_id, return_code, numOfActivities):
        url = get_activities_url(user_id)
        response = self.c.get(url, HTTP_AUTHORIZATION=self.authentication)
        self.assertEqual(response.status_code, return_code)
        if return_code != 200: return
        response = json.loads(response.content)
        self.assertEqual(len(response), numOfActivities)
        
    def expectCreate(self, user_id, return_code, contents, expected_contents):
        url = get_activities_url(user_id)
        response = self.c.post(url, data=json.dumps(contents), content_type='application/json', HTTP_AUTHORIZATION=self.authentication)
        self.assertEqual(response.status_code, return_code)
        if return_code != 200: return
        response = json.loads(response.content)
        self.assertDictContainsSubset(expected_contents, response)
        pass

    def setUp(self):
        self.c = Client()
    
    def test_getMyActivities(self):
        self.expect("1", 200, 1)
    
    def test_getMyFriendActivities(self):
        self.expect("3", 200, 2)
        
    def test_getOthersActivities(self):
        self.expect("2", 403, 0)
        
    def test_createMyActivity(self):
        contents = {"activity_id":10,"access":0, "type":"1", "description":"description", "longitude":931.291, "keyword":"keyword", "start_date":"2012-08-22T16:20:09", "num_of_participants":10}
        expected_contents = {"activity_id":1,"access":0, "type":"1", "description":"description", "longitude":931.291, "keyword":"keyword", "start_date":"2012-08-22T16:20:09", "num_of_participants":0}
        self.expectCreate("1", 201, contents, expected_contents)
        
    def test_createOtherActivity(self):
        self.expectCreate("2", 403, None, None)
        

    
    