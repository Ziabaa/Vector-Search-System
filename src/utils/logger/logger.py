import logging
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler

from telegram_handler import TelegramHandler


# ===== CREATE LOG DIRECTORY =====

BASE_DIR = Path(__file__).resolve().parents[3]

LOG_DIR = BASE_DIR / "LogFiles"

LOG_DIR.mkdir(exist_ok=True)

# ===== LOG FILE NAME =====

current_date = datetime.now().strftime("%Y-%m-%d")

log_file = LOG_DIR / f"{current_date}.log"

# ===== LOGGER =====

logger = logging.getLogger("app")

logger.setLevel(logging.INFO)

# ===== FORMAT =====

formatter = logging.Formatter(
    "[%(asctime)s] "
    "[%(levelname)s] "
    "%(name)s - %(message)s"
)

# ===== CONSOLE =====

console_handler = logging.StreamHandler()

console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# ===== FILE =====

file_handler = RotatingFileHandler(
    filename=log_file,
    maxBytes=10 * 1024 * 1024,
    backupCount=5,
    encoding="utf-8"
)

file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

# ===== TELEGRAM =====

telegram_handler = TelegramHandler(level=logging.ERROR)

telegram_handler.setFormatter(formatter)

# ===== REGISTER HANDLERS =====

logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.addHandler(telegram_handler)
