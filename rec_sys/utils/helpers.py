from typing import Union
import time


def get_formatted_number(number: Union[int,float]) -> str:
    """Добавляет при выводе числа разбиение на десятичные разряды

    Args:
        number (Union[int,float]): исходное число

    Returns:
        str: запись числа с разбиением на разряды
    """
    return '{0:,}'.format(number).replace(',', ' ')


def get_exec_time(start: float, end: float) -> str:
    """Возвращает время выполнения в секундах

    Args:
        start (float): время начала
        end (float): время окончания

    Returns:
        str: строка с форматированным временем выполнения
    """
    duration = end - start
    formatted_duration = time.strftime("%H:%M:%S", time.gmtime(duration))
    
    return formatted_duration


def display_exec_time(start: float, end: float) -> None:
    """Выводит время выполнения

    Args:
        start (float): время начала
        end (float): время окончания
    """
    exec_time = get_exec_time(start, end)
    print(f"Время выполнения: {exec_time}")