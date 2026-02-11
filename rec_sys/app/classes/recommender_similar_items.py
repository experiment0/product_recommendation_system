import pandas as pd
from rectools import Columns

from .similar_items_seacher import SimilarItemsSeacher
from .similar_items_ranker import SimilarItemsRanker


class RecommenderSimilarItems:
    def __init__(
        self,
        similar_items_seacher: SimilarItemsSeacher,
        similar_items_ranker: SimilarItemsRanker,
        events_data: pd.DataFrame, 
        similar_items_count: int = 10,
    ) -> None:
        """Класс для подбора рекомендаций мало активным (или гипер активным) пользователям

        Args:
            similar_items_seacher (SimilarItemsSeacher): Объект для поиска похожих товаров
            similar_items_ranker (SimilarItemsRanker): Объект для ранжирования товаров
            events_data (pd.DataFrame): Данные о взаимодействиях пользователей с товарами.
                Содержит 2 колонки - id пользователя и id товара.
                Данные отсортированы в порядке взаимодействия.
            similar_items_count (int, optional): Сколько похожих товаров будем ранжировать. 
                По умолчанию 10.
        """
        self.similar_items_seacher = similar_items_seacher
        self.similar_items_ranker = similar_items_ranker
        self.events_data = events_data.copy()
        self.similar_items_count = similar_items_count
    
    
    def get(self, user_id: int) -> list[int]:
        """Подбирает рекомендованные товары для переданного пользователя

        Args:
            user_id (int): id пользователя

        Returns:
            list[int]: рекомендуемые товары
        """
        # Отделим товары, с которыми взаимодействовал данный пользователь
        mask_user = self.events_data[Columns.User] == user_id
        user_items = list(
            self.events_data[mask_user][Columns.Item].unique()
        )
        
        # Количество уникальных товаров, с которыми взаимодействовал пользователь
        user_items_count = len(set(user_items))
        
        # Последний товар, с которым он взаимодействовал
        user_last_item = user_items[-1]
        
        # Ищем товары, похожие на последний
        similar_items = self.similar_items_seacher.get(
            item_id=user_last_item,
            # Берем товаров на user_items_count товаров больше, 
            # чтобы убрать просмотренные товары из рекомендованных.
            # И после этого было из чего ранжировать.
            items_count=self.similar_items_count + user_items_count,
        )
        # Убираем из похожих просмотренные товары
        similar_items = [item_id for item_id in similar_items if item_id not in user_items]
        
        # Получаем наши 3 ранжированные товара
        ranked_items = self.similar_items_ranker.get(similar_items)
        
        return ranked_items
