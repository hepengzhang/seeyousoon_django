from django.conf.urls import patterns, url, include
from webapi import apis

from webapi.Controllers import RootViews
urlpatterns = patterns('',
    url(r'^$', RootViews.RootView.as_view(), name='root'),
    url(r'^auth/', include('webapi.Controllers.AuthControllers.urls'), name='auth'),
    url(r'^activity$', apis.activity, name='avtivity'),
    url(r'^activity/comments$',apis.comments, name='comments'),
#    url(r'^activity/(?P<actv_id>d+)$',apis.actvinfo, name='activity_info'),
    url(r'^friends$',apis.friends,name='friends'),
    url(r'^user/search$',apis.searchUser,name='searchUser'),
    url(r'^user/activities$',apis.userActivities,name='userActivities'),
    url(r'^user/location$',apis.userLocation,name='userLocation'),
    url(r'^user/notification$',apis.userNotification,name='userNotification')
)
