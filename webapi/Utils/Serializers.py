from webapi import models
from rest_framework import serializers

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

class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)
                
class UserSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = models.user_info
        
class ActivitySerializer(DynamicFieldsModelSerializer):
    creator = UserSerializer()
    class Meta:
        model = models.activities

class FriendsSerializer(DynamicFieldsModelSerializer):
    friend = UserSerializer()
    class Meta:
        model = models.friends
        fields = ("friend", "status", "together_time", "updated_at")

class CommentSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = models.comments
