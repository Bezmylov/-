import time
import os
import json
from kafka import KafkaConsumer
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Базовая модель SQLAlchemy
Base = declarative_base()

# Конфигурация БД
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://stud:stud@db/archdb")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Конфигурация Kafka
TOPIC_NAME = "user_creation"
KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL", "kafka1:9092")

# Модель пользователя
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

# Создание таблиц, если их нет
Base.metadata.create_all(bind=engine)

# Ожидание готовности Kafka
def wait_for_kafka():
    consumer = None
    while not consumer:
        try:
            consumer = KafkaConsumer(
                TOPIC_NAME,
                bootstrap_servers=KAFKA_BROKER_URL,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                auto_offset_reset="earliest",
                group_id="user_consumer_group"
            )
            print("Successfully connected to Kafka.")
        except Exception as e:
            print(f"Waiting for Kafka... Error: {e}")
            time.sleep(5)
    return consumer

# Kafka Consumer
consumer = wait_for_kafka()

# Обработчик сообщений Kafka
def process_message(message):
    with SessionLocal() as session:
        user = User(**message)
        session.add(user)
        session.commit()
        print(f"User {user.username} saved to database.")

# Основной цикл обработки сообщений
print("Starting to consume messages...")
for msg in consumer:
    try:
        process_message(msg.value)
    except Exception as e:
        print(f"Error processing message: {e}")
