class MemberNotFound(Exception):
    def __init__(self, message='The ID you sent does not match any of the CEMIT members registered'):
        # Call the base class constructor with the parameters it needs
        super(MemberNotFound, self).__init__(message)

class MemberExists(Exception):
    def __init__(self, message="The CEMIT member ID you sent is already validated"):
        # Call the base class constructor with the parameters it needs
        super(MemberExists, self).__init__(message)