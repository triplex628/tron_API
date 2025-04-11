from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session

from database import SessionLocal, engine
import models

# создание таблиц БД
models.Base.metadata.create_all(bind=engine)

from tronpy import Tron
client = Tron()

app = FastAPI(title="Tron Wallet Info Service")

# dependency для получения и управления сессией SQLAlchemy
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# модель пост-запроса 
class WalletQueryRequest(BaseModel):
    wallet_address: str

# модель ответа
class WalletQueryResponse(BaseModel):
    wallet_address: str
    trx_balance: float
    bandwidth: int
    energy: int
    queried_at: str

# запрос для получения инфы по кошельку
@app.post("/query", response_model=WalletQueryResponse)
def query_wallet(wallet_query: WalletQueryRequest, db: Session = Depends(get_db)):
    address = wallet_query.wallet_address
    try:
        # получаем баланс TRX
        balance = client.get_account_balance(address)

        # получаем bandwidth и energy
        resource = client.get_account_resource(address)
        free_net_limit = resource.get("freeNetLimit", 0) or 0
        free_net_used = resource.get("freeNetUsed", 0) or 0
        bandwidth = free_net_limit - free_net_used

        energy_limit = resource.get("EnergyLimit", 0) or 0
        energy_used = resource.get("EnergyUsed", 0) or 0
        energy = energy_limit - energy_used
    except Exception:
        # кидаем 400 если что-то не так
        raise HTTPException(status_code=400, detail="Неверный адрес кошелька или ошибка в сети Tron.")

    # сохраняем результат в БД
    wallet_query_record = models.WalletQuery(
        wallet_address=address,
        trx_balance=balance,
        bandwidth=bandwidth,
        energy=energy
    )
    db.add(wallet_query_record)
    db.commit()
    db.refresh(wallet_query_record)

    return {
        "wallet_address": wallet_query_record.wallet_address,
        "trx_balance": wallet_query_record.trx_balance,
        "bandwidth": wallet_query_record.bandwidth,
        "energy": wallet_query_record.energy,
        "queried_at": wallet_query_record.queried_at.isoformat()
    }

# запрос для получения списка кошельков и инфы о них (с пагинацией, лимит 10)
@app.get("/queries", response_model=List[WalletQueryResponse])
def get_queries(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    queries = (
        db.query(models.WalletQuery)
          .order_by(models.WalletQuery.queried_at.desc())
          .offset(skip)
          .limit(limit)
          .all()
    )
    result = []
    for q in queries:
        result.append({
            "wallet_address": q.wallet_address,
            "trx_balance": q.trx_balance,
            "bandwidth": q.bandwidth,
            "energy": q.energy,
            "queried_at": q.queried_at.isoformat()
        })
    return result
