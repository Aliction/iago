from datetime import datetime
from enum import Enum, IntEnum

class Context(Enum):
    """ This is an enumeration class for available contexts during task life cycle"""
    GENERAL = 0     # context for the bot to do general conversation, not used
    TASK = 1        # context for discussing about the task (Default)
    SUBJECT = 2     # context about collecting mail subject
    MESSAGE = 3     # context about collecting mail message (body)
    ATTACHMENT = 4  # context about collecting attachments, not yet used.
    DATA_RANGE = 5  # context about collecting data range or currently sheet name as our range is the whole sheet.
    UNKNOWN_VARIABLES = 6  # context about showing variables that couldn't match any of the sheet variables (headers).

class Type(Enum):
    """ This is an enumeration class for task types """
    UNDEFINED = 0   # user has not yet selected the task type
    RECORD = 1      # user has selected to only update the records in the sheet
    DRAFT = 2       # user has selected to create drafts and don't send mails
    SEND = 3        # user has selected to create drafts and send them

class Status(IntEnum):
    """ This is an enumeration class for task status """
    INITIALIZED = 0 # new task is created
    INCOMPLETE = 1  # pre-reqs are not yet collected
    INPROGRESS = 2  # pre-reqs are collected
    EXPIRED = 3     # task lifetime has passed before finishing the task
    COMPLETED = 4   # task has completed successfully
    PARTIAL = 5     # task is partially completed (Compared to type) or (number of rows compared to total)
    FAILED = 6      # task has failed reaching COMPLETED or PARTIAL

class Task:
    """ 
    This is the data structure for every new task
    Tasks are attached to users and are created once the user sends a sheet URL
    Tasks has a life time and if MAX_LIFETIME is exceeded the tasks is marked expired == True
    If a user tries to interact with a task after life time, task status will be change to EXPIRED and a new task will be created
    Every task has 3 inputs before it starts to process (sheet_url, subject and message)
    subject and message can be found within the sheet or can be set separately during the life time of the task
    The task status and type are defined using the ENUM Status and Type respectively
    For reporting we use the following attributes:
        Attribute Total represent the total number of records in the sheet (excluding headers)
        Attributes (rows, drafts, mails) are total numbers for each task action and represent the successful responses only
"""
    MAX_LIFETIME = 2
    
    def __init__(self, id, user, sheet_url):
        self._id = id
        self._user = user
        self._creation_date = datetime.now()
        self._sheet_url = sheet_url
        self._sheet_check = True
        self._data_range = "'Iago'"
        self._data_range_check = True
        self._missing_variables = None
        self._missing_variables_check = True
        self._skip_check_missing_variables = False
        self._subject = ""
        self._subject_check = False
        self._message = ""
        self._message_check = False
        self._status = Status.INITIALIZED
        self.type = Type.UNDEFINED
        self.context = Context.TASK
        self.total = 0
        self.rows = 0
        self.drafts = 0 
        self.mails = 0

    @property
    def id(self):
        return self._id

    @property
    def user(self):
        return self._user

    @property
    def creation_date(self):
        self._creation_date

    @property
    def status(self):
        if self.expired:
            self._status = Status.EXPIRED
        return self._status
    
    @property
    def sheet_url(self):
        return self._sheet_url

    @property
    def data_range_check(self):
        return self._data_range_check

    @data_range_check.setter
    def data_range_check(self, data_range_check):
        self._data_range_check = data_range_check

    @property
    def data_range(self):
        return self._data_range

    @data_range.setter
    def data_range(self, data_range):
        self._data_range_check = True
        self._data_range = data_range
        return self.check_prereqs()

    @property
    def skip_check_missing_variables(self):
        return self._skip_check_missing_variables

    @skip_check_missing_variables.setter
    def skip_check_missing_variables(self, skip_check_missing_variables):
        self._skip_check_missing_variables = skip_check_missing_variables
        if skip_check_missing_variables:
            self._missing_variables_check = True
        return self.check_prereqs()

    @property
    def missing_variables_check(self):
        return self._missing_variables_check

    @missing_variables_check.setter
    def missing_variables_check(self, missing_variables_check):
        self._missing_variables_check = missing_variables_check

    @property
    def missing_variables(self):
        return self._missing_variables

    @missing_variables.setter
    def missing_variables(self, missing_variables):
        self._missing_variables_check = False
        self._missing_variables = missing_variables
        return self.check_prereqs()

    @property
    def subject_check(self):
        return self._subject_check

    @subject_check.setter
    def subject_check(self, subject_check):
        self._subject_check = subject_check

    @property
    def subject(self):
        return self._subject

    @subject.setter
    def subject(self, subject):
        self._subject_check = True
        self._subject = subject
        return self.check_prereqs()

    @property
    def message_check(self):
        return self._message_check

    @message_check.setter
    def message_check(self, message_check):
        self._message_check = message_check

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, message):
        self._message_check = True
        self._message = message
        return self.check_prereqs()

    @property
    def expired(self):
        lifetime = (datetime.now() - self._creation_date).seconds/60
        return True if lifetime > self.MAX_LIFETIME else False
    
    def check_prereqs(self):
        prereqs_fulfilled = self._sheet_check and self._subject_check and self._message_check and self._data_range_check and self._missing_variables_check
        if(prereqs_fulfilled):
            self.context = Context.TASK
            self._status = Status.INPROGRESS
        else:
            self._status = Status.INCOMPLETE
        if(self.expired):
            self._status = Status.EXPIRED
        return prereqs_fulfilled

