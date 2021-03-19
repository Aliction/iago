import os
import requests
import json
import _thread

from iago_encrypt import *

send_service_url = None
email_index = -1
subject_index = -1
message_index = -1

def send_draft(user, draft_id):
  global send_service_url
  payload['token'] = encrypt(user.token)
  payload['type'] = 'draft'
  payload['draft_id'] = draft_id
  body = json.dumps(payload)
  headers =  {'Content-Type': 'application/json'}
  resp = requests.post(send_service_url, headers=headers, json=body)

def send_mail(user, row):    
  send_service_url = os.getenv("SEND_SERVICE_URL")
  payload = dict.fromkeys(['token', 'type', 'receiver', 'subject', 'body'])
  receiver = row[email_index]
  subject = row[subject_index] if subject_index > -1 else user.task.subject
  message = row[message_index] if message_index > -1 else user.task.message
#  subject = user.task.subject if user.task.subject_check else row[subject_index]
#  message = user.task.message if user.task.message_check else row[message_index]

  payload['token'] = encrypt(user.token)
  payload['type'] = 'mail'
  payload['receiver'] = encrypt(receiver)
  payload['subject'] = encrypt(subject)
  payload['body'] = encrypt(message)

  body = json.dumps(payload)
  headers =  {'Content-Type': 'application/json'}
  resp = requests.post(send_service_url, headers=headers, json=body)
  message_id = json.loads(resp.text)
  return message_id

def generate_mails(user):
  global send_service_url
  global email_index
  global subject_index
  global message_index

  send_service_url = os.getenv("SEND_SERVICE_URL")
  headers = user.task.headers
  rows = user.task.data[1:]
  email_index = next(ind for ind, header in enumerate(headers) if header.lower() == 'email')
  subject_index = next(ind for ind, header in enumerate(headers) if header.lower() == 'subject')
  message_index = next(ind for ind, header in enumerate(headers) if header.lower() == 'message')

 # email_index = [header.lower() for header in headers].index("email")
 # subject_index = [header.lower() for header in headers].index("subject")
 # message_index = [header.lower() for header in headers].index("message")
  #email_index = next(ind for ind, header in enumerate(headers) if header.lower() == 'email')
  #subject_index = next(ind for ind, header in enumerate(headers) if header.lower() == 'subject')
  #message_index = next(ind for ind, header in enumerate(headers) if header.lower() == 'message')
  for row in rows:
    _thread.start_new_thread(send_mail, (user, row))
