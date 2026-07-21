import csv
import os
from typing import List
from models import Product, PRODUCT_FIELDS


def write_products_to_csv(products: List[Product]) -> None:
    # Визначаємо шлях до data відносно кореня проєкту
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "data", "products.csv")

    # Створюємо директорію data, якщо вона не існує
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)

    with open(csv_path, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(PRODUCT_FIELDS)
        writer.writerows([product.to_tuple() for product in products])