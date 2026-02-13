import sys
from pydantic import BaseModel, Field
from pathlib import Path
from fastapi import FastAPI
import logging
from logging.handlers import RotatingFileHandler
import traceback

# Путь к текущему файлу
current_file = Path(__file__).resolve()
# Путь к папке с приложением
APP_PATH = current_file.parent.resolve()

# Добавляем родительскую папку app в PATH,
# чтобы в пределах данного репо можно было импортировать из модуля app
sys.path.append(str(APP_PATH.parent))

from app.utils.types import ItemIdsType
from app.utils.metrics import (
    calculate_group_metrics, 
    GroupMetricsRequest,
    GroupMetricsResponse,
)
from app.recommender_factory import recommender_factory


# Версия и название приложения
APP_VERSION = "0.1.0"
APP_TITLE = "Product recommendation system API"


# Настраиваем логирование
logger = logging.getLogger(__name__)

def set_logger_settings():
    logs_path = APP_PATH / "logs"
    logs_file_path = logs_path / "recommender.log"

    if not logs_path.is_dir():
        logs_path.mkdir()
    
    log_handler = RotatingFileHandler(
        logs_file_path, 
        maxBytes= 10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    log_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s,%(msecs)03d - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(log_handler)
    
    logging.basicConfig(level=logging.INFO)


# Создаем приложение
app = FastAPI(
    title=APP_TITLE,
    description="API рекомендательной системы товаров",
    version=APP_VERSION,
    on_startup=[set_logger_settings],
    on_shutdown=[logging.shutdown]
)


# Эндпойнты

documentation_endpoints = { "docs": "/docs", "redoc": "/redoc" }

class AppInfo(BaseModel):
    service: str = Field(
        description="Название приложения", examples=[APP_TITLE]
    )
    version: str = Field(
        description="Версия приложения", examples=[APP_VERSION]
    )
    documentation_endpoints: dict[str,str] = Field(
        description="Ссылки на документацию", examples=[documentation_endpoints]
    )
    
@app.get("/", response_model=AppInfo, description="Информация о приложении")
def index() -> AppInfo:
    return AppInfo(
        service=APP_TITLE,
        version=APP_VERSION,
        documentation_endpoints=documentation_endpoints,
    )


class RecommendationsResponse(BaseModel):
    item_ids: ItemIdsType = Field(
        description="id рекомендуемых товаров", 
        examples=[[26477, 20017, 103127]],
    )

@app.get(
    "/recommend/{user_id}", 
    response_model=RecommendationsResponse, 
    description="Рекомендации товаров для пользователя"
)
def get_recommendations(user_id: int) -> RecommendationsResponse:
    try:
        # Первым значением мы получаем группу пользователя
        # Пока видится, что ее незачем возвращать в публичное апи
        _, recommend_items = recommender_factory.get_recommender_items(user_id)
        item_ids = recommend_items()
        
        return RecommendationsResponse(item_ids=item_ids)
    
    except Exception as error:
        error_message = ". ".join([
            f"Fail on get recommendations for user_id={user_id}",
            str(error),
            traceback.format_exc(),
        ])
        logger.error(error_message)
        
        raise


@app.post(
    "/metrics", 
    response_model=GroupMetricsResponse,
    description="Подсчитывает метрики по переданным интеракциям для каждой группы пользователей",
)
def calculate_metrics(request: GroupMetricsRequest) -> GroupMetricsResponse:
    try:
        return calculate_group_metrics(request)
    except Exception as error:
        error_message = ". ".join([
            "An error occurred while calculating metrics",
            str(error),
            traceback.format_exc(),
        ])
        logger.error(error_message)
        
        raise
