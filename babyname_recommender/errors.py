
class Error(Exception):
    """Base class for other exceptions"""
    pass

class ExitApp(Error):
    pass

class IPAnotAligned(Error):
    pass

class ExitFunction(Error):
    pass


#change table name ratinglists --> users_ratinglists
#version --> version_ipa_extended, version_ipa_simple, version_letters_simple

