import logging
import sys
import os
from pathlib import Path

# Create log directory if it doesn't exist
log_dir = Path.home() / ".uranus"
os.makedirs(log_dir, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_dir / "uranus.log", mode="a"),
    ],
)

# Create logger
logger = logging.getLogger("uranus")