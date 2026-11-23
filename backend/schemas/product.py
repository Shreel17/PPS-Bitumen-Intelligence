from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class ProductCreate(BaseModel):
    product_name: str = Field(min_length=2, max_length=150)
    grade: Optional[str] = None
    category: Optional[str] = None
    unit: str = "MT"
    description: Optional[str] = None


class ProductUpdate(BaseModel):
    product_name: Optional[str] = Field(default=None, min_length=2, max_length=150)
    grade: Optional[str] = None
    category: Optional[str] = None
    unit: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_name: str
    grade: Optional[str] = None
    category: Optional[str] = None
    unit: str
    description: Optional[str] = None
    is_active: bool
