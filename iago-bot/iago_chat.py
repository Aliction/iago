from google.oauth2.service_account import Credentials as SACredentials
from googleapiclient.discovery import build
#import logging
#logging.getLogger('googleapicliet.discovery_cache').setLevel(logging.ERROR)

CHAT = None

def iago_login():
  global CHAT
  scopes = ['https://www.googleapis.com/auth/chat.bot']
#  bot_credentials, project_id = google.auth.default()
#  bot_credentials = credentials.with_scopes(scopes=scopes)
#  bot_credentials, project_id = laod_credentials_from_file('chat_secret.json')
  bot_credentials = SACredentials.from_service_account_file('chat_secret.json', scopes=scopes)
#  CHAT = build('chat', 'v1', credentials=bot_credentials) #Was working and all of sudden threw File_cache not found#  This solution disable cache is proposed here: https://github.com/googleapis/google-api-python-client/issues/427
  CHAT = build('chat', 'v1', credentials=bot_credentials, cache_discovery=False)

def send_message(user, message):
    body = {'text': message}
    CHAT.spaces().messages().create(parent=user.space, body=body).execute()
