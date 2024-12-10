from kafka import KafkaConsumer
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, String
import json
import os
import time

# Конфигурация
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://stud:stud@localhost:5432/archdb")
KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL", "kafka:9092")
TOPIC_NAME = "user_creation"

# PostgreSQL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Модель для пользователя
class User:
    tablename = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

# Ожидание доступности Kafka
def wait_for_kafka():
    consumer = None
    while consumer is None:
        try:
            # Пробуем подключиться к Kafka
            consumer = KafkaConsumer(
                TOPIC_NAME,
                bootstrap_servers=[KAFKA_BROKER_URL],
                value_deserializer=lambda v: json.loads(v.decode("utf-8"))
            )
            print("Connected to Kafka.")
        except Exception as e:
            print(f"Kafka not ready, retrying... Error: {e}")
            time.sleep(5)  # Ждем 5 секунд перед повторной попыткой
    return consumer

# Подключаемся к Kafka
consumer = wait_for_kafka()

# Функция сохранения пользователя в базу данных PostgreSQL
def save_user_to_db(user_data):
    with SessionLocal() as db:
        user = User(**user_data)
        db.add(user)
        db.commit()

# Чтение сообщений из Kafka и сохранение пользователей в базу данных
for message in consumer:
    save_user_to_db(message.value)
