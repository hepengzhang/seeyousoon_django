from webapi import SYSMessages

class SYSError(Exception):
    
    def __init__(self, msg):
        self.msg = msg
    
    def __repr__(self, *args, **kwargs):
        return self.msg
    
    def __str__(self, *args, **kwargs):
        return self.msg

class invalidAccess(SYSError):
    def __init__(self, msg=SYSMessages.SYSMESSAGE_ERROR_INVALIDACCESS):
        super(invalidAccess, self).__init__(msg)
    pass

class unknownRoute(SYSError):
    def __init__(self, msg=SYSMessages.SYSMESSAGE_ERROR_UNKNOWNROUTE):
        super(unknownRoute, self).__init__(msg)
    pass