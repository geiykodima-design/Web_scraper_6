import logging
import sys
import os


def setup_logger(name: str) -> logging.Logger:
    # Визначаємо шлях до logs відносно кореня проєкту
    log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "logs", "parser.log")

    # Створюємо директорію logs, якщо вона не існує
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s]: %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ]
    )
    return logging.getLogger(name)
