
class Error(Exception):
    """Base class for other exceptions"""
    pass

class ExitApp(Error):
    pass

class IPAnotAligned(Error):
    pass

class ExitFunction(Error):
    pass

class RatingsOnlyOneKind(Error):
    pass


