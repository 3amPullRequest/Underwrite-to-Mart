import os

from dagster import Definitions, fs_io_manager, load_assets_from_modules

from .assets.bronze import scrape_nmvccs
from .resources.scrape_nmvccs import ScraperConfig

bronze_assets = load_assets_from_modules(
    [scrape_nmvccs], key_prefix="bronze", group_name="bronze"
)

defs = Definitions(
    assets=[*bronze_assets],
    resources={
        "scraper_config": ScraperConfig(
            sql_query=os.environ["NHTSA_SQL_QUERY"],
            tracking_token=os.getenv("NHTSA_TRACKING_TOKEN", ""),
            nhtsa_token=os.getenv("NHTSA_TOKEN", ""),
            bm_token=os.getenv("NHTSA_BM_TOKEN", ""),
            rt_token=os.getenv("NHTSA_RT_TOKEN", ""),
        ),
        "io_manager": fs_io_manager,
    },
)
