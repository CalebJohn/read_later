import os

SITE_HOST = os.getenv("SITE_HOST", "localhost")
SITE_PORT = os.getenv("SITE_PORT", "5000")
SITE_URL = os.getenv("SITE_URL", f"http://{SITE_HOST}:{SITE_PORT}")
APP_DIR = os.getenv("APP_DIR", "./")
