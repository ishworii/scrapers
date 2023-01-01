from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import utility
import os
import logging
import selenium

logging.basicConfig(
    filename="melbourne_scraping.log",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)


# Headless/incognito Chrome driver
chrome_options = Options()
chrome_options.add_argument("--incognito")
chrome_options.add_argument("start-maximized")
# chrome_options.add_argument("headless")
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), options=chrome_options
)

logging.info("Webdriver setup done.")


driver.get("https://data.melbourne.vic.gov.au/explore/?sort=modified")

sleep(2)

# # Set sleep time for the page to load on scroll
# SCROLL_PAUSE_TIME = 3

# # Get scroll height
# last_height = driver.execute_script("return document.body.scrollHeight")

# while True:
#     # Scroll down to bottom
#     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

#     # Wait to load page
#     sleep(SCROLL_PAUSE_TIME)

#     # Calculate new scroll height and compare with last scroll height
#     new_height = driver.execute_script("return document.body.scrollHeight")
#     if new_height == last_height:
#         break
#     last_height = new_height

# logging.info("Scrolling done.")

# all_divs = driver.find_elements(
#     By.CSS_SELECTOR, "a[class='ods-catalog-card__title-link']"
# )

# all_links = [x.get_attribute("href") for x in all_divs]


# all links
all_links = [
    "https://data.melbourne.vic.gov.au/explore/dataset/smart-bins-argyle-square/",
    "https://data.melbourne.vic.gov.au/explore/dataset/microlabs-accelerometer-sensor-data/",
    "https://data.melbourne.vic.gov.au/explore/dataset/guppy/",
    "https://data.melbourne.vic.gov.au/explore/dataset/melbourne-bike-share-station-readings-2011-2017/",
    "https://data.melbourne.vic.gov.au/explore/dataset/microlabs-sound-sensor-data/",
    "https://data.melbourne.vic.gov.au/explore/dataset/meshed-sensor-type-3/",
    "https://data.melbourne.vic.gov.au/explore/dataset/microlabs-co2-sensor-data/",
    "https://data.melbourne.vic.gov.au/explore/dataset/meshed-sensor-type-1/",
    "https://data.melbourne.vic.gov.au/explore/dataset/on-street-car-parking-sensor-data-2018/",
    "https://data.melbourne.vic.gov.au/explore/dataset/on-street-car-parking-sensor-data-2019/",
    "https://data.melbourne.vic.gov.au/explore/dataset/on-street-car-parking-sensor-data-2017/",
    "https://data.melbourne.vic.gov.au/explore/dataset/commingled-recycling-collected-at-degraves-st-hub-2016/",
    "https://data.melbourne.vic.gov.au/explore/dataset/mahlstedts-fire-plans-of-melbourne-1888/",
    "https://data.melbourne.vic.gov.au/explore/dataset/rooftops-with-environmental-retrofitting-opportunities-rooftop-project/",
    "https://data.melbourne.vic.gov.au/explore/dataset/thermal-image-2012/",
    "https://data.melbourne.vic.gov.au/explore/dataset/event-permits-2014-2018-including-film-shoots-photo-shoots-weddings-christmas-pa/",
    "https://data.melbourne.vic.gov.au/explore/dataset/2019-aerial-imagery/",
    "https://data.melbourne.vic.gov.au/explore/dataset/2019-false-colour-composite-aerial-imagery/",
    "https://data.melbourne.vic.gov.au/explore/dataset/2018-aerial-imagery-true-ortho/",
    "https://data.melbourne.vic.gov.au/explore/dataset/on-street-car-parking-sensor-data-2012/",
    "https://data.melbourne.vic.gov.au/explore/dataset/on-street-car-parking-sensor-data-2016/",
    "https://data.melbourne.vic.gov.au/explore/dataset/city-of-melbourne-3d-textured-mesh-photomesh-2018/",
    "https://data.melbourne.vic.gov.au/explore/dataset/pedestrian-network/",
    "https://data.melbourne.vic.gov.au/explore/dataset/bicycle-network/",
    "https://data.melbourne.vic.gov.au/explore/dataset/on-street-car-parking-sensor-data-2013/",
    "https://data.melbourne.vic.gov.au/explore/dataset/on-street-car-parking-sensor-data-2011/",
    "https://data.melbourne.vic.gov.au/explore/dataset/on-street-car-parking-sensor-data-2014/",
    "https://data.melbourne.vic.gov.au/explore/dataset/on-street-car-parking-sensor-data-2015/",
    "https://data.melbourne.vic.gov.au/explore/dataset/digital-surface-model/",
    "https://data.melbourne.vic.gov.au/explore/dataset/city-of-melbourne-3d-point-cloud-2018/",
]


logging.info(f"{len(all_links)} different tables found.")


# # iterate through each link
logging.info("Iterating through each table")
for each_link in all_links:
    os.chdir("C:\\Users\\PC\\Desktop\\upwork\\scraping_charles\\data\\processed_data")
    # create new tab for each new link, extract everything and return back
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])
    # get the new url
    driver.get(each_link)
    sleep(5)

    # check for number of records, if no of records is less than 200, skip this
    try:
        number_of_rows = driver.find_element(
            By.XPATH,
            "//div[@class='ods-filters']/h2/span[@class='ods-filters__count-number ng-binding']",
        ).text.replace(",", "")

    except selenium.common.exceptions.NoSuchElementException:
        continue

    if int(number_of_rows) >= 200:
        logging.info(f"{number_of_rows} rows in the table, scraping this table.")

        (
            table_name,
            table_description,
            table_metadata,
            table_url,
        ) = utility.extract_details(driver)
        download_link = utility.download_table(driver)

        logging.info(f"Extracted all the required data from table {table_url}")

        # save everything
        utility.save_everything(
            table_name, table_description, table_metadata, table_url, download_link
        )
        logging.info(f"Downloaded and saved files from table {table_name}")
    else:
        logging.info(f"{number_of_rows} less than 200, skipping this table.")

    # close and switch back to the original tab
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
