from django.http.response import HttpResponse, HttpResponseBadRequest
from webapi import SYSEncoder
import simplejson as json

def jsonResponse(result):
    return json.dumps(result, default=SYSEncoder.encode_models, indent=2)

class JSONResponse(HttpResponse):
    def __init__(self, response):
        super(JSONResponse, self).__init__(jsonResponse(response),content_type='application/json; charset=utf-8')

class JSONResponseBadRequest(HttpResponseBadRequest):
    def __init__(self, message):
        super(JSONResponseBadRequest, self).__init__(message)

