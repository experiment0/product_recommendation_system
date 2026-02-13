# Загружает зависимости проекта
install:
	uv sync

# Запускает сервер
start:
	uv run uvicorn rec_sys.app.main:app --reload

# Запускает пример подсчета метрик для первого батча тестовой выборки
# TODO - для linux будет python3
metrics:
	uv run python rec_sys/scripts/calculate_metrics.py
