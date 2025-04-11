import pytest
from sqlalchemy.orm import Session
from app import query_wallet
from models import WalletQuery
from database import SessionLocal
from fastapi import HTTPException

# класс-имитация запроса
class DummyRequest:
    wallet_address = "XYZ1234567890ABCDEF"

def test_db_write(monkeypatch):
    # подмена функций tronpy чтобы не делать реальный запрос в сеть
    def dummy_get_account_balance(address):
        return 123.45

    def dummy_get_account_resource(address):
        return {"freeNetLimit": 100, "freeNetUsed": 10, "EnergyLimit": 200, "EnergyUsed": 20}

    monkeypatch.setattr("app.client.get_account_balance", dummy_get_account_balance)
    monkeypatch.setattr("app.client.get_account_resource", dummy_get_account_resource)
    
    db: Session = SessionLocal()
    initial_count = db.query(WalletQuery).count()
    request = DummyRequest()
    result = query_wallet(request, db)
    new_count = db.query(WalletQuery).count()
    
    # проверяем что все добавилось и рассчиталось корректно
    assert new_count == initial_count + 1
    assert result["trx_balance"] == 123.45
    assert result["bandwidth"] == 90    # 100 - 10
    assert result["energy"] == 180       # 200 - 20
    db.close()
