from pydantic.main import BaseModel
import strawberry


from abc import ABC
from dataclasses import dataclass, field

from strawberry.asgi import GraphQL
from typing import List, Optional
from sqlmodel import select
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware



# from app.models.new_transaction import TransactionRead

from . import db, models
from uuid import uuid4

class Account(ABC):
  """Esta clase representa una cuenta donde se guarda o extre montos de dinero en distitnas divisas."""

  def add_child(self, account: 'Account'):
    account.parent = self
    self.children.append(account)

  def income(self, amount: float, origin: bool = True):
    self.total += amount
    
    if self.parent:
      self.parent.income(amount, False)

  def withdraw(self, amount: float, origin: bool = True):
    if amount > self.total: 
      raise Exception("No te pases de la raya chinchulin, te falta plata.")

    self.total -= amount

    if self.parent:
      self.parent.withdraw(amount, False)
  
  def transfer(self, amount: float, destination: 'Account'):
    self.withdraw(amount)
    destination.income(amount)
  
@dataclass
class Ingresos(Account):
  id: int = 101
  total: float = 0.0
  children: List = field(default_factory=lambda: [])
  parent: 'Account' = None
  category: str = "Ganancia"


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

      account = session.get(models.Account, account_id)
      account.total += amount
      session.add(account)
      session.commit()

    return data

  @strawberry.mutation
  def create_user(name: str, email: str, username: str) -> models.UserReadGraph:
    with db.Session(db.engine) as session:
      user = models.User(
        name=name,
        username=username,
        email=email)
      session.add(user)
      session.commit()
      session.refresh(user)

    return models.UserReadGraph(**user.dict())

  @strawberry.mutation
  def create_account(name: str, account_type: str, user_id: int, child: Optional[bool] = False, parent_account: Optional[int] = 0) -> models.AccountReadGraph:
    with db.Session(db.engine) as session:

      if child:
        account = models.Account(
          name=name,
          account_type=account_type,
          user_id=user_id,
          parent_id=parent_account)

        session.add(account)
        session.commit()
        session.refresh(account)

        parent = session.get(models.Account, parent_account)
        parent.children.append(account.id)
        session.add(parent)
        session.commit()
        session.refresh(parent)
      else:
        account = models.Account(
          name=name,
          account_type=account_type,
          user_id=user_id)

        session.add(account)
        session.commit()
        session.refresh(account)

    return models.AccountReadGraph(**account.dict())

def get_transactions() -> List[models.TransactionReadGraph]:
  with db.Session(db.engine) as session:
    transactions = session.exec(select(models.Transaction)).all()
    data = [models.TransactionReadGraph.from_pydantic(transaction) for transaction in transactions]
    return data

def get_transactions_by_user_id(user_id: int) -> List[models.TransactionReadGraph]:
  with db.Session(db.engine) as session:
    statement = select(models.Transaction).where(models.Transaction.user_id == user_id)
    transactions = session.exec(statement).all()
    data = [models.TransactionReadGraph.from_pydantic(transaction) for transaction in transactions]
    return data

def get_all_income(user_id: int) -> float:
  with db.Session(db.engine) as session:
    statement = select(models.Transaction).where(models.Transaction.user_id == user_id, models.Transaction.movement == 'I')
    transactions = session.exec(statement).all()
    total = [ transaction.amount for transaction in transactions ]
    return sum(total)

def get_user(user_id: int) -> models.UserReadGraph:
  with db.Session(db.engine) as session:
    user = session.get(models.User, user_id)
    # r = models.UserReadGraph.from_pydantic(user)
    # r.accounts = [models.AccountReadGraph.from_pydantic(account) for account in user.accounts]

    return models.UserReadGraph(**user.dict())

def get_accounts_by_user_id(user_id: int) -> List[models.AccountReadGraph]:
  with db.Session(db.engine) as session:
    accounts = session.exec(select(models.Account).where(models.Account.user_id == user_id)).all()
    # transactions = session.exec(select(models.Transaction).where(models.Transaction.user_id == user_id)).all()
    # print(transactions)
    # t = [models.TransactionReadGraph.from_pydantic(transaction) for transaction in transactions]
    # process_1 = [models.AccountReadGraph.from_pydantic(account) for account in accounts]
    data = [models.AccountReadGraph.from_pydantic(account) for account in accounts]
    # for account in data:
    #   account.transactions = t
    return data

# @strawberry.type
# class Query:
#   transactions: List[models.TransactionReadGraph] = strawberry.field(resolver=get_transactions)
#   transactions_by_user_id: List[models.TransactionReadGraph] = strawberry.field(resolver=get_transactions_by_user_id)
#   get_all_income: float = strawberry.field(resolver=get_all_income)
#   get_user: models.UserReadGraph = strawberry.field(resolver=get_user)
#   get_accounts_by_user_id: List[models.AccountReadGraph] = strawberry.field(resolver=get_accounts_by_user_id)


# class TestModel(BaseModel):
#   name: str
#   age: int

# def tesT_a(p: str):
#   return "test_" + p

# @strawberry.experimental.pydantic.type(model=TestModel, all_fields=True)
# class TestModelGraph:
#   test_field: str = strawberry.field(resolver=tesT_a)

@strawberry.type
class Query:
  user: models.UserReadGraph = strawberry.field(resolver=get_user)
  # transactions: List[models.TransactionReadGraph] = strawberry.field(resolver=get_transactions_by_user_id)
  # accounts: List[models.AccountReadGraph] = strawberry.field(resolver=get_accounts_by_user_id)

graphql_app = GraphQL(strawberry.Schema(mutation=Mutation, query=Query))
app = FastAPI()

app.add_route("/graphql", graphql_app)

@app.on_event("startup")
def on_startup():
    db.create_db_and_tables()