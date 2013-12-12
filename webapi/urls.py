from django.conf.urls import patterns, url, include

from webapi.Views import ActivityViews, AuthViews, PeopleViews, RootViews

def SYSInclude(controller):
    return include('webapi.Controllers.'+controller+'.urls')

urlpatterns = patterns('',
    url(r'^$', RootViews.RootView.as_view(), name='root'),
    url(r'^docs/', include('rest_framework_swagger.urls'), name='docs'),
    
    url(r'^auth/login$', AuthViews.LoginView.as_view()),
    url(r'^auth/register$', AuthViews.SignupView.as_view()),
    url(r'^auth/checkusername$', AuthViews.CheckUsernameView.as_view()),
    
    url(r'^people/(?P<user_id>\d+)$', PeopleViews.UserView.as_view()),
    url(r'^people/(?P<user_id>\d+)/friends/(?P<scope>(requests|friends|all))$', PeopleViews.FriendsView.as_view()),
    url(r'^people/(?P<user_id>\d+)/activities$', PeopleViews.ActivitiesView.as_view()),
    
    url(r'^activities/(?P<activity_id>\d+)$', ActivityViews.ActivitiesView.as_view()),
    
)
