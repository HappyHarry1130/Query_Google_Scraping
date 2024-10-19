
import logging
import time
import json
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import random
import urllib.parse
import re
from datetime import datetime
import json
import os
from bs4 import BeautifulSoup
from utilies import Extact_Email, write_to_google_sheet_3
import sys
def get_data_from_url(url, driver):
    print(url)
    try:
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        booking_keywords = ["book online", "book appointment"]
        content_text = soup.get_text().lower()
        info =Extact_Email(content_text)
        info = json.loads(info)
        Address = info.get("Address")
        Emails = info.get("Emails")
        Phonenumbers = info.get("Phonenumbers")
        Booking_Keywords_Found = info.get("Booking Keywords Found")
        print("Address:", Address)
        print("Emails:", Emails)
        print("Phonenumbers:", Phonenumbers)
        print("Booking Keywords Found:", Booking_Keywords_Found)
        if len(Emails) >= 1:
            email = Emails[0]
        else: email = ''
        if len(Phonenumbers) >= 1:
            phonenumber = Phonenumbers[0]
        else: phonenumber = ''
        data = [url, Address, email, phonenumber, Booking_Keywords_Found]
        write_to_google_sheet_3(data, "1fVsXaAfoAcGv58pr3E9CasBorg8d1BWZpn7WgJPelNE", "Sheet1")

    except selenium.common.exceptions.TimeoutException:
        print(f"Timeout while trying to load {url}. Retrying...")
        get_data_from_url(url, driver)
    except selenium.common.exceptions.WebDriverException as e:
        print(f"WebDriverException occurred: {e}")


def main():
    logging.info("Initializing the Chrome driver")
    search_query = input("Enter your search query: ")
    encoded_query = urllib.parse.quote(search_query)

    # chrome_options.add_argument("--headless")
    chrome_options = Options()
    # chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1280,800")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Install the Chrome driver
    # proxy = 'socks5://14ae1ada67095:8f3793607c@139.171.124.133:12324'
    # chrome_options.add_argument(f'--proxy-server={proxy}')

    driver.maximize_window()
    
    # search_query = 'intext:"call to schedule" "contact us" "bridal" -site:healthcare.com'
    driver.get(f"https://www.google.com/search?q={encoded_query}")
    time.sleep(random.uniform(20,30))    
    urls = []
    while True:
        links = driver.find_elements(By.XPATH, "//div[@class='yuRUbf']//a")
        urls.extend([link.get_attribute('href') for link in links])
        # urls = [link.get_attribute('href') for link in links]
        print(len(urls))
        # for url in urls:
        #     get_data_from_url(url, driver=driver)            
        # time.sleep(random.uniform(2,3))

        try:
            next_button = driver.find_element(By.ID, "pnnext")
            next_button.click()
            time.sleep(random.uniform(2,3))
        except Exception as e:
            print("No more pages to navigate.")
            break

    for index, url in enumerate( urls, start=1):
        percent = (index / len(urls)) * 100
        bar_length = 50  # Length of the progress bar
        filled_length = int(bar_length * index // len(urls))
        bar = '>' * filled_length + '-' * (bar_length - filled_length)
        sys.stdout.write(f"\rProcessing link {index}/{len(urls)}: [{bar}] {percent:.2f}%")
        sys.stdout.flush()
        try: 
            get_data_from_url(url, driver=driver)
            time.sleep(random.uniform(2,3))
        except TimeoutError:
            print (' Timeout Error')
        except: 
            print('error') 

main()
