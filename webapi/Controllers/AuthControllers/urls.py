from django.conf.urls import patterns,url
import AuthViews

urlpatterns = patterns('AuthControllers',
    url(r'^/login$',AuthViews.LoginView.as_view(), name='Login'),
    url(r'^/register$', AuthViews.SignupView.as_view(), name='Sign_up'),
    url(r'^/checkUsername', AuthViews.CheckUsernameView.as_view(), name='Check_username'),
)