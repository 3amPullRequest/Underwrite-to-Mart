"""
Adapted from https://github.com/manuelcaccone/NLP-Actuarial-Loss-Modeling/blob/main/notebooks/0_DATA_SCRAPING_NMVCCS.ipynb

Logic for scraping from NMVCCS
"""

import os
import time
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from curl_cffi import requests as cffi_requests

from ...constants import (
    BASE_URL_NMVCCS,
    SEARCH_URL_NMVCCS,
    XML_BASE_URL_NMVCCS,
)


def is_valid_xml(content: str) -> bool:
    """Checks if the content extracted is in fact from a valid XML file."""
    return content.strip().startswith("<?xml") or "<Case" in content


def extract_case_ids(html_content: str) -> list[dict]:
    """_summary_

    Args:
        html_content (str): _description_

    Returns:
        list[dict]: _description_
    """
    soup = BeautifulSoup(html_content, "html.parser")
    cases = []
    table = soup.find(
        "table", {"class": "display table table-condensed table-striped table-hover"}
    )

    if not table:
        return []

    for row in table.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) >= 5:
            case_link = cells[1].find("a")
            case_id = cells[4].text.strip()
            case_string = case_link.text.strip() if case_link else ""

            href = case_link["href"] if case_link and "href" in case_link.attrs else ""
            url = urljoin(BASE_URL_NMVCCS, href)

            cases.append({"case_string": case_string, "case_id": case_id, "url": url})
    return cases


def scrape_case_ids_page(session: cffi_requests.Session, page_num: int, search_critera: dict) -> list[dict]:
    """_summary_

    Args:
        session (requests.Session): _description_
        page_num (int): _description_
        cookies (dict): _description_

    Returns:
        list[dict]: _description_
    """
    params = {**search_critera, "currentPage": str(page_num)}

    response = session.get(SEARCH_URL_NMVCCS, params=params, timeout=30)
    if response.status_code == 404:  # fail fast
        raise RuntimeError(f"404 on {SEARCH_URL_NMVCCS} — site changed again")
    response.raise_for_status()
    return extract_case_ids(response.text)


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
    case_page_url = f"{XML_BASE_URL_NMVCCS}?caseid={case_id}"
    try:
        session.get(case_page_url, timeout=30)
        time.sleep(1.0) # Let the server process the session state
    except Exception:  # noqa: BLE001, S110
        pass
    
    url = f"{XML_BASE_URL_NMVCCS}?GetXML&caseid={case_id}"
    
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
