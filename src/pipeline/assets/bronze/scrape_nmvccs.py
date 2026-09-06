"""
Adapted from https://github.com/manuelcaccone/NLP-Actuarial-Loss-Modeling/blob/main/notebooks/0_DATA_SCRAPING_NMVCCS.ipynb

Assets for scraping from NMVCCS
"""

import csv
import os
import random
import time

from dagster import (
    AssetExecutionContext,
    AssetKey,
    DynamicPartitionsDefinition,
    MaterializeResult,
    RetryPolicy,
    asset,
)

from ...constants import BASE_URL_NMVCCS, SEARH_FILTERS
from ...logic.bronze.scrape_nmvccs import download_single_xml, scrape_case_ids_page
from ...resources.scrape_nmvccs import ScraperConfig

# Define the dynamic partition store
nmvccs_case_ids_partitions = DynamicPartitionsDefinition(name="nmvccs_case_ids")


@asset(
    retry_policy=RetryPolicy(max_retries=3),
    description="Scrapes all case IDs and registers them as dynamic partitions.",
)
def nmvccs_cases_csv(
    context: AssetExecutionContext, scraper_config: ScraperConfig
) -> MaterializeResult:
    """_summary_

    Args:
        context (AssetExecutionContext): _description_
        scraper_config (ScraperConfig): _description_

    Raises:
        Exception: _description_

    Returns:
        str: _description_
    """
    log = context.log
    output_dir = scraper_config.output_dir
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, "nmvccs_cases.csv")

    session = scraper_config.get_session()
    session.cookies.update(scraper_config.get_cookies())  # jar once, no per-request cookies=

    all_cases = []  # initialise

    for page_num in range(1, scraper_config.max_pages + 1):
        try:
            page_cases = scrape_case_ids_page(session, page_num, SEARH_FILTERS)
        except RuntimeError as e:
            log.error(f"{e}"); break # fail fast
        if not page_cases:
            log.info(f"No cases on page {page_num}; stopping."); break
        all_cases.extend(page_cases)
        time.sleep(random.uniform(0.5, 1.5))

    # Deduplicate
    unique_cases = []
    seen = set()
    for case in all_cases:
        if case["case_id"] not in seen:
            unique_cases.append(case)
            seen.add(case["case_id"])

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["case_string", "case_id", "url"])
        writer.writeheader()
        writer.writerows(unique_cases)

    # Register discovered IDs
    case_ids = [c["case_id"] for c in unique_cases]
    if case_ids:
        context.instance.add_dynamic_partitions("nmvccs_case_ids", case_ids)

    return MaterializeResult(
        value=csv_path, metadata={"total_cases": len(unique_cases)}
    )


@asset(
    partitions_def=nmvccs_case_ids_partitions,
    retry_policy=RetryPolicy(max_retries=3),
    deps=[AssetKey(["bronze", "nmvccs_cases_csv"])],
)
def nmvccs_xml_files(
    context: AssetExecutionContext, scraper_config: ScraperConfig
) -> MaterializeResult:
    """Downloads XML/HTML for a single partition (Case ID)."""
    log = context.log
    case_id = context.partition_key  # Dagster injects the specific Case ID here
    xml_dir = os.path.join(scraper_config.output_dir, "xml_files")
    os.makedirs(xml_dir, exist_ok=True)

    # Idempotency check: skip if already downloaded
    if os.path.exists(os.path.join(xml_dir, f"{case_id}.xml")) or os.path.exists(
        os.path.join(xml_dir, f"{case_id}.html")
    ):
        log.info(f"Skipping {case_id}, already exists.")
        return MaterializeResult(metadata={"status": "skipped_existing"})

    session = scraper_config.get_session()

    # Load cookies into the jar instead of passing them per request
    cookies = scraper_config.get_cookies()
    session.cookies.update(cookies)

    try:
        session.get(BASE_URL_NMVCCS, timeout=10)
    except Exception:  # noqa: BLE001, S110
        pass

    time.sleep(random.uniform(0.5, 1.5))

    _, success, msg = download_single_xml(session, case_id, xml_dir)

    if success:
        return MaterializeResult(metadata={"status": "success", "type": msg})
    else:
        raise Exception(f"Failed to download {case_id}: {msg}")  # noqa: TRY002
