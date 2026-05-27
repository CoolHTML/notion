import os
import logging
import time
from datetime import datetime, timezone
from notion_client import Client

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

#  Настройки из GitHub Secrets
NOTION_TOKEN = os.getenv("NOTION_API_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# Названия свойств (точно как в вашей базе Notion!)
STATUS_PROPERTY = "Статус"
DATE_PROPERTY = "Когда (в календаре)"
OVERDUE_STATUS = "Событие прошло"

client = Client(auth=NOTION_TOKEN)

def get_overdue_items():
    now = datetime.now(timezone.utc).isoformat()
    overdue_items = []
    has_more = True
    start_cursor = None

    while has_more:
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
        overdue_items.extend(response["results"])
        has_more = response.get("has_more", False)
        start_cursor = response.get("next_cursor")

    return overdue_items

def update_status(page_id):
    try:
        client.pages.update(
            page_id=page_id,
            properties={STATUS_PROPERTY: {"status": {"name": OVERDUE_STATUS}}}
        )
        logging.info("Updated: %s", page_id)
    except Exception as e:
        logging.error("Error %s: %s", page_id, e)

def main():
    if not NOTION_TOKEN or not DATABASE_ID:
        logging.error("Secrets not found! Check GitHub Settings -> Secrets")
        return

    logging.info("Searching for overdue tasks...")
    items = get_overdue_items()
    
    if not items:
        logging.info("No overdue tasks found.")
        return
        
    logging.info("Found %d tasks.", len(items))
    for i, item in enumerate(items, 1):
        update_status(item["id"])
        if i % 10 == 0:
            time.sleep(1)
            
    logging.info("Done!")

if __name__ == "__main__":
    main()
