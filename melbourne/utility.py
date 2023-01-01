from selenium.webdriver.common.by import By
from time import sleep
import os
import json
import requests
from contextlib import closing
import string
from selenium.common.exceptions import NoSuchElementException


# get the download link for the table
def download_table(driver):
    # go to extract tab
    driver.find_element(
        By.XPATH, "//div[@class='ods-tabs__tabs']/a[contains(.,'Export')]"
    ).click()
    sleep(2)
    # download link
    download_link = driver.find_element(
        By.CSS_SELECTOR, ".ods-dataset-export-link a",
    ).get_attribute("href")

    return download_link


# extract table name, description, metadata, and url from the site
def extract_details(driver):
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    try:
        table_description = driver.find_element(
            By.CSS_SELECTOR, ".ods-dataset-metadata-block__description"
        ).text
    except NoSuchElementException:
        table_description = ""

    # click to expand
    expand = driver.find_element(
        By.XPATH, "//div[@class='ods-collapsible__above-fold']",
    )
    expand.click()

    # get table_name
    table_name = driver.find_element(
        By.CSS_SELECTOR, ".ods-dataset-visualization__header span"
    ).text

    table_metadata = dict()

    for each_column in driver.find_elements(
        By.CSS_SELECTOR, ".odswidget-dataset-schema .odswidget-dataset-schema__field"
    ):
        name = each_column.find_element(
            By.CSS_SELECTOR, ".odswidget-dataset-schema__field-label"
        ).text
        description = each_column.find_element(
            By.CLASS_NAME, "odswidget-dataset-schema__field-description"
        ).text
        table_metadata[name] = description

    # get table url
    table = driver.find_element(
        By.XPATH, "//div[@class='ods-tabs__tabs']/a[contains(.,'Table')]"
    )
    table.click()

    table_url = driver.current_url

    return table_name, table_description, table_metadata, table_url


# download csv file, and create all necessary metadata files
def save_everything(
    table_name, table_description, table_metadata, table_url, download_link
):
    # convert table name to correct format
    table_name = table_name.lower()
    table_name = table_name.translate(str.maketrans("", "", string.punctuation))
    if len(table_name) > 50:
        table_name = table_name[:50]
    table_name = table_name.replace(" ", "_")

    if "tree_canopies" in table_name:
        return

    if not os.path.isdir(table_name):
        os.mkdir(table_name)
    os.chdir(table_name)

    # download the csv file
    filename = f"{table_name}.csv"
    with closing(requests.get(download_link, stream=True)) as r:
        f = (line.decode("utf-8") for line in r.iter_lines())
        with open(filename, "w") as csvfile:
            for each_row in f:
                csvfile.write(each_row)
                csvfile.write("\n")

    # write to tablename_URLtotable.txt
    with open(f"{table_name}_URLtotable.txt", "w") as f:
        f.write(table_url)

    # write metadata to a json file
    with open(f"{table_name}_metadata.json", "w") as f:
        json.dump(table_metadata, f)

    # write to a description file
    with open(f"{table_name}_description.txt", "w") as f:
        f.write("[Description]\n")
        f.writelines(table_description)
        f.write("\n\n")
        f.write("[URL]\n")
        f.write(table_url)
