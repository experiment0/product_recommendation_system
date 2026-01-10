# Функции для вывода информации по исследованию таблиц и признаков

from IPython.display import display, Markdown
from IPython.core.display import HTML
import pandas as pd


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
