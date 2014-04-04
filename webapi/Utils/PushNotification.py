import pyapns
import socket
from webapi import models

def SYSNotify(user_id, message):
    query = models.push_notification.objects.filter(user_id=user_id)
    try:
        if query.count() == 1:
            pushN = models.push_notification.objects.get(user_id=user_id)
            badge =pushN.friend_requests + pushN.activities
            pyapns.notify("SeeYouSoon", pushN.push_token, {'aps':{'alert':message,'badge':badge,'sound':'default'}})
        pass
    except socket.error as e:
        print "Notify error:", e