# Общие типы

from typing import Literal


# Тип списка с id товаров
ItemIdsType = list[int]

# Тип списка с id пользователей
UserIdsType = list[int]

# Группа пользователя
UserGroupType = Literal["normal", "extremal", "cold"]

# Названия метрик. Пока у нас одна - precision@3
MetricNameType = Literal["precision@3"]
