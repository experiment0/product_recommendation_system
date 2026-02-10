import pandas as pd
from rectools import Columns


class ItemsRanker:
    def __init__(self, items_data: pd.DataFrame) -> None:
        """Класс для ранжирования списка товаров

        Args:
            items_data (pd.DataFrame): Исходные данные товаров.
                Здесь передаются не все колонки.
                item_id - это индекс;
                last_price - последняя зафиксированная в обновлениях цена;
                transactions_count - сколько раз покупали товар.
        """
        self.items_data = items_data.set_index(Columns.Item).copy()
    
    
    def get(self, item_ids: list) -> list:
        """Ранжирует переданный список товаров.
            Оставляет и возвращает 3 товара:
            - самый близкий по метрике сходства (это первый в списке);
            - самый дешевый;
            - самый покупаемый.

        Args:
            item_ids (list): id товаров, из которых нужно выбрать 3

        Returns:
            list: отранжированные 3 товара
        """
        item_ids = item_ids.copy()
        
        # Если товаров не больше 3-х, то нам нечего ранжировать
        if len(item_ids) <= 3:
            return item_ids
        
        # Список с отранжированными товарами
        ranked_items = []
        
        # id товаров расположены в порядке увеличения метрики сходства с
        # товаром, для которого они подбирались, 
        # поэтому первый товар будет самым похожим
        most_similar_item = item_ids.pop(0)
        ranked_items.append(most_similar_item)
        
        # Отфильтруем товары по id, которые получили
        items_data = self.items_data[
            self.items_data.index.isin(item_ids)
        ]
        
        # Добавим товарам признак сходства (в порядке их следования)
        items_with_similar = [
            {Columns.Item: item_id, "similar": index} 
            for index, item_id in enumerate(item_ids)
        ]
        
        # Добавим колонку с рангом схожести
        items_data = items_data.merge(
            pd.DataFrame(items_with_similar).set_index(Columns.Item),
            on=Columns.Item,
            how="left"
        )
        
        # Выделим самый дешевый товар
        cheapest_item = items_data \
            .sort_values(by=["last_price", "similar"]).head(1).index[0]
        
        # Добавим его в отранжированный список
        ranked_items.append(cheapest_item)
        
        # Удалим самый дешевый товар из данных
        items_data.drop(cheapest_item, inplace=True)
        
        # Теперь найдем самый популярный товар
        most_popular_item = items_data \
            .sort_values(by=["transactions_count", "similar"], ascending=[False, True]) \
            .head(1).index[0]
        
        # Добавим самый популярный товар в отранжированный список
        ranked_items.append(most_popular_item)
        
        return ranked_items
        