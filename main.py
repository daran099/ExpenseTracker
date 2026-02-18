from fastapi import FastAPI
from database import Base, engine
from routers import users, transactions

app = FastAPI()

#create database tables
Base.metadata.create_all(bind=engine)

#add routers
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
