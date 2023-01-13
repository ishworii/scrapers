from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import os
import logging
import selenium
from selenium.webdriver.common.by import By
from time import sleep
import os
import json
import requests
from contextlib import closing
import string
from selenium.common.exceptions import NoSuchElementException
from urllib.request import urlretrieve
from urllib.error import HTTPError
import requests
import pandas as pd

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
    try:
        with closing(requests.get(table_download, stream=True)) as r:
            f = (line.decode("utf-8") for line in r.iter_lines())
            with open(filename, "w", encoding="utf-8") as csvfile:
                for index, each_row in enumerate(f):
                    if index == 20_000:
                        break
                    csvfile.write(each_row)
                    csvfile.write("\n")

    except Exception as e:
        logging.log("Error while writing to csv file.")
        return -1

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

    # check for number of rows
    tables_button = driver.find_element(By.XPATH, "//a[@data-ga='Table']")
    tables_button.click()

    number_of_rows = driver.find_element(
        By.CSS_SELECTOR, "div.dataTables_info"
    ).text.split(" ")
    number_of_rows = int([x for x in number_of_rows if x.isdigit()][-1])
    if number_of_rows < 190:
        return -1

    # table name
    name = driver.find_element(By.XPATH, "//h2[@class='package-title']").text

    # table description
    table_description = driver.find_element(
        By.XPATH, "//div[@class='dataset-description']"
    ).text

    # metadata
    table_metadata = dict()

    table_rows = driver.find_elements(
        By.XPATH, "//div[@class='resource-fields']/div[@class='hidden-phone']//tbody/tr"
    )

    # print(len(table_rows))
    # exit(-1)

    for index, each_row in enumerate(table_rows):
        # print(index + 1, each_row.text)
        tds = each_row.find_elements(By.TAG_NAME, "td")
        _, column_name, description, field_type, unit_of_measure, more_details = [
            x.text for x in tds
        ]
        # print(index + 1, column_name, description)
        table_metadata[column_name] = description

    # table url
    table_url = driver.current_url

    # table download link
    api_button = driver.find_element(
        By.XPATH,
        "//button[@class='btn datagovsg-btn btn-right btn-blue desktop-only ga-dataset-data-api']",
    )
    api_button.click()
    sleep(5)

    table_download = driver.find_element(
        By.XPATH, "//*[@id='collapse-querying']/div/p/code/a"
    ).get_attribute("href")

    print(f"table name = {name}")
    print(f"description = {table_description}")
    print(f"url = {table_url}\n")
    print(f"download_table = {table_download}")
    print(table_metadata)

    # return
    return (name, table_description, table_url, table_download, table_metadata)


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
    "https://data.gov.sg/dataset/total-number-of-outgoing-retail-international-telephone-call-minutes-including-transit"
)

sleep(2)

# os.chdir(
#     "C:\\Users\\Ishwor\\Desktop\\upwork\\scraping_charles\\data\\1st_batch_100k\\sandiego"
# )
# sleep(5)

# extract details
(
    table_name,
    table_description,
    table_url,
    table_download,
    dictionary_download,
) = extract_details(driver)


# save everything
save_everything(
    table_name, table_description, table_url, table_download, dictionary_download
)
