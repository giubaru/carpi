import strawberry

from typing import List, Optional
from uuid import uuid4

from strawberry.asgi import GraphQL
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from carpi import db, models, crud

@strawberry.type
class CreateUserSuccess:
  user_id: int

@strawberry.type
class UsernameAlreadyExistsError:
  username: str
  alternative_username: str

@strawberry.type
class EmailAlreadyInUseError:
  email: str

Response = strawberry.union(
  "CreateUserResponse",
  [CreateUserSuccess, UsernameAlreadyExistsError, EmailAlreadyInUseError]
)


@strawberry.type
class CreateAccountSuccess:
  account_id: int

@strawberry.type
class Mutation:
  @strawberry.mutation
  def add_income(self, amount: float, user_id: int, account_id: int) -> models.TransactionReadGraph:
    with db.Session(db.engine) as session:
      trans1 = models.Transaction(
          amount=amount,
          user_id=user_id,
          movement='I',
          category='Ganancia',
          account_id=account_id,
          id=str(uuid4())
      )
      session.add(trans1)
      session.commit()
      data = models.TransactionReadGraph.from_pydantic(trans1)

      crud.update_total(account_id, amount)
      
    return data

  @strawberry.mutation
  def create_user(name: str, email: str, username: str) -> Response:
    with db.Session(db.engine) as session:

      # Check if user exists
      user_username = crud.get_user_by_username(username)
      user_email = crud.get_user_by_email(email)

      if user_username:
        return UsernameAlreadyExistsError(
          username=user_username.username,
          alternative_username="new_username_alternative"
        )

      if user_email:
        return EmailAlreadyInUseError(email=user_email.email)

      user = models.User(
        name=name,
        username=username,
        email=email)
      session.add(user)
      session.commit()
      session.refresh(user)
    
    return CreateUserSuccess(user_id=user.id)


  @strawberry.mutation
  def create_account(name: str, account_type: str, user_id: int, parent_account: Optional[int] = None) -> CreateAccountSuccess:
    with db.Session(db.engine) as session:
      account = models.Account(
          name=name,
          account_type=account_type,
          user_id=user_id)

      session.add(account)
      

      if parent_account:
        parent = session.get(models.Account, parent_account)
        parent.append(account)
        session.add(parent)
        # session.refresh(parent)

        # account.parents.append(parent)        
        # session.add(account)
        # session.commit()
        # session.refresh(account)
      
      session.commit()
      session.refresh(account)
    return CreateAccountSuccess(account_id=account.id)


def get_user_graphql(user_id: int) -> models.UserReadGraph:
  user = crud.get_user(user_id)
  return models.UserReadGraph(**user.dict())
@strawberry.type
class Query:
  user: models.UserReadGraph = strawberry.field(resolver=get_user_graphql)

graphql_app = GraphQL(strawberry.Schema(mutation=Mutation, query=Query))
app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_route("/graphql", graphql_app)

@app.on_event("startup")
def on_startup():
    db.create_db_and_tables()

@app.get("/transactions")
def get_transactions():
  return crud.get_transactions()




