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
                
    def from_native(self, data, files):
        model = super(DynamicFieldsModelSerializer, self).from_native(data, files)
        if model == None: model = self.Meta.model()
        if 'view' in self.context: 
            pre_valid_model = getattr(self.context['view'], "pre_valid_model", None)
            if callable(pre_valid_model):
                self.context['view'].pre_valid_model(self, model)
        return model
                
class UserSerializer(DynamicFieldsModelSerializer):
    
    class Meta:
        model = models.user_info
        read_only_fields = ('user_id', 'username', 'last_login', 'user_created_date')
        
class ActivitySerializer(DynamicFieldsModelSerializer):
    creator = UserSerializer(read_only = True)
    
    class Meta:
        model = models.activities
        read_only_fields = ('activity_id', 'activity_created_date', 'num_of_participants', 'num_of_comments')

class FriendsSerializer(DynamicFieldsModelSerializer):
    friend = UserSerializer()
    class Meta:
        model = models.friends
        fields = ("friend", "status", "together_time", "updated_at")

class CommentSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = models.comments
        
class ParticipantSerializer(DynamicFieldsModelSerializer):
    participant = UserSerializer(read_only=True)
    class Meta:
        model = models.participants
        read_only_fields = ('updated_at', 'activity',)

class TimelineSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = models.user_timeline