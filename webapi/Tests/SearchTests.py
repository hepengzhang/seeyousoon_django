from django.test import TestCase
from django.test.client import Client
import simplejson as json

from TestUtils import get_authorization_credential

from webapi import models


def get_search_people_url():
    return "/webapi/search/people"


# class SearchPeopleTest(TestCase):
#     fixtures = ['TestFixtures.json']
#     c = Client()
#
#     def setUp(self):
#         self.authorization = get_authorization_credential(self.fixtures, 1)
#
#     def expect_search(self, keywords, return_code, expected_return):
#         response = self.c.get(get_search_people_url(), data={"keywords": keywords}, HTTP_AUTHORIZATION=self.authorization)
#         self.assertEqual(response.status_code, return_code)
#         if response.status_code != 200:
#             return
#         response = json.loads(response.content)
#         for expected_user in expected_return:
#             self.assertIn(expected_user, response)
#
#     def test_search(self):
#         users = [{'user_id':1}]
#         self.expect_search("hepeng", 200, users)
#
#     pass