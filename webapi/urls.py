from django.conf.urls import patterns, url
from webapi import apis

urlpatterns = patterns('',
    url(r'^$', apis.root, name='root'),
    url(r'^login$', apis.login, name='login'),
    url(r'^register$', apis.register, name='register'),
    url(r'^register/checkUsername$', apis.checkUsername, name='checkUsername'),
    url(r'^activity$', apis.activity, name='avtivity'),
    url(r'^activity/comments$',apis.comments, name='comments'),
#    url(r'^activity/(?P<actv_id>d+)$',apis.actvinfo, name='activity_info'),
    url(r'^friends$',apis.friends,name='friends'),
    url(r'^user/search$',apis.searchUser,name='searchUser'),
    url(r'^user/activities$',apis.userActivities,name='userActivities'),
    url(r'^user/location$',apis.userLocation,name='userLocation'),
    url(r'^user/notification$',apis.userNotification,name='userNotification')
)
