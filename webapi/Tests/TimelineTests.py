from django.test import TestCase
from django.test.client import Client

from webapi import models

import json
import TestUtils

class MyTestCase(TestCase):
    fixtures = ['TestFixtures.json']
    c = Client()

    def setUp(self):
        self.authorization = TestUtils.get_authorization_credential(self.fixtures, 1)

    def expect_new_timeline(self, user_id, activity_id, type, related_user_id):
        if activity_id is not None:
            timeline = models.user_timeline.objects.filter(user_id=user_id, activity_id=activity_id, type=type)
            self.assertEqual(len(timeline), 1)
        if related_user_id is not None:
            timeline = models.user_timeline.objects.filter(user_id=user_id, related_user_id=related_user_id, type=type)
            self.assertEqual(len(timeline), 1)

    def test_timeline_join_activity(self):
        url = TestUtils.get_activityParticipant_url("2")
        self.c.post(url, HTTP_AUTHORIZATION=self.authorization)
        self.expect_new_timeline('1', '2', models.TIMELINE_JOIN_ACTIVITY, None)

    def test_timeline_create_activity(self):
        url = TestUtils.get_activities_url('1')
        contents = {"keyword": "keyword", "start_date": "2012-08-22T16:20:09"}
        exist_activities = models.activities.objects.all().count()
        self.c.post(url, data=json.dumps(contents), content_type='application/json', HTTP_AUTHORIZATION=self.authorization)
        self.expect_new_timeline('1', str(exist_activities+1), models.TIMELINE_CREATE_ACTIVITY, None)

    def test_timeline_quit_activity(self):
        self.authorization = TestUtils.get_authorization_credential(self.fixtures, '3')
        url = TestUtils.get_participant_id_url('1', '3')
        self.c.delete(url, HTTP_AUTHORIZATION=self.authorization)
        self.expect_new_timeline('3', '1', models.TIMELINE_QUIT_ACTIVITY, None)

    def test_timeline_delete_activity(self):
        url = TestUtils.get_activities_ID_url('1')
        self.c.delete(url, HTTP_AUTHORIZATION=self.authorization)
        self.expect_new_timeline('1', '1', models.TIMELINE_DELETE_ACTIVITY, None)

    def test_timeline_modify_activity(self):
        url = TestUtils.get_activities_ID_url('1')
        update = {"description": "new description"}
        self.c.put(url, data=json.dumps(update), content_type='application/json', HTTP_AUTHORIZATION=self.authorization)
        self.expect_new_timeline('1', '1', models.TIMELINE_MODIFY_ACTIVITY, None)

    def test_timeline_become_friends(self):
        url = TestUtils.add_friends_url('2')
        self.c.post(url, HTTP_AUTHORIZATION=self.authorization)
        self.authorization = TestUtils.get_authorization_credential(self.fixtures, 2)
        url = TestUtils.add_friends_url('1')
        self.c.post(url, HTTP_AUTHORIZATION=self.authorization)
        self.expect_new_timeline('1', None, models.TIMELINE_BECOME_FRIENDS, '2')


    def expect_get_timeline(self, url, user_id, return_code):
        response = self.c.get(url, HTTP_AUTHORIZATION=self.authorization)
        self.assertEqual(response.status_code, return_code)
        if response.status_code != 200:
            return
        return json.loads(response.content)


    def test_get_friend_timeline(self):
        url = TestUtils.get_people_timeline("3")
        response = self.expect_get_timeline(url, "3", 200)
        self.assertEqual(len(response), 1)
        pass

    def test_get_all_friends_timeline(self):
        url = TestUtils.get_all_friends_timeline()
        response = self.expect_get_timeline(url, "1", 200)
        self.assertEqual(len(response), 2)
        pass
