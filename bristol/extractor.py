from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os
import logging
import utility
import json


logging.basicConfig(
    filename="logs.log",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)


def setup():
    # Headless/incognito Chrome driver
    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("start-maximized")
    # chrome_options.add_argument("headless")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options
    )

    logging.info("Webdriver setup done.")

    driver.get("https://www.google.com/")

    sleep(2)

    return driver


def main(driver, filename):
    try:
        # load all the links to all_datasets
        with open(filename, "r") as file:
            all_datasets = json.load(file)

        logging.info(f"{len(all_datasets)} different tables found.")

        scrapped = 0
        for each_link in all_datasets:
            if each_link["scraped"]:
                scrapped += 1

        logging.info(
            f"Scraped {scrapped} tables and {len(all_datasets) - scrapped} are remaining.."
        )

        # # iterate through each link
        logging.info("Iterating through each table")
        size = len(all_datasets)
        for index, each_link in enumerate(all_datasets):
            if each_link["scraped"]:
                continue
            logging.info(f"Scraping {index+1} / {size} table..")
            os.chdir(
                "C:\\Users\\Ishwor\\Desktop\\upwork\\scraping_charles\\data\\2nd_batch\\bristol"
            )

            # create new tab for each new link, extract everything and return back
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[1])
            # get the new url
            driver.get(each_link["link"])
            sleep(3)

            # extract details

            details = utility.extract_details(driver)
            if details == -1:
                each_link["scraped"] = True
                # close and switch back to the original tab
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                continue

            (
                table_name,
                table_description,
                table_url,
                table_download,
                table_metadata,
            ) = details

            logging.info(f"Extracted all the required data from table {table_url}")

            # save everything
            ret_val = utility.save_everything(
                table_name,
                table_description,
                table_url,
                table_download,
                table_metadata,
            )
            if ret_val == -1:
                return -1

            logging.info(f"Downloaded and saved files from table {table_name}")
            each_link["scraped"] = True

            # close and switch back to the original tab
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

    except (KeyboardInterrupt, Exception) as e:
        each_link["scraped"] = True

        logging.info(f"{e} in extractor")

        # save the current state json to the file
        os.chdir("C:\\Users\\Ishwor\\Desktop\\upwork\\scraping_charles\\bristol")
        with open(filename, "w") as file:
            json.dump(all_datasets, file)
        logging.info(f"Error {e} occured...restarting the program again...")
        driver.close()
        return -1


def all_scraped(filename):
    with open(filename, "r") as file:
        data = json.load(file)
    for each_row in data:
        if not each_row["scraped"]:
            return False
    return True


if __name__ == "__main__":
    filename = "C:\\Users\\Ishwor\\Desktop\\upwork\\scraping_charles\\bristol\\links_bristol.json"

    limit = 100
    count = 0
    while count < limit:
        sleep(2)
        driver = setup()
        retval = main(driver, filename)
        if retval == -1:
            count += 1

        if all_scraped(filename):
            break
