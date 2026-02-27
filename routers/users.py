from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import UserBase
from database import get_db
from schemas import UserCreate, UserUpdate, UserResponse
from typing import List
from sqlalchemy.exc import IntegrityError


router = APIRouter()


#CREATE
@router.post("/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = UserBase(name=user.name, email=user.email)

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already exists")

    return db_user


#READ ALL
@router.get("/", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db)):
    db_user = db.query(UserBase).all()
    return db_user


#READ ONE
@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(UserBase).filter(UserBase.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


# UPDATE
@router.put("/{user_id}")
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(UserBase).filter(UserBase.id == user_id).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.name is not None:
        db_user.name = user.name

    if user.email is not None:
        db_user.email = user.email

    try:
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already exists")

    return db_user


# DELETE
@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(UserBase).filter(UserBase.id == user_id).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(db_user)
    db.commit()

    return {"message": "User deleted"}