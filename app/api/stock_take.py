from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from ..models import models
from ..db import get_db
from fastapi import Depends

router = APIRouter(prefix="/stock_take", tags=["Stock Take"])

@router.get("/variance_report/{stock_take_id}")
def get_variance_report(stock_take_id: int, db: Session = Depends(get_db)):
    counts = db.query(models.StockTakeCount).filter(models.StockTakeCount.stock_take_id == stock_take_id).all()
    if not counts:
        raise HTTPException(status_code=404, detail="Stock take not found or no counts available.")
    report = [
        {
            "item_id": c.item_id,
            "system_quantity": c.system_quantity,
            "counted_quantity": c.counted_quantity,
            "variance": c.variance
        } for c in counts
    ]
    return {"stock_take_id": stock_take_id, "variance_report": report}
