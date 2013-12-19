from webapi import customField
from django.db import models


class user_info(models.Model):
    user_id = customField.PositiveBigAutoField(primary_key=True)
    username = models.CharField(max_length=32,unique=True)
    email = models.EmailField(max_length=254)
    last_login = models.DateTimeField(auto_now=True)
    user_access = models.PositiveSmallIntegerField(default=0)
    longitude = models.DecimalField(max_digits=12, decimal_places=8,default=0)
    latitude = models.DecimalField(max_digits=12, decimal_places=8,default=0)
    gender = models.PositiveSmallIntegerField(default=0)
    fb_id = customField.PositiveBigIntegerField(db_index=True,default=0)
    wb_id = customField.PositiveBigIntegerField(db_index=True,default=0)
    primary_sns = models.PositiveSmallIntegerField(default=0)
    name = models.CharField(max_length=90,blank=True)
    user_created_date = models.DateTimeField(auto_now_add=True)
    phone = models.CharField(max_length=16,blank=True)
    
    def natural_key(self):
        reprdict = {"last_login":self.last_login,
                "user_created_date":self.user_created_date,
                "email":self.email,
                "phone":self.phone,
                "user_access":self.user_access,
                "longitude":self.longitude,
                "latitude":self.latitude,
                "gender":self.gender,
                "fb_id":self.fb_id,
                "wb_id":self.wb_id,
                "primary_sns":self.longitude,
                "name":self.name,
                "user_id":self.user_id,
                "username":self.username
                }
        return reprdict
    
    def __repr__(self):
        reprdict = {"last_login":self.last_login,
                "user_created_date":self.user_created_date,
                "email":self.email,
                "phone":self.phone,
                "user_access":self.user_access,
                "longitude":self.longitude,
                "latitude":self.latitude,
                "gender":self.gender,
                "fb_id":self.fb_id,
                "wb_id":self.wb_id,
                "primary_sns":self.longitude,
                "name":self.name,
                "user_id":self.user_id,
                "username":self.username
                }
        return unicode(reprdict)
    
class user_auth(models.Model):
    username = models.CharField(max_length=32,unique=True)
    password = models.CharField(max_length=32)
    access_token = models.CharField(max_length=27)
    user = customField.BigForeignKey(user_info, primary_key=True,on_delete=models.CASCADE)


#===============================================================================
# full text search - how to deal with?
#===============================================================================
class user_search(models.Model):
    username = models.CharField(max_length=32)
    user = customField.BigForeignKey(user_info, primary_key=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=32,blank=True)
    
class push_notification(models.Model):
    user = customField.BigForeignKey(user_info, primary_key=True, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=32)
    push_token = models.CharField(max_length=64)
    config = models.PositiveSmallIntegerField(default=0)
    friend_requests = models.PositiveIntegerField(default=0)
    activities = models.PositiveIntegerField(default=0)
    
class friends(models.Model):
    status = models.PositiveSmallIntegerField(default=0)
    user = customField.BigForeignKey(user_info,related_name="%(class)s_related_self", on_delete=models.CASCADE)
    friend = customField.BigForeignKey(user_info,related_name="%(class)s_related_friend", on_delete=models.CASCADE)
    together_time = models.IntegerField(default=0)
    entry_id = customField.PositiveBigAutoField(primary_key=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ("user","friend");
        
class activities(models.Model):
    activity_id = customField.PositiveBigAutoField(primary_key=True)
    creator = customField.BigForeignKey(user_info, on_delete=models.CASCADE)
    access = models.PositiveSmallIntegerField(default=0)
    type = models.PositiveSmallIntegerField(default=0)
    status = models.PositiveSmallIntegerField(default=0)
    activity_created_date = models.DateTimeField(auto_now_add=True, db_index=True)
    description = models.CharField(max_length=255,blank=True)
    longitude = models.DecimalField(max_digits=12, decimal_places=8, default=0)
    latitude = models.DecimalField(max_digits=12, decimal_places=8, default=0)
    destination = models.CharField(max_length=128, blank=True)
    keyword = models.CharField(max_length=32)
    start_date = models.DateTimeField(blank=True,null=True)
    end_date = models.DateTimeField(blank=True,null=True)
    num_of_participants = models.IntegerField(default=0)
    num_of_comments = models.IntegerField(default=0)
    
    def __repr__(self):
        reprdict = {"activity_id":unicode(self.activity_id),
                "creator":repr(self.creator),
                "access":unicode(self.access),
                "type":unicode(self.type),
                "status":unicode(self.status),
                "activity_created_date":unicode(self.activity_created_date),
                "description":self.description,
                "longitude":unicode(self.longitude),
                "latitude":unicode(self.latitude),
                "destination":self.destination,
                "keyword":self.keyword,
                "start_date":unicode(self.start_date),
                "end_date":unicode(self.end_date)
                }
        return unicode(reprdict)
    
    class Meta:
        index_together = [
                          ["longitude", "latitude"],
                          ]

class comments(models.Model):
    comment_id = customField.PositiveBigAutoField(primary_key=True)
    contents = models.CharField(max_length=254)
    creator = customField.BigForeignKey(user_info, on_delete=models.CASCADE)
    activity = customField.BigForeignKey(activities, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)

class participants(models.Model):
    activity = customField.BigForeignKey(activities, on_delete=models.CASCADE)
    participant = customField.BigForeignKey(user_info, on_delete=models.CASCADE)
    status = models.PositiveSmallIntegerField(default=0)
    distance = models.PositiveIntegerField(default=0)
    longitude = models.DecimalField(max_digits=12, decimal_places=8,default=0)
    latitude = models.DecimalField(max_digits=12, decimal_places=8,default=0)
    entry_id = customField.PositiveBigAutoField(primary_key=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __repr__(self):
        return {"activity":self.activity_id,
                "participant":self.participant_id}
    
    class Meta:
        unique_together = ("activity","participant")

    