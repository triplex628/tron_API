import pytest
from fastapi.testclient import TestClient
from app import app
from database import Base, engine

# создание таблиц для тестовой среды (если не созданы)
Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_query_endpoint():

    # пример запроса к /query с тестовым адресом кошелька
    data = {"wallet_address": "TXYZ1234567890ABCDEF"}  # адрес выдумал
    response = client.post("/query", json=data)

    # ждем 200 если все ок и 400 если адрес невалидный
    assert response.status_code in [200, 400]

    print(response.json())


def test_get_queries_endpoint():

    # проверяем, что /queries кидает 200 и возвращает список
    response = client.get("/queries?skip=0&limit=1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

    print(response.json())

