from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models import TransactionBase, TransactionType
from database import get_db
from logic import calculate_balance

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


# READ ALL FROM USER
@router.get("/user/{user_id}/transactions")
def get_user_transactions(user_id: int, db: Session = Depends(get_db)):
    transactions = db.query(TransactionBase).filter(TransactionBase.user_id == user_id).all()
    return transactions


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


# CALCULATE BALANCE
@router.get("/user/{user_id}/balance")
def get_user_balance(user_id: int, db: Session = Depends(get_db)):
    balance = calculate_balance(db, user_id)
    return {"balance": balance}