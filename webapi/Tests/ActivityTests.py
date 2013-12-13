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
        
    def expectCreatedComment(self, activity_id, return_code, content):
        commentsCountBefore = models.comments.objects.filter(activity_id=activity_id).count()
        
        comment = {"contents":content}
        url = get_activityComment_url(activity_id)
        response = self.c.post(url, data=json.dumps(comment), content_type='application/json', HTTP_AUTHORIZATION=self.authorization)
        self.assertEqual(response.status_code, return_code)
        if response.status_code != 201: return 
        commentsCountNow = models.comments.objects.filter(activity_id=activity_id).count()
        self.assertEqual(commentsCountNow, commentsCountBefore+1, "Not added in database")
        response = json.loads(response.content)
        self.assertEqual(response["contents"], content)
        self.assertEqual(str(response["activity"]), activity_id)
        self.assertEqual(response["creator"], 1)
    
    def test_getAccessibleComments(self):
        self.expectGetComment("2", 200, 2)
    
    def test_getNoAccessComments(self):
        self.expectGetComment("4", 403, 0)
        
    def test_createAccessibleComment(self):
        self.expectCreatedComment("3", 201, "user1's comment")
        
    def test_createNonAccessibleComment(self):
        self.expectCreatedComment("4", 403, "Can't be created")
        
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
    