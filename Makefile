# Загружает зависимости проекта
install:
	uv sync


# Запускает сервер
# Приложение будет доступно по адресу http://localhost:8000, 
start:
	uv run uvicorn rec_sys.app.main:app --reload --port 8000


# Запускает пример подсчета метрик для первого батча тестовой выборки
# Приложение должно быть запущено на http://localhost:8000
# Команда для Linux
metrics:
	uv run python3 rec_sys/scripts/calculate_metrics.py
# Команда для Windows
metrics-win:
	uv run python rec_sys/scripts/calculate_metrics.py


# Собирает docker-образ приложения
app-docker-build:
	docker build -t experiment0/product_recommendation_system ./rec_sys/app

# Отправляет образ на hub.docker.com
app-docker-push:
	docker push experiment0/product_recommendation_system

# Скачивает образ
app-docker-pull:
	docker pull experiment0/product_recommendation_system:latest

# Запускает docker-контейнер (если он уже существует на машине)
app-docker-run:
	docker run -p 8000:8000 --rm --name rec_sys_image experiment0/product_recommendation_system:latest 


# Команды, которые могут совпадать с именами директорий и не должны быть с ними перепутаны
.PHONY: install start metrics metrics-win