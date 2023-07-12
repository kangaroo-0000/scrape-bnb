from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.select import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import xlsxwriter
import pandas as pd
import time
from dataclasses import dataclass
import re
from selenium.webdriver.chrome.options import Options


@dataclass
class Airbnb:
    id: str
    name: str
    ADR: str
    Occupancy: str
    bedroom_count: str
    rating_count: str


URL = "https://www.airdna.co/vacation-rental-data/app/login"
email = "chungmop@uci.edu"
password = "Hambeck0831"

"""
hover to element, click on element to reveal airbnb info. 
"""


def browser_init():
    options = Options()
    options.add_argument("--enable-javascript")
    browser = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )
    browser.get(URL)
    time.sleep(10)
    # send login email to input field
    browser.find_element(
        by=By.XPATH, value='//input[@id="login-email"]'
    ).send_keys(email)
    # send login password to input field
    browser.find_element(
        by=By.XPATH, value='//input[@id="login-password"]'
    ).send_keys(password)
    # click login button
    browser.find_element(
        by=By.XPATH,
        value='//button[@class="MuiButtonBase-root MuiButton-root MuiButton-contained MuiButton-containedPrimary MuiButton-sizeMedium MuiButton-containedSizeMedium css-ppsdaf"]',
    ).click()
    time.sleep(10)

    # test click on location bar, not yet tested since my subscription is expired
    # browser.find_element(
    #     by=By.XPATH,
    #     value='//div[@class="location-bar__city-select css-2b097c-container"]',
    # ).click()
    # browser.find_element(
    #     by=By.XPATH, value='//div[@id="react-select-2-option-0-0"]'
    # ).click()
    # time.sleep(2)

    # test click on region bar
    browser.find_element(
        by=By.XPATH,
        value='//div[@class="location-bar__region-select css-2b097c-container"]',
    ).click()
    print(browser.find_element(by=By.XPATH, value='//div[@class=" css-s67jrt-menu"]'
    ).get_attribute("innerHTML"))
    # browser.find_element(
    #     by=By.XPATH, value='//div[@id="react-select-3-option-1-1"]'
    # ).click()
    time.sleep(10)

    # select/click on a region so the map element is revealed
    # write page source to file
    with open("html.txt", "w+", encoding="UTF-8") as f:
        f.write(browser.page_source)
    dots = browser.find_elements(
    by=By.XPATH,
    value='//img[@alt and @src="https://maps.gstatic.com/mapfiles/transparent.png"]/parent::div'
    )
    print(dots)

    bnbs = []
    for dot in dots:
        time.sleep(5)
        browser.execute_script("arguments[0].scrollIntoView(true);", dot)
        time.sleep(1)
        ActionChains(browser).move_to_element(dot).click(dot).perform()
        time.sleep(1)

        # doc = browser.execute_script(
        #     "return new XMLSerializer().serializeToString(document)"
        # )
        # with open("html2.txt", "w+", encoding="UTF-8") as f:
        #     f.write(doc)
        # break

        id = browser.find_element(
            by=By.XPATH, value='//div[@class="info-window"]'
        ).get_attribute("data-id")
        id = re.findall("\d.+", id)
        print("Airbnb ID: " + id[0])

        name = (
            browser.find_element(
                by=By.XPATH,
                value=f'//a[@class="info-window__property-link"][@href="https://www.airbnb.com/rooms/{id[0]}"]',
            ).get_attribute("textContent")
        ).strip()

        avg = (
            browser.find_element(
                by=By.XPATH,
                value='//div/p[contains(text(), "Avg. Daily Rate")]/preceding-sibling::p[@class="info-window__statistics-value"]',
            ).get_attribute("textContent")
        ).strip()

        occupancy = (
            browser.find_element(
                by=By.XPATH,
                value='//div/p[contains(text(), "Occupancy")]/preceding-sibling::*[position()=2]',
            ).get_attribute("textContent")
        ).strip()

        bedroom = browser.find_element(
            by=By.XPATH,
            value='//p[@class="info-window__property-description info-window__property-description--beds"]/span',
        ).get_attribute("textContent")

        rating = browser.find_element(
            by=By.XPATH,
            value='//p[@class="info-window__property-description info-window__property-description--ratings"]/span',
        ).get_attribute("textContent")

        bnbs.append(
            Airbnb(
                id=id[0],
                name=name,
                ADR=int(avg.replace(",", "").strip("$")),
                Occupancy=int(occupancy.strip("%")),
                bedroom_count=int(bedroom),
                rating_count=int(rating.strip("()")),
            )
        )
    df = pd.DataFrame(bnbs)
    print(df)
    df.drop_duplicates()
    df = df.filter(["rating_count" < 20])
    df["Revenue"] = df["ADR"] * df["Occupancy"] / 100
    df["Max Rent"] = df["Revenue"] / 2
    df["Avg. Max Rent"] = df["Max Rent"].mean()
    df["Avg. Occupancy"] = df["Occupancy"].mean()
    df["Avg. ADR"] = df["ADR"].mean()
    df.to_excel("output.xlsx")



if __name__ == "__main__":
    browser_init()