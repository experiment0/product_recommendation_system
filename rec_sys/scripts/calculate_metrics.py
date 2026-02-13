import sys
from pathlib import Path
import pandas as pd
import requests
import json
from rectools import Columns

# Путь к текущему файлу
current_file = Path(__file__).resolve()
# Корневая папка проекта
root_path = current_file.parent.parent.parent.resolve()
# Добавим папку проекта в список системных директорий, чтобы Python видел путь к папке rec_sys
sys.path.append(str(root_path))

from rec_sys.utils.prepare_data import convert_timespamp_to_datetime
from rec_sys.utils.constants import SPLIT_DATE

# Папка с данными
DATA_PATH = root_path / "data"

# Размер батча для замера метрик
BATCH_SIZE = 1000


def main():
    # Загрузим данные обо всех интеракциях
    events_data = pd.read_csv(DATA_PATH / "events.csv")
    
    # Переведем признак timestamp в формат с отображением даты и времени
    events_data = convert_timespamp_to_datetime(events_data)
    
    # Отделим тестовую выборку
    mask_after_split_date = events_data["event_datetime"] >= SPLIT_DATE
    events_test_data = events_data[mask_after_split_date]
    
    # Отделим первый батч
    batch_data = events_test_data[:BATCH_SIZE]
    # Выделим и переименуем колонки
    batch_data = batch_data[["visitorid", "itemid"]].rename(
        columns={"visitorid": Columns.User, "itemid": Columns.Item}
    )
    # Преобразуем в словарь для передачи в тело POST запроса
    formatted_batch = batch_data.to_dict("list")
    
    # Урл для подсчета метрик
    metrics_url = "http://localhost:8000/metrics"

    # Делаем запрос
    response = requests.post(metrics_url, json=formatted_batch)
    
    # Выводим форматированный ответ
    print(
        json.dumps(
            response.json(), 
            indent=4
        )
    )

if __name__ == "__main__":
    main()
    