# Функции для вывода графиков

from typing import Optional
import pandas as pd
import matplotlib.pyplot as plt 
import seaborn as sns


def show_pie(data: pd.DataFrame, feature_name: str, title: str) -> None:
    """Выводит круговую диаграмму

    Args:
        data (pd.DataFrame): таблица с данными
        feature_name (str): название признака, для которого нужно вывести график
        title (str): название графика
    """
    counts = data[feature_name].value_counts()

    fig = plt.figure(figsize=(4, 4))
    axes = fig.add_axes([0, 0, 1, 1])

    axes.set_title(title)
    axes.pie(
        counts,
        labels=counts.index,
        autopct="%.2f%%",
    );


def show_countplot(
    data: pd.DataFrame,
    feature_name: str,
    title: str,
    xlabel: str,
    ylabel: str,
    figsize: tuple = (6, 4),
    hue_feature_name: Optional[str] = None,
) -> None:
    """Выводит количественную столбчатую диаграмму

    Args:
        data (pd.DataFrame): таблица с данными
        feature_name (str): название признака, для которого нужно построить диаграмму
        title (str): название графика
        xlabel (str): подпись по оси OX
        ylabel (str): подпись по оси OY
        figsize (tuple, optional): размер графика. 
            По умолчанию (6, 4).
        hue_feature_name (Optional[str], optional): в разрезе какого признака построить график. 
            По умолчанию None.
    """
    # Построим количественную столбчатую диаграмму
    fig = plt.figure(figsize=figsize)
    
    countplot_params = {
        "data": data,
        "x": data[feature_name],
    }
    if hue_feature_name is not None:
        countplot_params["hue"] = hue_feature_name
        
    ax = sns.countplot(**countplot_params)
    
    plt.title(title)
    ax.set(xlabel=xlabel, ylabel=ylabel)
    ax.grid(True)
    plt.show()
