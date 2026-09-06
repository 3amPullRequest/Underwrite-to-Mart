"""
Adapted from https://github.com/manuelcaccone/NLP-Actuarial-Loss-Modeling/blob/main/notebooks/0_DATA_SCRAPING_NMVCCS.ipynb

Handle the Config for the NMVCCS scraper.
"""

import json
import os
import time

import urllib3
from curl_cffi import requests as cffi_requests
from dagster import ConfigurableResource
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

from ..constants import BASE_URL_NMVCCS

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Origin": "https://crashviewer.nhtsa.dot.gov",
    "Referer": "https://crashviewer.nhtsa.dot.gov/LegacyNMVCCS",
}


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ScraperConfig(ConfigurableResource):
    """Handle the Config for the nmvcccs scraper"""

    output_dir: str = r"data/bronze/raw_nmvccs"
    max_pages: int = 174
    
    sql_query: str = "[YOUR_ANONYMIZED_SQL_QUERY]"

    # Secrets (injected via EnvVar in definitions.py)
    session_id: str | None = None
    tracking_token: str | None = None
    nhtsa_token: str | None = None
    bm_token: str | None = None
    rt_token: str | None = None

    # Proxy settings
    proxy_host: str | None = None
    proxy_port: str | None = None
    proxy_username: str | None = None
    proxy_password: str | None = None

    def fetch_cookies_with_playwright(self) -> dict[str, str]:
        with Stealth().use_sync(sync_playwright()) as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=HEADERS["User-Agent"],
                viewport={"width": 1920, "height": 1080},
            )
            page = context.new_page()

            page.goto(BASE_URL_NMVCCS, wait_until="networkidle")
            time.sleep(5)

            raw_cookies = context.cookies()
            browser.close()
            return {c["name"]: c["value"] for c in raw_cookies}

    def get_cookies(self) -> dict[str, str]:
        """Returns session cookies, fetching via Playwright if manual tokens aren't provided."""
        cookie_cache_path = os.path.join(self.output_dir, "session_cookies.json")
        os.makedirs(self.output_dir, exist_ok=True)

        # Check if manual tokens are provided (e.g., via EnvVar)
        if self.tracking_token and self.nhtsa_token and self.bm_token and self.rt_token:
            cookies = {
                "ak_bmsc": self.tracking_token,
                "NHTSA": self.nhtsa_token,
                "bm_sv": self.bm_token,
                "RT": self.rt_token,
            }
            if self.session_id:
                cookies["ASP.NET_SessionId"] = (
                    self.session_id
                )  # BUG FIX: Removed trailing comma

            # Cache manual tokens for downstream assets
            with open(cookie_cache_path, "w") as f:
                json.dump(cookies, f)
            return cookies

        # Fallback. Check cache or fetch via Playwright.
        if os.path.exists(cookie_cache_path):
            with open(cookie_cache_path, "r") as f:
                return json.load(f)
        
        return self.fetch_cookies_with_playwright()

    def get_session(self) -> cffi_requests.Session:
        """Creates the current session."""
        session = cffi_requests.Session(impersonate="chrome131")

        if self.proxy_host and self.proxy_port:
            if self.proxy_username and self.proxy_password:
                proxy_url = f"http://{self.proxy_username}:{self.proxy_password}@{self.proxy_host}:{self.proxy_port}"
            else:
                proxy_url = (
                    f"http://{self.proxy_host}:{self.proxy_port}"  # Handle missing auth
                )

            session.proxies = {"http": proxy_url, "https": proxy_url}
            session.verify = False

        return session
