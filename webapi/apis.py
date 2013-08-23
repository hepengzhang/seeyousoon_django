import simplejson as json
from datetime import datetime
from django.core.signing import Signer
import pyapns
from webapi import models
from django.http.response import HttpResponse,HttpResponseBadRequest
from webapi import SYSEncoder, SYSExceptions, SYSMessages

def root(request):
    try:
        verify_access(request)
    except SYSExceptions.SYSError as e:
        return error(-1, e.msg)
    paraDict = json.loads(request.body)
#     a = models.activities.objects.all()
#     a = [b for b in a]
    return jsonResponse(paraDict)

###aux function###
def jsonResponse(result):
    return HttpResponse(json.dumps(result, default=SYSEncoder.encode_models, indent=2))

def error(code, message):
    return HttpResponse(json.dumps({'return_code':code, 'error':message}, indent=4))

def success(code, message):
    return HttpResponse(json.dumps({'return_code':code, 'message':message}, indent=4))

def verify_access(request):
    userID = None
    access_token = None
    try:
        if request.method == 'GET' or request.method == 'DELETE':
            userID = request.GET['user_id']
            access_token = request.GET['access_token']
        elif request.method == 'POST':
            paraDict = json.loads(request.body)
            userID = paraDict['user_id']
            access_token = paraDict['access_token']
        elif request.method == "DELETE":
            paraDict = dict(request.body)
            userID = paraDict['user_id']
            
    except Exception:
        raise SYSExceptions.invalidAccess(SYSMessages.SYSMESSAGE_ERROR_INVALIDACCESS+str(request.body))
    
    count = models.user_auth.objects.filter(user_id=userID,access_token=access_token).count()
    if count != 1: raise SYSExceptions.invalidAccess(SYSMessages.SYSMESSAGE_ERROR_INVALIDACCESS)
    
def generate_accessToken(userID):
    signer = Signer()
    return signer.sign(str(userID)+str(datetime.now()))[-27:]

def SYSNotify(user_id, message):
    query = models.push_notification.objects.filter(user_id=user_id)
    if query.count() == 1:
        pushN = models.push_notification.objects.get(user_id=user_id)
        badge =pushN.friend_requests + pushN.activities
        pyapns.notify("SeeYouSoon", pushN.push_token, {'aps':{'alert':message,'badge':badge,'sound':'default'}})
    pass

#real api starts here
def login(request):
    """method login"""
    if request.method =='POST':
        try:
            paraDict = json.loads(request.body)

            info = None
            auth = None
            if 'fb_id' in paraDict:
                info = models.user_info.objects.filter(fb_id=paraDict['fb_id'])
                if len(info) != 1: return error(-1,u"Facebook id "+paraDict['fb_id']+" not linked.")
                info = info[0]
            elif 'wb_id' in paraDict:
                info = models.user_info.objects.filter(fb_id=paraDict['wb_id'])
                if len(info) != 1: return error(-1,u"Weibo id "+paraDict['wb_id']+" not linked.")
                info = info[0]
            elif 'username' in paraDict:
                auth = models.user_auth.objects.select_related().filter(username=paraDict['username'])
                if len(auth) != 1: return error(-1,u"Username "+paraDict['username']+" does not exist.")
                auth = auth[0] 
                if auth.password != paraDict['password']: return error(-1,"Wrong password")
                info = auth.user
            
            ##update access_token
            auth.access_token = generate_accessToken(info.user_id)
            auth.save()
            
            #update user location
            if 'latitude' in paraDict:
                info.latitude = paraDict['latitude']
                info.longitude = paraDict['longitude']
           
            info.save()
           
            result = {"user_info":info,
                      "access_token":auth.access_token,
                      "return_code":1}
            
            return jsonResponse(result)
        except Exception as e:
            return error(-1,str(type(e).__name__+str(e)))
    else:
        return error(-1,u'not in api')

def register(request):
    if request.method == 'POST':
        try:
            paraDict = json.loads(request.body)
            exist = models.user_auth.objects.filter(username=paraDict['username']).exists()
            if exist:
                return error(-1,"Username exists.")
            
            ### user_info
            info = models.user_info(email=paraDict['email'],
                             username=paraDict['username'])
            if 'phone' in paraDict: info.phone=paraDict['phone']
            if 'name' in paraDict: info.name=paraDict['name']
            if 'primary_sns' in paraDict: info.primary_sns=paraDict['primary_sns']
            if 'wb' in paraDict: info.wb_id=paraDict['wb']
            if 'fb' in paraDict: info.fb_id=paraDict['fb']
            info.save()
            
            ### user_auth
            token = generate_accessToken(paraDict['username'])
            auth = models.user_auth(username=paraDict['username'],
                             password=paraDict['password'],
                             access_token=token,
                             user=info)
            auth.save()
            
            ### user search
            search = models.user_search(username=auth.username,
                                 user=info)
            if 'name' in paraDict: search.name=paraDict['name']
            search.save()
            
            ### retrieve
            result = {"user_info":info,
                      "access_token":auth.access_token,
                      "return_code":1}
            
            return jsonResponse(result)
        except Exception as e:
            return error(-1, str(type(e).__name__+str(e)+"\n"+request.body))
    else:
        return error(-1,u'not in api')
    
def checkUsername(request):
    """"check if username is available"""
    if request.method == 'GET':
        try:
            user = models.user_auth.objects.filter(username=request.GET['username'])
            r = len(user)
            return error(-1,"Username exists") if r>0 else success(1,"Username available")
        except Exception as e:
            return error(-1,str(type(e).__name__+str(e)))
    else:
        return error(-1,u'not in api')
    
def activity(request):
    try:
        verify_access(request)
    except SYSExceptions.SYSError as e:
        return error(-1, e.msg)
    
    if request.method == 'GET':
        try:
            result = None;
            if request.GET['type']=='nearby':#return all nearby public activities
                return error(-1, 'web api not implemented')
            if request.GET['type']=='friends':#return all friends's visible activities
                uid = request.GET['user_id']
                dtformat = '%Y%m%d%H%M%S'
                timeMin = datetime.strptime(request.GET['min_date'], dtformat)
                timeMax = datetime.strptime(request.GET['max_date'], dtformat)
                
                user_self = models.user_info.objects.get(pk=uid)
                friendsList = models.friends.objects.filter(user=user_self, status__gt=0).values_list('friend_id',flat=True)
                friendsList = [uid] + list(friendsList)
                queryset = models.activities.objects.select_related().filter(creator__in=friendsList,
                                                              activity_created_date__range=(timeMin,timeMax),
                                                              access__lt=2)
                activities = queryset.order_by('-activity_created_date')[:50]
                activities = [a for a in activities]
                result = {"activities":activities,
                          "return_code":1}
                return jsonResponse(result)
        except Exception as e:
            return error(-1, str(type(e).__name__+str(e)))
    elif request.method == "POST":
        try:
            paraDict = json.loads(request.body)
            activity = models.activities(keyword=paraDict['keyword'], creator_id=paraDict['user_id'],access=paraDict['access'])
            
            #add to database
            if 'type' in paraDict: activity.type=paraDict['type']
            if 'status' in paraDict: activity.status=paraDict['status']
            if 'description' in paraDict: activity.description=paraDict['description']
            if 'start_date' in paraDict: activity.start_date=paraDict['start_date']
            if 'end_date' in paraDict: activity.end_date=paraDict['end_date']
            if 'latitude' in paraDict: activity.latitude=paraDict['latitude']
            if 'longitude' in paraDict: activity.longitude=paraDict['longitude']
            if 'destination' in paraDict: activity.destination=paraDict['destination']

            activity.save()
            
            activity_id = activity.activity_id
            if paraDict['access']=='2':
                #get the invited friends list
                friends_list = paraDict['invited_list']
                for user_id in friends_list:
                    models.participants.objects.create(activity=activity_id,participant=user_id)
                    SYSNotify(user_id, u"You are invited to a new event")
                models.participants.objects.create(activity=activity_id,participant=paraDict['user_id'],status=1)
            
            result = {"return_code":1,
                      "activity":activity}
            return jsonResponse(result)
        except Exception as e:
            return error(-1, str(type(e).__name__+str(e)))
    else:
        return error(-1, SYSMessages.SYSMESSAGE_ERROR_NOTIMPLEMENTED)

def comments(request):
    try:
        verify_access(request)
    except SYSExceptions.SYSError as e:
        return error(-1, e.msg)
    
    if request.method == 'GET':
        try:
            offset = int(request.GET['offset'])
            activity_id = request.GET['activity_id']
            results = models.comments.objects.filter(activity_id=activity_id)
            results = results.order_by('-created_date')[offset:offset+50]
            results = [a for a in results]
            
            results = {"return_code":1,
                       "comments":results,
                       "offset":offset}
            
            return jsonResponse(results)
        except Exception as e:
            return error(-1,str(type(e).__name__+str(e)))
        
    elif request.method == 'POST':
        try:
            paraDict = json.loads(request.body)
            user_id = paraDict['user_id']
            contents = paraDict['contents']
            activity_id = paraDict['activity_id']
            
            models.comments.objects.create(creator_id=user_id, activity_id=activity_id,contents=contents)
            activity = models.activities.objects.get(pk=activity_id)
            activity.num_of_comments += 1
            activity.save()
            
            result = {"return_code":1}
            return jsonResponse(result)
        except Exception as e:
            return error(-1, str(type(e).__name__+str(e)))
    elif request.method == 'DELETE':
        try:
            user_id = request.GET['user_id']
            comment_id = request.GET['comment_id']
            activity_id = request.GET['activity_id']
            
            models.comments.objects.filter(creator_id=user_id, comment_id=comment_id, activity_id=activity_id).delete()
            activity = models.activities.objects.get(pk=activity_id)
            activity.num_of_comments -= 1
            activity.save()
            
            result = {"return_code":1}
            return jsonResponse(result)
        except Exception as e:
            return error(-1, str(type(e).__name__+str(e)))
                 
            
def friends(request):
    try:
        verify_access(request)
    except SYSExceptions.SYSError as e:
        return error(-1, e.msg)
    
    if request.method == 'GET':
        #return user's all friends given user's
        #or all request sent to this user.
        try:
            uid = request.GET['user_id']
            get_type = request.GET['type']
            results = None
            if get_type == 'friends':#return all friends
                queryset = models.friends.objects.select_related().filter(user_id=uid,status__gt=0)
                results = [friends.friend for friends in queryset]
                
            if get_type == 'request':#return request sent to this user
                queryset = models.friends.objects.select_related().filter(friend_id=uid,status=0)
                results = [friends.user for friends in queryset]
                models.push_notification.objects.filter(user_id=uid).update(friend_requests=0)
                
            results = {"return_code":1,
                      "type":get_type,
                      "results":results}
            return jsonResponse(results)
        except Exception as e:
            return error(-1,str(type(e).__name__+str(e)))

    elif request.method == 'POST':#respond to friend request and send friend request
        try:
            paraDict = json.loads(request.body)
            user_id = paraDict['user_id']
            requested_user = None;
            
            #get friend user_id
            r = models.user_auth.objects.filter(username=paraDict['friend_username'])
            if len(r) < 1: return error(-1,u"Username doesn't exist.")
            requested_user = r[0]
            if str(requested_user.user_id)==str(user_id): return error(-1,u"You're sending request to yourself.")
            #initial status should be 0
            status = 0
            #check on self
            count = models.friends.objects.filter(user_id=user_id, friend_id=requested_user.user_id).count()
            if count > 0: 
                return success(1, SYSMessages.SYSMESSAGE_SUCCESS_FRIENDREQUEST)
            #check on friend
            count = models.friends.objects.filter(user_id=requested_user.user_id, friend_id=user_id).count()
            if count > 0: status = 1
            
            #add to database
            models.friends.objects.create(user_id=user_id,friend_id=requested_user.user_id,status=status)
            
            #update friends if necessary
            if status == 1:
                models.friends.objects.filter(user_id=requested_user.user_id,friend_id=user_id).update(status=1)
                
            #send notification
            pushN = models.push_notification.objects.filter(user_id=user_id)
            if pushN.count() == 1:
                models.push_notification.objects.get(user_id=user_id)
                pushN.friend_requests += 1
                pushN.save()
                if status == 0 :
                    SYSNotify(requested_user.user_id, u"You have a new friend request.")
                else :
                    SYSNotify(requested_user.user_id, u"Your friend request has been accepted.")
            
            return success(1, SYSMessages.SYSMESSAGE_SUCCESS_FRIENDREQUEST)
        except Exception as e:
            return error(-1,str(type(e).__name__+str(e)))
    
    elif request.method == 'DELETE':
        try:
            uid = request.GET['user_id']
            friend_id = request.GET['friend_id']
            
            models.friends.objects.filter(user_id=user_id, friend_id=friend_id).delete()
            models.friends.objects.filter(friend_id=user_id, user_id=friend_id).delete()
            
            return success(1,"success")
        except Exception as e:
            return HttpResponseBadRequest(str(type(e).__name__+str(e)))
    
    else:
        return HttpResponseBadRequest(request.method+u' request method not in api') 


def searchUser(request):
    if request.method == 'GET':#return search result
        try:
            keywords = request.GET['keyword'].split()
            keywords = [u"+"+k+u"*" for k in keywords]
            keywords = u" ".join(keywords)
            query = models.user_search.objects.raw('''SELECT * FROM `webapi_user_search` WHERE MATCH (`username`,`name`) AGAINST (%s IN BOOLEAN MODE) LIMIT 10''', [keywords])
            users_ids = [q.user_id for q in query]
            users = models.user_info.objects.filter(user_id__in=users_ids)
            users = [u for u in users]
            result = {"return_code":1,
                      "results":users}
            return jsonResponse(result)
        except Exception as e:
            return error(-1,str(type(e).__name__+str(e)))
    else:
        return HttpResponseBadRequest(request.method+u' request method not in api') 

def userActivities(request):
    try:
        verify_access(request)
    except SYSExceptions.SYSError as e:
        return error(-1, e.msg)
    
    if request.method == 'GET':#return search result
        try:
            uid = request.GET['uid']
            dtformat = '%Y%m%d%H%M%S'
            timeMin = datetime.strptime(request.GET['min_date'], dtformat)
            timeMax = datetime.strptime(request.GET['max_date'], dtformat)
            
            queryset = models.activities.objects.select_related().filter(creator_id=uid, activity_created_date__range=(timeMin,timeMax),access__lt=2)
            activities = queryset.order_by('-activity_created_date')[:50]
            activities = [a for a in activities]
            result = {"activities":activities,
                      "return_code":1}
            return jsonResponse(result)
            
        except Exception as e:
            return error(-1,str(type(e).__name__+str(e)))
    else:
        return HttpResponseBadRequest(request.method+u' request method not in api')

def userLocation(request):
    try:
        verify_access(request)
    except SYSExceptions.SYSError as e:
        return error(-1, e.msg)
    
    if request.method == 'POST':#return search result
        try:
            paraDict = json.loads(request.body)
            user_id = paraDict['user_id']
            longitude = paraDict['longitude']
            latitude = paraDict['latitude']
            models.user_info.objects.filter(user_id=user_id).update(longitude=longitude, latitude=latitude)
            return success(1, SYSMessages.SYSMESSAGE_SUCCESS_UPDATELOCATION)
        except Exception as e:
            return error(-1,str(type(e).__name__+str(e)))
    else:
        return error(-1, SYSMessages.SYSMESSAGE_ERROR_NOTIMPLEMENTED)

def userNotification(request):
    try:
        verify_access(request)
    except SYSExceptions.SYSError as e:
        return error(-1, e.msg)
    
    if request.method == 'POST':#register user's device for APNS
        try:
            paraDict = json.loads(request.body)
            user_id = paraDict['user_id']
            device_id = paraDict['device_id']
            push_token = paraDict['push_token']
            config = paraDict['config']
            
            query = models.push_notification.objects.filter(user_id=user_id)
            count = query.count()
            push_notification = None
            if count == 0: 
                push_notification = models.push_notification.objects.create(user_id=user_id,device_id=device_id, push_token=push_token, config=config)
            else:
                push_notification = models.push_notification.objects.get(user_id=user_id)
                query.update(device_id=device_id, push_token=push_token, config=config)
            
            result = {"return_code":1, 
                      "push_info":push_notification}
            return jsonResponse(result);
        except Exception as e:
            return error(-1,str(type(e).__name__+str(e)))
    else:
        return HttpResponseBadRequest(request.method+u' request method not in api')


