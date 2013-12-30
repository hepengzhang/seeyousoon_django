from django.conf.urls import patterns, url, include

from webapi.Views import ActivityViews, AuthViews, PeopleViews, SearchViews, TimelineViews

def SYSInclude(controller):
    return include('webapi.Controllers.'+controller+'.urls')

urlpatterns = patterns('',
    
    url(r'^docs/', include('rest_framework_swagger.urls')),
    url(r'^auth/login$', AuthViews.LoginView.as_view()),
    url(r'^auth/register$', AuthViews.SignupView.as_view()),
    url(r'^auth/checkusername$', AuthViews.CheckUsernameView.as_view()),

    url(r'^people/(?P<user_id>\d+)$', PeopleViews.UserView.as_view()),
    url(r'^people/(?P<user_id>\d+)/friends/(?P<scope>(requests|friends|all))$', PeopleViews.FriendsView.as_view()),
    url(r'^people/(?P<user_id>\d+)/friends$', PeopleViews.AddFriendsView.as_view()),
    url(r'^people/(?P<user_id>\d+)/friends/(?P<friend_id>\d+)$', PeopleViews.FriendView.as_view()),
    url(r'^people/(?P<user_id>\d+)/timeline$', PeopleViews.TimelineView.as_view()),

    url(r'^people/(?P<user_id>\d+)/activities$', PeopleViews.ActivitiesView.as_view()),
    
    url(r'^activities/(?P<activity_id>\d+)$', ActivityViews.ActivitiesView.as_view()),
    url(r'^activities/(?P<activity_id>\d+)/comments$', ActivityViews.ActivityCommentsView.as_view()),
    url(r'^activities/(?P<activity_id>\d+)/comments/(?P<comment_id>\d+)$', ActivityViews.ActivityCommentView.as_view()),
    
    url(r'^activities/(?P<activity_id>\d+)/participants$', ActivityViews.ParticipantsView.as_view()),
    url(r'^activities/(?P<activity_id>\d+)/participants/(?P<entry_id>\d+)$', ActivityViews.ParticipantView.as_view()),

    url(r'^search/people$', SearchViews.SearchPeopleView.as_view()),

    url(r'^timeline$', TimelineViews.TimelineView.as_view()),

)
