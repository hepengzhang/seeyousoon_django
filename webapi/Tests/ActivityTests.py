from django.test import TestCase
from django.test.client import Client
import simplejson as json
from webapi import models

from TestUtils import get_authorization_credential, get_activities_ID_url, get_activityComment_url, \
    get_activityParticipant_url, get_participant_id_url, delete_activityComment_url


class ActivitiesTest(TestCase):
    fixtures = ['TestFixtures.json']
    authorization = "1 hepengzhangAT"
    c = Client()

    def expect(self, activity_id, return_code):
        response = self.c.get(get_activities_ID_url(activity_id))
        self.assertEqual(response.status_code, 403)

        response = self.c.get(get_activities_ID_url(activity_id), HTTP_AUTHORIZATION=self.authorization)
        self.assertEqual(response.status_code, return_code)
        if return_code != 200: return
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
        activity = models.activities.objects.get(activity_id=activity_id)
        self.assertEqual(activity.status, -1, "Activiy status is not set to -1")

    def expectUpdate(self, activity_id, return_code, updateContents, expectResult):
        if updateContents == None: updateContents = {}
        url = get_activities_ID_url(activity_id)

        response = self.c.put(url, data=json.dumps(updateContents), content_type='application/json')
        self.assertEqual(response.status_code, 403)

        response = self.c.put(url, data=json.dumps(updateContents), content_type='application/json',
                              HTTP_AUTHORIZATION=self.authorization)
        self.assertEqual(response.status_code, return_code, response.content)
        if return_code != 200: return
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
        updateContents = {u"access": 1, u"keyword": u"updateKeyword"}
        self.expectUpdate("1", 200, updateContents, updateContents)

    def test_updateMyActivityUnmodifiable(self):
        updateContents = {"activity": 2, "creator": {"user_id": 2, "username": "testUpdate", "name": "testName"}}
        expectContents = {"activity_id": 1}
        response = self.expectUpdate("1", 200, updateContents, expectContents)
        self.assertEqual(response["creator"]["user_id"], 1)
        self.assertEqual(response["creator"]["username"], "hepengzhang")
        self.assertEqual(response["creator"]["name"], "Hepeng Zhang")

    def test_updateOtherActivity(self):
        self.expectUpdate("2", 403, None, None)


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

        comment = {"contents": content}
        url = get_activityComment_url(activity_id)
        response = self.c.post(url, data=json.dumps(comment), content_type='application/json')
        self.assertEqual(response.status_code, 403)

        response = self.c.post(url, data=json.dumps(comment), content_type='application/json',
                               HTTP_AUTHORIZATION=self.authorization)
        self.assertEqual(response.status_code, return_code)
        if response.status_code != 201: return
        commentsCountNow = models.comments.objects.filter(activity_id=activity_id).count()
        self.assertEqual(commentsCountNow, commentsCountBefore + 1, "Not added in database")
        response = json.loads(response.content)
        self.assertEqual(response["contents"], content)
        self.assertEqual(str(response["activity"]), activity_id)
        self.assertEqual(response["creator"], 1)

    def expectDeletedComment(self, comment_id, activity_id, return_code):
        commentsCountBefore = models.comments.objects.filter(activity_id=activity_id).count()

        url = delete_activityComment_url(comment_id)
        response = self.c.delete(url)
        self.assertEqual(response.status_code, 403)
        response = self.c.delete(url, HTTP_AUTHORIZATION=self.authorization)
        self.assertEqual(response.status_code, return_code)
        if return_code != 204: return;
        commentsCountNow = models.comments.objects.filter(activity_id=activity_id).count()
        self.assertEqual(commentsCountBefore, commentsCountNow + 1)

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
        self.expectDeletedComment("4", "1", 404)


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

    def expectDeleteParticipant(self, activity_id, entry_id, return_code):
        url = get_participant_id_url(activity_id, entry_id)
        response = self.c.delete(url, HTTP_AUTHORIZATION=self.authorization)
        self.assertEqual(response.status_code, return_code)

    def test_deleteMyActivityParticipant(self):
        self.expectDeleteParticipant("1", "3", 204)

    def test_deleteMyselfAsParticipant(self):
        self.expectDeleteParticipant("1", "1", 204)

    def test_deleteOthersActivityParticipant(self):
        self.expectDeleteParticipant("4", "3", 403)

    def expectJoinParticipant(self, activity_id, user_id, return_code):
        url = get_activityParticipant_url(activity_id)
        self.authorization = get_authorization_credential(self.fixtures, user_id)
        response = self.c.post(url, data={}, content_type='application/json', HTTP_AUTHORIZATION=self.authorization)
        self.assertEqual(response.status_code, return_code)
        if response.status_code > 299: return

    def test_joinUnaccessableActivity(self):
        self.expectJoinParticipant("3", "2", 403)

    def test_joinAccessibleAcitivyt(self):
        self.expectJoinParticipant("3", "1", 201)
    