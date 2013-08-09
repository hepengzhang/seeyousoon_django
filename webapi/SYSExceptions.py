class SYSError(Exception):
    def __init__(self, msg):
        self.msg = msg

class invalidAccess(SYSError):
    pass
