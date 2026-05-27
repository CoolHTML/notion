import os
import logging
import time
from datetime import datetime, timezone
from notion_client import Client

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Секреты из GitHub (имена переменных, не значения!)
NOTION_TOKEN = os.getenv("NOTION_API_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# Ваши названия свойств из Notion (точно как в интерфейсе!)
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
                    {
                        "property": DATE_PROPERTY,
                        "date": {"before": now}
                    },
                    {
                        "property": STATUS_PROPERTY,
                        "status": {"does_not_equal": OVERDUE_STATUS}
                    }
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
        logging.info("Updated: %s", page_id)
