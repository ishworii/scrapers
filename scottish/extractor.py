from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import utility
import os
import logging

logging.basicConfig(
    filename="scottish_scraping.log",
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

sleep(2)

# all links
all_links = [
    "https://www.opendata.nhs.scot/dataset/covid-19-vaccination-in-scotland",
    "https://www.opendata.nhs.scot/dataset/covid-19-wider-impacts-contacts-with-nhs-24",
    "https://www.opendata.nhs.scot/dataset/psychological-therapies-waiting-times",
    "https://www.opendata.nhs.scot/dataset/covid-19-wider-impacts-deaths",
    "https://www.opendata.nhs.scot/dataset/community-pharmacy-contractor-activity",
    "https://www.opendata.nhs.scot/dataset/covid-19-wider-impacts-scottish-ambulance-services",
    "https://www.opendata.nhs.scot/dataset/cancer-waiting-times",
    "https://www.opendata.nhs.scot/dataset/covid-19-wider-impacts-out-of-hours-consultations",
    "https://www.opendata.nhs.scot/dataset/hospital-beds-information",
    "https://www.opendata.nhs.scot/dataset/covid-19-wider-impacts-induction-of-labour",
]


logging.info(f"{len(all_links)} different tables found.")


# # iterate through each link
logging.info("Iterating through each table")
for each_link in all_links:
    os.chdir("C:\\Users\\PC\\Desktop\\upwork\\scraping_charles\\data\\scottish\\data")
    # create new tab for each new link, extract everything and return back
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])

    # get the new url
    driver.get(each_link)
    sleep(2)

    # find the first link
    first_link = driver.find_element(
        By.XPATH, "//ul[@class='resource-list']//li[@class='resource-item']//a"
    )
    first_link.click()
    sleep(5)

    logging.info("Ready to scrape")

    # ready
    ret = utility.extract_details(driver)
    if ret is None:
        continue
    (table_name, table_description, table_metadata, table_url,) = ret
    download_link = utility.download_table(driver)

    logging.info(f"Extracted all the required data from table {table_url}")

    # save everything
    utility.save_everything(
        table_name, table_description, table_metadata, table_url, download_link
    )
    logging.info(f"Downloaded and saved files from table {table_name}")

    # close and switch back to the original tab
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
