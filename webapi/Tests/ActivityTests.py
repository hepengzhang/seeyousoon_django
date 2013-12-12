from django.test import TestCase
from django.test.client import Client
import simplejson as json
from webapi import models

API_ACTIVITY_URL = "/webapi/activity"
API_COMMENT_URL = "/webapi/activity/comment"

def get_activities_ID_url(activity_id):
    return "/webapi/activities/"+activity_id

def get_activityComment_url(activity_id):
    return "/webapi/activities/"+activity_id+"/comments"

def get_activityParticipant_url(activity_id):
    return "/webapi/activities/"+activity_id+"/participants"

class ActivitiesTest(TestCase):
    fixtures = ['TestFixtures.json']
    authorization = "1 hepengzhangAT"
    c = Client()
    
    def expect(self, activity_id, return_code):
        response = self.c.get(get_activities_ID_url(activity_id), HTTP_AUTHORIZATION=self.authorization)
        self.assertEqual(response.status_code, return_code)
        if return_code!=200:return
        response = json.loads(response.content)
        self.assertEqual(str(response['activity_id']), activity_id)
        
    def test_getMyAcitivity(self):
        self.expect("1", 200)
    
    def test_getFriendPublicActivity(self):
        self.expect("2", 200)

    def test_getFriendPrivateActivity(self):
        self.expect("3", 200)
            
    def test_getOtherPrivateActivity(self):
        self.expect("4", 403)
    
    def test_getOtherPublicActivity(self):
        self.expect("5", 200)
        
    def test_getNonExistActivity(self):
        self.expect("6", 404)
        
    

class activityTest(TestCase):
    
    fixtures = ['TestFixtures.json']
    authentication = "1 hepengzhangAT"
    
    def setUp(self):
        self.c = Client()
        pass
    
    def test_createActivitySuccess(self):
        request = {
                   "user_id":"1",
                   "access_token":"hepengzhangAT",
                   "keyword":"TestCreateActivity",
                   "access":0
                   }
        numOfActs = models.activities.objects.all().count();
        self.assertEqual(numOfActs, 3)
        response = self.c.post(API_ACTIVITY_URL, data=json.dumps(request), content_type='application/json', HTTP_AUTHORIZATION=self.authentication)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertTrue('activity' in response, "return doesn't contain activity")
        self.assertEqual(response['activity']['activity_id'], 4)
        pass
    
    def test_getActivity(self):
        request = {
                   "user_id":"1",
                   "min_date":"2011-05-16T15:00:00",
                   "max_date":"2014-05-16T15:00:00",
                   "access_token":"hepengzhangAT",
                   "type":"friends"
                   }
        response = self.c.get(API_ACTIVITY_URL, data=request, HTTP_AUTHORIZATION=self.authentication)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertTrue(isinstance(response["activities"], list))
        self.assertEqual(len(response["activities"]), 2)
    
class CommentsTest(TestCase):
    
    fixtures = ['TestFixtures.json']
    authorization = u"1 hepengzhangAT"
    c = Client()
    
    def expectGetComment(self, activity_id, return_code, numOfComment):
        url = get_activityComment_url(activity_id)
        response = self.c.get(url, HTTP_AUTHORIZATION=self.authorization)
        self.assertEqual(response.status_code, return_code)
        if response.status_code != 200: return
        response = json.loads(response.content)
        self.assertEqual(len(response), numOfComment)
    
    def test_getAccessibleComments(self):
        self.expectGetComment("2", 200, 2)
    
    def test_getNoAccessComments(self):
        self.expectGetComment("4", 403, 0)
        
    def test_createComment(self):
        request = dict(self.request)
        comment = {"activity_id":1, "contents":"user1's comments"}
        request.update(comment)
        response = self.c.post(API_COMMENT_URL, data=json.dumps(request), content_type='application/json', HTTP_AUTHORIZATION=self.authentication)

        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        comment = models.comments.objects.filter(activity_id=request['activity_id'])
        self.assertEqual(comment.count(), 1)
        self.assertEqual(comment[0].creator_id, request["user_id"])
        self.assertEqual(comment[0].contents, request["contents"])
        self.assertEqual(comment[0].activity_id, request["activity_id"])
        activity = models.activities.objects.get(pk=1)
        self.assertEqual(activity.num_of_comments, 1)

        request.update({"user_id":2})
        self.c.post(API_COMMENT_URL, data=json.dumps(request), content_type='application/json', HTTP_AUTHORIZATION=self.authentication)
        activity = models.activities.objects.get(pk=1)
        self.assertEqual(activity.num_of_comments, 2)
    
    def test_getComments(self):
        numOfComments = models.comments.objects.filter(activity_id=2).count()
        self.assertEqual(numOfComments, 2)
        request = dict(self.user)
        request.update({"activity_id":2, "offset":0, "number":50})
        response = self.c.get(API_COMMENT_URL, data=request, HTTP_AUTHORIZATION=self.authentication)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(len(response['comments']), 2)
        
    def test_deleteComments(self):
        request = dict(self.user)
        request.update({"activity_id":2, "comment_id":1})
        response = self.c.delete(API_COMMENT_URL, data=json.dumps(request), content_type='application/json', HTTP_AUTHORIZATION=self.authentication)

        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        comments = models.comments.objects.filter(activity_id=2)
        self.assertEqual(comments.count(), 1)
        self.assertEqual(comments[0].creator_id, 2)

class ParticipantsTest(TestCase):
    fixtures = ['TestFixtures.json']
    authorization = u"1 hepengzhangAT"
    c = Client()
    
    def expect(self, activity_id, return_code, expectedNumParticipants):
        url = get_activityParticipant_url(activity_id)
        response = self.c.get(url, HTTP_AUTHORIZATION=self.authorization)
        self.assertEqual(response.status_code, return_code)
        if response.status_code != 200: return
        response = json.loads(response.content)
        self.assertEqual(len(response), expectedNumParticipants)

    def test_getAccessibleParticipants(self):
        self.expect("1", 200, 2)
    
    def test_getUnaccessibleParticipants(self):
        self.expect("4", 403, 0)
    