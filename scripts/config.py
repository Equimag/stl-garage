# STL GARAGE — BOT & CHANNEL CONFIGURATION
import os
from pathlib import Path

# Load local .env if present (git-ignored for security)
# Checks both current directory and parent directory
for env_candidate in [
    Path(__file__).resolve().parent / ".env",
    Path(__file__).resolve().parent.parent / ".env",
    Path("/opt/stl-news-poster/.env")
]:
    if env_candidate.exists():
        try:
            with open(env_candidate, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ.setdefault(k.strip(), v.strip())
            break
        except Exception:
            pass

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
BOT_USERNAME = "STLGarage_bot"
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "-1002753288392"))
CHANNEL_USERNAME = "stl_garage"
CHANNEL_URL = "https://t.me/stl_garage"
BOOSTY_URL = "https://boosty.to/stl_garage/donate"

# Base site URL on GitHub Pages
SITE_URL = "https://revermag.github.io/stl-garage/"

# Google Gemini API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
