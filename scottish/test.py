from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By


# Headless/incognito Chrome driver
chrome_options = Options()
chrome_options.add_argument("--incognito")
chrome_options.add_argument("start-maximized")
# chrome_options.add_argument("headless")
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), options=chrome_options
)

driver.get(
    "https://www.opendata.nhs.scot/dataset/drug-and-alcohol-treatment-waiting-times/resource/c16b6f2a-fc4d-4542-bb39-a0861b880b9e"
)

table_rows = driver.find_element(
    By.CSS_SELECTOR, "div.module-content table"
).find_elements(By.CSS_SELECTOR, "tbody tr")

for each_row in table_rows:
    tds = each_row.find_elements(By.CSS_SELECTOR, "td")
    column_name = tds[0].text
    description = tds[-2].text
    print(column_name, description)
