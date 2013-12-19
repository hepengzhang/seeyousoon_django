import json

def get_authorization_credential(fixtures, user_id):
    
    user_id = long(user_id)
    json_data = [open("webapi/fixtures/"+fixture).read() for fixture in fixtures]
    data = [json.loads(piece) for piece in json_data]
    data = [item for sub in data for item in sub]
    a = [{x['pk']:x['fields']['access_token']} for x in data if x['model']=='webapi.user_auth' and x['pk']==user_id]
    if len(a)==0:
        print "data:\n", data, "user_id", user_id
    return unicode(user_id)+u" "+a[0][user_id]
    