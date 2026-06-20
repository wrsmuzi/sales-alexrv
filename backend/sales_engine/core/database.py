import os
import traceback
from dotenv import load_dotenv
from supabase import create_client, Client
from sales_engine.core.logger import get_logger
import httpx
original_httpx_client_init = httpx.Client.__init__
def patched_httpx_client_init(self, *args, **kwargs):
    try:
        original_httpx_client_init(self, *args, **kwargs)
    except TypeError as e:
        if 'proxy' in str(e):
            kwargs.pop('proxy', None)
            original_httpx_client_init(self, *args, **kwargs)
        else:
            raise e
httpx.Client.__init__ = patched_httpx_client_init

logger = get_logger("database")

load_dotenv()

# Set Playwright environment variables to bypass host requirement checks
os.environ['PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS'] = 'true'

class SupabaseManager:

    def __init__(self):
        logger.info("--- DEBUG: Starting Supabase Diagnostics ---")
        
        # 1. Log library versions
        try:
            import supabase
            logger.info(f"DEBUG: supabase version: {supabase.__version__}")
            logger.info(f"DEBUG: httpx version: {httpx.__version__}")
        except Exception as e:
            logger.error(f"DEBUG: Could not get versions: {e}")

        # 2. Check environment variables
        proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'NO_PROXY']
        for var in proxy_vars:
            val = os.environ.get(var)
            logger.info(f"DEBUG: ENV {var} = {val}")

        # Forcefully disable all proxy settings to prevent the 'proxy' keyword argument error
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
            # We use create_client from supabase. 
            # If the proxy error persists, it's happening inside the supabase/gotrue library
            self.client: Client = create_client(self.url, self.key)
            logger.info("✅ Successfully connected to Supabase.")
        except Exception as e:
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
