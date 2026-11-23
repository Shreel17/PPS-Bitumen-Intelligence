from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.buyer import Buyer
from backend.schemas.buyer import (
    BuyerCreate,
    BuyerUpdate,
    BuyerResponse
)

router = APIRouter(prefix="/buyers", tags=["Buyers"])


@router.post("/", response_model=BuyerResponse, status_code=201)
def create_buyer(
    buyer_data: BuyerCreate,
    db: Session = Depends(get_db)
):
    new_buyer = Buyer(**buyer_data.model_dump())

    db.add(new_buyer)
    db.commit()
    db.refresh(new_buyer)

    return new_buyer


@router.get("/", response_model=list[BuyerResponse])
def get_buyers(db: Session = Depends(get_db)):
    return db.query(Buyer).order_by(Buyer.id.desc()).all()


@router.get("/{buyer_id}", response_model=BuyerResponse)
def get_buyer(buyer_id: int, db: Session = Depends(get_db)):
    buyer = db.query(Buyer).filter(Buyer.id == buyer_id).first()

    if buyer is None:
        raise HTTPException(status_code=404, detail="Buyer not found")

    return buyer


@router.put("/{buyer_id}", response_model=BuyerResponse)
def update_buyer(
    buyer_id: int,
    buyer_data: BuyerUpdate,
    db: Session = Depends(get_db)
):
    buyer = db.query(Buyer).filter(Buyer.id == buyer_id).first()

    if buyer is None:
        raise HTTPException(status_code=404, detail="Buyer not found")

    update_data = buyer_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(buyer, field, value)

    db.commit()
    db.refresh(buyer)

    return buyer


@router.delete("/{buyer_id}")
def delete_buyer(buyer_id: int, db: Session = Depends(get_db)):
    buyer = db.query(Buyer).filter(Buyer.id == buyer_id).first()

    if buyer is None:
        raise HTTPException(status_code=404, detail="Buyer not found")

    db.delete(buyer)
    db.commit()

    return {
        "message": "Buyer deleted successfully",
        "buyer_id": buyer_id
    }
