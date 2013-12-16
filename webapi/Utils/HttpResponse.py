from django.http.response import HttpResponse
from webapi import SYSEncoder
import simplejson as json

def jsonResponse(result):
    return json.dumps(result, default=SYSEncoder.encode_models, indent=2)

class JSONResponse(HttpResponse):
    def __init__(self, response):
        super(JSONResponse, self).__init__(jsonResponse(response),content_type='application/json')

class JSONResponse4xx(HttpResponse):
    def __init__(self, message, status=400):
        super(JSONResponse4xx, self).__init__(message, status=status)
    

