
# Delete AdjustmentLog route

# Delete AdjustmentLog route (placed after router and imports)

from fastapi import APIRouter, Request, Depends, Form, Query, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .db import get_db
from .models import models
from .models.adjustment_log import AdjustmentLog
from fastapi import status
from starlette.status import HTTP_303_SEE_OTHER
from sqlalchemy import or_
from pydantic import BaseModel

router = APIRouter()
templates = Jinja2Templates(directory="ganana/app/templates")

# Show all information page
@router.get("/show-information")
def show_information(request: Request, db: Session = Depends(get_db)):
    stock_takes = db.query(models.StockTake).all()
    stock_counts = db.query(models.StockTakeCount).all()
    inventory = db.query(models.InventoryLevel).all()
    adjustment_logs = db.query(AdjustmentLog).all()
    # Prepare data for template with correct keys
    return templates.TemplateResponse("show_information.html", {
        "request": request,
        "stock_takes": stock_takes,
        "stock_counts": stock_counts,
        "inventory": inventory,
        "adjustment_logs": adjustment_logs
    })

@router.post("/clear-all-data")
def clear_all_data(request: Request, db: Session = Depends(get_db)):
    # Delete in order to avoid foreign key issues
    db.query(AdjustmentLog).delete()
    db.query(models.StockTakeCount).delete()
    db.query(models.InventoryLevel).delete()
    db.query(models.StockTake).delete()
    db.commit()
    return {"message": "All data cleared successfully"}

# List and delete for StockTakeCount
@router.get("/stock-count")
def stock_count_page(request: Request, db: Session = Depends(get_db)):
    counts = db.query(models.StockTakeCount).all()
    return templates.TemplateResponse("stock_count.html", {"request": request, "counts": counts})

@router.post("/stock-count/{count_id}/delete")
def delete_stock_count(request: Request, count_id: int, db: Session = Depends(get_db)):
    count = db.query(models.StockTakeCount).filter(models.StockTakeCount.id == count_id).first()
    if count:
        db.delete(count)
        db.commit()
    referer = request.headers.get("referer", "")
    if "/show-information" in referer:
        return RedirectResponse(url="/show-information", status_code=HTTP_303_SEE_OTHER)
    return RedirectResponse(url="/stock-count", status_code=HTTP_303_SEE_OTHER)

# List and delete for InventoryLevel
@router.get("/inventory")
def inventory_page(request: Request, db: Session = Depends(get_db)):
    inventory = db.query(models.InventoryLevel).all()
    return templates.TemplateResponse("inventory.html", {"request": request, "inventory": inventory})

@router.post("/inventory/{inv_id}/delete")
def delete_inventory(request: Request, inv_id: int, db: Session = Depends(get_db)):
    inv = db.query(models.InventoryLevel).filter(models.InventoryLevel.id == inv_id).first()
    if inv:
        db.delete(inv)
        db.commit()
    referer = request.headers.get("referer", "")
    if "/show-information" in referer:
        return RedirectResponse(url="/show-information", status_code=HTTP_303_SEE_OTHER)
    return RedirectResponse(url="/inventory", status_code=HTTP_303_SEE_OTHER)


# Delete AdjustmentLog route
@router.post("/adjustment-log/{log_id}/delete")
def delete_adjustment_log(request: Request, log_id: int, db: Session = Depends(get_db)):
    log = db.query(AdjustmentLog).filter(AdjustmentLog.id == log_id).first()
    if log:
        db.delete(log)
        db.commit()
    referer = request.headers.get("referer", "")
    if "/show-information" in referer:
        return RedirectResponse(url="/show-information", status_code=HTTP_303_SEE_OTHER)
    return RedirectResponse(url="/adjust-stock", status_code=HTTP_303_SEE_OTHER)

# Delete StockTake route
@router.post("/stock-take/{stock_take_id}/delete")
def delete_stock_take(request: Request, stock_take_id: int, db: Session = Depends(get_db)):
    stock_take = db.query(models.StockTake).filter(models.StockTake.id == stock_take_id).first()
    if stock_take:
        db.delete(stock_take)
        db.commit()
    referer = request.headers.get("referer", "")
    if "/show-information" in referer:
        return RedirectResponse(url="/show-information", status_code=HTTP_303_SEE_OTHER)
    return RedirectResponse(url="/stock-take", status_code=HTTP_303_SEE_OTHER)


# Stock Take create routes (must be above /stock-take/{stock_take_id})
@router.get("/stock-take/create")
def create_stock_take_page(request: Request):
    return templates.TemplateResponse("create_stock_take.html", {"request": request})


@router.post("/stock-take/create")
def create_stock_take(
    request: Request,
    id: int = Form(...),
    location_id: int = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(None),
    status: str = Form(...),
    db: Session = Depends(get_db)
):
    from datetime import datetime
    stock_take = models.StockTake()
    stock_take.__dict__["id"] = id
    setattr(stock_take, 'location_id', location_id)  # Fix Pylance type error
    # Parse start_date and end_date as date strings
    try:
        setattr(stock_take, 'start_date', datetime.strptime(start_date, '%Y-%m-%d'))  # Fix Pylance type error
    except ValueError:
        msg = "Invalid start date format. Use YYYY-MM-DD."
        return templates.TemplateResponse("create_stock_take.html", {"request": request, "message": msg})
    if end_date:
        try:
            setattr(stock_take, 'end_date', datetime.strptime(end_date, '%Y-%m-%d'))  # Fix Pylance type error
        except ValueError:
            msg = "Invalid end date format. Use YYYY-MM-DD."
            return templates.TemplateResponse("create_stock_take.html", {"request": request, "message": msg})
    else:
        setattr(stock_take, 'end_date', None)  # Fix Pylance type error
    setattr(stock_take, 'status', status)  # Fix Pylance type error
    db.add(stock_take)
    try:
        db.commit()
        db.refresh(stock_take)
        msg = f"Stock Take #{id} created."
    except IntegrityError:
        db.rollback()
        msg = f"Error: Stock Take ID {id} already exists. Please use a unique ID."
    return RedirectResponse(url="/stock-take", status_code=HTTP_303_SEE_OTHER)

# Stock Take detail and update page
@router.get("/stock-take/{stock_take_id}")
def stock_take_detail(request: Request, stock_take_id: int, db: Session = Depends(get_db)):
    stock_take = db.query(models.StockTake).filter(models.StockTake.id == stock_take_id).first()
    if not stock_take:
        return templates.TemplateResponse("stock_take_detail.html", {"request": request, "error": f"Stock Take {stock_take_id} not found."})
    return templates.TemplateResponse("stock_take_detail.html", {"request": request, "stock_take": stock_take})

@router.post("/stock-take/{stock_take_id}")
def update_stock_take(request: Request, stock_take_id: int, location_id: int = Form(...), start_date: str = Form(...), end_date: str = Form(None), status: str = Form(...), db: Session = Depends(get_db)):
    stock_take = db.query(models.StockTake).filter(models.StockTake.id == stock_take_id).first()
    if not stock_take:
        return templates.TemplateResponse("stock_take_detail.html", {"request": request, "error": f"Stock Take {stock_take_id} not found."})
    from datetime import datetime
    setattr(stock_take, 'location_id', int(location_id))  # Fix Pylance type error
    try:
        setattr(stock_take, 'start_date', datetime.strptime(start_date, '%Y-%m-%d'))  # Fix Pylance type error
    except ValueError:
        return templates.TemplateResponse("stock_take_detail.html", {"request": request, "stock_take": stock_take, "error": "Invalid start date format. Use YYYY-MM-DD."})
    if end_date:
        try:
            setattr(stock_take, 'end_date', datetime.strptime(end_date, '%Y-%m-%d'))  # Fix Pylance type error
        except ValueError:
            return templates.TemplateResponse("stock_take_detail.html", {"request": request, "stock_take": stock_take, "error": "Invalid end date format. Use YYYY-MM-DD."})
    else:
        setattr(stock_take, 'end_date', None)  # Fix Pylance type error
    setattr(stock_take, 'status', status)  # Fix Pylance type error
    db.commit()
    db.refresh(stock_take)
    return templates.TemplateResponse("stock_take_detail.html", {"request": request, "stock_take": stock_take, "message": "Stock Take updated."})

# Stock Take Variance Report page
@router.get("/report")
def report_page(request: Request, stock_take_id: str = Query(default=""), db: Session = Depends(get_db)):
    stock_take = None
    counts = []
    inventory = {}
    adjustment_logs = []
    message = None
    parsed_id = None
    if stock_take_id is not None and stock_take_id != "":
        try:
            parsed_id = int(stock_take_id)
        except ValueError:
            message = f"Invalid Stock Take ID: {stock_take_id}"
    if parsed_id is not None:
        stock_take = db.query(models.StockTake).filter(models.StockTake.id == parsed_id).first()
        if not stock_take:
            message = f"Stock Take ID {stock_take_id} not found."
        else:
            counts = db.query(models.StockTakeCount).filter(models.StockTakeCount.stock_take_id == parsed_id).all()
            # Get inventory for all items in this stock take
            item_ids = [c.item_id for c in counts]
            invs = db.query(models.InventoryLevel).filter(models.InventoryLevel.item_id.in_(item_ids), models.InventoryLevel.location_id == stock_take.location_id).all()
            for inv in invs:
                inventory[inv.item_id] = {"on_hand": inv.quantity_on_hand, "committed": inv.quantity_committed}
            for iid in item_ids:
                if iid not in inventory:
                    inventory[iid] = None
            # Get adjustment logs for this location and items
            if stock_take:
                adjustment_logs = db.query(AdjustmentLog).filter(AdjustmentLog.location_id == stock_take.location_id, AdjustmentLog.item_id.in_(item_ids)).all()
    return templates.TemplateResponse("variance_report.html", {"request": request, "stock_take": stock_take, "counts": counts, "inventory": inventory, "adjustment_logs": adjustment_logs, "message": message, "stock_take_id": stock_take_id})



# InventoryLevel creation
@router.get("/inventory/create")
def create_inventory_page(request: Request):
    return templates.TemplateResponse("create_inventory.html", {"request": request})

@router.post("/inventory/create")
def create_inventory(
    request: Request,
    id: int = Form(...),
    item_id: int = Form(...),
    location_id: int = Form(...),
    quantity_on_hand: float = Form(...),
    quantity_committed: float = Form(...),
    db: Session = Depends(get_db)
):
    inv = models.InventoryLevel()
    inv.__dict__["id"] = id
    setattr(inv, 'item_id', item_id)  # Fix Pylance type error
    setattr(inv, 'location_id', location_id)  # Fix Pylance type error
    setattr(inv, 'quantity_on_hand', quantity_on_hand)  # Fix Pylance type error
    setattr(inv, 'quantity_committed', quantity_committed)  # Fix Pylance type error
    db.add(inv)
    try:
        db.commit()
        db.refresh(inv)
        msg = f"Inventory #{id} for item {item_id} at location {location_id} created."
    except IntegrityError:
        db.rollback()
        msg = f"Error: Inventory ID {id} already exists. Please use a unique ID."
    return templates.TemplateResponse("create_inventory.html", {"request": request, "message": msg})

# StockTakeCount creation
@router.get("/stock-count/create")
def create_stock_count_page(request: Request):
    return templates.TemplateResponse("create_stock_count.html", {"request": request})

from sqlalchemy.exc import IntegrityError

@router.post("/stock-count/create")
def create_stock_count(
    request: Request,
    id: int = Form(...),
    stock_take_id: int = Form(...),
    item_id: int = Form(...),
    system_quantity: float = Form(...),
    counted_quantity: float = Form(...),
    db: Session = Depends(get_db)
):
    # Check if stock_take exists
    stock_take = db.query(models.StockTake).filter(models.StockTake.id == stock_take_id).first()
    if not stock_take:
        msg = f"Error: Stock Take ID {stock_take_id} not found."
        return templates.TemplateResponse("create_stock_count.html", {"request": request, "message": msg})
    
    variance = counted_quantity - system_quantity
    count = models.StockTakeCount()
    count.__dict__["id"] = id
    setattr(count, 'stock_take_id', stock_take_id)  # Fix Pylance type error
    setattr(count, 'item_id', item_id)  # Fix Pylance type error
    setattr(count, 'system_quantity', system_quantity)  # Fix Pylance type error
    setattr(count, 'counted_quantity', counted_quantity)  # Fix Pylance type error
    setattr(count, 'variance', variance)  # Fix Pylance type error
    db.add(count)
    try:
        db.commit()
        db.refresh(count)
        msg = f"Stock count #{id} for item {item_id} added to stock take {stock_take_id}."
    except IntegrityError:
        db.rollback()
        msg = f"Error: Stock count ID {id} already exists. Please use a unique ID."
    return templates.TemplateResponse("create_stock_count.html", {"request": request, "message": msg})

@router.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/stock-take")
def stock_take_page(request: Request, db: Session = Depends(get_db)):
    stock_takes = db.query(models.StockTake).all()
    return templates.TemplateResponse("stock_take.html", {"request": request, "stock_takes": stock_takes})




@router.get("/variance-report/{stock_take_id}")
def variance_report(request: Request, stock_take_id: int, db: Session = Depends(get_db)):
    counts = db.query(models.StockTakeCount).filter(models.StockTakeCount.stock_take_id == stock_take_id).all()
    stock_take = db.query(models.StockTake).filter(models.StockTake.id == stock_take_id).first()
    # Build inventory mapping keyed by item_id to match template expectations
    inventory = {}
    adjustment_logs = []
    if stock_take:
        item_ids = [c.item_id for c in counts]
        invs = db.query(models.InventoryLevel).filter(
            models.InventoryLevel.item_id.in_(item_ids),
            models.InventoryLevel.location_id == stock_take.location_id
        ).all()
        for inv in invs:
            inventory[inv.item_id] = {"on_hand": inv.quantity_on_hand, "committed": inv.quantity_committed}
        # Ensure all items present in counts are represented in inventory mapping
        for iid in item_ids:
            if iid not in inventory:
                inventory[iid] = None
        adjustment_logs = db.query(AdjustmentLog).filter(
            AdjustmentLog.location_id == stock_take.location_id,
            AdjustmentLog.item_id.in_(item_ids)
        ).all()
    return templates.TemplateResponse("variance_report.html", {
        "request": request,
        "counts": counts,
        "stock_take_id": stock_take_id,
        "stock_take": stock_take,
        "inventory": inventory,
        "adjustment_logs": adjustment_logs
    })

## Warning report removed

# PDF download for variance report
from fastapi.responses import StreamingResponse
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


@router.get("/variance-report/{stock_take_id}/pdf")
def variance_report_pdf(stock_take_id: int, db: Session = Depends(get_db)):
    counts = db.query(models.StockTakeCount).filter(models.StockTakeCount.stock_take_id == stock_take_id).all()
    stock_take = db.query(models.StockTake).filter(models.StockTake.id == stock_take_id).first()
    item_ids = [c.item_id for c in counts]
    invs = db.query(models.InventoryLevel).filter(models.InventoryLevel.item_id.in_(item_ids), models.InventoryLevel.location_id == stock_take.location_id).all() if stock_take else []
    inventory = {inv.item_id: inv for inv in invs}
    adjustment_logs = db.query(AdjustmentLog).filter(AdjustmentLog.location_id == stock_take.location_id, AdjustmentLog.item_id.in_(item_ids)).all() if stock_take else []
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    y = 750
    p.setFont("Helvetica-Bold", 14)
    p.drawString(30, y, f"Stock Take Variance Report - Stock Take #{stock_take_id}")
    y -= 30
    if stock_take:
        p.setFont("Helvetica", 10)
        p.drawString(30, y, f"Location ID: {stock_take.location_id}  |  Status: {stock_take.status}  |  Start: {stock_take.start_date}  |  End: {stock_take.end_date}")
        y -= 20
    p.setFont("Helvetica-Bold", 12)
    p.drawString(30, y, "Item ID  System Qty  Counted Qty  Variance  On Hand  Committed  Adj Qty  Adj Reason  Adj Time")
    y -= 20
    p.setFont("Helvetica", 10)
    for c in counts:
        inv = inventory.get(c.item_id)
        adj = None
        for log in adjustment_logs:
            # Compare as Python ints to avoid SQLAlchemy column logic
            if int(getattr(log, 'item_id', 0)) == int(getattr(c, 'item_id', 0)):
                adj = log
                break
        p.drawString(30, y, f"{c.item_id}      {c.system_quantity}      {c.counted_quantity}      {c.variance}      {getattr(inv, 'quantity_on_hand', '-')}      {getattr(inv, 'quantity_committed', '-')}      {getattr(adj, 'new_quantity', '-')}      {getattr(adj, 'reason_code', '-')}      {getattr(adj, 'timestamp', '-')} ")
        y -= 15
        if y < 100:
            p.showPage()
            y = 750
    p.save()
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=variance_report_{stock_take_id}.pdf"})



@router.get("/adjust-stock")
def adjust_stock_page(request: Request, db: Session = Depends(get_db)):
    all_inventory = db.query(models.InventoryLevel).all()
    all_stock_takes = db.query(models.StockTake).all()
    all_stock_counts = db.query(models.StockTakeCount).all()
    adjustment_logs = db.query(AdjustmentLog).all()
    return templates.TemplateResponse("adjust_stock.html", {
        "request": request,
        "all_inventory": all_inventory,
        "all_stock_takes": all_stock_takes,
        "all_stock_counts": all_stock_counts,
        "adjustment_logs": adjustment_logs
    })

@router.get("/adjust-stock-input")
def adjust_stock_input_page(request: Request):
    return templates.TemplateResponse("adjust_stock_input.html", {"request": request})

@router.post("/adjust-stock-input")
def adjust_stock_input(
    request: Request,
    item_id: int = Form(...),
    location_id: int = Form(...),
    new_quantity: float = Form(...),
    reason_code: str = Form(...),
    other_reason: str = Form(None),
    db: Session = Depends(get_db)
):
    # Handle other reason
    if reason_code == "OTHER" and other_reason:
        reason_code = other_reason

    # Check if inventory exists
    inventory = db.query(models.InventoryLevel).filter(
        models.InventoryLevel.item_id == item_id,
        models.InventoryLevel.location_id == location_id
    ).first()

    if not inventory:
        return templates.TemplateResponse("adjust_stock_input.html", {
            "request": request,
            "error": f"No inventory found for Item ID {item_id} at Location ID {location_id}."
        })

    old_quantity = inventory.quantity_on_hand

    # Update inventory
    setattr(inventory, 'quantity_on_hand', new_quantity)

    # Create adjustment log
    adjustment_log = AdjustmentLog(
        item_id=item_id,
        location_id=location_id,
        old_quantity=old_quantity,
        new_quantity=new_quantity,
        reason_code=reason_code
    )
    db.add(adjustment_log)

    try:
        db.commit()
        db.refresh(inventory)
        db.refresh(adjustment_log)
        return RedirectResponse(url=f"/adjust-stock?success=1", status_code=HTTP_303_SEE_OTHER)
    except Exception as e:
        db.rollback()
        return templates.TemplateResponse("adjust_stock_input.html", {
            "request": request,
            "error": f"Error adjusting stock: {str(e)}"
        })




@router.get("/search")
def search(request: Request, query: str = Query(default=""), db: Session = Depends(get_db)):
    q = (query or "").strip()
    results = {
        "stock_takes": [],
        "stock_counts": [],
        "inventory": [],
        "adjustment_logs": []
    }
    if not q:
        return templates.TemplateResponse("search_results.html", {"request": request, "query": q, "results": results})

    is_int = False
    try:
        q_int = int(q)
        is_int = True
    except ValueError:
        q_int = None

    # StockTake
    st_conditions = []
    if is_int:
        st_conditions.extend([
            models.StockTake.id == q_int,
            models.StockTake.location_id == q_int
        ])
    st_conditions.append(models.StockTake.status.ilike(f"%{q}%"))
    results["stock_takes"] = db.query(models.StockTake).filter(or_(*st_conditions)).all() if st_conditions else []

    # StockTakeCount
    stc_conditions = []
    if is_int:
        stc_conditions.extend([
            models.StockTakeCount.id == q_int,
            models.StockTakeCount.stock_take_id == q_int,
            models.StockTakeCount.item_id == q_int
        ])
    results["stock_counts"] = db.query(models.StockTakeCount).filter(or_(*stc_conditions)).all() if stc_conditions else []

    # Inventory
    inv_conditions = []
    if is_int:
        inv_conditions.extend([
            models.InventoryLevel.id == q_int,
            models.InventoryLevel.item_id == q_int,
            models.InventoryLevel.location_id == q_int
        ])
    results["inventory"] = db.query(models.InventoryLevel).filter(or_(*inv_conditions)).all() if inv_conditions else []

    # Adjustment Logs
    adj_conditions = []
    if is_int:
        adj_conditions.extend([
            AdjustmentLog.id == q_int,
            AdjustmentLog.item_id == q_int,
            AdjustmentLog.location_id == q_int
        ])
    adj_conditions.append(AdjustmentLog.reason_code.ilike(f"%{q}%"))
    results["adjustment_logs"] = db.query(AdjustmentLog).filter(or_(*adj_conditions)).all() if adj_conditions else []

    return templates.TemplateResponse("search_results.html", {"request": request, "query": q, "results": results})
