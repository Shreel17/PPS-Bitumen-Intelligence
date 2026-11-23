from datetime import date, timedelta

from fastapi import APIRouter

from typing import Optional


from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.supplier import Supplier
from backend.models.buyer import Buyer
from backend.models.product import Product
from backend.models.supplier_rate import SupplierRate

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard Analytics"]
)


@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db)
):
    today = date.today()

    # Basic business counts
    total_suppliers = db.query(Supplier).filter(
        Supplier.is_active == True
    ).count()

    total_buyers = db.query(Buyer).filter(
        Buyer.is_active == True
    ).count()

    total_products = db.query(Product).filter(
        Product.is_active == True
    ).count()

    total_rate_records = db.query(SupplierRate).count()

    # Get all rates applicable today
    current_rates = (
        db.query(SupplierRate)
        .join(Supplier, Supplier.id == SupplierRate.supplier_id)
        .join(Product, Product.id == SupplierRate.product_id)
        .filter(Supplier.is_active == True)
        .filter(Product.is_active == True)
        .filter(SupplierRate.effective_date <= today)
        .filter(
            (SupplierRate.valid_until.is_(None))
            | (SupplierRate.valid_until >= today)
        )
        .order_by(
            SupplierRate.supplier_id,
            SupplierRate.product_id,
            SupplierRate.effective_date.desc(),
            SupplierRate.id.desc()
        )
        .all()
    )

    # Keep only the latest applicable rate per supplier-product pair
    latest_rates = {}

    for rate in current_rates:
        key = (rate.supplier_id, rate.product_id)

        if key not in latest_rates:
            latest_rates[key] = rate

    rate_values = [
        rate.rate for rate in latest_rates.values()
    ]

    lowest_rate = min(rate_values) if rate_values else None
    highest_rate = max(rate_values) if rate_values else None

    return {
        "as_of_date": today,
        "total_active_suppliers": total_suppliers,
        "total_active_buyers": total_buyers,
        "total_active_products": total_products,
        "total_rate_records": total_rate_records,
        "current_supplier_product_rates": len(latest_rates),
        "lowest_current_rate": lowest_rate,
        "highest_current_rate": highest_rate,
        "currency": "INR",
        "unit": "MT"
    }


@router.get("/recent-rates")
def get_recent_rate_updates(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    limit = max(1, min(limit, 100))

    recent_rates = (
        db.query(SupplierRate, Supplier, Product)
        .join(Supplier, Supplier.id == SupplierRate.supplier_id)
        .join(Product, Product.id == SupplierRate.product_id)
        .order_by(SupplierRate.id.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "rate_id": rate.id,
            "supplier_name": supplier.company_name,
            "product_name": product.product_name,
            "rate": rate.rate,
            "unit": rate.unit,
            "effective_date": rate.effective_date,
            "source": rate.source,
            "notes": rate.notes
        }
        for rate, supplier, product in recent_rates
    ]


@router.get("/rate-history/{product_id}")
def get_rate_history(
    product_id: int,
    start_date: date = Query(
        default_factory=lambda: date.today() - timedelta(days=30)
    ),
    end_date: date = Query(default_factory=date.today),
    db: Session = Depends(get_db)
):
    # Validate product
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    # Validate date range
    if start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="Start date cannot be later than end date"
        )

    # Retrieve recorded rate updates in the selected period
    records = (
        db.query(SupplierRate, Supplier)
        .join(Supplier, Supplier.id == SupplierRate.supplier_id)
        .filter(SupplierRate.product_id == product_id)
        .filter(SupplierRate.effective_date >= start_date)
        .filter(SupplierRate.effective_date <= end_date)
        .order_by(SupplierRate.effective_date.asc())
        .all()
    )

    history = []

    for rate, supplier in records:
        history.append({
            "rate_id": rate.id,
            "supplier_id": supplier.id,
            "supplier_name": supplier.company_name,
            "rate": rate.rate,
            "unit": rate.unit,
            "effective_date": rate.effective_date,
            "source": rate.source
        })

    # Calculate statistics from recorded entries
    values = [item["rate"] for item in history]

    return {
        "product_id": product.id,
        "product_name": product.product_name,
        "start_date": start_date,
        "end_date": end_date,
        "total_rate_updates": len(history),
        "lowest_recorded_rate": min(values) if values else None,
        "highest_recorded_rate": max(values) if values else None,
        "average_recorded_rate": (
            round(sum(values) / len(values), 2) if values else None
        ),
        "rate_history": history
    }


@router.get("/market-trend/{product_id}")
def get_market_trend(
    product_id: int,
    start_date: date = Query(
        default_factory=lambda: date.today() - timedelta(days=30)
    ),
    end_date: date = Query(default_factory=date.today),
    supplier_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    # Validate product
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    # Validate date range
    if start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="Start date cannot be later than end date"
        )

    # Retrieve historical rates
    query = (
        db.query(SupplierRate, Supplier)
        .join(Supplier, Supplier.id == SupplierRate.supplier_id)
        .filter(SupplierRate.product_id == product_id)
        .filter(SupplierRate.effective_date >= start_date)
        .filter(SupplierRate.effective_date <= end_date)
        .filter(Supplier.is_active.is_(True))
    )

    # Optional supplier filter
    if supplier_id is not None:
        query = query.filter(
            SupplierRate.supplier_id == supplier_id
        )

    records = query.order_by(
        SupplierRate.effective_date.asc(),
        SupplierRate.id.asc()
    ).all()

    if not records:
        return {
            "product_id": product.id,
            "product_name": product.product_name,
            "start_date": start_date,
            "end_date": end_date,
            "supplier_id": supplier_id,
            "total_rate_updates": 0,
            "opening_rate": None,
            "latest_rate": None,
            "average_rate": None,
            "minimum_rate": None,
            "maximum_rate": None,
            "absolute_change": None,
            "percentage_change": None,
            "trend": "Insufficient Data",
            "supplier_movements": []
        }

    # Group records supplier-wise
    supplier_history = {}

    for rate, supplier in records:
        supplier_history.setdefault(
            supplier.id,
            {
                "supplier_id": supplier.id,
                "supplier_name": supplier.company_name,
                "rates": []
            }
        )

        supplier_history[supplier.id]["rates"].append({
            "rate_id": rate.id,
            "rate": rate.rate,
            "unit": rate.unit,
            "effective_date": rate.effective_date
        })

    supplier_movements = []

    for supplier_data in supplier_history.values():
        history = supplier_data["rates"]

        opening_rate = history[0]["rate"]
        latest_rate = history[-1]["rate"]

        absolute_change = round(
            latest_rate - opening_rate, 2
        )

        percentage_change = (
            round((absolute_change / opening_rate) * 100, 2)
            if opening_rate > 0
            else None
        )

        if absolute_change > 0:
            trend = "Increasing"
        elif absolute_change < 0:
            trend = "Decreasing"
        else:
            trend = "Stable"

        supplier_movements.append({
            "supplier_id": supplier_data["supplier_id"],
            "supplier_name": supplier_data["supplier_name"],
            "total_rate_updates": len(history),
            "opening_rate": opening_rate,
            "latest_rate": latest_rate,
            "absolute_change": absolute_change,
            "percentage_change": percentage_change,
            "trend": trend,
            "rate_history": history
        })

    # Product-wide statistics across recorded rate updates
    all_values = [
        rate.rate for rate, supplier in records
    ]

    return {
        "product_id": product.id,
        "product_name": product.product_name,
        "start_date": start_date,
        "end_date": end_date,
        "supplier_id": supplier_id,
        "total_rate_updates": len(records),
        "opening_rate": records[0][0].rate,
        "latest_rate": records[-1][0].rate,
        "average_rate": round(
            sum(all_values) / len(all_values), 2
        ),
        "minimum_rate": min(all_values),
        "maximum_rate": max(all_values),
        "absolute_change": round(
            records[-1][0].rate - records[0][0].rate, 2
        ),
        "percentage_change": (
            round(
                (
                    (records[-1][0].rate - records[0][0].rate)
                    / records[0][0].rate
                ) * 100,
                2
            )
            if records[0][0].rate > 0
            else None
        ),
        "trend": (
            "Increasing"
            if records[-1][0].rate > records[0][0].rate
            else "Decreasing"
            if records[-1][0].rate < records[0][0].rate
            else "Stable"
        ),
        "supplier_movements": supplier_movements
    }


