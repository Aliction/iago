import json, base64, logging 
import requests
import flask
from flask_restful import request
from email.mime.text import MIMEText
from cryptography.fernet import Fernet

sender = flask.Flask(__name__)

def create_message(sender, to, subject, message_text):
  message = MIMEText(message_text, 'html')
  message['to'] = to
  message['from'] = sender
  message['subject'] = subject
  return { 'raw': base64.urlsafe_b64encode(message.as_bytes()).decode('ascii') }

@sender.route('/',methods = ['POST'])
def main():
  input_request = request.get_json()
  input_request = json.loads(input_request)
  send_type = input_request['type']
  token = input_request['token']
  token = decrypt(token)
  if send_type == 'mail':
    receiver = decrypt(input_request['receiver'])
    subject = decrypt(input_request['subject'])
    body = decrypt(input_request['body'])
    message = create_message('me', receiver, subject, body)
    details = send_message(token,  message)
    return details
  elif send_type == 'draft':
    draft_id = input_request['draft_id']
    details = send_draft(token, draft_id)
    message_draft_id = { "id" : draft_id }
    return details
  else:
    return { 'error': 'Invalid type, supported are "mail" and "draft"' }


def send_draft(token, message_draft_id):
  send_draft_url = 'https://www.googleapis.com/gmail/v1/users/me/drafts/send'
  headers =  {'Authorization': 'Bearer {}'.format(token), 'Content-Type': 'application/json'}
  resp = requests.post(send_draft_url, headers=headers, json=message_draft_id)
  if (resp.status_code == 401):
  return resp.text


def send_message(token, message):
  #                     'https://gmail.googleapis.com/gmail/v1/users/me/messages/send'
  send_message_url = 'https://gmail.googleapis.com/gmail/v1/users/me/messages/send'
  headers =  {'Authorization': 'Bearer {}'.format(token), 'Content-Type': 'application/json'}
  resp = requests.post(send_message_url, headers=headers, json=message)
  if (resp.status_code == 401):
  return resp.text


def decrypt(message):
  key =  open('.config/iago/key.pem', 'rb').read()
  key = base64.b64decode(key)

  fernet = Fernet(key)
  decoded = base64.b64decode(message)
  decrypted = fernet.decrypt(decoded).decode("ascii")
  return decrypted

#sender.run(debug=True,port=8082)
