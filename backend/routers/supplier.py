from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.supplier import Supplier
from backend.schemas.supplier import (
    SupplierCreate,
    SupplierUpdate,
    SupplierResponse
)

router = APIRouter(
    prefix="/suppliers",
    tags=["Suppliers"]
)


# CREATE: Add a new supplier
@router.post("/", response_model=SupplierResponse, status_code=201)
def create_supplier(
    supplier_data: SupplierCreate,
    db: Session = Depends(get_db)
):
    new_supplier = Supplier(
        **supplier_data.model_dump()
    )

    db.add(new_supplier)
    db.commit()
    db.refresh(new_supplier)

    return new_supplier


# READ: Get all suppliers
@router.get("/", response_model=list[SupplierResponse])
def get_suppliers(db: Session = Depends(get_db)):
    return db.query(Supplier).order_by(Supplier.id.desc()).all()


# READ: Get one supplier by ID
@router.get("/{supplier_id}", response_model=SupplierResponse)
def get_supplier(supplier_id: int, db: Session = Depends(get_db)):

    supplier = db.query(Supplier).filter(
        Supplier.id == supplier_id
    ).first()

    if supplier is None:
        raise HTTPException(
            status_code=404,
            detail="Supplier not found"
        )

    return supplier


# UPDATE: Update supplier information
@router.put("/{supplier_id}", response_model=SupplierResponse)
def update_supplier(
    supplier_id: int,
    supplier_data: SupplierUpdate,
    db: Session = Depends(get_db)
):

    supplier = db.query(Supplier).filter(
        Supplier.id == supplier_id
    ).first()

    if supplier is None:
        raise HTTPException(
            status_code=404,
            detail="Supplier not found"
        )

    update_data = supplier_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(supplier, field, value)

    db.commit()
    db.refresh(supplier)

    return supplier


# DELETE: Delete a supplier
@router.delete("/{supplier_id}")
def delete_supplier(
    supplier_id: int,
    db: Session = Depends(get_db)
):

    supplier = db.query(Supplier).filter(
        Supplier.id == supplier_id
    ).first()

    if supplier is None:
        raise HTTPException(
            status_code=404,
            detail="Supplier not found"
        )

    db.delete(supplier)
    db.commit()

    return {
        "message": "Supplier deleted successfully",
        "supplier_id": supplier_id
    }
