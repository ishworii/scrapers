from time import sleep
from selenium.webdriver.common.by import By
import os
import logging
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from time import sleep
import os
import json
import requests
import string
import requests
import pandas as pd




def extract_details(driver):
    try:
        # check for number of rows
        tables_button = driver.find_element(By.XPATH, "//a[@data-ga='Table']")
        tables_button.click()
        number_of_rows = driver.find_element(
            By.CSS_SELECTOR, "div.dataTables_info"
        ).text.split(" ")
        number_of_rows = int([x for x in number_of_rows if x.isdigit()][-1])
        if number_of_rows < 190:
            return -1
    except NoSuchElementException:
        pass

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
    try:
        api_button = driver.find_element(
            By.XPATH,
            "//button[@class='btn datagovsg-btn btn-right btn-blue desktop-only ga-dataset-data-api']",
        )
        api_button.click()
        sleep(5)

    except NoSuchElementException:
        return -1

    table_download = driver.find_element(
        By.XPATH, "//*[@id='collapse-querying']/div/p/code/a"
    ).get_attribute("href")

    # print(f"table name = {name}")
    # print(f"description = {table_description}")
    # print(f"url = {table_url}\n")
    # print(f"download_table = {table_download}")
    # print(table_metadata)

    # return
    return (name, table_description, table_url, table_download, table_metadata)


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
    table_download = table_download.split("&")
    table_download = table_download[0] + "&limit=20000"
    filename = f"{table_name}.csv"
    response = requests.get(table_download).json()
    # print(response.keys())
    # exit(-1)
    df = pd.DataFrame(response["result"]["records"])
    df.to_csv(filename, index=False)

    # write to tablename_URLtotable.txt
    with open(f"{table_name}_URLtotable.txt", "w") as f:
        f.write(table_url)

    # write metadata to a json file
    with open(f"{table_name}_metadata.json", "w", encoding="utf-8") as f:
        json.dump(table_metadata, f)

    # write to a description file
    with open(f"{table_name}_description.txt", "w") as f:
        f.writelines(table_description)
