from datetime import datetime
from google.oauth2.credentials import Credentials

class User:
    """ Each user who added iago will be represented by an immutable object of user, this object is used to link user to tasks and for reporting purpose.
    No selections or sensitive data of the user is collected in the user object
    The email address is the only user identification
    user is not removed once created """

    def __init__(self, id, user_email, chat_space=None):
        self._id = id
        self._email = user_email
        self._gid = None
        self._space = chat_space
        self._creation_date = datetime.now()
        self._task = None
        self._token = None

    @property
    def id(self):
        return self._id

    @property
    def email(self):
        return self._email

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
    def task(self):
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

