from datetime import datetime
import pytest

from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from ..main import app, db, models

from logging import Logger

logger = Logger(__name__)

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[db.get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_create_user(client: TestClient):
    response = client.post(
        "/users/", json={"name": "Test", "email": "test.user@test.com", "username": "testuser"}
    )
    data = response.json()
    
    assert response.status_code == 200
    assert data["name"] == "Test"
    assert data["email"] == "test.user@test.com"
    assert data["username"] == "testuser"
    assert data["id"] is not None

def test_create_user_incomplete(client: TestClient):
    response = client.post("/users/", json={"name": "Test"})
    assert response.status_code == 422

def test_create_transaction(session: Session, client: TestClient):
    action1 = models.ActionType(name="Income", code="I", description="")
    user = models.User(**{"name": "Test", "email": "test.user@test.com", "username": "testuser"})
    session.add_all([action1, user])
    session.commit()

    response = client.post(
        "/transactions/", json={
            "category_id": 1,
            "currency_id": 0,
            "amount": 100,
            "description": "Test 1",
            "date": "2021-09-05T06:56:04.158Z",
            "user_id": 1,
            "action_type_id": 1
        }
    )
    data = response.json()
    print(data)
    assert response.status_code == 200
    assert data["amount"] == 100
    assert data["description"] == "Test 1"
    assert data["id"] is not None
    assert data["user_id"] is not None
    assert data["category_id"] is not None
    assert data["action_type_id"] is not None

def test_read_user_transactions(session: Session, client: TestClient):
    user = models.User(name="Test 2", email="test@test.com", username="test")
    session.add(user)
    session.commit()

    trans_1 = models.Transaction(**{
            "category_id": 1,
            "currency_id": 0,
            "amount": 100,
            "description": "Test 1",
            "date": datetime.now(),
            "user_id": 1,
            "action_type_id": 1
        })
    
    trans_2 = models.Transaction(**{
            "category_id": 1,
            "currency_id": 0,
            "amount": 100,
            "description": "Test 2",
            "date": datetime.now(),
            "user_id": 1,
            "action_type_id": 1
        })

    trans_3 = models.Transaction(**{
            "category_id": 1,
            "currency_id": 0,
            "amount": 100,
            "description": "Test 1",
            "date": datetime.now(),
            "user_id": 0,
            "action_type_id": 1
        })

    session.add(trans_1)
    session.add(trans_2)
    session.add(trans_3)
    session.commit()

    response = client.get(
        "/users/1"
    )
    data = response.json()
    
    assert response.status_code == 200
    assert data["id"] == 1
    assert data["username"] == "test"
    assert len(data["transactions"]) == 2
    assert data["transactions"][0]["description"] == "Test 1"
    assert data["transactions"][0]["amount"] == 100.0

    