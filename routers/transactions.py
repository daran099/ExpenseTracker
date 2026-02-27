from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import TransactionBase, TransactionType, UserBase
from database import get_db
from logic import calculate_balance
from schemas import TransactionCreate, TransactionUpdate, TransactionResponse, BalanceResponse
from typing import List

router = APIRouter()

# CALCULATE BALANCE
@router.get("/users/{user_id}/balance", response_model=BalanceResponse)
def get_user_balance(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserBase).filter(UserBase.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    balance = calculate_balance(db, user_id)
    return {"balance": balance}


# CREATE
@router.post("/", response_model=TransactionResponse)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    user = db.query(UserBase).filter(UserBase.id == transaction.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if transaction.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    db_transaction = TransactionBase(
        title=transaction.title,
        amount=transaction.amount,
        type=transaction.type,
        user_id=transaction.user_id
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction



# READ ALL
@router.get("/", response_model=List[TransactionResponse])
def list_transactions(db: Session = Depends(get_db)):
    bd_transaction = db.query(TransactionBase).all()
    return bd_transaction


# READ ONE
@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    bd_transaction = db.query(TransactionBase).filter(TransactionBase.id == transaction_id).first()

    if not bd_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return bd_transaction


# READ ALL FROM USER
@router.get("/user/{user_id}/transactions", response_model=List[TransactionResponse])
def get_user_transactions(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserBase).filter(UserBase.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    bd_transactions = db.query(TransactionBase).filter(TransactionBase.user_id == user_id).all()
    return bd_transactions


# UPDATE
@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(transaction_id: int, transaction: TransactionUpdate, db: Session = Depends(get_db)):
    db_transaction = db.query(TransactionBase).filter(TransactionBase.id == transaction_id).first()
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if transaction.title is not None:
        db_transaction.title = transaction.title
    if transaction.amount is not None:
        if transaction.amount <= 0:
            raise HTTPException(status_code=400, detail="Amount must be positive")
        db_transaction.amount = transaction.amount
    if transaction.type is not None:
        db_transaction.type = transaction.type

    db.commit()
    db.refresh(db_transaction)
    return db_transaction


# DELETE
@router.delete("/{transaction_id}")
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    bd_transaction = db.query(TransactionBase).filter(TransactionBase.id == transaction_id).first()

    if not bd_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    db.delete(bd_transaction)
    db.commit()
    return {"message": "Transaction deleted"}
