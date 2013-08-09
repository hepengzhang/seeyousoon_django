import json
from webapi import models

class modelsEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, models.user_info):
            reprdict = {"last_login":o.last_login,
                "user_created_date":o.user_created_date,
                "email":o.email,
                "phone":o.phone,
                "user_access":o.user_access,
                "longitude":o.longitude,
                "latitude":o.latitude,
                "gender":o.gender,
                "fb_id":o.fb_id,
                "wb_id":o.wb_id,
                "primary_sns":o.longitude,
                "name":o.name,
                "user_id":o.user_id,
                "username":o.username
                }
            return reprdict
        if isinstance(o, models.activities):
            reprdict = {"activity_id":o.activity_id,
                "creator":o.creator,
                "access":o.access,
                "type":o.type,
                "status":o.status,
                "activity_created_date":o.activity_created_date,
                "description":o.description,
                "longitude":o.longitude,
                "latitude":o.latitude,
                "destination":o.destination,
                "keyword":o.keyword,
                "start_date":o.start_date,
                "end_date":o.end_date,
#                 "num_of_participants":o.num_of_participants
                }
            return reprdict
        return json.JSONEncoder.default(self, o)
    
def encode_models(o):
    if isinstance(o, models.user_info):
        reprdict = {"last_login":o.last_login,
            "user_created_date":o.user_created_date,
            "email":o.email,
            "phone":o.phone,
            "user_access":o.user_access,
            "longitude":o.longitude,
            "latitude":o.latitude,
            "gender":o.gender,
            "fb_id":o.fb_id,
            "wb_id":o.wb_id,
            "primary_sns":o.longitude,
            "name":o.name,
            "user_id":o.user_id,
            "username":o.username
            }
        return reprdict
    if isinstance(o, models.activities):
        reprdict = {"activity_id":o.activity_id,
            "creator":o.creator,
            "access":o.access,
            "type":o.type,
            "status":o.status,
            "activity_created_date":o.activity_created_date,
            "description":o.description,
            "longitude":o.longitude,
            "latitude":o.latitude,
            "destination":o.destination,
            "keyword":o.keyword,
            "start_date":o.start_date,
            "end_date":o.end_date,
            "num_of_participants":o.num_of_participants
            }
        return reprdict
    if isinstance(o, models.push_notification):
        reprdict = {"user_id":o.user_id,
            "device_id":o.device_id,
            "push_token":o.push_token,
            "config":o.config,
            }
        return reprdict
    if isinstance(o, models.comments):
        reprdict = {"contents":o.contents,
            "creator_id":o.creator_id,
            "activity_id":o.activity_id,
            "created_date":o.created_date,
            "comment_id":o.comment_id
            }
        return reprdict
    return o.isoformat() if hasattr(o, 'isoformat') else o
