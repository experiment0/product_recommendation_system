# Загружает зависимости проекта
install:
	uv sync

# Запускает сервер
start:
	uv run uvicorn rec_sys.app.main:app --reload
