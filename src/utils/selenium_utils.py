from selenium import webdriver
from selenium.webdriver.common.by import By
from urllib.parse import urljoin
from bs4 import Tag
from typing import Dict
from utils.logger import setup_logger

logger = setup_logger(__name__)
_driver: webdriver.Chrome | None = None


def get_driver() -> webdriver.Chrome:
    return _driver


def set_driver(new_driver: webdriver.Chrome) -> None:
    global _driver
    _driver = new_driver


def parse_hdd_block_prices(product_soup: Tag) -> Dict[str, float]:
    absolute_url = urljoin("https://webscraper.io/", product_soup.select_one(".title")["href"])
    driver = get_driver()
    driver.get(absolute_url)

    swatches = driver.find_element(By.CLASS_NAME, "swatches")
    buttons = swatches.find_elements(By.TAG_NAME, "button")

    prices = {}
    for button in buttons:
        if not button.get_property("disabled"):
            button.click()
            prices[button.get_property("value")] = float(
                driver.find_element(By.CLASS_NAME, "price").text.replace("$", "")
            )
    return prices
