import os, re, logging, _thread
from flask import Flask, request, json, session, redirect, url_for
from flask_restful import Resource, reqparse, Api
import jwt, requests

#from google.oauth2.service_account import Credentials as SACredentials
#from google.oauth2.credentials import Credentials
#from googleapiclient.discovery import build

from user import User
from task import Task, Type, Context
from card import Card

from iago_sheets import *
from iago_chat import *
from iago_draft import *
from iago_send import *

#logging.getLogger('googleapicliet.discovery_cache').setLevel(logging.ERROR)

iago = Flask(__name__)
api = Api(iago)

USERS = None
TASKS = None
CHAT = None
CLIENT_ID = ''
CLIENT_SECRET = ''
REDIRECT_URI = ''
SHEETS_SCOPES = ''
DRAFTS_SCOPES = ''
SEND_SCOPES = ''
SUCCESS_AUTH_PAGE = ''
FAILURE_AUTH_PAGE = ''
CHAT_SERVICE_URL = None

def collect_missing_input(user):
  if not user.task.data_range_check:
    user.task.context = Context.DATA_RANGE
    send_message(user, "I couldn't find a sheet with name `" + user.task.data_range + "`, Can you provide the sheet name here?")
    return
  if not user.task.subject_check:
    user.task.context = Context.SUBJECT
    send_message(user, "I couldn't find the mail subject in the input data can you send it here?")
    return
  if not user.task.message_check:
    user.task.context = Context.MESSAGE
    send_message(user, "What is the email body that you're trying to send?")
    return

def process_task(user):
  if user.task is None:
    send_message(user, "It's been a while and I totally foget which sheet are you talking about, Can you share it again?")
    return
  try:
    analyze_input_sheet(user)
  except ValueError:
    print("Value Error: Data Range")
    print("Task Context:", user.task.context)
#  print(user.email + " has triggered a task of type " + str(user.task.type))
  print("A user has triggered a task of type " + str(user.task.type))
  if user.task.check_prereqs():
    send_message(user, "Processing the sheet ...")
    if update_sheet(user):
      send_message(user, 'The sheet has been updated')
    if user.task.type == Type.DRAFT:
#      create_drafts()
      generate_drafts(user)
      send_message(user, 'I created the required draft e-mails')
    if user.task.type == Type.SEND:
#      send_mails()
      generate_mails(user)
      send_message(user, 'I sent the e-mails on your bahalf as requested')
  else:
    collect_missing_input(user)

def handle_confirmation(event):
    action = event['action']
    action_name = action['actionMethodName']
    user_email = event['user']['email']
    user = get_or_create_user(user_email)
    if (action_name == "confirm_subject"):
        parameters = action['parameters']
        if parameters[1]['value'] == "true":
            user.task.subject = parameters[0]['value']
            user.task.context = Context.TASK
            _thread.start_new_thread(process_task,(user,))
            return {"text": "Confirmed"}
        else:
            return { "text": "OK, Can you send the Subject again here?"}
    elif (action_name == "confirm_message"):
        parameters = action['parameters']
        if parameters[1]['value'] == "true":
            user.task.message = parameters[0]['value']
            user.task.context = Context.TASK
            _thread.start_new_thread(process_task,(user,))
            return {"text": "Confirmed"}
        else:
            return {"text":  "OK, Can you send you send the Message again here?"}

def handle_card(event):
    SCOPES = ""
    action = event['action']
    action_name = action['actionMethodName']
    user_email = event['user']['email']
    user = get_or_create_user(user_email)
    if user.task is None:
#        send_message(user, "It's been a while and I totally foget which sheet are you talking about, Can you share it again?")
        return { "text" : "Sorry, It's been a while and I totally foget which sheet you are alking about, Can you share it again?" }
    if (action_name == "confirm_subject") or (action_name == "confirm_message"):
        return handle_confirmation(event)
    elif (action_name == "update_sheet") :
        user.task.type = Type.RECORD;
        SCOPES = SHEETS_SCOPES
        auth_uri = ('https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id={}&redirect_uri={}&scope={}').format(CLIENT_ID, REDIRECT_URI, SCOPES)
        return Card().access_card(auth_uri)
    elif (action_name == "create_drafts") :
        user.task.type = Type.DRAFT;
        SCOPES = DRAFTS_SCOPES
        auth_uri = ('https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id={}&redirect_uri={}&scope={}').format(CLIENT_ID, REDIRECT_URI, SCOPES)
        return Card().access_card(auth_uri)
    elif (action_name == "send_emails") :
        user.task.type = Type.SEND;
        SCOPES = SEND_SCOPES
        auth_uri = ('https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id={}&redirect_uri={}&scope={}').format(CLIENT_ID, REDIRECT_URI, SCOPES)
        return Card().access_card(auth_uri)

def handle_message(event):
  sender = event['message']['sender']
  message = event['message']['text']
  google_sheet_pattern=re.compile(".*https:\/\/docs\.google\.com\/spreadsheets\/.*")
  user_email = sender['email']
  user_space_name = event['space']['name']
  user = get_or_create_user(user_email, user_space_name)
  sheet_url_list = google_sheet_pattern.findall(message)
  if sheet_url_list:
      user.task = Task(len(TASKS), user.id, sheet_url_list[0])
      return Card.menu
  if user.task is None:
      user_first_name = sender['displayName'].split()[0]
      headers = {'Content-Type': 'application/json'}
      data = json.dumps({ "message": message })
      r = requests.post(CHAT_SERVICE_URL, headers=headers, data=data)
      text = {'text' : json.loads(r.text)['response']}
#      text = {'text' : 'Hello ' + user_first_name + ', send me a sheet to start my work'}
  elif user.task.context == Context.TASK:
      user_first_name = sender['displayName'].split()[0]
      text = {'text' : 'Sorry ' + user_first_name + ', I am still busy with your lastest task, will chat again once done.\nIf you have another task for me just send me the new sheet link.'}
  elif user.task.context == Context.DATA_RANGE:
      user.task.data_range = message
      user.task.context = Context.TASK
      _thread.start_new_thread(process_task,(user,))
      text = {'text' : 'Checking if we can process with sheet name `' + message + '`' }
  elif user.task.context == Context.SUBJECT:
      action = "confirm_subject"
      confirmation_item = "Subject"
      return Card.confirmation_card("Can you confirm this is your subject?", action, confirmation_item, message)
  elif user.task.context == Context.MESSAGE:
      action = "confirm_message"
      confirmation_item = "Message"
      return Card.confirmation_card("Can you confirm this is your message?", action, confirmation_item, message)
  return text

@iago.route('/',methods=['POST'])
def on_event():
    event = request.get_json()
    sender = event['message']['sender']    
    if event['type'] == 'ADDED_TO_SPACE' and event['space']['singleUserBotDm']:
        text = 'Thanks "%s" for your interest in me !' % (user_email if user_email else 'this chat')
        resp = json.jsonify({'text': text})
    elif event['type'] == 'MESSAGE':
        resp = handle_message(event)
    elif event['type'] == 'CARD_CLICKED':
        resp = handle_card(event)
    return resp


@iago.route('/authorize')
def authorize():
  if 'code' not in request.args:
    return {'AUTHORIZED' : False}
  else:
    auth_code = request.args.get('code')
    data = {'code': auth_code,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'redirect_uri': REDIRECT_URI,
            'grant_type': 'authorization_code'}
    r = requests.post('https://oauth2.googleapis.com/token', data=data)
    id_token = r.json()['id_token']
    user = get_user_from_token(id_token)
    tmp_tkn = None
    tmp_tkn = r.json()['access_token']
    if tmp_tkn is None:
      return FAILURE_AUTH_PAGE
    else:
      user.token = r.json()['access_token']
      _thread.start_new_thread(process_task, (user, ) )
      return SUCCESS_AUTH_PAGE
#      return {'Authorized':True}

def update_task(user, sheet_url):
    if user.task is not None:
        user.task = create_task(len(TASKS), user.id, sheet_url)
    elif user.task.expired:
        user.task = create_task(len(TASKS), user.id, sheet_url)
    elif user.task.status.value < 3:
        pass



def get_or_create_user(email, space_name=None):
    user = next((user for user in USERS if user.email == email), None)
    if user is None:
        user = User(len(USERS), email)
        USERS.append(user)
    if space_name is not None:
        user.space = space_name
    return user

def get_user_from_token(id_token):
    user_data = jwt.decode(id_token, options={"verify_signature" : False})
    gid = user_data['sub']
    email = user_data['email']
    user = get_or_create_user(email)
    user.gid = gid
    return user

def load_creds():
  global CLIENT_ID
  global CLIENT_SECRET
  global REDIRECT_URI
  global SHEETS_SCOPES
  global DRAFTS_SCOPES
  global SEND_SCOPES
  global SUCCESS_AUTH_PAGE
  global FAILURE_AUTH_PAGE
  global CHAT_SERVICE_URL

  CHAT_SERVICE_URL = os.getenv("CHAT_SERVICE_URL")
  
  USER_SCOPE = 'openid%20profile%20email'
  SHEETS_SCOPES = USER_SCOPE + '+https%3A//www.googleapis.com/auth/spreadsheets'
  DRAFTS_SCOPES = SHEETS_SCOPES + '+https%3A//www.googleapis.com/auth/gmail.compose'
  SEND_SCOPES = DRAFTS_SCOPES + '+https%3A//www.googleapis.com/auth/gmail.send'
  REDIRECT_URI = "https://iago.aliction.com/bot/authorize"
  try:
    with open("client_secret.json", "r") as client_data:
      client = json.load(client_data)["web"]
      CLIENT_ID = client["client_id"]
      CLIENT_SECRET = client["client_secret"]
  except IOError:
    logging.info("client_secret.json file is missing")
  try:
    with open('auth_success.html', 'r') as success_html:
       SUCCESS_AUTH_PAGE = success_html.read().replace('\n', '')
    with open('auth_failed.html', 'r') as failure_html:
       FAILURE_AUTH_PAGE = failure_html.read().replace('\n', '')
  except IOError:
    logging.info("auth_success.html or auth failed.html file or both are missing")

#if __name__ == '__main__':
import uuid
iago.secret_key = str(uuid.uuid4())
USERS = []
TASKS = []
load_creds()
iago_login()
#iago.debug = True
#iago.run(port=5000)

#iago.run(debug=True,port=5000)

