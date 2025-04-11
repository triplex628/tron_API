from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.sql import func
from database import Base

class WalletQuery(Base):
    __tablename__ = "wallet_queries"
    
    id = Column(Integer, primary_key=True, index=True)
    wallet_address = Column(String, nullable=False)
    trx_balance = Column(Float, nullable=True)
    bandwidth = Column(Integer, nullable=True)
    energy = Column(Integer, nullable=True)
    queried_at = Column(DateTime(timezone=True), server_default=func.now())
