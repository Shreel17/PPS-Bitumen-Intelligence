from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    Date,
    DateTime,
    ForeignKey,
    Text
)
from sqlalchemy.sql import func

from backend.database import Base


class SupplierRate(Base):
    __tablename__ = "supplier_rates"

    id = Column(Integer, primary_key=True, index=True)

    supplier_id = Column(
        Integer,
        ForeignKey("suppliers.id"),
        nullable=False,
        index=True
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False,
        index=True
    )

    rate = Column(Float, nullable=False)

    unit = Column(String(30), default="MT")

    effective_date = Column(Date, nullable=False)

    valid_until = Column(Date, nullable=True)

    source = Column(String(100), nullable=True)

    notes = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
