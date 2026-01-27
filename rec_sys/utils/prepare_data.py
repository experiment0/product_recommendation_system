# Функции для обработки данных

from typing import Optional
import numpy as np
import pandas as pd


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


def get_time_of_day(hour: int) -> str:
    """Определяет временной интервал (время дня)

    Args:
        hour (int): час

    Returns:
        str: временной интервал
    """
    if hour >= 3 and hour < 7:
        return "3-7"
    elif hour >= 7 and hour < 12:
        return "7-12"
    elif hour >= 12 and hour < 16:
        return "12-16"
    elif hour >= 16 and hour < 22:
        return "16-22"
    else:
        return "22-3"
    

def get_categories_levels_path(
    catid_to_parentid: dict, 
    catid: Optional[int]
) -> list[int]:
    """Собирает путь из цепочки категорий (от корневой до текущей)

    Args:
        catid_to_parentid (dict): словарь, где ключ - категория
                                значение - ее родительская
        catid (Optional[int]):  идентификатор категории, для которой нужно собрать цепочку

    Returns:
        list[int]: цепочка категорий (от корневой до текущей)
    """
    if catid is None or np.isnan(catid):
        return []
    
    levels_path = [int(catid)]
    
    if catid not in catid_to_parentid:
        return levels_path
    
    is_top_level = False
    
    while not is_top_level:
        parentid = catid_to_parentid[catid]
        
        if np.isnan(parentid):
            is_top_level = True
        else:
            levels_path.append(int(parentid))        
            catid = parentid
            
    levels_path = levels_path[::-1]
    
    return levels_path


def get_categories_levels_count(levels_path: list[int]) -> int:
    """Считает количество количество уровней каталога для данной категории

    Args:
        levels_path (list[int]): цепочка категорий (от корневой до текущей)

    Returns:
        int: количество уровней
    """
    return len(levels_path)


def get_root_category(levels_path: list[int]) -> int:
    """Возвращает корневую категорию для текущей

    Args:
        levels_path (list[int]): цепочка категорий (от корневой до текущей)

    Returns:
        int: id корневой категории
    """    
    return levels_path[0]


def get_values_count(value: str) -> int:
    """Возвращает количество значений, указанных в поле value через пробел

    Args:
        value (str): значение поля value

    Returns:
        int: количество отдельных значений в поле
    """
    values = value.split()
    
    return len(values)


def get_unique_values_count(value: str) -> int:
    """Возвращает количество уникальных значений, указанных в поле value через пробел

    Args:
        value (str): значение поля value

    Returns:
        int: количество уникальных отдельных значений в поле
    """
    values = value.split()
    
    return len(set(values))
