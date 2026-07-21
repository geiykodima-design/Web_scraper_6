from typing import List
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup, Tag
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from models import Product
from utils.logger import setup_logger
from utils.selenium_utils import parse_hdd_block_prices

logger = setup_logger(__name__)

# Session setup
user_agent = UserAgent()
retry_strategy = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504], allowed_methods=["GET"])
session = requests.Session()
session.mount("https://", HTTPAdapter(max_retries=retry_strategy))
session.mount("http://", HTTPAdapter(max_retries=retry_strategy))

BASE_URL = "https://webscraper.io/"
HOME_URL = urljoin(BASE_URL, "test-sites/e-commerce/allinone/")
LAPTOP_URL = urljoin(BASE_URL, "test-sites/e-commerce/static/computers/laptops/")

HEADERS = {
    'User-Agent': user_agent.random,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}


class WebScraper:
    def __init__(self):
        self.session = session
        self.headers = HEADERS
        self.base_url = BASE_URL

    def get_home_products(self) -> List[Product]:
        try:
            response = self.session.get(HOME_URL, headers=self.headers, timeout=10, verify=True)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, features="html.parser")
            products = soup.select(".card-body")
            return [self.parse_single_product(product) for product in products]
        except requests.exceptions.RequestException as e:
            logger.error(f"Помилка при виконанні запиту до HOME_URL: {e}")
            return []
        except Exception as e:
            logger.warning(f"Неочікувана помилка в get_home_products(): {e}")
            return []

    def parse_single_product(self, product: Tag) -> Product:
        hdd_prices = parse_hdd_block_prices(product)
        return Product(
            title=product.select_one(".title")["title"],
            description=product.select_one(".description").text,
            price=float(product.select_one(".price").text.replace("$", "")),
            rating=int(product.select_one("[data-rating]")["data-rating"]),
            num_of_reviews=int(product.select_one(".review-count").text.split()[0]),
            additional_info={"hdd_prices": hdd_prices}
        )

    def get_laptop_page_products(self) -> List[Product]:
        try:
            response = self.session.get(LAPTOP_URL, headers=self.headers, timeout=10, verify=True)
            response.raise_for_status()
            first_page_soup = BeautifulSoup(response.content, features="html.parser")
            all_products = self.get_single_page_products(first_page_soup)
            num_pages = self.get_num_pages(first_page_soup)
            logger.info(f"Всього знайдено сторінок: {num_pages}")
            logger.info(f"Початок парсингу сторінки 1 з {num_pages}")

            for page_num in range(2, num_pages + 1):
                logger.info(f"Початок парсингу сторінки {page_num} з {num_pages}")
                response = self.session.get(LAPTOP_URL, headers=self.headers, params={"page": page_num}, timeout=10,
                                            verify=True)
                response.raise_for_status()
                next_page_soup = BeautifulSoup(response.content, features="html.parser")
                page_products = self.get_single_page_products(next_page_soup)
                all_products.extend(page_products)

            logger.info(f"Всього знайдено товарів: {len(all_products)}")
            return all_products
        except requests.exceptions.RequestException as e:
            logger.error(f"Помилка при завантаженні сторінок: {e}")
            return []
        except Exception as e:
            logger.warning(f"Неочікувана помилка: {e}")
            return []

    def get_num_pages(self, page_soup: Tag) -> int:
        pagination = page_soup.select_one(".pagination")
        return int(pagination.select("li")[-2].text) if pagination else 1

    def get_single_page_products(self, page_soup: Tag) -> List[Product]:
        products = page_soup.select(".card-body")
        return [self.parse_single_product(product) for product in products]