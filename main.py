import os
import logging
from datetime import datetime, timezone
from notion_client import Client

logging.basicConfig(level=logging.INFO)

NOTION_TOKEN = os.getenv("NOTION_API_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
STATUS_PROPERTY = "Статус"
DATE_PROPERTY = "Когда (в календаре)"
OVERDUE_STATUS = "Событие прошло"

client = Client(auth=NOTION_TOKEN)

def get_overdue_items():
    now = datetime.now(timezone.utc).isoformat()
    results = []
    start_cursor = None
    while True:
        response = client.databases.query(
            database_id=DATABASE_ID,
            filter={
                "and": [
                    {"property": DATE_PROPERTY, "date": {"before": now}},
                    {"property": STATUS_PROPERTY, "status": {"does_not_equal": OVERDUE_STATUS}}
                ]
            },
            start_cursor=start_cursor,
            page_size=100
        )
        results.extend(response["results"])
        if not response.get("has_more"):
            break
        start_cursor = response.get("next_cursor")
    return results

def update_status(page_id):
    try:
        client.pages.update(
            page_id=page_id,
            properties={
                STATUS_PROPERTY: {
                    "status": {"name": OVERDUE_STATUS}
                }
            }
        )
        logging.info("Updated: " + page_id)
    except Exception as e:
        logging.error("Error: " + str(e))

def main():
    if not NOTION_TOKEN or not DATABASE_ID:
        logging.error("Secrets not set")
        return
    logging.info("Searching...")
    items = get_overdue_items()
    if not items:
        logging.info("No overdue tasks")
        return
    logging.info("Found: " + str(len(items)))
    for item in items:
