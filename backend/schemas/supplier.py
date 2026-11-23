from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


# Used when creating a supplier
class SupplierCreate(BaseModel):
    company_name: str = Field(min_length=2, max_length=150)
    contact_person: Optional[str] = None
    phone: Optional[str] = Field(default=None, max_length=20)
    email: Optional[str] = Field(default=None, max_length=150)
    city: Optional[str] = None
    state: Optional[str] = None
    address: Optional[str] = None


# Used when updating a supplier
class SupplierUpdate(BaseModel):
    company_name: Optional[str] = Field(default=None, min_length=2, max_length=150)
    contact_person: Optional[str] = None
    phone: Optional[str] = Field(default=None, max_length=20)
    email: Optional[str] = Field(default=None, max_length=150)
    city: Optional[str] = None
    state: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None


# Used when returning supplier information
class SupplierResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    address: Optional[str] = None
    is_active: bool
