from sqlalchemy import Column, Integer, String, Text, Boolean
from backend.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    product_name = Column(String(150), nullable=False, index=True)

    grade = Column(String(50), nullable=True)

    category = Column(String(100), nullable=True)

    unit = Column(String(30), default="MT")

    description = Column(Text, nullable=True)

    is_active = Column(Boolean, default=True)
