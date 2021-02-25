import re, logging
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from iago_chat import *

class iago_sheets_service:

    def __init__(self, credentials, user):
        pass

SHEETS_API = "sheets"
SHEETS_API_VERSION = "v4"

def analyze_input_sheet(user):
  sheets_service = None
  sheets_service = build(SHEETS_API, SHEETS_API_VERSION, credentials=user.g_creds, cache_discovery=False)
  if sheets_service is not None:
    send_message(user, 'Authorization is successful')
    send_message(user, 'Analyzing the sheet')
  user.task.headers, user.task.data = extract_data(user)

def extract_data(user):
  sheets_service = build(SHEETS_API, SHEETS_API_VERSION, credentials=user.g_creds, cache_discovery=False)
  sheet_url = user.task.sheet_url
  spreadsheet_id = sheet_url.split('/')[5]
  range_name = user.task.data_range
  sheet = sheets_service.spreadsheets()
  try:
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    data = result.get('values', [])
    headers = data[0]
    header_count = len(headers)
    if user.task.subject_check or "Subject".lower() in (header.lower() for header in headers): # TODO: Check for lower and upper case
        user.task.subject_check = True
    if user.task.message_check or "Message".lower() in (header.lower() for header in headers): # TODO: Check for lower and upper case
        user.task.message_check = True
    values = data[1:]
    return headers, data
  except HttpError as err:
    if str(err).find("Unable to parse range:"):
      user.task.data_range_check = False
      raise ValueError("Incorrect sheet name " + user.task.data_range) 
    else:
      logging.info(err)

def patternize_headers(headers):
  patterns=[]
  for header in headers:
      pattern = '.*{' + header + '}.*'
      patterns.append(pattern)
  return patterns

def update_cells_values(cells_values_list, patterns_list):
  cells_list = []
  for pattern_ind in range(0, len(patterns_list)):
    pattern = patterns_list[pattern_ind]
    compiled_pattern = re.compile(pattern, re.DOTALL)
    key = pattern[2:-2]
    resultList = []
    for x in range(0, len(cells_values_list)):
        for y in range(0, len(cells_values_list[x])):
          content = cells_values_list[x][y]
          if compiled_pattern.match(content):
            value = cells_values_list[x][pattern_ind]
            cells_values_list[x][y] = content.replace(key, value)
            resultList.append((x, y))
    cells_list.append(resultList)
  return cells_list

def update_sheet(user):
  sheets_service = build(SHEETS_API, SHEETS_API_VERSION, credentials=user.g_creds, cache_discovery=False)
  sheet_url = user.task.sheet_url
  spreadsheet_id = sheet_url.split('/')[5]
  range_name = user.task.data_range
  sheet = sheets_service.spreadsheets()
  if not ("Subject".lower() in (header.lower() for header in user.task.headers)):
      user.task.headers.append("Subject")
      for row  in user.task.data[1:]:
          row.append(user.task.subject)
  if not ("Message".lower() in (header.lower() for header in user.task.headers)):
      user.task.headers.append("Message")
      for row in user.task.data[1:]:
          row.append(user.task.message)
  patterns = patternize_headers(user.task.headers)

  user.task.updated_data = update_cells_values(user.task.data, patterns)
  update_body = { 'range': range_name,  'majorDimension': 'ROWS', 'values': user.task.data }
  update_response = sheet.values().update(spreadsheetId=spreadsheet_id,range=range_name, valueInputOption='RAW', body=update_body).execute() 
  if update_response is not None:
  #TODO: check return values of (numOfROW/ numOfCOLUMN) against input values
      return True
  else:
      return False

