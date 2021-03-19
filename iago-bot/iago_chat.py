from google.oauth2.service_account import Credentials as SACredentials
from googleapiclient.discovery import build
import requests
import json
import os

CHAT = None
TOKEN = None

def google_login():
  global CHAT
  scopes = ['https://www.googleapis.com/auth/chat.bot']
  bot_credentials = SACredentials.from_service_account_file('chat_secret.json', scopes=scopes)
  CHAT = build('chat', 'v1', credentials=bot_credentials, cache_discovery=False)

def slack_login():
    global TOKEN
    TOKEN = os.getenv('SLACK_TOKEN')

def send_message(user, message):
    if user.platform == 0:
        send_google(user, message)
    elif user.platform == 1:
        send_slack(user, message)

def send_google(user, message):
    body = {'text': message}
    CHAT.spaces().messages().create(parent=user.chat_room, body=body).execute()

def send_slack(user, message):
    url = "https://slack.com/api/chat.postMessage"
    headers = { 'Authorization': 'Bearer ' + TOKEN, 'Content-Type': 'application/json'}
    body = json.dumps({ 'channel': user.chat_room, 'text': message })
    resp =requests.post(url=url, data=body, headers=headers)
    
def send_slack_interactive(user, blocks):
    url = "https://slack.com/api/chat.postMessage"
    token = "xoxb-1892106908128-1853724554423-A0ENaUOebrwuWlGcpVrbPJkh"
    headers = { 'Authorization': 'Bearer ' + TOKEN, 'Content-Type': 'application/json'}
    body = json.dumps({ 'channel': user.chat_room, 'blocks': blocks })
    resp =requests.post(url=url, data=body, headers=headers)

