from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import sessionmaker, relationship, declarative_base, Session
from pymongo import MongoClient, ASCENDING
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Generator
import os

# Конфигурация базы данных PostgreSQL
DATABASE_URL = "postgresql://stud:stud@127.0.0.1:5432/archdb"

# Инициализация PostgreSQL
engine = create_engine(DATABASE_URL)
SessionLocal: sessionmaker[Session] = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Инициализация MongoDB
MONGO_URL = "mongodb://mongo:27017"
mongo_client = MongoClient(MONGO_URL)
mongo_db = mongo_client["chat_service"]
mongo_chats = mongo_db["chats"]

# Инициализация FastAPI
app = FastAPI()

# Настройка хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Модель пользователя в PostgreSQL
class User(Base):
    __tablename__ = "users"  # Добавлено tablename
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    chats = relationship("Chat", secondary="user_chats")

# Модель чата в PostgreSQL
class Chat(Base):
   __tablename__ = "chats"  # Добавлено tablename
   id = Column(Integer, primary_key=True, index=True)
   name = Column(String, unique=True)
   type = Column(String)  # 'group' или 'ptp'
   users = relationship("User", secondary="user_chats")

# Таблица связи пользователей и чатов
user_chats = Table(
    "user_chats", Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("chat_id", Integer, ForeignKey("chats.id"))
)

# Зависимость для сессии PostgreSQL
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# MongoDB: Индексы
mongo_chats.create_index([("name", ASCENDING)], unique=True)

# Схемы Pydantic для запросов
class UserCreate(BaseModel):
    username: str
    first_name: str
    last_name: str
    password: str

class ChatCreate(BaseModel):
    name: str
    type: str  # 'group' или 'ptp'

class Message(BaseModel):
    chat_id: str
    sender_id: int
    content: str

# API: Создание нового пользователя
@app.post("/users/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# API: Поиск пользователя по логину
@app.get("/users/{username}")
def get_user(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# API: Создание группового чата
@app.post("/chats/")
def create_chat(chat: ChatCreate):
    if chat.type not in ["group", "ptp"]:
        raise HTTPException(status_code=400, detail="Invalid chat type")
    chat_doc = {"name": chat.name, "type": chat.type, "messages": []}
    try:
        mongo_chats.insert_one(chat_doc)
    except:
        raise HTTPException(status_code=400, detail="Chat already exists")
    return chat_doc

# API: Добавление сообщения в чат
@app.post("/chats/{chat_name}/messages/")
def add_message(chat_name: str, message: Message):
    chat = mongo_chats.find_one({"name": chat_name})
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    message_doc = {"sender_id": message.sender_id, "content": message.content}
    mongo_chats.update_one({"name": chat_name}, {"$push": {"messages": message_doc}})
    return {"message": "Message added"}

# API: Получение сообщений чата
@app.get("/chats/{chat_name}/messages/")
def get_messages(chat_name: str):
    chat = mongo_chats.find_one({"name": chat_name})
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat.get("messages", [])