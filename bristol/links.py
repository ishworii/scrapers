from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import logging
import pandas as pd

logging.basicConfig(
    filename="logs.log",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)


# Headless/incognito Chrome driver
chrome_options = Options()
chrome_options.add_argument("--incognito")
chrome_options.add_argument("start-maximized")
# chrome_options.add_argument("headless")
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), options=chrome_options
)

logging.info("Webdriver setup done.")


driver.get("https://data.melbourne.vic.gov.au/explore/?sort=modified")

sleep(2)

# Set sleep time for the page to load on scroll
SCROLL_PAUSE_TIME = 1

# Get scroll height
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    # Scroll down to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait to load page
    sleep(SCROLL_PAUSE_TIME)

    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

logging.info("Scrolling done.")

arr = []

all_divs = driver.find_elements(
    By.CSS_SELECTOR, "a[class='ods-catalog-card__title-link']"
)

for each_div in all_divs:
    tmp = dict()
    tmp["link"] = each_div.get_attribute("href")
    tmp["scraped"] = False
    arr.append(tmp)


df = pd.DataFrame(arr)
df.to_json("links_bristol.json", orient="records")
