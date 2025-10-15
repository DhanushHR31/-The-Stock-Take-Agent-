from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from .base import Base
import datetime

class StockTake(Base):
    __tablename__ = 'stock_take'
    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, nullable=False)
    start_date = Column(DateTime, default=datetime.datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    status = Column(String, default='open')
    counts = relationship("StockTakeCount", back_populates="stock_take")

class StockTakeCount(Base):
    __tablename__ = 'stock_take_count'
    id = Column(Integer, primary_key=True, index=True)
    stock_take_id = Column(Integer, ForeignKey('stock_take.id'))
    item_id = Column(Integer, nullable=False)
    system_quantity = Column(Float, nullable=False)
    counted_quantity = Column(Float, nullable=False)
    variance = Column(Float, nullable=False)
    stock_take = relationship("StockTake", back_populates="counts")

class InventoryLevel(Base):
    __tablename__ = 'inventory_level'
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, nullable=False)
    location_id = Column(Integer, nullable=False)
    quantity_on_hand = Column(Float, nullable=False)
    quantity_committed = Column(Float, default=0)
