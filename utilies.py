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
        {"role": "system", "content": f"""You need to separate emails.
                    
                    Your output should be in json format {{"Email":XXX,"Email":XXX}}, nothing else needed such as explain.
                    You must print only json format. don't need ```json  .... ```.
                    """},
        {"role": "user", "content": f"""
            {question}
        """}
    ]

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

def get_informations(question, max_retries=5):
    messages = [
        {"role": "system", "content": f"""You are an information analyst.
                    You need to analyze the information and return these values ​​in the corresponding json format.
                    The information you need to get is:
                    Name, Address, Email, Phone Number
                     {{"Name":XXX,"Address":XXX, "Email":XXX, "Phone Number":XXX}}, nothing else needed such as explain.
                    You must print only json format. don't need ```json  .... ```.
                    """},
        {"role": "user", "content": f"""
            {question}
        """}
    ]

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




