import os
import time

import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


PATH_TO_WEBDRIVER = "../webdrivers/chromedriver"


def scroll_with_selenium(url, number_of_scrolls, sleep_time=3):
    service = webdriver.ChromeService(PATH_TO_WEBDRIVER)
    driver = webdriver.Chrome(service=service)
    driver.get(url)
    body = driver.find_element(By.TAG_NAME, 'body')
    for i in range(number_of_scrolls):
        body.send_keys(Keys.END)
        time.sleep(sleep_time)
    return driver.page_source


def export_to_csv(products):
    new_data = pd.DataFrame(products)
    if os.path.exists("dataset/table.csv"):
        existing_data = pd.read_csv("dataset/table.csv")
        updated_data = pd.concat([existing_data, new_data], ignore_index=True)
    else:
        updated_data = new_data
    updated_data.to_csv("dataset/table.csv", index=False)
