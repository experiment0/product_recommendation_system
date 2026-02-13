# Для annoy нужна полная версия python, поэтому не берем *-slim
FROM python:3.10

# Рабочая папка с приложением внутри контейнера
WORKDIR /usr/src/app

# Копируем содержимое текущей папки в рабочую папку контейнера
COPY ./ ./app

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r app/requirements.txt

# Запускаем сервер
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]