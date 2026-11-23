import logging
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger


# --------------------------------------------------
# Configuration
# --------------------------------------------------

IST = ZoneInfo("Asia/Kolkata")

API_BASE_URL = "http://127.0.0.1:8000"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = PROJECT_ROOT / "reports"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler(timezone=IST)


# --------------------------------------------------
# Daily Market Report Job
# --------------------------------------------------

def generate_daily_market_reports():

    today = datetime.now(IST).date()
    start_date = today - timedelta(days=30)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("Starting daily market report generation.")

    try:
        response = requests.get(
            f"{API_BASE_URL}/products/",
            timeout=30
        )
        response.raise_for_status()

        products = response.json()

        # Support either a direct list or a wrapped response.
        if isinstance(products, dict):
            products = (
                products.get("items")
                or products.get("data")
                or products.get("products")
                or []
            )

        if not isinstance(products, list):
            logger.error("Unexpected products API response.")
            return

        active_products = [
            product for product in products
            if product.get("id") is not None
            and product.get("is_active", True)
        ]

        if not active_products:
            logger.info("No active products found.")
            return

        for product in active_products:

            product_id = product["id"]

            try:
                report_response = requests.get(
                    f"{API_BASE_URL}/reports/market/{product_id}",
                    params={
                        "start_date": start_date.isoformat(),
                        "end_date": today.isoformat()
                    },
                    timeout=60
                )

                report_response.raise_for_status()

                file_path = (
                    REPORTS_DIR
                    / f"Daily_Market_Report_Product_{product_id}_{today}.pdf"
                )

                file_path.write_bytes(report_response.content)

                logger.info(
                    "Report generated successfully: %s",
                    file_path
                )

            except requests.RequestException:
                logger.exception(
                    "Failed to generate report for product ID %s",
                    product_id
                )

    except requests.RequestException:
        logger.exception("Could not retrieve active products.")

    logger.info("Daily market report job completed.")


# --------------------------------------------------
# Scheduler Controls
# --------------------------------------------------

def start_scheduler():

    if scheduler.running:
        logger.info("Scheduler is already running.")
        return

    scheduler.add_job(
        generate_daily_market_reports,
        trigger=CronTrigger(
            hour=18,
            minute=0,
            timezone=IST
        ),
        id="daily_market_reports",
        name="Daily Market Intelligence Reports",
        replace_existing=True,
        max_instances=1,
        coalesce=True
    )

    scheduler.start()

    logger.info(
        "Daily market report scheduler started. "
        "Next scheduled time: 6:00 PM IST."
    )


def stop_scheduler():

    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Daily market report scheduler stopped.")
