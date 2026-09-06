import os
import sys

# Add project root to sys.path (one level up from /notebooks)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import random
import time

from curl_cffi import requests as cffi_requests

from src.pipeline.constants import BASE_URL_NMVCCS, XML_BASE_URL_NMVCCS
from src.pipeline.logic.bronze.scrape_nmvccs import is_valid_xml
from src.pipeline.resources.scrape_nmvccs import ScraperConfig


def download_single_xml(
    session: cffi_requests.Session, case_id: str, output_dir: str
) -> tuple[str, bool, str]:
    """_summary_

    Args:
        session (requests.Session): _description_
        case_id (str): _description_
        output_dir (str): _description_

    Returns:
        tuple[str, bool, str]: _description_
    """

    # # Warm up the session by visiting the case page first.
    # case_page_url = f"{XML_BASE_URL_NMVCCS}?caseid={case_id}"
    # try:
    #     session.get(case_page_url, timeout=30)
    #     time.sleep(1.0) # Let the server process the session state
    # except Exception:
    #     pass

    url = f"{XML_BASE_URL_NMVCCS}?GetXML&caseid={case_id}"

    print(f"\n\n\n\n\nCASE ID IS THIS: {case_id}\n\n\n\n\n\n")

    try:
        response = session.get(url, timeout=30)

        if response.status_code == 404:
            return (case_id, False, "404 Not Found - It's likely the endpoint moved.")

        response.raise_for_status()
        content = response.text

        ext = "xml" if is_valid_xml(content) else "html"
        file_path = os.path.join(output_dir, f"{case_id}.{ext}")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return (case_id, True, ext.upper())
    except Exception as e:  # noqa: BLE001
        return (case_id, False, str(e))


case_id = 2005004112741
scraper_config = ScraperConfig(
    sql_query=os.environ["NHTSA_SQL_QUERY"],
    tracking_token=os.getenv("NHTSA_TRACKING_TOKEN", ""),
    nhtsa_token=os.getenv("NHTSA_TOKEN", ""),
    bm_token=os.getenv("NHTSA_BM_TOKEN", ""),
    rt_token=os.getenv("NHTSA_RT_TOKEN", ""),
)

xml_dir = os.path.join(scraper_config.output_dir, "xml_files")
os.makedirs(xml_dir, exist_ok=True)

session = scraper_config.get_session()

# Load cookies into the jar instead of passing them per request
cookies = scraper_config.get_cookies()
session.cookies.update(cookies)

try:
    session.get(BASE_URL_NMVCCS, timeout=10)
except Exception:  # noqa: BLE001, S110
    pass

time.sleep(random.uniform(0.5, 1.5))

cid, success, msg = download_single_xml(session, case_id, xml_dir)

