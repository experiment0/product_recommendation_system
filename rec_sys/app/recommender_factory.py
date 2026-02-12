from typing import Literal, Optional, Union, Callable
import json
from pathlib import Path
import numpy as np
import pandas as pd
from annoy import AnnoyIndex
import pickle

from rectools import Columns
from rectools.dataset import Dataset
from rectools.models import load_model, ImplicitALSWrapperModel

from .types import ItemsType
from .classes import (
    SimilarItemsSeacher,
    SimilarItemsRanker,
    RecommenderSimilarItems,
)
from .constants import (
    ANNOY_VECTOR_SIZE, 
    ANNOY_METRIC, 
    SIMILAR_ITEMS_COUNT,
    RECOMMENDATIONS_COUNT,
)

# Путь к текущему файлу
current_file = Path(__file__).resolve()
# Путь к папке с приложением
APP_PATH = current_file.parent.resolve()


# Загрузка моделей и данных
with open(APP_PATH / "data/annoy_index_to_item_id.json", "r", encoding="utf-8") as file:  
    annoy_index_to_item_id = json.load(file)

with open(APP_PATH / "data/item_id_to_annoy_index.json", "r", encoding="utf-8") as file:  
    item_id_to_annoy_index = json.load(file)

with open(APP_PATH / "data/dense_features_normal_dataset.pkl", "rb") as file:
    dense_features_normal_dataset = pickle.load(file)

with open(APP_PATH / "data/popular_items.pkl", "rb") as file:
    popular_items = pickle.load(file)

items_ranking_data = pd.read_csv(APP_PATH / "data/items_ranking_data.csv")
events_train_extremal_data = pd.read_csv(APP_PATH / "data/events_train_extremal_data.csv")

annoy_index = AnnoyIndex(ANNOY_VECTOR_SIZE, metric=ANNOY_METRIC)
# annoy_index_path = APP_PATH / "models/annoy_items_index.ann"
# annoy_index_path_str = str(annoy_index_path)
# TODO - на windows annoy видит путь от корня папки и не видит абсолютных путей
# Это проявляется в python файлах
annoy_index.load("./rec_sys/app/models/annoy_items_index.ann")

model_als = load_model(APP_PATH / "models/model_als.pkl")


# Далее создадим объекты для формирования рекомендаций каждой из 3-х групп


# Создаем класс и объект для группы "normal" (пользователи с нормальной активностью)
class RecommenderAlsItems:
    def __init__(
        self,
        model_als: ImplicitALSWrapperModel,
        dense_features_normal_dataset: Dataset,
        recommendations_count: int,
    ) -> None:
        """Находит рекомендации с помощью модели ALS

        Args:
            model_als (ImplicitALSWrapperModel): обертка модели ALS
            dense_features_normal_dataset (Dataset): датасет с информацией 
                о взаимодействиях пользователей с товарами, 
                а также данными о товарах и пользователях
            recommendations_count (int): количество рекомендаций для возврата
        """
        self.model_als = model_als
        self.dense_features_normal_dataset = dense_features_normal_dataset
        self.recommendations_count = recommendations_count
    
    def get(self, user_id: int) -> ItemsType:
        """Обращается к модели ALS за получением рекомендованых товаров
        И далее из датафрейма вынимает id товаров и преобразует в список.

        Args:
            user_id (int): id пользователя

        Returns:
            ItemsType: рекомендуемые товары
        """
        recomendations_data = self.model_als.recommend(
            users=[user_id],
            dataset=self.dense_features_normal_dataset,
            k=self.recommendations_count, 
            filter_viewed=True
        )
        
        return list(recomendations_data[Columns.Item].values)

recommender_normal_group = RecommenderAlsItems(
    model_als,
    dense_features_normal_dataset,
    RECOMMENDATIONS_COUNT,
)


# Создаем класс и объект для группы "extremal" (пользователи с низкой или высокой активностью)
similar_items_seacher = SimilarItemsSeacher(
    annoy_index,
    annoy_index_to_item_id,
    item_id_to_annoy_index,
)

similar_items_ranker = SimilarItemsRanker(items_ranking_data)

recommender_extremal_group = RecommenderSimilarItems(
    similar_items_seacher=similar_items_seacher,
    similar_items_ranker=similar_items_ranker,
    events_data=events_train_extremal_data,
    similar_items_count=SIMILAR_ITEMS_COUNT,
)


# Создаем класс и объект для группы "cold" (холодные пользователи, о которых нет информации)
class RecommenderPopularItems:
    def __init__(self, popular_items: np.ndarray) -> None:
        self.popular_items = list(popular_items)
        
    def get(self, user_id: Optional[int] = None) -> ItemsType:
        return self.popular_items

recommender_cold_group = RecommenderPopularItems(popular_items)


# Типы данных и маппер объектов для рекомендаций
UserGroupType = Literal["normal", "extremal", "cold"]
RecommenderForGroupType = Union[
    RecommenderAlsItems,
    RecommenderSimilarItems,
    RecommenderPopularItems
]
RecommendersMapperType = dict[UserGroupType, RecommenderForGroupType]

recommenders: RecommendersMapperType = {
    "normal": recommender_normal_group,
    "extremal": recommender_extremal_group,
    "cold": recommender_cold_group,
}


# Класс-фабрика для формирования объекта-рекомендателя
class RecommenderFactory:
    def __init__(
        self, 
        normal_user_ids: set, 
        extremal_user_ids: set,
        recommenders: RecommendersMapperType,
    ) -> None:
        """Фабрика для определения алгоритма рекомендаций по группе пользователя

        Args:
            normal_user_ids (set): id пользователей, которые относятся к группе "нормальных",
                то есть их активность не слишком низакая и не слишком высокая.
            extremal_user_ids (set): id пользователей, которые относятся к группе "экстремальных"
                в плане активности. Т.е. покупают либо слишком мало, либо слишком много.
            recommenders (RecommendersMapperType): мапер {группа} -> {объект с алгоритмом поиска рекомендаций}
        """
        self.normal_user_ids = normal_user_ids
        self.extremal_user_ids = extremal_user_ids
        self.recommenders = recommenders    
    
    def get_user_group(self, user_id: int) -> UserGroupType:
        """Определяет и возвращает группу пользователя

        Args:
            user_id (int): id пользователя

        Returns:
            UserGroupType: имя группы, к которой относится пользователь
        """
        if user_id in self.normal_user_ids:
            return "normal"        
        if user_id in self.extremal_user_ids:
            return "extremal"        
        return "cold"
        
    def get_recommender_items(self, user_id: int) -> Callable:
        """Определяет функцию, которая будет возвращать рекомендации для переданного пользователя

        Args:
            user_id (int): id пользователя

        Returns:
            Callable: функция, которая будет возвращать рекомендации
        """
        user_group = self.get_user_group(user_id)
        
        def get_items() -> ItemsType:
            return self.recommenders[user_group].get(user_id)
        
        return get_items

recommender_factory = RecommenderFactory(
    normal_user_ids=set(dense_features_normal_dataset.user_id_map.external_ids),
    extremal_user_ids=set(events_train_extremal_data[Columns.User].unique()),
    recommenders=recommenders,
)

# Как использовать:
# recommend_items = recommender_factory.get_recommender_items(1222911)
# print(recommend_items())
# -> [26477, 20017, 103127]
