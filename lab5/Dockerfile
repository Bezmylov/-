FROM python:3.10

WORKDIR /app

# Копируем файлы проекта
COPY . .

# Устанавливаем зависимости
RUN pip install -r requirements.txt

# Даем права на выполнение скрипта инициализации
RUN chmod +x /app/init_mongo.py

# Указываем переменную окружения для FastAPI
ENV PYTHONUNBUFFERED=1

# Открываем порт приложения
EXPOSE 8000

# Команда запуска приложения
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]