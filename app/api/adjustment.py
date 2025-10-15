from fastapi import APIRouter, HTTPException, Body
from sqlalchemy.orm import Session
from ..models import models
from ..models.adjustment_log import AdjustmentLog
from ..db import get_db
from fastapi import Depends
from pydantic import BaseModel

class AdjustStockRequest(BaseModel):
    item_id: int
    location_id: int
    new_quantity: float
    reason_code: str

router = APIRouter(prefix="/adjust_stock", tags=["Stock Adjustment"])

@router.post("")
def AdjustStockAPI(request: AdjustStockRequest, db: Session = Depends(get_db)):
    inv = db.query(models.InventoryLevel).filter(
        models.InventoryLevel.item_id == request.item_id,
        models.InventoryLevel.location_id == request.location_id
    ).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Inventory record not found.")
    old_quantity = inv.quantity_on_hand
    setattr(inv, 'quantity_on_hand', request.new_quantity)
    # Log the adjustment
    log = AdjustmentLog(
        item_id=request.item_id,
        location_id=request.location_id,
        old_quantity=old_quantity,
        new_quantity=request.new_quantity,
        reason_code=request.reason_code
    )
    db.add(log)
    try:
        db.commit()
        db.refresh(inv)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to adjust stock: {str(e)}")
    return {"message": "Stock adjusted", "item_id": request.item_id, "location_id": request.location_id, "new_quantity": request.new_quantity, "reason_code": request.reason_code}
