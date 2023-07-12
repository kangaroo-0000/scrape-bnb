import time
import re
import traceback
import getpass
import pandas as pd
from dataclasses import dataclass, field
from typing import List
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.select import By
from selenium.webdriver.common.action_chains import ActionChains

URL = "https://www.airdna.co/vacation-rental-data/app/login"

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
    def __init__(self, username, password, driver):
        self.username = username
        self.password = password
        self.driver = driver
        self.cities = []

    def login(self):
        self.driver.get(URL)
        time.sleep(10)
        self.driver.find_element(by=By.XPATH, value='//input[@id="login-email"]').send_keys(self.username)
        self.driver.find_element(by=By.XPATH, value='//input[@id="login-password"]').send_keys(self.password)
        self.driver.find_element(
        by=By.XPATH,
        value='//button[@class="MuiButtonBase-root MuiButton-root MuiButton-contained MuiButton-containedPrimary MuiButton-sizeMedium MuiButton-containedSizeMedium css-ppsdaf"]').click()
        time.sleep(10)

    def get_subscribed_cities(self):
        # trigger the drop-down menu event by clicking the select tag to reveal subscriptions
        self.driver.find_element(
            by=By.XPATH,
            value='//div[@class="location-bar__city-select css-2b097c-container"]',
        ).click()
        html = self.driver.find_element(
            by=By.XPATH, value='//div[@class=" css-s67jrt-menu"]'
        ).get_attribute("innerHTML")
        subscribed_cities_info = re.findall(
            '\B id="(\S+)" tabindex="-1">(\w.+?)<\/div>\B', html
        )
        print(f"you have subscribed to {len(subscribed_cities_info)} cities. These are the cities: {subscribed_cities_info}")

        # click again to close the drop-down menu
        self.driver.find_element(
            by=By.XPATH,
            value='//div[@class="location-bar__city-select css-2b097c-container"]',
        ).click()
        for subscribed_city_info in subscribed_cities_info:
            self.cities.append(
                City(subscribed_city_info[1], f'//div[@id="{subscribed_city_info[0]}"]', [])
            )

    def get_zipcodes(self):
        for city in self.cities:
            zipcodes = []
            # iterate through each city and click on the city to reveal zipcodes for that city
            self.driver.find_element(
                by=By.XPATH,
                value='//div[@class="location-bar__city-select css-2b097c-container"]',
            ).click()
            self.driver.find_element(by=By.XPATH, value=city.xpath).click()
            time.sleep(2)
    
            self.driver.find_element(
                by=By.XPATH,
                value='//div[@class="location-bar__region-select css-2b097c-container"]',
            ).click()
            html = self.driver.find_element(
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


    def scrape(self, city_name, input_zipcode):
        # TODO: click on the city and zipcode to reveal airbnb dots
        # verify if city name is in City list:
        city = next((city for city in self.cities if city.city.lower() == city_name.lower()), None)
        if city is None:
            print("city name not found")
            return
        # verify if zipcode is in Zipcode list:
        zipcode = next((zipcode for zipcode in city.zipcode_list if zipcode.zipcode == input_zipcode), None)
        if zipcode is None:
            print("zipcode not found")
            return

        # Click on city
        self.driver.find_element(
            by=By.XPATH,
            value='//div[@class="location-bar__city-select css-2b097c-container"]').click()
        city_element = self.browser.find_element(by=By.XPATH, value=city.xpath)
        city_element.click()
        time.sleep(2)

        # Click on zipcode
        self.driver.find_element(
            by=By.XPATH,
            value='//div[@class="location-bar__region-select css-2b097c-container"]').click()
        zipcode_element = self.browser.find_element(By.XPATH, zipcode.xpath)
        zipcode_element.click()
        time.sleep(2) 
        
        dots = self.driver.find_elements(
            by=By.XPATH,
            value='//img[@alt and @src="https://maps.gstatic.com/mapfiles/transparent.png"]/parent::div'
        )
        print(dots)

        bnbs = []
        for dot in dots:
            time.sleep(4)
            self.driver.execute_script("arguments[0].scrollIntoView(true);", dot)
            time.sleep(1)
            ActionChains(self.driver).move_to_element(dot).click(dot).perform()
            time.sleep(1)

            id = self.driver.find_element(
                by=By.XPATH, value='//div[@class="info-window"]'
            ).get_attribute("data-id")
            id = re.findall("\d.+", id)
            print("Airbnb ID: " + id[0])
            try:
                name = (
                    self.driver.find_element(
                        by=By.XPATH,
                        value=f'//a[@class="info-window__property-link"][@href="https://www.airbnb.com/rooms/{id[0]}"]',
                    ).get_attribute("textContent")
                ).strip()
            except:
                name = "N/A"

            try:
                avg = (
                    self.driver.find_element(
                        by=By.XPATH,
                        value='//div/p[contains(text(), "Avg. Daily Rate")]/preceding-sibling::p[@class="info-window__statistics-value"]',
                    ).get_attribute("textContent")
                ).strip()
            except:
                avg = "N/A"

            try:
                occupancy = (
                    self.driver.find_element(
                        by=By.XPATH,
                        value='//div/p[contains(text(), "Occupancy")]/preceding-sibling::*[position()=2]',
                    ).get_attribute("textContent")
                ).strip()
            except:
                occupancy = "N/A"

            try: 
                bedroom = self.driver.find_element(
                    by=By.XPATH,
                    value='//p[@class="info-window__property-description info-window__property-description--beds"]/span',
                ).get_attribute("textContent")
            except:
                bedroom = "N/A"

            try:
                rating = self.driver.find_element(
                    by=By.XPATH,
                    value='//p[@class="info-window__property-description info-window__property-description--ratings"]/span',
                ).get_attribute("textContent")
            except:
                rating = "N/A"

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

        df = pd.DataFrame([vars(bnb) for bnb in bnbs])
        print(df)
        df.drop_duplicates(inplace=True)
        df = df[df["rating_count"] < 20]
        df["Revenue"] = df["ADR"] * df["Occupancy"] / 100
        df["Max Rent"] = df["Revenue"] / 2
        df["Avg. Max Rent"] = df["Max Rent"].mean()
        df["Avg. Occupancy"] = df["Occupancy"].mean()
        df["Avg. ADR"] = df["ADR"].mean()
        df.to_excel(f"{city_name}_{zipcode}_output.xlsx")


if __name__ == "__main__":
    options = Options()
    options.add_argument("--enable-javascript")
    # options.add_argument("--headless")
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        # prompt for email and password
        email = input("Enter email: ")
        password = getpass.getpass("Enter password: ")
        bot = AirdnaBot(email, password, driver)
        print("logging in...")
        bot.login()
        print("getting subscribed cities...")
        bot.get_subscribed_cities()
        print("getting zipcodes for each city...")
        bot.get_zipcodes()
        # prompt user to enter city and zipcode
        city_name = input("Enter city name: ")
        zipcode = input("Enter zipcode: ")
        bot.scrape(city_name, zipcode)
    except Exception as e:
        print("".join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)))
    finally:
        driver.quit()
