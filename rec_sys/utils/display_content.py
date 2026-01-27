# Функции для вывода информации по исследованию таблиц и признаков

from IPython.display import display, Markdown
from IPython.core.display import HTML
import pandas as pd


def display_nan_count(data: pd.DataFrame) -> None:
    """Выводит суммарное количество пропусков в таблице"""
    display(Markdown(f"**Количество пропусков: {data.isna().sum().sum()}**"))


def display_common_data_info(data: pd.DataFrame) -> None:
    """Выводит основную информацию о таблице

    Args:
        data (pd.DataFrame): таблица
    """
    display(Markdown("**Первые строки таблицы:**"))
    display(data.head())
    
    display(Markdown(f"**Размерность таблицы:** {data.shape}"))
    
    display(Markdown("**Информация о столбцах:**"))
    display(data.info())
    
    display(Markdown("**Пропуски:**"))
    display(data.isna().sum())


def display_property_info(data: pd.DataFrame, property: str) -> None:
    """Выводит информацию о свойстве товара

    Args:
        data (pd.DataFrame): данные с товарами
        property (str): значение свойства, для которого нужно вывести информацию
    """
    # Маска для фильтрации строк с этим свойством
    mask_property = (data["property"] == property)
    
    display(Markdown("**Примеры значений свойства:**"))
    display(data[mask_property].head())
    
    display(Markdown(f"**Количество уникальных значений `value` свойства:** {data[mask_property]['value'].nunique()}"))
    
    display(Markdown(f"**Максимальное значение `values_count`:** {data[mask_property]['values_count'].max()}"))
    
    display(Markdown("**Количество переопределений для каждого товара (всего и с уникальным `value`):**"))
    
    values_volume = data[mask_property].pivot_table(
        index="itemid",
        values="value",
        aggfunc=["count", "nunique"]
    ) \
    .sort_values([("count", "value"), ("nunique", "value")], ascending=False)
    
    display(values_volume)
    
    display(Markdown("**Распределение значений в предыдущей таблице:**"))
    display(values_volume.describe())
    
    display(Markdown("**Пример изменения значений для одного товара:**"))
    
    itemid_with_max_values = values_volume.index[0]
    item_mask = (data["itemid"] == itemid_with_max_values)
    display(data[mask_property & item_mask])
