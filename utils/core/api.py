from decouple import config
from .errors import MemberExists, MemberNotFound
import requests

base_url = config('CORE_URL') 

class CEMIT:
    def __init__(self):
        self

    def validate_member(self, user_id, name):
        r = requests.post(
            base_url + 'validate/', 
            data={
                "id": str(user_id),
                "name": str(name)
            }
        )
        data = r.json()
        if data.get("id"):
            return data
        elif data.get("message") == "Already Validated":
            raise MemberExists
        elif r.status_code == 404:
            raise MemberNotFound

