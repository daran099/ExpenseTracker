import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from models import UserBase, TransactionBase
from main import app
from database import Base, get_db


TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False},)

TestingSessionLocal = sessionmaker(bind=engine)


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)

    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture
def create_user(client):
    def _create_user(name="test", email="test@test.com"):
        response = client.post("/users/", json={
            "name": name,
            "email": email
        })
        assert response.status_code == 200
        return response.json()
    return _create_user


def test_create_user(db, create_user):
    data = create_user()

    user = db.query(UserBase).filter(UserBase.id == data["id"]).first()
    assert user is not None


def test_update_user(db, client, create_user):
    user = create_user()

    response = client.put(f"/users/{user['id']}", json={
        "name": "test2",
        "email": "test2@test.com"
    })

    assert response.status_code == 200

    updated = db.query(UserBase).filter(UserBase.id == user["id"]).first()
    assert updated.name == "test2"


def test_delete_user(db, client, create_user):
    user = create_user()

    response = client.delete(f"/users/{user['id']}")
    assert response.status_code == 200

    deleted = db.query(UserBase).filter(UserBase.id == user["id"]).first()
    assert deleted is None


def test_create_user_duplicate_email(client, create_user):
    create_user(email="test@test.com")

    response = client.post("/users/", json={
        "name": "another",
        "email": "test@test.com"
    })

    assert response.status_code == 400


def test_create_user_transaction(client, create_user, db):
    user = create_user()

    response = client.post("/transactions/", json={
        "title": "Salary January",
        "amount": 3500.00,
        "type": "income",
        "user_id": user["id"]
    })
    assert response.status_code == 200

    salary_january_transaction = db.query(TransactionBase).filter(
        TransactionBase.title == "Salary January",
        TransactionBase.amount == 3500.00,
        TransactionBase.type == "income",
        TransactionBase.user_id == user["id"]
    ).first()

    assert salary_january_transaction is not None


    response_2 = client.post("/transactions/", json={
        "title": "Electricity Bill",
        "amount": 90.75,
        "type": "expense",
        "user_id": user["id"]
    })
    assert response_2.status_code == 200

    electricity_transaction = db.query(TransactionBase).filter(
        TransactionBase.title == "Electricity Bill",
        TransactionBase.amount == 90.75,
        TransactionBase.type == "expense",
        TransactionBase.user_id == user["id"]
    ).first()

    assert electricity_transaction is not None


    response_3 = client.post("/transactions/", json={
        "title": "Ghost Transaction",
        "amount": 100.00,
        "type": "income",
        "user_id": 999999
    })
    assert response_3.status_code == 404

    ghost_transaction = db.query(TransactionBase).filter(
        TransactionBase.title == "Ghost Transaction",
        TransactionBase.amount == 100.00,
        TransactionBase.type == "income",
        TransactionBase.user_id == 999999
    ).first()

    assert ghost_transaction is None


    response_4 = client.post("/transactions/", json={
        "title": "Invalid Type",
        "amount": 100.00,
        "type": "invalid_type",
        "user_id": user["id"]
    })
    assert response_4.status_code == 422

    invalid_type_transaction = db.query(TransactionBase).filter(
        TransactionBase.title == "Invalid Type",
        TransactionBase.amount == 100.00,
        TransactionBase.type == "invalid_type",
        TransactionBase.user_id == user["id"]
    ).first()

    assert invalid_type_transaction is None


    response_5 = client.post("/transactions/", json={
        "title": "Negative Amount",
        "amount": -50.00,
        "type": "expense",
        "user_id": user["id"]
    })
    assert response_5.status_code == 422

    negative_amount_transaction = db.query(TransactionBase).filter(
        TransactionBase.title == "Negative Amount",
        TransactionBase.amount == -50.00,
        TransactionBase.type == "expense",
        TransactionBase.user_id == user["id"]
    ).first()

    assert negative_amount_transaction is None


def test_transaction_update(client, create_user):
    user = create_user()

    response = client.post("/transactions/", json={
        "title": "old_title",
        "amount": 3500.00,
        "type": "income",
        "user_id": user["id"]
    })
    assert response.status_code == 200

    transaction_id = response.json()["id"]

    response_2 = client.put(f"/transactions/{transaction_id}", json={
        "title": "new_title",
        "amount": 5000,
        "type": "expense"
    })
    assert response_2.status_code == 200
    assert response_2.json()["title"] == "new_title"
    assert response_2.json()["amount"] == 5000
    assert response_2.json()["type"] == "expense"


def test_wrong_transaction_transaction_type(client, create_user, db):
    user = create_user()

    response = client.post("/transactions/", json={
        "title": "test_title",
        "amount": 1000,
        "type": "bug",
        "user_id": user["id"]
    })
    assert response.status_code == 422

    error_transaction = db.query(TransactionBase).filter(
        TransactionBase.title == "test_title",
        TransactionBase.amount == 1000,
        TransactionBase.user_id == user["id"]
    ).first()

    assert error_transaction is None


def test_transaction_delite(client, create_user, db):
    user = create_user()

    response = client.post("/transactions/", json={
        "title": "test_title",
        "amount": 1000,
        "type": "income",
        "user_id": user["id"]
    })
    assert response.status_code == 200

    transaction_id = response.json()["id"]

    response_2 = client.delete(f"/transactions/{transaction_id}")
    assert response_2.status_code == 200

    deleted = db.query(TransactionBase).filter(TransactionBase.id == transaction_id).first()
    assert deleted is None


def test_balance_calculate(client, create_user):
    user = create_user()

    # создаём доход через API
    client.post("/transactions/", json={
        "title": "income",
        "amount": 1000,
        "type": "income",
        "user_id": user["id"]
    })

    client.post("/transactions/", json={
        "title": "expense",
        "amount": 200,
        "type": "expense",
        "user_id": user["id"]
    })

    response = client.get(f"/transactions/users/{user['id']}/balance")
    assert response.status_code == 200
    assert response.json()["balance"] == 800