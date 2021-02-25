import json, base64, logging
import requests
import flask
from flask_restful import request
from email.mime.text import MIMEText
from cryptography.fernet import Fernet

drafter = flask.Flask(__name__)

logging.basicConfig(level=logging.INFO)

def create_message(sender, to, subject, message_text):
  message = MIMEText(message_text, 'html')
  message['to'] = to
  message['from'] = sender
  message['subject'] = subject
  return { 'raw': base64.urlsafe_b64encode(message.as_bytes()).decode('ascii') }

@drafter.route('/', methods = ['POST'])
def main():
  input_request = request.get_json()
  input_request = json.loads(input_request)
  token = input_request['token']
  receiver = decrypt(input_request['receiver'])
  subject = decrypt(input_request['subject'])
  message_body = decrypt(input_request['message_body'])
  message = create_message('me', receiver, subject, message_body)
  token = decrypt(token)
  details = create_draft(token, { "message" : message })
  return details



def create_draft(token, message):
  draft_url = 'https://www.googleapis.com/gmail/v1/users/me/drafts'
  headers =  {'Authorization': 'Bearer {}'.format(token), 'Content-Type': 'application/json'}
  resp = requests.post(draft_url, headers=headers, json=message)
  if (resp.status_code == 401):
  return resp.text

def decrypt(message):
  key =  open('.config/iago/key.pem', 'rb').read()
  key = base64.b64decode(key)

  fernet = Fernet(key)
  decoded = base64.b64decode(message)
  decrypted = fernet.decrypt(decoded).decode("ascii")
  return decrypted

def encrypt(message):
#  try:
  with open('.config/key.pem', 'rb') as f:
    key = f.read()
    key = base64.b64decode(key)
  if key == None:
    key = Fernet.generate_key()

  fernet = Fernet(key)
  encrypted = fernet.encrypt(message)
  encoded = base64.b64encode(encrypted)

  key = base64.b64encode(key)
  open('.config/key.pem', 'wb').write(key)
  return encoded

#drafter.run(debug=True,port=8081)

