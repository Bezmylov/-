# Используем Python 3.10
FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости (включая Tkinter)
RUN apt-get update && apt-get install -y \
    wait-for-it \
    python3-tk \
    && apt-get clean

# Копируем файлы проекта в контейнер
COPY . .

COPY consumer.py /app/consumer.py

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Даем права на выполнение скрипта инициализации MongoDB
RUN chmod +x /app/init_mongo.py

# Устанавливаем переменную окружения для корректного вывода логов
ENV PYTHONUNBUFFERED=1

# Открываем порт для FastAPI
EXPOSE 8000

# Используем wait-for-it для ожидания Kafka перед запуском приложения
CMD ["bash", "-c", "wait-for-it kafka:9092 -- python /app/init_mongo.py && uvicorn main:app --host 0.0.0.0 --port 8000"]