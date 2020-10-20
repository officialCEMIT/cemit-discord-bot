import urllib3
from decouple import config
from .errors import MemberExists, MemberNotFound

http = urllib3.PoolManager()
base_url = config('CORE_URL') 

class CEMIT:
    def __init__(self):
        self

    def validate_member(self, user_id):
        # TODO: VALIDATE MEMBER ID FROM CEMIT CORE API
        print('VALIDATE:', user_id)
        
        if user_id == '69':
            return {}
        elif user_id == '911':
            raise MemberExists
        else:
            raise MemberNotFound

