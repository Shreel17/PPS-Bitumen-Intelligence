from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date, datetime


class SupplierRateCreate(BaseModel):
    supplier_id: int = Field(gt=0)
    product_id: int = Field(gt=0)

    rate: float = Field(gt=0)

    unit: str = "MT"

    effective_date: date

    valid_until: Optional[date] = None

    source: Optional[str] = None

    notes: Optional[str] = None


class SupplierRateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    supplier_id: int
    product_id: int
    rate: float
    unit: str
    effective_date: date
    valid_until: Optional[date] = None
    source: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

class RateComparisonItem(BaseModel):
    supplier_id: int
    supplier_name: Optional[str] = None
    rate: float
    unit: str
    effective_date: date
    is_lowest: bool
    difference_from_lowest: float
