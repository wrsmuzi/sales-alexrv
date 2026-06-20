import os
import requests
from sales_engine.core.database import supabase
from sales_engine.core.logger import get_logger

logger = get_logger("telegram")

class TelegramNotifier:
    def __init__(self):
        logger.info("Initializing TelegramNotifier...")
        self.token = os.environ.get("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    async def send_notification(self, message: str):
        if not self.token or not self.chat_id:
            logger.warning("Telegram credentials missing. Skipping notification.")
            return

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": message, "parse_mode": "HTML"}
        try:
            logger.debug(f"Sending Telegram notification: {message[:50]}...")
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info("Successfully sent Telegram notification.")
        except Exception as e:
            logger.error(f"Telegram Error: {e}")

telegram_bot = TelegramNotifier()
