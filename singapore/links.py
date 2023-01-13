from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import logging
import sys
import pandas as pd
import json


sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")

logging.basicConfig(
    filename="logs.log",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)


# Headless/incognito Chrome driver
chrome_options = Options()
# chrome_options.add_argument("--incognito")
chrome_options.add_argument("start-maximized")
# chrome_options.add_argument("headless")
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), options=chrome_options
)

logging.info("Webdriver setup done.")


driver.get("https://data.gov.sg/dataset?res_format=CSV")

sleep(2)

arr = []

# with open("links_datasets.json", "r") as file:
#     data = json.load(file)


while True:
    found = False
    all_divs = driver.find_elements(By.XPATH, "//div[@class='col-12']//h3/a")
    for each_div in all_divs:
        link = each_div.get_attribute("href")
        tmp = {"link": link, "scraped": False, "possible": True}
        # if tmp not in data:
        #     arr.append(tmp)
        arr.append(tmp)

    # find buttons
    buttons = driver.find_elements(
        By.XPATH, "//div[@class='pagination pagination-centered']/ul/li/a"
    )
    for each_button in buttons:
        if each_button.text == "»":
            found = True
            url = each_button.get_attribute("href")
            driver.get(url)
    if not found:
        break


df = pd.DataFrame(arr)
df.to_json("links.json", orient="records")
