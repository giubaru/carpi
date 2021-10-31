import pytest

from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from carpi.main import app, db, models
from .consts import Mutations, Queries
from logging import Logger

logger = Logger(__name__)


@pytest.fixture(name="session")
def session_fixture():
  engine = create_engine(
      "sqlite:///database-test.db", connect_args={"check_same_thread": False}, poolclass=StaticPool
  )
  SQLModel.metadata.create_all(engine)
  db.engine = engine
  with Session(engine) as session:
    yield session

@pytest.fixture(name="client")
def client_fixture(session: Session):
  client = TestClient(app)
  yield client
  # remove db to avoid persistent data

def test_create_user(client: TestClient, session: Session):
  '''This test creates a user using the mutation and then checks if the user was created'''

  result = client.post('/graphql', json={
    'query': Mutations.CREATE_USER.value, 
    'variables': {"username": "testuser", "email": "testuser@test.com", "name": "Test"}}
  )

  user: models.User = session.exec(select(models.User).where(models.User.username == "testuser")).first()

  assert result.json() == {'data': {'createUser': {'__typename': 'CreateUserSuccess', 'userId': user.id}}}

def test_create_user_with_existent_username(client: TestClient):
  '''This test tries to create a user with an already used username'''

  result = client.post('/graphql', json={
    'query': Mutations.CREATE_USER.value, 
    'variables': {"username": "testuser", "email": "new_testuser@test.com", "name": "Test"}}
  )

  assert result.json() == {'data': {'createUser': {'__typename': 'UsernameAlreadyExistsError', 'username': "testuser", "alternativeUsername": "new_username_alternative"}}}

def test_create_user_with_existent_email(client: TestClient):
  '''This test tries to create a user with an already used email'''

  result = client.post('/graphql', json={
    'query': Mutations.CREATE_USER.value, 
    'variables': {"username": "new_testuser", "email": "testuser@test.com", "name": "Test"}}
  )

  assert result.json() == {'data': {'createUser': {'__typename': 'EmailAlreadyInUseError', 'email': "testuser@test.com"}}}


def test_create_user_incomplete(client: TestClient):
  '''This test tries to create a user with an incomplete data'''
  
  result = client.post('/graphql', json={
    'query': Mutations.CREATE_USER_INCOMPLETE.value, 
    'variables': {"email": "testuser@test.com", "name": "Test"}}
  )

  assert result.json().get("errors")[0].get("message") == "Field 'createUser' argument 'username' of type 'String!' is required, but it was not provided."

def test_get_user(client: TestClient, session: Session):
  '''This test gets a user using the query and then checks if the user was created correctly'''
  
  user: models.User = session.exec(select(models.User).where(models.User.username == "testuser")).first()
  
  result = client.post('/graphql', json={'query': Queries.GET_USER.value, "variables": {"userId": user.id}})
  
  assert result.json() == {"data": {"user": {"id": user.id, "name": "Test", "email": "testuser@test.com", "username": "testuser" }}}

def test_create_account(client: TestClient, session: Session):
  '''This test creates an account using the mutation and then checks if the account was created'''

  user: models.User = session.exec(select(models.User).where(models.User.username == "testuser")).first()

  result = client.post('/graphql', json={
    'query': Mutations.CREATE_ACCOUNT.value, 
    'variables': {"accountType": "I", "name": "Ingresos", "userId": user.id}}
  )
  
  account_id = result.json().get("data").get("createAccount").get("accountId")
  account: models.Account = session.get(models.Account, account_id)
  
  assert account.user_id == user.id
  assert account.name == "Ingresos"
  assert account.account_type == "I"

def test_add_child_account(client: TestClient, session: Session):
  '''This test creates an account and then adds a child account to it'''

  user: models.User = session.exec(select(models.User).where(models.User.username == "testuser")).first()

  result = client.post('/graphql', json={
    'query': Mutations.CREATE_CHILD_ACCOUNT.value, 
    'variables': {"accountType": "I", "name": "Salarios", "userId": user.id, "parentAccount": 1}}
  )

  account_id = result.json().get("data").get("createAccount").get("accountId")
  account: models.Account = session.get(models.Account, account_id)
  
  assert account.user_id == user.id
  assert account.name == "Salarios"
  assert account.account_type == "I"
  assert account.parents[0].id == 1

def test_add_new_income(client: TestClient, session: Session):
  '''This test adds a new income to an existent account'''

  user: models.User = session.exec(select(models.User).where(models.User.username == "testuser")).first()
  
  result = client.post('/graphql', json={
    'query': Mutations.CREATE_TRANSACTION.value, 
    'variables': {"accountId": 2, "amount": 100, "userId": 1}
  })

  account: models.Account = session.get(models.Account, 2)

  income = result.json().get("data").get("addIncome").get("id")
  
  assert account.total == 100
  # assert income.amount == 100
  # assert income.date == "2020-01-01"
  # assert income.description == "Salario"