from pydantic import BaseModel, Field
from pathlib import Path
from fastapi import FastAPI
import logging
from logging.handlers import RotatingFileHandler
import traceback

from .utils.types import ItemIdsType
from .utils.metrics import (
    calculate_group_metrics, 
    GroupMetricsRequest,
    GroupMetricsResponse,
)
from .recommender_factory import recommender_factory


# Версия приложения
VERSION = "0.1.0"


# Путь к текущему файлу
current_file = Path(__file__).resolve()
# Путь к папке с приложением
APP_PATH = current_file.parent.resolve()


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
    title="Product recommendation system API",
    description="API рекомендательной системы товаров",
    version=VERSION,
    on_startup=[set_logger_settings],
    on_shutdown=[logging.shutdown]
)


# Эндпойнты
@app.get("/", description="Информация о приложении")
def index() -> dict:
    return {
        "service": "Product recommendation system",
        "version": VERSION,
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "recommend": "/recommend/{user_id}"
        }
    }


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
            traceback.format_exc()
        ])
        logger.error(error_message)
        
        raise


@app.post(
    "/metrics", 
    response_model=GroupMetricsRequest,
    description="Подсчитывает метрики по переданным интеракциям для каждой группы пользователей",
)
def calculate_metrics(request: GroupMetricsRequest) -> GroupMetricsResponse:
    return calculate_group_metrics(request)
