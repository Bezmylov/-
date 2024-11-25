from pymongo import MongoClient
import json

def initialize_mongodb():
    # Подключение к MongoDB
    client = MongoClient('mongodb://mongo:27017/')  # Подключение к контейнеру MongoDB
    db = client['mydatabase']  # Укажите имя базы данных
    collection = db['mycollection']  # Укажите имя коллекции

    # Документ для вставки
    document = {
        'name': 'Jone',
        'age': 30,
        'email': 'J30@mail.ru'
    }

    # Вставка документа
    result = collection.insert_one(document)
    if result.acknowledged:
        print('Document inserted successfully.')
        print('Inserted document ID:', result.inserted_id)
    else:
        print('Failed to insert document.')

    # Запрос документов с определенными условиями
    query = {'age': {'$gte': 20}}  # Возвращаем документы, где возраст >= 20
    documents = collection.find(query)

    # Вывод документов
    for document in documents:
        json_document = json.dumps(document, indent=2, default=str)
        print(json_document)

if __name__ == "__main__":
    initialize_mongodb()