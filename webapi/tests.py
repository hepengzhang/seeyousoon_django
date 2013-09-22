"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client, RequestFactory
import simplejson as json
from webapi import models, SYSMessages,SYSEncoder, apis

API_LOGIN_URL = "/webapi/login"
API_REGISTER_URL = "/webapi/register"
API_CHECKUSERNAME_URL = "/webapi/register/checkUsername"
API_ACTIVITY_URL = "/webapi/activity"
API_FRIEND_URL = "/webapi/friends"
API_COMMENT_URL = "/webapi/activity/comments"
API_USERSEARCH_URL = "/webapi/user/search"


class registerTest(TestCase):
    
    basicRequest = None;
    FBRequest = None;
    WBRequest = None;
    bothRequest = None;
    
    def setUp(self):
        self.basicRequest = {'email':'test@test.com', 
                             'username':'test',
                             'password':'testtest' }
        pass
    
    def test_NewUser(self):
        c = Client()
        paraDict = self.basicRequest
        response = c.post(API_REGISTER_URL, data=json.dumps(paraDict), content_type='application/json')
        self.assertEqual(response.status_code, 200, msg='Response error status code')
        response = json.loads(response.content)
        print response
        self.assertIsNotNone(response['access_token'], 'access_token should not be null')
        fields = response['user_info']
        self.assertTrue('user_info' in response, "return doesn't contain user_info")
        self.assertEqual(fields['username'], paraDict['username'], 'return wrong username')
        self.assertEqual(fields['email'], paraDict['email'], 'return wrong email')
        
        info = models.user_info.objects.filter(username=paraDict['username'])
        self.assertEqual(len(info), 1, 'not inserted in databse user_info')
        auth = models.user_auth.objects.filter(username=paraDict['username'])
        self.assertEqual(len(auth), 1, 'not inserted in databse user_info')
        search = models.user_search.objects.filter(username=paraDict['username'])
        self.assertEqual(len(search), 1, 'not inserted in databse user_info')
        pass
    
    def test_alreadyExist(self):
        c = Client()
        paraDict = self.basicRequest
        info = models.user_info.objects.filter(username=paraDict['username'])
        self.assertEqual(len(info), 0, 'should not exist in database user_info')
        c.post(API_REGISTER_URL, data=json.dumps(paraDict), content_type='application/json')
        response = c.post(API_REGISTER_URL, data=json.dumps(paraDict), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, "Username exists.")
        print '\ntest_alreadyExist:' + str(response)
        pass

class loginTest(TestCase):
    
    correctUser = None;
    userNotExist = None;
    wrongPassword = None;
    bothRequest = None;
    c = None;
    
    def setUp(self):
        self.correctUser = {'email':'test@test.com', 
                             'username':'logintest',
                             'password':'testtest' }
        self.userNotExist = {'username':'usernotexist',
                             'password':'testtest' }
        self.wrongPassword = {'username':'logintest',
                             'password':'test' }
        self.c = Client()
        self.c.post(API_REGISTER_URL, data=json.dumps(self.correctUser), content_type='application/json')
        pass
    
    def test_correctLogin(self):
        response = self.c.post(API_LOGIN_URL, data=json.dumps(self.correctUser), content_type='application/json')
        print '\nloginTest:test_correctLogin:'+ str(response)
        self.assertEqual(response.status_code, 200, msg='Response error status code')
        response = json.loads(response.content)
        self.assertIsNotNone(response['access_token'], 'access_token should not be null')
        fields = response['user_info']
        self.assertTrue('user_info' in response, "return doesn't contain user_info")
        self.assertEqual(fields['username'], self.correctUser['username'], 'return wrong username')
        pass
    
    def test_userNotExist(self):
        response = self.c.post(API_LOGIN_URL, data=json.dumps(self.userNotExist), content_type='application/json')
        print '\nloginTest:test_userNotExist: '+ str(response)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content, "Username usernotexist does not exist.")
        pass
    
    def test_wrongPassword(self):
        response = self.c.post(API_LOGIN_URL, data=json.dumps(self.wrongPassword), content_type='application/json')
        print '\nloginTest:test_wrongPassword: '+ str(response)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.content, "Wrong password")
        pass
    
    def test_lastLoginChanged(self):
        
        pass
    
class checkUsernameTest(TestCase):
    
    existUser = None;
    nonexistUser = None;
    c = None;
    
    def setUp(self):
        self.correctUser = {'email':'checkUsernameTest@test.com',
                            'username':'checkUsernameTest',
                             'password':'testtest' }
        self.existUser = {'username':'checkUsernameTest'}
        self.nonexistUser = {'username':'checkUsernameTestNotExist'}
        self.c = Client()
        pass
    
    def test_nonexistUser(self):
        response = self.c.get(API_CHECKUSERNAME_URL, self.nonexistUser)
        print '\ncheckUsernameTest:test_nonexistUser: '+ str(response)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['available'], True)
        pass
        
    def test_existUser(self):
        self.c.post(API_REGISTER_URL, data=json.dumps(self.correctUser), content_type='application/json')
        response = self.c.get(API_CHECKUSERNAME_URL, self.existUser)
        print '\ncheckUsernameTest:test_existUser: '+ str(response)
        self.assertEqual(response.status_code, 200, msg='Response error status code')
        response = json.loads(response.content)
        self.assertEqual(response['available'], False)
        pass
    
class activityTest(TestCase):
    
    user = None
    access_token = None
    createRequest = None
    getRequest = None
    c = Client()
    
    def setUp(self):
        self.user = {'email':'test@test.com', 
                     'username':'test',
                     'password':'testtest' }
        response = self.c.post(API_REGISTER_URL, data=json.dumps(self.user),content_type='application/json')
        response = json.loads(response.content)
        user_id = response['user_info']['user_id']
        self.user = models.user_info.objects.get(pk=user_id)
        self.access_token = response['access_token']
        self.createRequest = {
                       "user_id":user_id,
                       "min_date":"2011-05-16T15:00:00",
                       "max_date":"2014-05-16T15:00:00",
                       "access_token":self.access_token,
                       "keyword":"food",
                       "access":0
                       }
        self.getRequest = dict(self.createRequest)
        self.getRequest['type']="friends"
        pass
    
    def test_createActivitySuccess(self):
        response = self.c.post(API_ACTIVITY_URL,data=json.dumps(self.createRequest),content_type='application/json')
        print '\nactivityTest:createActivitySuccessTest '+ str(response)
        self.assertEqual(response.status_code, 200, msg='Response error status code')
        response = json.loads(response.content)
        self.assertTrue('activity' in response, "return doesn't contain activity")
        self.assertEqual(response['activity']['activity_id'],1,"id should be 1")
        pass
    
    def test_getActivity(self):
        response = self.c.get(API_ACTIVITY_URL,data=self.getRequest)
        print '\nactivityTest: test_invalidAccess '+ str(response)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertTrue(isinstance(response, list))
        pass
     
class friendsTest(TestCase):
    
    c = Client()
    def setUp(self):
        self.user1 = {'email':'friend@test.com', 
                     'username':'friendTest1',
                     'password':'friendTest',
                     'friend_username':'friendTest2'}
        self.user2 = {'email':'friend@test.com', 
                     'username':'friendTest2',
                     'password':'friendTest',
                     'friend_username':'friendTest1' }
        response = self.c.post(API_REGISTER_URL, json.dumps(self.user1), "application/json")
        response = json.loads(response.content)
        self.user1['user_id'] = response['user_info']['user_id']
        self.user1['access_token'] = response['access_token']
        response = self.c.post(API_REGISTER_URL, json.dumps(self.user2), "application/json")
        response = json.loads(response.content)
        self.user2['user_id'] = response['user_info']['user_id']
        self.user2['access_token'] = response['access_token']
        self.assertEqual(self.user1['user_id'], 1)
        self.assertEqual(self.user2['user_id'], 2)
        
    def test_sendFriendRequest(self):
        request = dict(self.user1)
        response = self.c.post(API_FRIEND_URL, json.dumps(request), 'application/json')
        print '\n friendsTest: test_sendFriendRequest - post '+ str(response)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['message'], "success")
        friend = models.friends.objects.filter(user_id=self.user1['user_id'],friend_id=self.user2['user_id'],status=0)
        self.assertEqual(friend.count(), 1)

    def test_acceptFriendRequest(self):
        request = dict(self.user1)
        self.c.post(API_FRIEND_URL, json.dumps(request), 'application/json')
        request = dict(self.user2)
        response = self.c.post(API_FRIEND_URL, json.dumps(request), 'application/json')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['message'], "success")
        friend = models.friends.objects.filter(user_id=self.user1['user_id'],friend_id=self.user2['user_id'],status=1)
        self.assertEqual(friend.count(), 1)
    
    def test_getFriends(self):
        request = dict(self.user1)
        self.c.post(API_FRIEND_URL, json.dumps(request), 'application/json')
        request = dict(self.user2)
        self.c.post(API_FRIEND_URL, json.dumps(request), 'application/json')
        
        request = dict(self.user1)
        request['type'] = 'friends'
        response = self.c.get(API_FRIEND_URL, request)
        print '\n friendsTest: test_getFriends - get '+ str(response)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertIsNotNone(response)
        self.assertEqual(len(response), 1)
        user2 = models.user_info.objects.get(pk=2)
        user2 = json.dumps(user2, default=SYSEncoder.encode_models)
        user2 = json.loads(user2)
        self.maxDiff = None
        self.assertDictEqual(user2, response[0])
        
class commentsTest(TestCase):
    
    c = Client()
    user1 = {'email':'user1@test.com', 
             'username':'user1',
             'password':'testtest'}
    user2 = {'email':'user2@test.com', 
             'username':'user2',
             'password':'testtest'}
    activity = {"user_id":"1",
                "access_token":'testaccess',
                "keyword":"food",
                "access":0}
    comments1 = {"activity_id":1,
                 "user_id":1,
                 "contents":"user1's comments",
                 "access_token":'testaccess',
                 }
    comments2 = {"activity_id":1,
                 "user_id":2,
                 "contents":"user2's comments",
                 "access_token":'testaccess',
                 }
    getcomments = {"activity_id":1,
                   "user_id":1,
                   "access_token":'testaccess',
                   "offset":0,
                   "number":50
                   }
    deletecomment = {"activity_id":1,
                     "user_id":1,                     
                     "access_token":'testaccess',
                     "comment_id":1,
                     "number":50
                     }
    def setUp(self):
        self.c.post(API_REGISTER_URL, data=json.dumps(self.user1),content_type='application/json')
        self.c.post(API_REGISTER_URL, data=json.dumps(self.user2),content_type='application/json')
        models.user_auth.objects.all().update(access_token='testaccess')
        self.c.post(API_ACTIVITY_URL, data=json.dumps(self.activity),content_type='application/json')
        activity = models.activities.objects.all()
        self.assertEqual(activity.count(),1)
        self.factory = RequestFactory()
        
    def test_createComment(self):
        response = self.c.post(API_COMMENT_URL, data=json.dumps(self.comments1), content_type='application/json')
        print '\n commentTest: createComment - post '+ str(response)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        comment = models.comments.objects.all()
        self.assertEqual(comment.count(),1)
        self.assertEqual(comment[0].creator_id,1)
        self.assertEqual(comment[0].contents,"user1's comments")
        self.assertEqual(comment[0].activity_id,1)
        activity = models.activities.objects.get(pk=1)
        self.assertEqual(activity.num_of_comments, 1)
        self.c.post(API_COMMENT_URL, data=json.dumps(self.comments2), content_type='application/json')
        activity = models.activities.objects.get(pk=1)
        self.assertEqual(activity.num_of_comments, 2)
    
    def test_getComments(self):
        self.c.post(API_COMMENT_URL,data=json.dumps(self.comments1),content_type='application/json')
        self.c.post(API_COMMENT_URL,data=json.dumps(self.comments2),content_type='application/json')
        response = self.c.get(API_COMMENT_URL, data=self.getcomments)
        print '\n commentTest: getComments - get '+ str(response)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(len(response['comments']), 2)
        self.assertEqual(response['comments'][0]['contents'], self.comments2['contents'])
        self.assertEqual(response['comments'][0]['creator_id'], self.comments2['user_id'])
        self.assertEqual(response['comments'][0]['activity_id'], self.comments2['activity_id'])
        self.assertEqual(response['comments'][1]['contents'], self.comments1['contents'])
        self.assertEqual(response['comments'][1]['creator_id'], self.comments1['user_id'])
        self.assertEqual(response['comments'][1]['activity_id'], self.comments1['activity_id'])
        
    def test_deleteComments(self):
        self.c.post(API_COMMENT_URL,data=json.dumps(self.comments1),content_type='application/json')
        self.c.post(API_COMMENT_URL,data=json.dumps(self.comments2),content_type='application/json')
        request = self.factory.delete(API_COMMENT_URL, self.deletecomment, content_type='application/json')
        request.GET = self.deletecomment
        response = apis.comments(request)
        print '\n commentTest: delete Comments - delete '+ str(response)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        comments = models.comments.objects.filter(activity_id=1)
        self.assertEqual(comments.count(), 1)
        self.assertEqual(comments[0].creator_id, 2)

# ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! !
# Painful to test on user search feature
# Reason: test database of sqlite has different syntax of Fulltext search
# If using test database of MySQL, then need to create fulltext index first,
# which I can't figure out right now
#
# class userSearchTest(TestCase):
#     
#     c = Client()
#     searchFortest = {'keyword':'test'}
#     searchForZhang = {'keyword':'Zhang'}
#     searchForKang = {'keyword':'Kang'}
#     searchForYimingKang = {'keyword':'Yiming Kang'}
#     
#     def setUp(self):
#         self.user1 = {'email':'user1@test.com', 
#              'username':'testuser1',
#              'password':'testtest',
#              'name':'Hepeng Zhang'}
#         self.user2 = {'email':'user1@test.com', 
#              'username':'test2',
#              'password':'testtest',
#              'name':'Yiming Kang'}
#         self.user3 = {'email':'user1@test.com', 
#              'username':'dnz1918',
#              'password':'testtest',
#              'name':'Dingni Zhang'}
#         self.c.post(API_REGISTER_URL,data=json.dumps(self.user1),content_type='application/json')
#         self.c.post(API_REGISTER_URL,data=json.dumps(self.user2),content_type='application/json')
#         self.c.post(API_REGISTER_URL,data=json.dumps(self.user3),content_type='application/json')
#     
#     def test_searchFortest(self):
#         response = self.c.get(API_USERSEARCH_URL, data=self.searchFortest)
#         print '\n userSearchTest: test_searchFortest - get '+ str(response)
#         self.assertEqual(response.status_code, 200)
#         response = json.loads(response.content)
#         self.assertEqual(response['return_code'], 1)
#         results = response['results']
#         self.assertEqual(len(results), 2)
        
