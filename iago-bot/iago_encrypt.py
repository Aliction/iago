import base64
from cryptography.fernet import Fernet

def encrypt(message):
  with open('.config/iago/key.pem', 'rb') as f:
    key = f.read()
    key = base64.b64decode(key)
  if key == None:
    key = Fernet.generate_key()
  fernet = Fernet(key)
  encrypted = fernet.encrypt(bytes(message, "utf8"))
  encoded = base64.b64encode(encrypted).decode("ascii")
  return encoded

