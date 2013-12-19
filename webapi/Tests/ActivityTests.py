from django.test import TestCase
from django.test.client import Client
import simplejson as json
from webapi import models

from TestUtils import get_authorization_credential

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
        response = self.c.get(get_activities_ID_url(activity_id))
        self.assertEqual(response.status_code, 403)
        
        response = self.c.get(get_activities_ID_url(activity_id), HTTP_AUTHORIZATION=self.authorization)
        self.assertEqual(response.status_code, return_code)
        if return_code!=200:return
        response = json.loads(response.content)
        self.assertEqual(str(response['activity_id']), activity_id)
        
    def expectDeletedActivity(self, activity_id, return_code):
        countBefore = models.activities.objects.filter(activity_id=activity_id).count()
        self.assertEqual(countBefore, 1, "Initial data not correct")

        url = get_activities_ID_url(activity_id)
        
        response = self.c.delete(url)
        self.assertEqual(response.status_code, 403)
        
        response = self.c.delete(url, HTTP_AUTHORIZATION=self.authorization)
        self.assertEqual(response.status_code, return_code)
        
        if return_code != 204: return
        countNow = models.activities.objects.filter(activity_id=activity_id).count()
        self.assertEqual(countNow, 0, "Activiy is not deleted in database")
        
    def expectUpdate(self, activity_id, return_code, updateContents, expectResult):
        if updateContents == None : updateContents = {}
        url = get_activities_ID_url(activity_id)
        
        response = self.c.put(url, data=json.dumps(updateContents), content_type='application/json')
        self.assertEqual(response.status_code, 403)
        
        response = self.c.put(url, data=json.dumps(updateContents), content_type='application/json', HTTP_AUTHORIZATION=self.authorization)
        self.assertEqual(response.status_code, return_code, response.content)
        if return_code != 200 : return
        response = json.loads(response.content)
        self.assertDictContainsSubset(expected=expectResult, actual=response)
        return response
        
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
        
    def test_deleteMyActivity(self):
        self.expectDeletedActivity("1", 204)
        
    def test_deleteOthersActivity(self):
        self.expectDeletedActivity("2", 403)
        
    def test_updateMyActivity(self):
        updateContents = {u"access":1, u"keyword":u"updateKeyword"}
        self.expectUpdate("1", 200, updateContents, updateContents)
    
    def test_updateMyActivityUnmodifiable(self):
        updateContents = {"activity":2, "creator":{"user_id":2, "username":"testUpdate", "name":"testName"}}
        expectContents = {"activity_id":1}
        response = self.expectUpdate("1", 200, updateContents, expectContents)
        self.assertEqual(response["creator"]["user_id"], 1)
        self.assertEqual(response["creator"]["username"], "hepengzhang")
        self.assertEqual(response["creator"]["name"], "Hepeng Zhang")
    
    def test_updateOtherActivity(self):
        self.expectUpdate("2", 403, None, None)
        
# class activityTest(TestCase):
#     
#     fixtures = ['TestFixtures.json']
#     authentication = "1 hepengzhangAT"
#     
#     def setUp(self):
#         self.c = Client()
#         pass
#     
#     def test_createActivitySuccess(self):
#         request = {
#                    "user_id":"1",
#                    "access_token":"hepengzhangAT",
#                    "keyword":"TestCreateActivity",
#                    "access":0
#                    }
#         numOfActs = models.activities.objects.all().count();
#         self.assertEqual(numOfActs, 5)
#         response = self.c.post(API_ACTIVITY_URL, data=json.dumps(request), content_type='application/json', HTTP_AUTHORIZATION=self.authentication)
#         self.assertEqual(response.status_code, 200)
#         response = json.loads(response.content)
#         self.assertTrue('activity' in response, "return doesn't contain activity")
#         self.assertEqual(response['activity']['activity_id'], 6)
#         pass
#     
#     def test_getActivity(self):
#         request = {
#                    "user_id":"1",
#                    "min_date":"2011-05-16T15:00:00",
#                    "max_date":"2014-05-16T15:00:00",
#                    "access_token":"hepengzhangAT",
#                    "type":"friends"
#                    }
#         response = self.c.get(API_ACTIVITY_URL, data=request, HTTP_AUTHORIZATION=self.authentication)
#         self.assertEqual(response.status_code, 200)
#         response = json.loads(response.content)
#         self.assertTrue(isinstance(response["activities"], list))
#         self.assertEqual(len(response["activities"]), 2)
    
class CommentsTest(TestCase):
    
    fixtures = ['TestFixtures.json']
    authorization = u"1 hepengzhangAT"
    c = Client()
    
    def expectGetComment(self, activity_id, return_code, numOfComment):
        url = get_activityComment_url(activity_id)
        response = self.c.get(url)
        self.assertEqual(response.status_code, 403)
        
        response = self.c.get(url, HTTP_AUTHORIZATION=self.authorization)
        self.assertEqual(response.status_code, return_code)
        if response.status_code != 200: return
        response = json.loads(response.content)
        self.assertEqual(len(response), numOfComment)
        
    def expectCreatedComment(self, activity_id, return_code, content):
        commentsCountBefore = models.comments.objects.filter(activity_id=activity_id).count()
        
        comment = {"contents":content}
        url = get_activityComment_url(activity_id)
        response = self.c.post(url, data=json.dumps(comment), content_type='application/json')
        self.assertEqual(response.status_code, 403)
        
        response = self.c.post(url, data=json.dumps(comment), content_type='application/json', HTTP_AUTHORIZATION=self.authorization)
        self.assertEqual(response.status_code, return_code)
        if response.status_code != 201: return 
        commentsCountNow = models.comments.objects.filter(activity_id=activity_id).count()
        self.assertEqual(commentsCountNow, commentsCountBefore+1, "Not added in database")
        response = json.loads(response.content)
        self.assertEqual(response["contents"], content)
        self.assertEqual(str(response["activity"]), activity_id)
        self.assertEqual(response["creator"], 1)
        
    def expectDeletedComment(self, comment_id, activity_id, return_code):
        commentsCountBefore = models.comments.objects.filter(activity_id=activity_id).count()
        
        url = get_activityComment_url(activity_id) + "/" + comment_id
        response = self.c.delete(url)
        self.assertEqual(response.status_code, 403)
        response = self.c.delete(url, HTTP_AUTHORIZATION=self.authorization)
        self.assertEqual(response.status_code, return_code)
        if return_code != 204: return;
        commentsCountNow = models.comments.objects.filter(activity_id=activity_id).count()
        self.assertEqual(commentsCountBefore, commentsCountNow+1)
    
    def test_getAccessibleComments(self):
        self.expectGetComment("2", 200, 2)
    
    def test_getNoAccessComments(self):
        self.expectGetComment("4", 403, 0)
        
    def test_createAccessibleComment(self):
        self.expectCreatedComment("3", 201, "user1's comment")
        
    def test_createNonAccessibleComment(self):
        self.expectCreatedComment("4", 403, "Can't be created")
        
    def test_deleteMyComments(self):
        self.expectDeletedComment("1", "2", 204)

    def test_deleteOtherComments(self):
        self.expectDeletedComment("2", "2", 403)
    
    def test_deleteNonExistingComment(self):
        self.expectDeletedComment("3", "1", 404)
        

class ParticipantsTest(TestCase):
    fixtures = ['TestFixtures.json']
    c = Client()

    def setUp(self):
        self.authorization = get_authorization_credential(self.fixtures, "1")
    
    def expect(self, activity_id, return_code, expectedNumParticipants):
        url = get_activityParticipant_url(activity_id)
        response = self.c.get(url)
        self.assertEqual(response.status_code, 403)
        response = self.c.get(url, HTTP_AUTHORIZATION=self.authorization)
        self.assertEqual(response.status_code, return_code)
        if response.status_code != 200: return
        response = json.loads(response.content)
        self.assertEqual(len(response), expectedNumParticipants)

    def test_getAccessibleParticipants(self):
        self.expect("1", 200, 2)
    
    def test_getUnaccessibleParticipants(self):
        self.expect("4", 403, 0)
    