import logging
import sys
from pathlib import Path

# Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_dir / "sales_engine.log", encoding='utf-8')
    ]
)

logger = logging.getLogger("sales_engine")

def get_logger(name):
    return logging.getLogger(f"sales_engine.{name}")
