# Функции для обработки данных

import numpy as np
import pandas as pd

from rec_sys.utils.constants import (
    CATEGORY_SEPARATOR,
)


def convert_timespamp_to_datetime(
    data: pd.DataFrame,
    should_drop_timestamp_feature: bool = True,
) -> pd.DataFrame:
    """Переводит время события из формата timestamp в формат YYYY-MM-DD HH:MM:SS.

    Args:
        data (pd.DataFrame): исходные данные
        should_drop_timestamp_feature (bool, optional): Нужно ли удалить признак в формате timestamp. 
        По умолчанию True.

    Returns:
        pd.DataFrame: данные с новым признаком (и при необходимости с удаленным старым)
    """
    # Скорипруем данные, чтобы не мутировать исходные
    data = data.copy()
    
    data["event_datetime"] = pd.to_datetime(
        data["timestamp"], 
        unit="ms"
    )
    
    # Отсортируем по колонке со временем
    data.sort_values(by="event_datetime", inplace=True)
    
    # Сбросим индекс
    data.reset_index(inplace=True, drop=True)
    
    # При необходимости удалим старый признак
    if should_drop_timestamp_feature:
        data.drop(columns=["timestamp"], inplace=True)
    
    return data


def add_datetime_features(data: pd.DataFrame) -> pd.DataFrame:
    """Добавляет признаки даты и времени

    Args:
        data (pd.DataFrame): исходные данные

    Returns:
        pd.DataFrame: данные с добавленными признаками
    """
    # Скорипруем данные, чтобы не мутировать исходные
    data = data.copy()
    
    # Добавим временные признаки
    data["date"] = data["event_datetime"].dt.date
    data["date"] = pd.to_datetime(data["date"]) 
    
    data["year"] = data["event_datetime"].dt.year
    data["month"] = data["event_datetime"].dt.month
    data["day"] = data["event_datetime"].dt.day
    data["day_of_week"] = data["event_datetime"].dt.dayofweek
    data["hour"] = data["event_datetime"].dt.hour
    data["minute"] = data["event_datetime"].dt.minute
    
    return data


def get_categories_levels_path(data: pd.DataFrame, categoryid: int) -> str:
    """Собирает путь из цепочки категорий (от корневой до текущей)

    Args:
        data (pd.DataFrame): таблица с деревом категорий
        categoryid (int): идентификатор категории, для которого нужно собрать цепочку

    Returns:
        str: цепочка категорий (от корневой до текущей)
    """
    levels_path = [str(int(categoryid))]
    
    is_top_level = False
    
    while not is_top_level:
        mask = data["categoryid"] == categoryid        
        parent_category = data[mask]["parentid"].values[0]
        
        if np.isnan(parent_category):
            is_top_level = True
        else:
            levels_path.append(str(int(parent_category)))        
            categoryid = parent_category
            
    levels_path = levels_path[::-1]
    
    return CATEGORY_SEPARATOR.join(levels_path)


def get_categories_levels_count(levels_path: str) -> int:
    """Считает количество количество уровней каталога для данной категории

    Args:
        levels_path (str): цепочка категорий (от корневой до текущей)

    Returns:
        int: количество уровней
    """
    levels = levels_path.split(CATEGORY_SEPARATOR)
    
    return len(levels)


def get_root_category(levels_path: str) -> int:
    """Возвращает корневую категорию для текущей

    Args:
        levels_path (str): цепочка категорий (от корневой до текущей)

    Returns:
        int: id корневой категории
    """
    levels = levels_path.split(CATEGORY_SEPARATOR)
    
    return int(levels[0])

