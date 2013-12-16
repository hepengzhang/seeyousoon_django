from webapi import models
from rest_framework import serializers

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
        
class ParticipantSerializer(DynamicFieldsModelSerializer):
    participant = UserSerializer()
    class Meta:
        model = models.participants
