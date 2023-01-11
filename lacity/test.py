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
    table_name, table_description, table_url, table_download, table_metadata
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

    # write metadata to a json file
    with open(f"{table_name}_metadata.json", "w", encoding="utf-8") as f:
        json.dump(table_metadata, f)

    # write to a description file
    with open(f"{table_name}_description.txt", "w") as f:
        f.writelines(table_description)


def extract_details(driver):
    # table name
    name = driver.find_element(By.XPATH, "//h1[@class='info-pane-name']").text

    # table description
    table_description = driver.find_element(
        By.XPATH, "//div[@class='collapsible-content entry-description']/div"
    ).text

    # table url
    table_url = driver.current_url

    # table download link
    download_button = driver.find_element(
        By.XPATH, "//button[@class='btn btn-simple btn-sm download']"
    )
    download_button.click()
    table_download = driver.find_element(
        By.XPATH, "//div[@id='export-flannel']/section//ul/li/a[@data-type='CSV']"
    ).get_attribute("href")

    close_button = driver.find_element(
        By.CSS_SELECTOR, "div.export-flannel span.btn-wrapper"
    )
    close_button.click()

    # metadata
    table_metadata = dict()

    show_more = driver.find_element(
        By.XPATH, "//a[@class='table-collapse-toggle more']"
    )

    driver.execute_script(
        "arguments[0].scrollIntoView();",
        show_more,
    )

    # sleep(5)

    show_more.click()

    table_rows = driver.find_elements(
        By.CSS_SELECTOR, ".table-wrapper tr.column-summary"
    )

    for index, each_row in enumerate(table_rows):
        # print(index + 1, each_row.text)
        column_name = each_row.find_element(By.CSS_SELECTOR, "td.column-name").text
        description = each_row.find_element(
            By.CSS_SELECTOR, "td.column-description"
        ).text
        # print(index + 1, column_name, description)
        table_metadata[column_name] = description

    # print(f"table name = {name}")
    # print(f"description = {table_description}")
    # print(f"url = {table_url}")
    # print(f"download_table = {table_download}")
    # print(table_metadata)

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
    "https://data.sfgov.org/Economy-and-Community/Registered-Business-Locations-San-Francisco/g8m3-pdis"
)

sleep(2)

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


# save everything
save_everything(
    table_name, table_description, table_url, table_download, dictionary_download
)
