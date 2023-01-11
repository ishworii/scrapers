from time import sleep
from selenium.webdriver.common.by import By
import os
import json
import requests
from contextlib import closing
import string
from selenium.common.exceptions import NoSuchElementException
import logging


# define a universal function to find elements
def xpath_finder(driver, xpath):
    try:
        element = driver.find_element(By.XPATH, xpath)
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
    if len(table_name) > 50:
        table_name = table_name[:50]
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

    # check for no of rows
    try:
        no_of_rows = driver.find_element(
            By.XPATH,
            "//section[@class='landing-page-section dataset-contents']//div[@class='metadata-pair']//dd",
        ).text
    except NoSuchElementException:
        logging.info("number of rows not found")
        return -1
    if "K" not in no_of_rows and "M" not in no_of_rows:
        no_of_rows = "".join([x for x in no_of_rows if x.isdigit()])
        if int(no_of_rows) < 190:
            logging.info("number of rows less than 200")
            return -1

    # table name
    name = driver.find_element(By.XPATH, "//h1[@class='info-pane-name']").text

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

    try:
        show_more = driver.find_element(
            By.XPATH, "//a[@class='table-collapse-toggle more']"
        )

        driver.execute_script(
            "arguments[0].scrollIntoView();",
            show_more,
        )

        # sleep(5)

        show_more.click()
    except NoSuchElementException:
        pass

    table_rows = driver.find_elements(
        By.CSS_SELECTOR, ".table-wrapper tr.column-summary"
    )

    for each_row in table_rows:
        column_name = each_row.find_element(By.CSS_SELECTOR, "td.column-name").text
        description = each_row.find_element(
            By.CSS_SELECTOR, "td.column-description"
        ).text
        table_metadata[column_name] = description

    # print(f"table name = {name}")
    # print(f"description = {table_description}")
    # print(f"url = {table_url}")
    # print(f"download_table = {table_download}")
    # print(table_metadata)

    # return
    return (name, table_description, table_url, table_download, table_metadata)
