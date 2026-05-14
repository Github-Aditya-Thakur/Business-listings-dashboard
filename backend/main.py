from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.dialects.mysql import insert  # NEW: for INSERT IGNORE

from database import get_db
from models import ListingMaster
from schemas import BulkInsertRequest

app = FastAPI(title="Business Listings Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

# 1) Bulk insert API (dedupe via UNIQUE + MySQL INSERT IGNORE)
@app.post("/api/listings/bulk")
def bulk_insert(payload: BulkInsertRequest, db: Session = Depends(get_db)):
    values = [
        {
            "business_name": item.business_name,
            "category": item.category,
            "city": item.city,
            "address": item.address,
            "phone": item.phone,
            "source": item.source,
        }
        for item in payload.listings
    ]

    stmt = insert(ListingMaster).values(values).prefix_with("IGNORE")
    result = db.execute(stmt)
    db.commit()

    return {"inserted": int(result.rowcount or 0), "received": len(values)}

# 2) Dashboard APIs
@app.get("/api/dashboard/city-wise")
def city_wise(db: Session = Depends(get_db)):
    data = (
        db.query(ListingMaster.city, func.count(ListingMaster.id))
        .group_by(ListingMaster.city)
        .order_by(func.count(ListingMaster.id).desc())
        .all()
    )
    return [{"name": (city or "Unknown"), "count": count} for city, count in data]

@app.get("/api/dashboard/category-wise")
def category_wise(db: Session = Depends(get_db)):
    data = (
        db.query(ListingMaster.category, func.count(ListingMaster.id))
        .group_by(ListingMaster.category)
        .order_by(func.count(ListingMaster.id).desc())
        .all()
    )
    return [{"name": (cat or "Unknown"), "count": count} for cat, count in data]

@app.get("/api/dashboard/source-wise")
def source_wise(db: Session = Depends(get_db)):
    data = (
        db.query(ListingMaster.source, func.count(ListingMaster.id))
        .group_by(ListingMaster.source)
        .order_by(func.count(ListingMaster.id).desc())
        .all()
    )
    return [{"name": (src or "Unknown"), "count": count} for src, count in data]
