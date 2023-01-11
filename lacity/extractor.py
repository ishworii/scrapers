from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os
import logging
import utility
import sys
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
chrome_options.add_argument("--incognito")
chrome_options.add_argument("start-maximized")
# chrome_options.add_argument("headless")
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), options=chrome_options
)

logging.info("Webdriver setup done.")


driver.get("https://www.google.com/")

sleep(5)

# # Set sleep time for the page to load on scroll
# SCROLL_PAUSE_TIME = 3

# # Get scroll height
# last_height = driver.execute_script("return document.body.scrollHeight")

# while True:
#     # Scroll down to bottom
#     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

#     # Wait to load page
#     sleep(SCROLL_PAUSE_TIME)

#     # Calculate new scroll height and compare with last scroll height
#     new_height = driver.execute_script("return document.body.scrollHeight")
#     if new_height == last_height:
#         break
#     last_height = new_height

# logging.info("Scrolling done.")


# load all the links to all_datasets
with open("links_filters.json", "r") as file:
    all_datasets = json.load(file)


logging.info(f"{len(all_datasets)} different tables found.")

scrapped = 0
for each_link in all_datasets:
    if each_link["scraped"] == True or each_link["possible"] == False:
        scrapped += 1

logging.info(
    f"Scraped {scrapped} tables and {len(all_datasets) - scrapped} are remaining.."
)

# # iterate through each link
logging.info("Iterating through each table")
for each_link in all_datasets:
    if each_link["scraped"] == True or each_link["possible"] == False:
        continue
    os.chdir(
        "C:\\Users\\Ishwor\\Desktop\\upwork\\scraping_charles\\data\\1st_batch_100k\\lacity"
    )
    try:
        # create new tab for each new link, extract everything and return back
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        # get the new url
        driver.get(each_link["link"])
        sleep(5)

        # extract details

        details = utility.extract_details(driver)
        if details == -1:
            continue

        (
            table_name,
            table_description,
            table_url,
            table_download,
            table_metadata,
        ) = details

        logging.info(f"Extracted all the required data from table {table_url}")

        # save everything

        utility.save_everything(
            table_name,
            table_description,
            table_url,
            table_download,
            table_metadata,
        )
        logging.info(f"Downloaded and saved files from table {table_name}")
        each_link["scraped"] = True
    except Exception as e:
        each_link["possible"] = False

        logging.info(f"{e} in extractor")

        # save the correct state json to the file
        os.chdir("C:\\Users\\Ishwor\\Desktop\\upwork\\scraping_charles\\lacity")
        with open("links_filters.json", "w") as file:
            json.dump(all_datasets, file)
        logging.info("Error occured...please restart the program")
        logging.info("Exiting now...")
        exit(-1)

    # close and switch back to the original tab
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
logging.info("Scrapped all possible datasets.")
