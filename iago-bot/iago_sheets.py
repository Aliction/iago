import re
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
  lookups = check_lookups(user.task.headers)
  if len(lookups) > 0:
    user.task.data = update_data_lookup(lookups, user.task.data)
  if not user.task.skip_check_missing_variables:
    unknown_variables = check_missing_variables(user.task.headers, user.task.data)
    if len(unknown_variables) > 0 :
      user.task.missing_variables = unknown_variables

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
      print(err)

def check_lookups(headers):
    lookups = []
    for h, header in enumerate(headers):
        key_value = header.split("_")
        if len(key_value) == 2 :
            key = key_value[0]
            key_id = headers.index(key)
            value_id = h
            lookup_dict = dict()
            lookups.append((key_id, value_id, lookup_dict))
    return lookups

def update_data_lookup(lookups, data):
    for lookup in lookups:
        key_id = lookup[0]
        value_id = lookup[1]
        lookup_data = lookup[2]
        for r, row in enumerate(data):
            key = row[key_id]
            value = row[value_id]
            if lookup_data.get(key) is None and value.strip() != "" :
                lookup_data[key] = value
            if value.strip() == "":
                row[value_id] = lookup_data.get(key)
    return data

def check_missing_variables(headers, data):
  pattern = "{.*?}"
  missing_variables = []
  compiled_pattern = re.compile(pattern, re.DOTALL)
  for x in range(0, len(data)):
    for y in range(0, len(data[x])):
      content = data[x][y]
      var = re.findall(compiled_pattern, content)
      missing_variables = missing_variables + [v for v in var if v[1:-1] not in headers]
  return set(missing_variables)
      

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
          if content is not None and compiled_pattern.match(content):
            value = cells_values_list[x][pattern_ind] 
            if value is None:
                value = ""
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

