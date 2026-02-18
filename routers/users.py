from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models import UserBase
from database import get_db


router = APIRouter()


#CREATE
@router.post("/")
def create_user(name: str, email: str, db: Session = Depends(get_db)):
    user = UserBase(name=name, email=email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


#READ ALL
@router.get("/")
def list_users(db: Session = Depends(get_db)):
    return db.query(UserBase).all()


#READ ONE
@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    return db.query(UserBase).filter(UserBase.id == user_id).first()


# UPDATE
@router.put("/{user_id}")
def update_user(user_id: int, name: str, email: str, db: Session = Depends(get_db)):
    user = db.query(UserBase).filter(UserBase.id == user_id).first()
    if not user:
        return {"error": "User not found"}

    user.name = name
    user.email = email
    db.commit()
    db.refresh(user)
    return user


# DELETE
@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserBase).filter(UserBase.id == user_id).first()
    if not user:
        return {"error": "User not found"}

    db.delete(user)
    db.commit()
    return {"message": "User deleted"}
