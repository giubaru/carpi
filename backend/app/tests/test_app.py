import pytest


from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from ..main import app, db, models

from logging import Logger

logger = Logger(__name__)


@pytest.fixture(name="session")
def session_fixture():
  engine = create_engine(
      "sqlite:///database-tests.db", connect_args={"check_same_thread": False}, poolclass=StaticPool
  )
  SQLModel.metadata.create_all(engine)
  with Session(engine) as session:
    yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
  def get_session_override():
      return session

  app.dependency_overrides[db.get_session] = get_session_override
  db.Session = session
  client = TestClient(app)
  yield client
  app.dependency_overrides.clear()

def test_create_user(client: TestClient):
  mutation = '''
    mutation {
      createUser(email: "testuser@test.com", name: "TestUser", username: "testuser"){
        name
        username
      }
    }
  '''
  
  result = client.post('/graphql', json={'query': mutation})

  assert result.json() == {'data': {'createUser': {'name': 'TestUser', 'username': 'testuser'}}}

def test_create_user_incomplete(client: TestClient):
  mutation = '''
    mutation {
      createUser(email: "testuser@test.com", name: "TestUser"){
        name
        username
      }
    }
  '''
  
  result = client.post('/graphql', json={'query': mutation})

  assert result.json() == {'data': None, 'errors': [{'locations': [{'column': 7, 'line': 3}], 'message': "Field 'createUser' argument 'username' of type 'String!' is required, but it was not provided.", 'path': None}]}

def test_get_user(client: TestClient, session: Session):
  query = '''
  query GetUser($userId: Int!) {
    user(userId: $userId) {
      id
      name
      email
      username
    }
  }
  '''

  user: models.User = session.exec(select(models.User).where(models.User.username == "testuser")).first()
  
  result = client.post('/graphql', json={'query': query, "variables": {"userId": user.id}})
  
  assert result.json() == {"data": {"user": {"id": 6, "name": "TestUser", "email": "testuser@test.com", "username": "testuser" }}}