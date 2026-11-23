from io import BytesIO
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.product import Product
from backend.models.supplier import Supplier
from backend.models.supplier_rate import SupplierRate
from backend.routers.dashboard import get_market_trend
from backend.services.report_service import generate_market_report


router = APIRouter(
    prefix="/reports",
    tags=["Market Reports"]
)


@router.get("/market/{product_id}")
def download_market_report(
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

    # Get historical market trend using existing dashboard logic
    trend_data = get_market_trend(
        product_id=product_id,
        start_date=start_date,
        end_date=end_date,
        supplier_id=None,
        db=db
    )

    # Get supplier rates applicable on the report end date
    comparison_records = (
        db.query(SupplierRate, Supplier)
        .join(
            Supplier,
            Supplier.id == SupplierRate.supplier_id
        )
        .filter(SupplierRate.product_id == product_id)
        .filter(Supplier.is_active.is_(True))
        .filter(SupplierRate.effective_date <= end_date)
        .filter(
            (SupplierRate.valid_until.is_(None))
            | (SupplierRate.valid_until >= end_date)
        )
        .order_by(
            SupplierRate.supplier_id,
            SupplierRate.effective_date.desc(),
            SupplierRate.id.desc()
        )
        .all()
    )

    # Keep the latest applicable rate per supplier
    latest_supplier_rates = {}

    for rate, supplier in comparison_records:
        if supplier.id not in latest_supplier_rates:
            latest_supplier_rates[supplier.id] = {
                "supplier_id": supplier.id,
                "supplier_name": supplier.company_name,
                "rate": rate.rate,
                "unit": rate.unit,
                "effective_date": rate.effective_date
            }

    # Sort suppliers by rate
    rates = sorted(
        latest_supplier_rates.values(),
        key=lambda item: item["rate"]
    )

    lowest_rate = rates[0]["rate"] if rates else None
    highest_rate = rates[-1]["rate"] if rates else None

    # Prepare supplier comparison data
    for item in rates:
        item["difference_from_lowest"] = round(
            item["rate"] - lowest_rate, 2
        ) if lowest_rate is not None else 0

        item["is_lowest"] = (
            item["rate"] == lowest_rate
            if lowest_rate is not None
            else False
        )

    comparison_data = {
        "product_id": product.id,
        "product_name": product.product_name,
        "comparison_date": end_date,
        "total_suppliers": len(rates),
        "lowest_rate": lowest_rate,
        "highest_rate": highest_rate,
        "rates": rates
    }

    # Generate PDF
    try:
        pdf_bytes = generate_market_report(
            trend_data=trend_data,
            comparison_data=comparison_data,
            start_date=start_date,
            end_date=end_date
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Could not generate market report: {str(exc)}"
        )

    # Return downloadable PDF
    filename = (
        f"Bitumen_Market_Report_{product_id}_"
        f"{start_date}_{end_date}.pdf"
    )

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )
