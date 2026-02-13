from typing import get_args
import pandas as pd
from pydantic import BaseModel, Field, model_validator
from rectools.metrics import Precision

from .constants import RECOMMENDATIONS_COUNT
from .types import (
    UserIdsType, 
    ItemIdsType, 
    UserGroupType, 
    MetricNameType,
)
from ..recommender_factory import recommender_factory


class FormattedRecommendations(BaseModel):
    user_id: UserIdsType = Field(
        description="id пользователей",
        examples=[[1097496, 1097496, 1097496]],
    )
    item_id: ItemIdsType = Field(
        description="id рекомендованных товаров",
        examples=[[461686, 5411, 48030]],
    )
    rank: list[int] = Field(
        description="Ранг товара",
        examples=[[1, 2, 3]],
    )
    user_group: list[UserGroupType] = Field(
        description="Группа пользователя",
        examples=[["cold", "cold", "cold"]],
    )


def get_formatted_recommendations(
    user_ids: UserIdsType
) -> FormattedRecommendations:
    """Формирует рекомендации для каждого пользователя из переданного списка.
    И преобразует результат в формат, ожидаемый rectools.
    С той оговоркой, что rectools ожидает DataFrame, а мы формируем словарь,
    чтобы указать типы данных.

    Args:
        user_ids (UserIdsType): id пользователей, 
            для которых нужно сформировать рекомендации.

    Returns:
        FormattedRecommendations: рекомендации для пользователей, 
            преобразованные в формат, подходящий для rectools.
    """
    reco = {
        "user_id": [], "item_id": [], "rank": [], "user_group": []
    }
    for user_id in user_ids:
        user_group, recommend_items = recommender_factory.get_recommender_items(user_id)
        item_ids = recommend_items()
        
        for index, item_id in enumerate(item_ids):
            reco["user_id"].append(user_id)
            reco["item_id"].append(item_id)
            reco["rank"].append(index + 1)
            reco["user_group"].append(user_group)
    
    return FormattedRecommendations(**reco)


class Interactions(BaseModel):
    user_id: UserIdsType = Field(
        description="Идентификаторы пользователей",
        examples=[[1017234, 73836, 1097496, 3673, 1268070]],
    )    
    item_id: ItemIdsType = Field(
        description="Идентификаторы товаров, с которыми взаимодействовали пользователи",
        examples=[[158237, 297765, 132469, 106720, 122087]],
    )    
    @model_validator(mode="after")
    def check_equality_lists_length(self):
        if len(self.user_id) != len(self.item_id):
            raise ValueError("The lengths of the lists must be equal.")
        return self

class Metric(BaseModel):
    name: MetricNameType = Field(
        description="Название метрики",
        examples=[["precision@3"]],
    )
    value: float = Field(
        description="Значение метрики",
        examples=[[0.005]],
    )    
    
class GroupMetrics(BaseModel):
    group_name: UserGroupType
    unique_user_ids_count: int = Field(
        description="Количество уникальных пользователей",
        examples=[[100]],
    )
    metrics: list[Metric]

GroupMetricsRequest = Interactions
GroupMetricsResponse = list[GroupMetrics]

def calculate_group_metrics(
    interactions: GroupMetricsRequest
) -> GroupMetricsResponse:
    """Подсчитывает метрики для каждой группы пользователей.
    Пока подсчитываем только precision@3.

    Args:
        interactions (GroupMetricsRequest): Данные о фактических взаимодействиях 
            пользователей с товарами.

    Returns:
        GroupMetricsResponse: Метрики, посчитанные для каждой группы пользователей.
    """
    # Создадим объект для подсчета метрики `precision@3`.
    precision_3_calculator = Precision(k=RECOMMENDATIONS_COUNT)
    
    # Приведем данные об интерациях к формату DataFrame, т.к. в таком виде
    # их принимает rectools
    interactions_data = pd.DataFrame(interactions.model_dump())

    # Уникальные id пользователей, для которых будем генерировать рекомендации
    unique_user_ids = list(set(interactions.user_id))
    
    # Генерируем рекомендации для всего набора пользователей
    recommendations = get_formatted_recommendations(unique_user_ids)
    # И приводим их к формату DataFrame, чтобы проще было фильтровать по группам
    # Плюс в виде DataFrame их принимает rectools
    recommendations_data = pd.DataFrame(recommendations.model_dump())
    
    # Итоговый ответ, который сформируем
    response = []
    # Имя нашей единственной метрики
    precision_3_name: MetricNameType = "precision@3"
    # Имена групп пользователей вынем из типа данных
    user_groups = get_args(UserGroupType)
    
    # Итерируемся по именам групп
    for group_name in user_groups:
        # Фильтруем рекомендации только для текущей группы
        mask_group = recommendations_data["user_group"] == group_name
        group_data = recommendations_data[mask_group].drop(columns=["user_group"])
        
        # Здесь будем собирать данные текущей группы
        group_metrics = GroupMetrics(
            group_name=group_name,
            unique_user_ids_count=group_data["user_id"].nunique(),
            metrics=[],
        )
        
        # С помощью метода из rectools считаем метрику
        precision_3_value = precision_3_calculator.calc(
            reco=group_data, 
            interactions=interactions_data,
        )
        
        # Собираем вместе данные по метрике группы и добавляем в респонс
        metric = Metric(
            name=precision_3_name,
            value=precision_3_value,
        )        
        group_metrics.metrics.append(metric)
        
        response.append(group_metrics)
    
    return response
