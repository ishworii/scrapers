from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import string
import json
import requests
from contextlib import closing
from time import sleep
import logging
import os


logging.basicConfig(
    filename="logs.log",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)


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


def css_finder(driver, xpath, many=False):
    if many:
        try:
            element = driver.find_elements(By.CSS_SELECTOR, xpath)
            return element
        except NoSuchElementException:
            return -1
    try:
        element = driver.find_element(By.CSS_SELECTOR, xpath)
        return element
    except NoSuchElementException:
        return -1


# download csv file, and create all necessary metadata files
def save_everything(
    table_name, table_description, table_url, table_download, table_metadata
):
    # convert table name to correct format
    table_name = table_name.lower()
    table_name = table_name.encode("ascii", errors="ignore").decode()
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

    # check for number of rows
    rows = xpath_finder(driver, "//span[@class='ods-filters__count-number ng-binding']")
    if rows != -1:
        rows = int(rows.text.replace(",", ""))
        if rows < 190:
            logging.info("Number of rows less than 190")
            return -1
    else:
        logging.info("Number of rows not found..")

    # print(rows)
    # exit(-1)

    table_description = css_finder(driver, ".ods-dataset-metadata-block__description")
    if table_description != -1:
        table_description = table_description.text
    else:
        logging.info("table description not found..")
        return -1
    # print(table_description)
    # exit(-1)

    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    # find all schema
    expand = xpath_finder(driver, "//div[@class='ods-collapsible__above-fold']")
    if expand != -1:
        expand.click()
    else:
        logging.info("Schema definition not found..")
        return -1

    # sleep(5)
    # exit(-1)

    # find table name
    table_name = css_finder(driver, ".ods-dataset-visualization__header span")
    if table_name != -1:
        table_name = table_name.text

    # print(table_name)
    # return -1

    table_metadata = dict()
    for each_column in xpath_finder(
        driver, "//div[@class='odswidget-dataset-schema__field ng-scope'] ", many=True
    ):
        name = css_finder(each_column, ".odswidget-dataset-schema__field-label").text
        description = css_finder(
            each_column, ".odswidget-dataset-schema__field-description-wrapper"
        ).text
        table_metadata[name] = description

    # get table_url
    table_url = driver.current_url

    # find export button and click
    export_button = xpath_finder(
        driver, "//div[@class='ods-tabs__tabs']//a[contains(.,'Export')]"
    )
    if export_button != -1:
        export_button.click()
    else:
        logging.info("Export button not found...")
        return -1

    sleep(2)
    # find accept terms button and click
    accept_terms = css_finder(
        driver,
        ".ods-dataset-export__mandatory-license__license-content button",
    )
    if accept_terms == -1:
        logging.info("Accept button not found..")
    else:
        accept_terms.click()

    table_download = css_finder(driver, ".ods-dataset-export-link a")
    if table_download != -1:
        table_download = table_download.get_attribute("href")
    else:
        logging.info("Table download url not found..")
        return -1

    print(f"table name = {name}")
    print(f"description = {table_description}")
    print(f"url = {table_url}")
    print(f"download_table = {table_download}")
    print(table_metadata)

    # return
    return (name, table_description, table_url, table_download, table_metadata)


# Headless/incognito Chrome driver
chrome_options = Options()
# chrome_options.add_argument("--incognito")
chrome_options.add_argument("start-maximized")
# chrome_options.add_argument("headless")
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), options=chrome_options
)

logging.info("Webdriver setup done.")


driver.get("https://opendata.bristol.gov.uk/explore/dataset/lsoa110/information/")

sleep(2)


# extract details
(
    table_name,
    table_description,
    table_url,
    table_download,
    table_metadata,
) = extract_details(driver)


save_everything(
    table_name, table_description, table_url, table_download, table_metadata
)
