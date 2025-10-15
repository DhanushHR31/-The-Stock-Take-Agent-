from sqlalchemy import Column, Integer, String, Float, DateTime
import datetime
from .base import Base

class AdjustmentLog(Base):
    __tablename__ = 'adjustment_log'
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, nullable=False)
    location_id = Column(Integer, nullable=False)
    old_quantity = Column(Float, nullable=False)
    new_quantity = Column(Float, nullable=False)
    reason_code = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
