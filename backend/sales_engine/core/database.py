import os
import traceback
from dotenv import load_dotenv
from supabase import create_client, Client
import httpx

# Monkeypatch httpx.Client to handle 'proxy' argument errors
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

load_dotenv()

class SupabaseManager:
    def __init__(self):
        print("\n--- [DATABASE] STARTING INIT ---")
        
        # Force disable proxies
        os.environ['HTTP_PROXY'] = ''
        os.environ['HTTPS_PROXY'] = ''
        os.environ['http_proxy'] = ''
        os.environ['https_proxy'] = ''
        os.environ['NO_PROXY'] = '*'
        
        self.url = os.environ.get("SUPABASE_URL", "")
        self.key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
        
        if not self.url or not self.key:
            print("❌ [DATABASE] ERROR: SUPABASE_URL or KEY is missing!")
            self.client = None
            return
            
        try:
            print(f"Attempting to connect to: {self.url[:15]}...")
            self.client: Client = create_client(self.url, self.key)
            print("✅ [DATABASE] SUCCESSFULLY CONNECTED")
        except Exception as e:
            print(f"❌ [DATABASE] CRITICAL ERROR: {e}")
            print(traceback.format_exc())
            self.client = None

    def get_client(self) -> Client:
        return self.client

try:
    supabase_manager = SupabaseManager()
    supabase = supabase_manager.get_client()
except Exception as e:
    print(f"❌ [DATABASE] FATAL FAILURE: {e}")
    supabase = None
