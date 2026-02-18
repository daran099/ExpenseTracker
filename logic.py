from sqlalchemy.orm import Session
from models import TransactionBase, TransactionType

def calculate_balance(db: Session, user_id: int) -> float:
    transactions = db.query(TransactionBase).filter(TransactionBase.user_id == user_id).all()

    balance = 0
    for t in transactions:
        if t.type == TransactionType.income:
            balance += t.amount
        else:
            balance -= t.amount

    return balance
