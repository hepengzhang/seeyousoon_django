from django.conf.urls import patterns, url, include
from webapi import apis

def SYSInclude(controller):
    return include('webapi.Controllers.'+controller+'.urls')

from webapi.Controllers import RootViews
urlpatterns = patterns('',
    url(r'^$', RootViews.RootView.as_view(), name='root'),
    url(r'^auth', SYSInclude('AuthControllers'), name='auth'),
    url(r'^activity', SYSInclude('ActivityControllers'), name='avtivity'),
#    url(r'^activity/(?P<actv_id>d+)$',apis.actvinfo, name='activity_info'),
    url(r'^friends$',apis.friends,name='friends'),
    url(r'^user/search$',apis.searchUser,name='searchUser'),
    url(r'^user/activities$',apis.userActivities,name='userActivities'),
    url(r'^user/location$',apis.userLocation,name='userLocation'),
    url(r'^user/notification$',apis.userNotification,name='userNotification')
)
