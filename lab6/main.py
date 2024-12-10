from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session, sessionmaker, declarative_base
from sqlalchemy import create_engine, Column, Integer, String
from pymongo import MongoClient
from redis import Redis
from kafka import KafkaProducer
import json
import os

# Конфигурация
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://stud:stud@localhost:5432/archdb")
MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27017")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL", "kafka:9092")
TOPIC_NAME = "user_creation"

# PostgreSQL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

# MongoDB
mongo_client = MongoClient(MONGO_URL)
mongo_db = mongo_client["chat_service"]
mongo_chats = mongo_db["chats"]

# Redis
redis_client = Redis.from_url(REDIS_URL, decode_responses=True)

# Kafka
producer = KafkaProducer(bootstrap_servers="kafka:9092")  # Заменено с localhost на kafka

# FastAPI
app = FastAPI()

# Зависимость для базы данных PostgreSQL
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API: Создание пользователя (Command)
@app.post("/users/")
def create_user(username: str, email: str, password: str):
    hashed_password = "hashed_" + password  # Простая хеш-функция
    message = {"username": username, "email": email, "hashed_password": hashed_password}
    producer.send(TOPIC_NAME, message)
    return {"message": "User creation event sent to Kafka"}

# API: Получение пользователя (Query)
@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    redis_key = f"user:{user_id}"
    cached_user = redis_client.get(redis_key)
    if cached_user:
        return json.loads(cached_user)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_data = {"id": user.id, "username": user.username, "email": user.email}
    redis_client.set(redis_key, json.dumps(user_data), ex=3600)
    return user_data

# API: Создание чата (MongoDB)
@app.post("/chats/")
def create_chat(name: str, chat_type: str):
    if chat_type not in ["group", "ptp"]:
        raise HTTPException(status_code=400, detail="Invalid chat type")
    chat_doc = {"name": name, "type": chat_type, "messages": []}
    mongo_chats.insert_one(chat_doc)
    return chat_doc

# API: Добавление сообщения в чат (MongoDB)
@app.post("/chats/{chat_name}/messages/")
def add_message(chat_name: str, sender_id: int, content: str):
    chat = mongo_chats.find_one({"name": chat_name})
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    message_doc = {"sender_id": sender_id, "content": content}
    mongo_chats.update_one({"name": chat_name}, {"$push": {"messages": message_doc}})
    return {"message": "Message added"}

# API: Получение сообщений чата (MongoDB)
@app.get("/chats/{chat_name}/messages/")
def get_messages(chat_name: str):
    chat = mongo_chats.find_one({"name": chat_name})
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat.get("messages", [])