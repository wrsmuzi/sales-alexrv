import os
from dotenv import load_dotenv
from supabase import create_client, Client
from sales_engine.core.logger import get_logger

logger = get_logger("database")

load_dotenv()

import os
import traceback
from dotenv import load_dotenv
from supabase import create_client, Client
from sales_engine.core.logger import get_logger
import httpx

logger = get_logger("database")

load_dotenv()

class SupabaseManager:
    def __init__(self):
        logger.info("--- DEBUG: Starting Supabase Diagnostics ---")
        
        # 1. Логуємо версії бібліотек, щоб зрозуміти, чи немає конфлікту
        try:
            import supabase
            import httpx
            logger.info(f"DEBUG: supabase version: {supabase.__version__}")
            logger.info(f"DEBUG: httpx version: {httpx.__version__}")
        except Exception as e:
            logger.error(f"DEBUG: Could not get versions: {e}")

        # 2. Перевіряємо системні змінні, які можуть провокувати помилку проксі
        proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'NO_PROXY']
        for var in proxy_vars:
            val = os.environ.get(var)
            logger.info(f"DEBUG: ENV {var} = {val}")

        # РАДИКАЛЬНО ПРИМУСОВО ВИМИКАЄМО ВСЕ, що стосується проксі
        os.environ['HTTP_PROXY'] = ''
        os.environ['HTTPS_PROXY'] = ''
        os.environ['http_proxy'] = ''
        os.environ['https_proxy'] = ''
        os.environ['NO_PROXY'] = '*'
        
        self.url = os.environ.get("SUPABASE_URL", "")
        self.key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
        
        if not self.url or not self.key:
            logger.error("SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY is missing in .env")
            raise Exception("Supabase credentials missing in .env")
            
        try:
            logger.info("Attempting to create Supabase client...")
            self.client: Client = create_client(self.url, self.key)
            logger.info("✅ Successfully connected to Supabase.")
        except Exception as e:
            # ВИВОДИМО ПОВНИЙ ТЕХНІЧНИЙ СЛЕД (TRACEBACK)
            logger.error("❌ CRITICAL ERROR DURING SUPABASE INIT:")
            logger.error(traceback.format_exc())
            raise e

    def get_client(self) -> Client:
        return self.client

try:
    supabase_manager = SupabaseManager()
    supabase = supabase_manager.get_client()
except Exception as e:
    logger.critical(f"Critical failure initializing database: {e}")
    supabase = None


    def get_client(self) -> Client:
        return self.client

try:
    supabase_manager = SupabaseManager()
    supabase = supabase_manager.get_client()
except Exception as e:
    logger.critical(f"Critical failure initializing database: {e}")
    supabase = None
