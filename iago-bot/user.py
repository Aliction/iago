from datetime import datetime
from google.oauth2.credentials import Credentials
from enum import IntEnum

class Platform(IntEnum):
    GOOGLE = 0
    SLACK = 1

class User:
    """ Each user who added iago will be represented by an immutable object of user, this object is used to link user to tasks and for reporting purpose.
    No selections or sensitive data of the user is collected in the user object
    The email address is the only user identification
    user is not removed once created """

    def __init__(self, id, user_key, platform, chat_room=None):
        print("USER_KEY: ", user_key)
        self._emails = []
        if platform == Platform.GOOGLE:
            print("User Platform GOOGLE: ", platform)
            self._emails.append(user_key) #We use Google email as User identifier for Google (different from gid which is used for other authentication later)
            self._key = user_key
        elif platform == Platform.SLACK:
            print("User Platform SLACK: ", platform)
            self._sid = user_key #We use Slack User ID as User Identifier (We can collect user email and name later)
            self._key = self._sid
        print("User Platform: ", platform)
        self._id = id # Iago generated ID
        self._platform = platform
        self._gid = None # Google ID
#        self._sid = None # Slack ID
        self._chat_room = chat_room
        self._creation_date = datetime.now()
        self._task = None
        self._token = None

    @property
    def id(self):
        return self._id

    @property
    def key(self):
        return self._key

    @property
    def platform(self):
        return self._platform
    
    @property
    def emails(self):
        return self._emails

    def add_email(self, user_email):
#        if self._platform == Platform.SLACK :
        self._emails.append(user_email)
        return True

    def check_email(email):
        for e in self._emails:
            if e == email.strip():
                return True

    @property
    def date(self):
        format = "%d-%b-%Y %HH:%MM"
        return self._creation_date.strftime(format)

    @property
    def gid(self):
        return self._gid

    @gid.setter
    def gid(self, gid):
        self._gid = gid

    @property
    def sid(self):
        return self._sid

    @property
    def chat_room(self):
        return self._chat_room

    @property
    def task(self):
        if self._task is not None:
            if int(self._task.status) > 2 : # EXPIRED or FINISHED (COMPLETED, PARTIAL, etc..)
                self._task = None
        return self._task

    @task.setter
    def task(self, task):
        self._task = task

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, token):
        self._token = token
        g_creds = Credentials(self._token)
        self._credentials = g_creds
 
    @token.deleter
    def token(self):
        del self._credentials
        self._token = None
    
    @property
    def g_creds(self):
        return self._credentials

