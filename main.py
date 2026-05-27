import os
import logging
import time
from datetime import datetime, timezone
from notion_client import Client

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# 🔑 Настройки (берутся из GitHub Secrets по ИМЕНАМ)
NOTION_TOKEN = os.getenv("NOTION_API_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# ⚙️ Названия свойств из вашей базы (точно как в Notion!)
STATUS_PROPERTY = "Статус"
DATE_PROPERTY = "Когда (в календаре)"
OVERDUE_STATUS = "Событие прошло"

# ✅ Исправлено: client (было lient)
client = Client(auth=NOTION_TOKEN)

def get_overdue_items():
    """Поиск задач с прошедшей датой и статусом != Событие прошло"""
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
    """Обновление статуса"""
    try:
        client.pages.update(
            page_id=page_id,
            properties={STATUS_PROPERTY: {"status": {"name": OVERDUE_STATUS}}}
        )
        logging.info(f"✅ Обновлено: {page_id}")
    except Exception as e:
        logging.error(f"❌ Ошибка {page_id}: {e}")

def main():
    if not NOTION_TOKEN or not DATABASE_ID:
        logging.error("❌ Не найдены секреты! Проверьте Settings → Secrets in GitHub")
        return

    logging.info("🔍 Поиск просрочен
