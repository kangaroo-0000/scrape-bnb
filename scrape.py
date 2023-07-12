from importlib.metadata import files
import time
import re
import click
import random
from dataclasses import dataclass, asdict, field
import pandas as pd
from typing import List
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.select import By

URL = "https://www.airdna.co/vacation-rental-data/app/login"
email = "chungmop@uci.edu"
password = "Hambeck0831"


# @click.command
# @click.option("-c", "--city_name", type=str)
# @click.option("-z", "--zipcode", type=int)
def browser_init():
    options = Options()
    options.add_argument("--enable-javascript")
    browser = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )
    browser.get(URL)
    browser.find_element(
        by=By.XPATH, value='//input[@id="registration-email"]'
    ).send_keys(email)
    browser.find_element(
        by=By.XPATH, value='//input[@id="registration-password"]'
    ).send_keys(password)
    browser.find_element(
        by=By.XPATH,
        value='//button[@class="sc-13d50qi-0 gYMQam sc-3z4g7g-0 bTqrnB button sc-l7ox60-5 klCvCH"]',
    ).click()
    time.sleep(10)

    cities = []
    # trigger the drop-down menu event by clicking the select tag to reveal subscriptions
    browser.find_element(
        by=By.XPATH,
        value='//div[@class="location-bar__city-select css-2b097c-container"]',
    ).click()
    html = browser.find_element(
        by=By.XPATH, value='//div[@class=" css-s67jrt-menu"]'
    ).get_attribute("innerHTML")
    subscribed_cities_info = re.findall(
        '\B id="(\S+)" tabindex="-1">(\w.+?)<\/div>\B', html
    )
    print(f"you have subscribed to {len(subscribed_cities_info)} cities. These are the cities: {subscribed_cities_info}")
    print("getting zipcodes for each city...")

    browser.find_element(
        by=By.XPATH,
        value='//div[@class="location-bar__city-select css-2b097c-container"]',
    ).click()
    for subscribed_city_info in subscribed_cities_info:
        cities.append(
            City(subscribed_city_info[1], f'//div[@id="{subscribed_city_info[0]}"]', [])
        )
    for city in cities:
        zipcodes = []
        browser.find_element(
            by=By.XPATH,
            value='//div[@class="location-bar__city-select css-2b097c-container"]',
        ).click()
        browser.find_element(by=By.XPATH, value=city.xpath).click()
        time.sleep(2)
        browser.find_element(
            by=By.XPATH,
            value='//div[@class="location-bar__region-select css-2b097c-container"]',
        ).click()
        html = browser.find_element(
            by=By.XPATH, value='//div[@class=" css-s67jrt-menu"]'
        ).get_attribute("innerHTML")
        subscribed_zipcodes = re.findall(
            '\B id="(\S+)" tabindex="-1">Zip code: (\w.+?)<\/div>\B', html
        )
        for subscribed_zipcode in subscribed_zipcodes:
            zipcodes.append(
                Zipcode(
                    subscribed_zipcode[1], f'//div[@id="{subscribed_zipcode[0]}"]', []
                )
            )
        city.zipcode_list = zipcodes
    print(cities)

    # prompt user scrape preference here
    print("Which city would you like to scrape? Please enter the city name followed by the zipcode.")



def random_wait():
    return random.randint(6, 10)


def print_as_df():
    pass


@dataclass
class Airbnb:
    id: int
    name: str  # f'//a[@class="info-window__property-link"][@href="https://www.airbnb.com/rooms/{id}"]'  get text content
    ADR: int  # '//p[text()="Avg. Daily Rate"]/preceding-sibling::p[@class="info-window__statistics-value"]'
    Occupancy: int  # '//p[text()="Occupancy"]/preceding-sibling::p[@class="info-window__statistics-value"]'
    bedroom_count: int  # '//p[@class="info-window__property-description info-window__property-description--beds"]/span/text()' get text content
    rating_count: int  # '//p[@class="info-window__property-description info-window__property-description--ratings"]/span/text()'


@dataclass
class Zipcode:
    zipcode: str
    xpath: str
    airbnb_list: List[Airbnb] = field(default_factory=list)


@dataclass
class City:
    city: str
    xpath: str
    zipcode_list: List[Zipcode] = field(default_factory=list)


class AirdnaBot:
    def __init__(username, pw, driver):
        pass

    def get_subscribed_cities(self):
        pass

    def get_zipcodes(self):
        pass

    def get_bnbs_in(self, city, zipcode):
        pass


if __name__ == "__main__":
    browser_init()
