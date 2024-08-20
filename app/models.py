from sqlalchemy import Column, Integer, Float, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Sell(Base):
    __tablename__ = 'sells'
    
    id = Column(Integer, primary_key=True)
    qty = Column(Float, nullable=False)
    rate = Column(Float, nullable=False)
    buy_rate = Column(Float)
    user_id = Column(Integer)
    deleted_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    

class Buy(Base):
    __tablename__ = 'buys'
    
    id = Column(Integer, primary_key=True)
    qty = Column(Float, nullable=False)
    rate = Column(Float, nullable=False)
    user_id = Column(Integer)
    deleted_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    
