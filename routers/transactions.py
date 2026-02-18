from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models import TransactionBase, TransactionType
from database import get_db

router = APIRouter()

# CREATE
@router.post("/")
def create_transaction(title: str, amount: float, type: TransactionType, user_id: int, db: Session = Depends(get_db)):
    transaction = TransactionBase(title=title, amount=amount, type=type, user_id=user_id)
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


# READ ALL
@router.get("/")
def list_transactions(db: Session = Depends(get_db)):
    return db.query(TransactionBase).all()


# READ ONE
@router.get("/{transaction_id}")
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.query(TransactionBase).filter(TransactionBase.id == transaction_id).first()

    if not transaction:
        return {"error": "Transaction not found"}

    return transaction


# UPDATE
@router.put("/{transaction_id}")
def update_transaction(transaction_id: int, title: str, amount: float, type: TransactionType, db: Session = Depends(get_db)):
    transaction = db.query(TransactionBase).filter(TransactionBase.id == transaction_id).first()

    if not transaction:
        return {"error": "Transaction not found"}

    transaction.title = title
    transaction.amount = amount
    transaction.type = type

    db.commit()
    db.refresh(transaction)
    return transaction


# DELETE
@router.delete("/{transaction_id}")
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.query(TransactionBase).filter(TransactionBase.id == transaction_id).first()

    if not transaction:
        return {"error": "Transaction not found"}

    db.delete(transaction)
    db.commit()
    return {"message": "Transaction deleted"}
