
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.supplier_rate import SupplierRate
from backend.models.supplier import Supplier
from backend.models.product import Product
from backend.schemas.supplier_rate import (
    SupplierRateCreate,
    SupplierRateResponse,
)

router = APIRouter(
    prefix="/supplier-rates",
    tags=["Supplier Rate Management"]
)


# 1. Add a new supplier rate
@router.post("/", response_model=SupplierRateResponse, status_code=201)
def create_supplier_rate(
    rate_data: SupplierRateCreate,
    db: Session = Depends(get_db)
):
    supplier = db.query(Supplier).filter(
        Supplier.id == rate_data.supplier_id
    ).first()

    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    product = db.query(Product).filter(
        Product.id == rate_data.product_id
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if (
        rate_data.valid_until is not None
        and rate_data.valid_until < rate_data.effective_date
    ):
        raise HTTPException(
            status_code=400,
            detail="Valid-until date cannot be earlier than effective date"
        )

    # Append-only: preserve all historical rate records
    new_rate = SupplierRate(**rate_data.model_dump())

    db.add(new_rate)
    db.commit()
    db.refresh(new_rate)

    return new_rate


# 2. Get historical rates with optional filters
@router.get("/", response_model=list[SupplierRateResponse])
def get_supplier_rates(
    supplier_id: Optional[int] = None,
    product_id: Optional[int] = None,
    effective_on: Optional[date] = Query(default=None),
    db: Session = Depends(get_db)
):
    query = db.query(SupplierRate)

    if supplier_id is not None:
        query = query.filter(
            SupplierRate.supplier_id == supplier_id
        )

    if product_id is not None:
        query = query.filter(
            SupplierRate.product_id == product_id
        )

    if effective_on is not None:
        query = query.filter(
            SupplierRate.effective_date <= effective_on
        ).filter(
            (SupplierRate.valid_until.is_(None))
            | (SupplierRate.valid_until >= effective_on)
        )

    return query.order_by(
        SupplierRate.effective_date.desc(),
        SupplierRate.id.desc()
    ).all()


# 3. Compare supplier rates for a product on a given date
# IMPORTANT: Keep this route before /{rate_id}
@router.get("/compare/{product_id}")
def compare_supplier_rates(
    product_id: int,
    effective_on: date = Query(default_factory=date.today),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    rates = (
        db.query(SupplierRate, Supplier)
        .join(Supplier, Supplier.id == SupplierRate.supplier_id)
        .filter(SupplierRate.product_id == product_id)
        .filter(Supplier.is_active.is_(True))
        .filter(SupplierRate.effective_date <= effective_on)
        .filter(
            (SupplierRate.valid_until.is_(None))
            | (SupplierRate.valid_until >= effective_on)
        )
        .order_by(
            SupplierRate.supplier_id,
            SupplierRate.effective_date.desc(),
            SupplierRate.id.desc()
        )
        .all()
    )

    # Keep the latest applicable rate for each supplier
    latest_by_supplier = {}

    for rate, supplier in rates:
        if supplier.id not in latest_by_supplier:
            latest_by_supplier[supplier.id] = {
                "supplier_id": supplier.id,
                "supplier_name": supplier.company_name,
                "product_id": product.id,
                "product_name": product.product_name,
                "rate": rate.rate,
                "unit": rate.unit,
                "effective_date": rate.effective_date,
                "valid_until": rate.valid_until,
                "source": rate.source,
            }

    result = list(latest_by_supplier.values())

    # Sort suppliers from lowest to highest rate
    result.sort(key=lambda item: item["rate"])

    if result:
        lowest_rate = result[0]["rate"]

        for item in result:
            difference = item["rate"] - lowest_rate

            item["is_lowest"] = difference == 0

            item["difference_from_lowest"] = round(
                difference, 2
            )

            item["percentage_difference"] = (
                round((difference / lowest_rate) * 100, 2)
                if lowest_rate > 0
                else 0
            )

    return {
        "product_id": product.id,
        "product_name": product.product_name,
        "comparison_date": effective_on,
        "total_suppliers": len(result),
        "lowest_rate": result[0]["rate"] if result else None,
        "highest_rate": result[-1]["rate"] if result else None,
        "rates": result
    }


# 4. Get a particular rate record
@router.get("/{rate_id}", response_model=SupplierRateResponse)
def get_supplier_rate(
    rate_id: int,
    db: Session = Depends(get_db)
):
    rate = db.query(SupplierRate).filter(
        SupplierRate.id == rate_id
    ).first()

    if not rate:
        raise HTTPException(
            status_code=404,
            detail="Supplier rate not found"
        )

    return rate
