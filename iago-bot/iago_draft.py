import os
import requests
import json
import _thread

from iago_encrypt import *

draft_service_url = None
email_index = -1
subject_index = -1
message_index = -1

def create_draft(user, row):
    global draft_service_url
    payload = dict.fromkeys(['token', 'type', 'receiver', 'subject', 'body'])
    receiver = row[email_index]
    subject = row[subject_index] if subject_index > -1 else user.task.subject
    message = row[message_index] if message_index > -1 else user.task.message

    payload['token'] = encrypt(user.token)
    payload['type'] = 'mail'
    payload['receiver'] = encrypt(receiver)
    payload['subject'] = encrypt(subject)
    payload['message_body'] = encrypt(message)

    body = json.dumps(payload)
    headers =  {'Content-Type': 'application/json'}
    resp = requests.post(draft_service_url, headers=headers, json=body)
    message_id = json.loads(resp.text)['message']['id']
    return message_id


def generate_drafts(user):
  global draft_service_url
  global email_index
  global subject_index
  global message_index
  draft_service_url = os.getenv("DRAFT_SERVICE_URL")
  headers = user.task.headers
  rows = user.task.data[1:]
  email_index = next(ind for ind, header in enumerate(headers) if header.lower() == 'email')
  subject_index = next(ind for ind, header in enumerate(headers) if header.lower() == 'subject')
  message_index = next(ind for ind, header in enumerate(headers) if header.lower() == 'message')
  for row in rows:
    _thread.start_new_thread(create_draft,(user,row))
