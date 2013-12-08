from webapi import models
from rest_framework import authentication, exceptions, HTTP_HEADER_ENCODING

def get_authorization_header(request):
    """
    Return request's 'Authorization:' header, as a bytestring.

    Hide some test client ickyness where the header can be unicode.
    """
    auth = request.META.get('HTTP_AUTHORIZATION', b'')
    if type(auth) == type(''):
        # Work around django test client oddness
        auth = auth.encode(HTTP_HEADER_ENCODING)
    return auth

class SYSAPIAuthentication(authentication.BaseAuthentication):
    
    model = models.user_auth
    
    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        
        if not auth:
            return None

        if len(auth) < 2:
            msg = 'Invalid token header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Invalid token header. Token string should not contain spaces.'
            raise exceptions.AuthenticationFailed(msg)
        return self.authenticate_credentials(auth[0],auth[1])
    
    def authenticate_credentials(self, userID, token):
        
        try:
            auth = models.user_auth.objects.get(user_id=userID, access_token=token)
        except models.user_auth.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid userID/token pair')

        return (auth.user, token)
        