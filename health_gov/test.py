from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import string
import json
import requests
from contextlib import closing
from time import sleep
import os
import logging

# define some universal funtions for extraction
def xpath_finder(driver, xpath, many=False):
    if many:
        try:
            element = driver.find_elements(By.XPATH, xpath)
            return element
        except NoSuchElementException:
            return -1
    try:
        element = driver.find_element(By.XPATH, xpath)
        return element
    except NoSuchElementException:
        return -1


def css_finder(driver, css, many=False):
    if many:
        try:
            element = driver.find_elements(By.CSS_SELECTOR, css)
            return element
        except NoSuchElementException:
            return -1
    try:
        element = driver.find_element(By.CSS_SELECTOR, css)
        return element
    except NoSuchElementException:
        return -1


# download csv file, and create all necessary metadata files
def save_everything(
    table_name, table_description, table_url, table_download, table_metadata
):
    # convert table name to correct format
    table_name = table_name.lower()
    table_name = table_name.translate(str.maketrans("", "", string.punctuation))
    if len(table_name) > 80:
        table_name = table_name[:80]
    table_name = table_name.replace(" ", "_")

    if not os.path.isdir(table_name):
        os.mkdir(table_name)
    os.chdir(table_name)

    # download the csv file
    filename = f"{table_name}.csv"
    with closing(requests.get(table_download, stream=True)) as r:
        f = (line.decode("utf-8", errors="ignore") for line in r.iter_lines())
        with open(filename, "w", encoding="utf-8") as csvfile:
            for index, each_row in enumerate(f):
                if index == 20_000:
                    break
                csvfile.write(each_row)
                csvfile.write("\n")

    # write to tablename_URLtotable.txt
    with open(f"{table_name}_URLtotable.txt", "w") as f:
        f.write(table_url)

    # write metadata to a json file
    with open(f"{table_name}_metadata.json", "w", encoding="utf-8") as f:
        json.dump(table_metadata, f)

    # write to a description file
    with open(f"{table_name}_description.txt", "w") as f:
        f.writelines(table_description)


def extract_details(driver):

    # table name
    name = xpath_finder(driver, "//h1[@class='info-pane-name']")
    if name == -1:
        logging.info("table name not found.")
        return -1
    name = name.text
    print(f"table name = {name}")

    # table description
    table_description = xpath_finder(
        driver, "//div[@class='collapsible-content entry-description']/div"
    )
    if table_description == -1:
        logging.info("table description not found.")
        return -1
    table_description = table_description.text
    print(f"description = {table_description}")

    # table url
    table_url = driver.current_url
    print(f"url = {table_url}")

    # try finding table download button with csv file.
    table_download = xpath_finder(
        driver, "//div[@class='download-buttons']/a[contains(.,'text/csv')]"
    )
    if table_download == -1:
        logging.info("could not find button to download csv file.")
        return -1

    table_download = table_download.get_attribute("href")
    print(f"download_table = {table_download}")

    # try finding the data dictionary button
    # first find the application/json

    table_metadata = None
    all_download_buttons = xpath_finder(
        driver, "//div[@class='download-buttons']", many=True
    )
    for each_button in all_download_buttons:
        tmp = css_finder(each_button, "a", many=True)
        if len(tmp) == 2:
            app, dd = tmp
            if app.text.lower() == "application/json":
                table_metadata = dd
                break

    if not table_metadata:
        logging.info("Data dictionary not found..")
        return -1

    table_metadata = table_metadata.get_attribute("href")

    table_metadata = requests.get(table_metadata).json()
    data_dict = dict()
    for each_column in table_metadata:
        col = each_column.get("name", None)
        desc = each_column.get("description", None)
        data_dict[col] = desc

    # print(f"table name = {name}")
    # print(f"description = {table_description}")
    # print(f"url = {table_url}")
    # print(f"download_table = {table_download}")
    print(table_metadata)

    # return
    return (name, table_description, table_url, table_download, data_dict)


# Headless/incognito Chrome driver
chrome_options = Options()
chrome_options.add_argument("--incognito")
chrome_options.add_argument("start-maximized")
# chrome_options.add_argument("headless")
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), options=chrome_options
)

logging.info("Webdriver setup done.")


driver.get(
    "https://healthdata.gov/dataset/COVID-19-Vaccine-Distribution-Allocations-by-Juris/86eu-w6d6"
)

# sleep(2)

# os.chdir(
#     "C:\\Users\\Ishwor\\Desktop\\upwork\\scraping_charles\\data\\1st_batch_100k\\sandiego"
# )
sleep(5)

# extract details
(
    table_name,
    table_description,
    table_url,
    table_download,
    dictionary_download,
) = extract_details(driver)


# # save everything
save_everything(
    table_name, table_description, table_url, table_download, dictionary_download
)
