
import logging
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
import random
import urllib.parse
import re
from datetime import datetime
import json
import os
from bs4 import BeautifulSoup
from utilies import Extact_Email
def get_data_from_url(url, driver):
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Check for booking-related phrases
    booking_keywords = ["book online", "book appointment"]
    content_text = soup.get_text().lower()

    emails =Extact_Email(content_text)
    print(emails)

def main():
    logging.info("Initializing the Chrome driver")
    search_query = input("Enter your search query: ")
    encoded_query = urllib.parse.quote(search_query)
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    time.sleep(random.uniform(2,3))
    # search_query = 'intext:"call to schedule" "contact us" "bridal" -site:healthcare.com'
    driver.get(f"https://www.google.com/search?q={encoded_query}")

    driver.maximize_window()

    links = driver.find_elements(By.XPATH, "//div[@class='yuRUbf']//a")
    urls = [link.get_attribute('href') for link in links]
    print(len(urls))
    for url in urls:
        get_data_from_url(url, driver=driver)
        print(url)
    time.sleep(random.uniform(2,3))

main()
