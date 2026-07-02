import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output" / "reports"
VECTORS_DIR = DATA_DIR / "vectors"
TEMPLATES_DIR = BASE_DIR / "templates"

# Create directories
for d in [DATA_DIR, OUTPUT_DIR, VECTORS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "true").lower() == "true"

GITHUB_RAW_BASE = "https://raw.githubusercontent.com/manymore13/report/main"
EASTMONEY_API = "https://reportapi.eastmoney.com"
