import os
import logging
import time
from datetime import datetime, timezone
from notion_client import Client

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# 🔑 Конфигурация (берётся из переменных окружения)
NOTION_TOKEN = os.getenv("ntn_W5013721559uzxMvHRtM9N0MRTiyMXeYqsr8XgAPcEK5jv")
DATABASE_ID = os.getenv("d6591a99-229f-41e1-bc39-61b59a454181")
STATUS_PROPERTY = "Статус"       # Точное название колонки статуса
DATE_PROPERTY = "Когда (в календаре)"       # Точное название колонки с датой
OVERDUE_STATUS = "Событие прошло"    # Значение статуса для просроченных

lient = Client(auth=NOTION_TOKEN)

def get_overdue_items():
    """Поиск задач с прошедшим дедлайном и статусом != Просрочено"""
    now = datetime.now(timezone.utc).isoformat()
    overdue_items = []
    has_more = True
    start_cursor = None

    while has_more:
        # ✅ Явная передача аргументов (фиксит AttributeError)
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
    """Обновление статуса на 'Просрочено'"""
    try:
        client.pages.update(
            page_id=page_id,
            properties={STATUS_PROPERTY: {"status": {"name": OVERDUE_STATUS}}}
        )
        logging.info(f"✅ Обновлено: {page_id}")
    except Exception as e:
        logging.error(f"❌ Ошибка {page_id}: {e}")

def main():
    logging.info("🔍 Поиск просроченных задач...")
    items = get_overdue_items()
    
    if not items:
        logging.info("✨ Просроченных задач не найдено.")
        return
        
    logging.info(f"📦 Найдено {len(items)} задач.")
    for i, item in enumerate(items, 1):
        update_status(item["id"])
        if i % 10 == 0:
            time.sleep(1)  # Защита от rate limit
            
    logging.info("🏁 Готово!")

if __name__ == "__main__":
    main()
