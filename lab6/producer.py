import os
import time
import json
from kafka import KafkaProducer

# Конфигурация Kafka
KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL", "kafka1:9092")
TOPIC_NAME = "user_creation"

# Ожидание готовности Kafka
def wait_for_kafka():
    producer = None
    while not producer:
        try:
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BROKER_URL,
                value_serializer=lambda v: json.dumps(v).encode("utf-8")
            )
            print("Successfully connected to Kafka.")
        except Exception as e:
            print(f"Waiting for Kafka... Error: {e}")
            time.sleep(5)
    return producer

# Kafka Producer
producer = wait_for_kafka()

# Функция отправки данных
def produce_message(user_data):
    try:
        producer.send(TOPIC_NAME, value=user_data)
        producer.flush()
        print(f"Sent message: {user_data}")
    except Exception as e:
        print(f"Error sending message: {e}")

# Тестовые сообщения
users = [
    {"id": 1, "username": "user1", "email": "user1@example.com", "hashed_password": "password1"},
    {"id": 2, "username": "user2", "email": "user2@example.com", "hashed_password": "password2"},
]

print("Producing messages...")
for user in users:
    produce_message(user)
    time.sleep(1)  # Имитируем задержку между отправками