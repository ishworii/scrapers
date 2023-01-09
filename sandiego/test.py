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

# download csv file, and create all necessary metadata files
def save_everything(
    table_name, table_description, table_url, table_download, dictionary_download
):
    # convert table name to correct format
    table_name = table_name.lower()
    table_name = table_name.translate(str.maketrans("", "", string.punctuation))
    if len(table_name) > 50:
        table_name = table_name[:50]
    table_name = table_name.replace(" ", "_")

    if not os.path.isdir(table_name):
        os.mkdir(table_name)
    os.chdir(table_name)

    # download the csv file
    filename = f"{table_name}.csv"
    with closing(requests.get(table_download, stream=True)) as r:
        f = (line.decode("utf-8") for line in r.iter_lines())
        with open(filename, "w") as csvfile:
            for index, each_row in enumerate(f):
                if index == 20_000:
                    break
                csvfile.write(each_row)
                csvfile.write("\n")

    # write to tablename_URLtotable.txt
    with open(f"{table_name}_URLtotable.txt", "w") as f:
        f.write(table_url)

    # download the metadata csv file
    filename = f"{table_name}_metadata.csv"
    try:
        urlretrieve(url=dictionary_download, filename=filename)
    except HTTPError:
        return -1

    # write to a description file
    with open(f"{table_name}_description.txt", "w") as f:
        f.writelines(table_description)
        f.write("\n\n")


def extract_details(driver):
    # table name
    name = driver.find_element(
        By.XPATH, "//div[@class='col-sm-12']//span[@property='dct:title']"
    ).text

    # table description
    description = driver.find_element(
        By.XPATH, "//div[@class='col-sm-12']//div[@property='dct:description']"
    ).text

    # table url
    table_url = driver.current_url

    # table download link
    table = driver.find_element(
        By.XPATH,
        "//table",
    )
    rows = table.find_elements(By.TAG_NAME, "tr")

    # print(len(rows))

    if len(rows) < 3:
        return -1

    # rows indicationg downloadable table files
    table_rows = rows[:-1:]
    table_download = None
    for each_table in table_rows[1::]:
        tmp = (
            each_table.find_element(
                By.XPATH,
                "//td[@class='table-content-centered']//div[@property='dcat:mediaType']",
            )
            .text.strip()
            .lower()
        )
        print(tmp)
        if tmp == "csv":
            table_download = each_table.find_elements(
                By.XPATH, "td[@class='table-content-centered']//a"
            )[-1].get_attribute("href")

    # print(dictionary_row)

    dictionary_download = driver.find_element(
        By.XPATH,
        "//table//tr//td[@class='table-content-centered']//a[contains(translate(@title,'Dictionary','dictionary'),'dictionary')]",
    ).get_attribute("href")

    print(f"table name = {name}")
    print(f"description = {description}")
    print(f"url = {table_url}")
    print(f"download_table = {table_download}")
    print(f"download dictionary = {dictionary_download}")

    if table_download is None or dictionary_download is None:
        return -1

    # return
    return (name, description, table_url, table_download, dictionary_download)


# Headless/incognito Chrome driver
chrome_options = Options()
chrome_options.add_argument("--incognito")
chrome_options.add_argument("start-maximized")
# chrome_options.add_argument("headless")
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), options=chrome_options
)

logging.info("Webdriver setup done.")


driver.get("https://data.sandiego.gov/datasets/police-ripa-stops/")

sleep(2)

# os.chdir(
#     "C:\\Users\\Ishwor\\Desktop\\upwork\\scraping_charles\\data\\1st_batch_100k\\sandiego"
# )
sleep(5)

# extract details
extracted_details = extract_details(driver)
if extracted_details != -1:
    (
        table_name,
        table_description,
        table_url,
        table_download,
        dictionary_download,
    ) = extracted_details


# save everything
save_everything(
    table_name, table_description, table_url, table_download, dictionary_download
)
