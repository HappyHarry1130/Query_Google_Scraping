import openai
from openai import OpenAIError  # Import the correct exception
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
import traceback
import requests
import re
from datetime import datetime
from dotenv import load_dotenv
import os
import requests

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
openai.api_key = api_key


def parse_time(time_str):
    return datetime.strptime(time_str, '%I:%M %p')

def extract_level(data):
    match = re.search(r'LV\d+', data)
    return match.group(0) if match else None

proxies = {
    'http': 'socks5://14ae1ada67095:8f3793607c@139.171.124.133:12324',
    'https': 'socks5://14ae1ada67095:8f3793607c@139.171.124.133:12324'
}   
session = requests.Session()
session.proxies.update(proxies)
openai.proxy = proxies

def Extact_Email(question, max_retries=5):
    messages = [
        {"role": "system", "content": """You need to analyze whether a link for booking is included with <a> elements.
                    Maybe the <a> element has text such as "book online", "book appointment", "schedule online".
                    "FIND OUT MORE!" is not a booking related keyword.
                    The only elements related to booking can be <a>. So even if other elements contain booking-related content, you can ignore them.
                    Your output should be in json format {"Booking Keywords Found": true/false, "Emails": [XXX, YYY], "Phonenumbers": [XXX, YYY], "Address" : XXX,  "href": [XXX,YYY]}, nothing else needed such as explain.
                    You must print only json format. don't need ```json  .... ```.
                    """},
        {"role": "user", "content": f"""
            {question}
        """}
    ]


    for attempt in range(max_retries):
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-4o-mini",  # Correct model name
                messages=messages
            )
            return completion.choices[0].message['content']
        except OpenAIError as e:  # Use the correct exception
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print("Retrying...")
            else:
                print("Max retries reached. Exiting.")
                raise

def Ckeck_booking(question, max_retries=5):
    messages = [
        {"role": "system", "content": """Please find booking-relative keywords such as "book online", "book appointment", "schedule online".
                    "FIND OUT MORE!" and "Contact US" are not booking-related keywords.
                    Please output like this format:
                    {"Booking Keywords Found": true/false}, nothing else needed such as explain.
                    You must print only json format. don't need ```json  .... ```.
                    """}
    ]

    for q in question:
        messages.append({"role": "user", "content": q})

    for attempt in range(max_retries):
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Correct model name
                messages=messages
            )
            return completion.choices[0].message['content']
        except OpenAIError as e:  # Use the correct exception
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print("Retrying...")
            else:
                print("Max retries reached. Exiting.")
                raise


def write_to_google_sheet_3(data, spreadsheet_id, sheet_name="Data"):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('./credentials.json', scope)
    client = gspread.authorize(creds)


    spreadsheet = client.open_by_key(spreadsheet_id)

    try:
        sheet = spreadsheet.worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        sheet = spreadsheet.add_worksheet(title=sheet_name, rows="100", cols="20")

    headers = ["Link" , "Adress", "Email", "Phone Number", "Booking"]
    current_headers = sheet.row_values(1)        
    if current_headers:
        None
    else:
        sheet.update('A1:E1', [headers])

    existing_rows = sheet.get_all_values()


    row_to_update = None
    for i, row in enumerate(existing_rows):
        if row[0] == data[0]:
            row_to_update = i + 1
            break

    if row_to_update:
        cell_range = f'A{row_to_update}:E{row_to_update}'
        sheet.update(cell_range, [data])
        next_row = row_to_update
    else:
        sheet.append_row(data)
        next_row = len(existing_rows) + 1


    header_range = f"A1:E1" 
    sheet.format(header_range, {
        "backgroundColor": {"red": 0, "green": 0.8, "blue": 0.8},
        "textFormat": {"bold": True},
        "horizontalAlignment": "CENTER",
        "verticalAlignment": "MIDDLE" 
    })


    service = build('sheets', 'v4', credentials=creds)
    body = {
        "requests": [
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": sheet.id,
                        "dimension": "COLUMNS",
                        "startIndex": 0,  
                        "endIndex": 1,    
                    },
                    "properties": {
                        "pixelSize": 500
                    },
                    "fields": "pixelSize"
                }
            },
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": sheet.id,
                        "dimension": "COLUMNS",
                        "startIndex": 1,  
                        "endIndex": 2,    
                    },
                    "properties": {
                        "pixelSize": 400
                    },
                    "fields": "pixelSize"
                }
            },
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": sheet.id,
                        "dimension": "COLUMNS",
                        "startIndex": 2,  
                        "endIndex": 3,   
                    },
                    "properties": {
                        "pixelSize": 250
                    },
                    "fields": "pixelSize"
                }
            },
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": sheet.id,
                        "dimension": "COLUMNS",
                        "startIndex": 3,  
                        "endIndex": 4,
                    },
                    "properties": {
                        "pixelSize": 200
                    },
                    "fields": "pixelSize"
                }
            },
           
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": sheet.id,
                        "dimension": "ROWS",
                        "startIndex": 0, 
                        "endIndex": 1,    
                    },
                    "properties": {
                        "pixelSize": 70  
                    },
                    "fields": "pixelSize"
                }
            },
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": sheet.id,
                        "dimension": "ROWS",
                        "startIndex": 1, 
                        "endIndex": next_row,  
                    },
                    "properties": {
                        "pixelSize": 30 
                    },
                    "fields": "pixelSize"
                }
            },
            {
                "sortRange": {
                    "range": {
                        "sheetId": sheet.id,
                        "startRowIndex": 1,
                        "endRowIndex": next_row, 
                        "startColumnIndex": 0, 
                        "endColumnIndex": 7 
                    },
                    "sortSpecs": [
                        {
                            "dimensionIndex": 0, 
                            "sortOrder": "ASCENDING"
                        }
                    ]
                },
                
            },
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet.id,
                        "startRowIndex": 0,
                        "endRowIndex": next_row,
                        "startColumnIndex": 0,
                        "endColumnIndex": 7
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "horizontalAlignment": "CENTER",
                            "verticalAlignment": "MIDDLE"  
                        }
                    },
                    "fields": "userEnteredFormat(horizontalAlignment,verticalAlignment)"
                }
            },
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet.id,
                        "startRowIndex": 0,
                        "endRowIndex": next_row,  
                        "startColumnIndex": 6,  
                        "endColumnIndex": 9
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "wrapStrategy": "WRAP"  
                        }
                    },
                    "fields": "userEnteredFormat.wrapStrategy"
                }
            },

            
        ]
    }
    freeze_request = {
        "requests": [
            {
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": sheet.id,
                        "gridProperties": {
                            "frozenRowCount": 1,
                            "frozenColumnCount": 1
                        }
                    },
                    "fields": "gridProperties.frozenRowCount,gridProperties.frozenColumnCount"
                }
            }
        ]
    }
    service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=freeze_request).execute()

    service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()




