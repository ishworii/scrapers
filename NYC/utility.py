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
    no_of_rows = xpath_finder(
        driver,
        "//section[@class='landing-page-section dataset-contents']//div[@class='metadata-pair']//dd",
    )
    if no_of_rows != -1:
        no_of_rows = no_of_rows.text
        if "K" not in no_of_rows and "M" not in no_of_rows:
            no_of_rows = "".join([x for x in no_of_rows if x.isdigit()])
            if int(no_of_rows) < 190:
                logging.info("number of rows less than 200")
                return -1

    # table name
    name = xpath_finder(driver, "//h1[@class='info-pane-name']")
    if name == -1:
        logging.info("table name not found.")
        return -1
    name = name.text

    # table description
    table_description = xpath_finder(
        driver, "//div[@class='collapsible-content entry-description']/div"
    )
    if table_description == -1:
        logging.info("table description not found.")
        return -1
    table_description = table_description.text

    # table url
    table_url = driver.current_url

    # table download link
    export_button = xpath_finder(
        driver, "//button[@class='btn btn-simple btn-sm download']"
    )
    if export_button == -1:
        logging.info("Export button not found..")
        return -1
    export_button.click()
    table_download = xpath_finder(
        driver, "//div[@id='export-flannel']/section//ul/li/a[@data-type='CSV']"
    )
    if table_download == -1:
        logging.info("Download csv option not found.")
        return -1
    table_download = table_download.get_attribute("href")

    # find close button and click
    close_button = driver.find_element(
        By.CSS_SELECTOR, "div.export-flannel span.btn-wrapper"
    )
    close_button.click()

    # metadata
    table_metadata = dict()

    show_more = xpath_finder(driver, "//a[@class='table-collapse-toggle more']")
    # only try to click if show more button exists.
    if show_more == -1:
        pass
    else:
        driver.execute_script(
            "arguments[0].scrollIntoView();",
            show_more,
        )
        show_more.click()

    table_rows = css_finder(driver, ".table-wrapper tr.column-summary", many=True)
    if table_rows == -1:
        logging.info("table rows not found..")
        return -1

    for _, each_row in enumerate(table_rows):
        # print(index + 1, each_row.text)
        column_name = css_finder(each_row, "td.column-name").text
        description = css_finder(each_row, "td.column-description").text
        # print(index + 1, column_name, description)
        table_metadata[column_name] = description

    # print(f"table name = {name}")
    # print(f"description = {table_description}")
    # print(f"url = {table_url}")
    # print(f"download_table = {table_download}")
    # print(table_metadata)

    # return
    return (name, table_description, table_url, table_download, table_metadata)
