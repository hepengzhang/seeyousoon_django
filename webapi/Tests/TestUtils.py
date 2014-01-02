import json


def get_authorization_credential(fixtures, user_id):
    user_id = long(user_id)
    json_data = [open("webapi/fixtures/" + fixture).read() for fixture in fixtures]
    data = [json.loads(piece) for piece in json_data]
    data = [item for sub in data for item in sub]
    a = [{x['pk']: x['fields']['access_token']} for x in data if
         x['model'] == 'webapi.user_auth' and x['pk'] == user_id]
    if len(a) == 0:
        print "data:\n", data, "user_id", user_id
    return unicode(user_id) + u" " + a[0][user_id]


def get_activities_ID_url(activity_id):
    return "/webapi/activities/" + activity_id


def get_activityComment_url(activity_id):
    return "/webapi/activities/" + activity_id + "/comments"


def get_activityParticipant_url(activity_id):
    return "/webapi/activities/" + activity_id + "/participants"


def get_participant_id_url(activity_id, user_id):
    return "/webapi/activities/" + activity_id + "/participants/" + user_id


def get_people_url(user_id):
    return "/webapi/people/" + user_id


def get_friends_url(user_id, scope):
    return "/webapi/people/" + user_id + "/friends/" + scope


def get_friends_id_url(user_id, friend_id):
    return "/webapi/people/" + user_id + "/friends/" + friend_id


def add_friends_url(friend_id):
    return "/webapi/people/" + friend_id + "/friends"


def get_activities_url(user_id):
    return "/webapi/people/" + user_id + "/activities"


def get_people_timeline(user_id):
    return "/webapi/people/" + user_id + "/timeline"


def get_all_friends_timeline():
    return "/webapi/timeline"


def delete_activityComment_url(comment_id):
    return "/webapi/activity/comments/" + comment_id