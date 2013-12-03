from django.conf.urls import patterns,url
import ActivityViews

urlpatterns = patterns('ActivityControllers',
    url(r'^$',ActivityViews.AcitivityView.as_view(), name='Activity'),
    url(r'^/comment$', ActivityViews.ActivityComments.as_view(), name='Activity_comments'),
)