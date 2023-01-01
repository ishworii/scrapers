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
    download_link = driver.find_element(
        By.XPATH, "//div[@class='btn-group']//a"
    ).get_attribute("href")
    return download_link


# extract table name, description, metadata, and url from the site
def extract_details(driver):
    # get table_name
    table_name = driver.find_element(By.CSS_SELECTOR, "h1.page-heading").text

    table_description = driver.find_element(By.CSS_SELECTOR, "div.notes p").text

    table_metadata = dict()

    table_rows = driver.find_element(
        By.CSS_SELECTOR, "div.module-content table"
    ).find_elements(By.CSS_SELECTOR, "tbody tr")

    for each_row in table_rows:
        tds = each_row.find_elements(By.CSS_SELECTOR, "td")
        try:
            column_name = tds[0].text
            description = tds[-2].text
            table_metadata[column_name] = description
        except IndexError:
            return

    # get table url
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

    if not os.path.isdir(table_name):
        os.mkdir(table_name)
    os.chdir(table_name)

    # write to tablename_URLtotable.txt
    with open(f"{table_name}_URLtotable.txt", "w", encoding="utf-8") as f:
        f.write(table_url)

    # write metadata to a json file
    with open(f"{table_name}_metadata.json", "w", encoding="utf-8") as f:
        json.dump(table_metadata, f)

    # write to a description file
    with open(f"{table_name}_description.txt", "w", encoding="utf-8") as f:
        f.write("[Description]\n")
        f.writelines(table_description)
        f.write("\n\n")
        f.write("[URL]\n")
        f.write(table_url)

    # download the csv file
    filename = f"{table_name}.csv"
    with closing(requests.get(download_link, stream=True)) as r:
        f = (line.decode("utf-8") for line in r.iter_lines())
        with open(filename, "w", encoding="utf-8") as csvfile:
            for each_row in f:
                csvfile.write(each_row)
                csvfile.write("\n")
