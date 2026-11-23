from sqlalchemy import Column, Integer, String, Text, Boolean
from backend.database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)

    company_name = Column(String(150), nullable=False, index=True)

    contact_person = Column(String(100), nullable=True)

    phone = Column(String(20), nullable=True, index=True)

    email = Column(String(150), nullable=True)

    city = Column(String(100), nullable=True)

    state = Column(String(100), nullable=True)

    address = Column(Text, nullable=True)

    is_active = Column(Boolean, default=True)

    created_at = Column(String(30), nullable=True)
