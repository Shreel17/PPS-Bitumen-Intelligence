from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class BuyerCreate(BaseModel):
    company_name: str = Field(min_length=2, max_length=150)
    contact_person: Optional[str] = None
    phone: Optional[str] = Field(default=None, max_length=20)
    email: Optional[str] = Field(default=None, max_length=150)
    city: Optional[str] = None
    state: Optional[str] = None
    address: Optional[str] = None
    buyer_type: Optional[str] = None


class BuyerUpdate(BaseModel):
    company_name: Optional[str] = Field(default=None, min_length=2, max_length=150)
    contact_person: Optional[str] = None
    phone: Optional[str] = Field(default=None, max_length=20)
    email: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    address: Optional[str] = None
    buyer_type: Optional[str] = None
    is_active: Optional[bool] = None


class BuyerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    address: Optional[str] = None
    buyer_type: Optional[str] = None
    is_active: bool
