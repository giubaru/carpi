import strawberry


from abc import ABC
from dataclasses import dataclass, field

from strawberry.asgi import GraphQL
from typing import List, Optional
from sqlmodel import select
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models.new_transaction import TransactionRead

from . import db, models

# def create_transaction():
#     # TODO: Check if is automated
#     from datetime import datetime
#     with db.Session(db.engine) as session:
#         trans1 = models.Transaction(
#             amount=1000,
#             category_id=6,
#             date=datetime.now(),
#             currency_id=1,
#             description='Test transaction',
#             action_type_id=1,
#             user_id=1
#         )
#         session.add(trans1)
#         session.commit()
#         session.refresh(trans1)

#         print('Created Transaction:', trans1)

# def create_actions_type():
#     # TODO: Add to automated tests
#     with db.Session(db.engine) as session:
#         action1 = models.ActionType(
#             code="I",
#             description="This action is used to indicate income movements",
#             name="Income"
#         )
#         action2 = models.ActionType(
#             code="W",
#             description="This action is used to indicate withdrawal movements",
#             name="Withdrawal"
#         )
#         session.add(action1)
#         session.add(action2)
#         session.commit()
#         session.refresh(action1)
#         session.refresh(action2)

# def create_user():
#     # TODO: Check if is automated
#     with db.Session(db.engine) as session:
#         user1 = models.User(
#             name="Demo",
#             email="demo@email.com",
#             username="demo"
#         )
#         session.add(user1)
#         session.commit()
#         session.refresh(user1)


# def main():
#     db.create_db_and_tables()
    # create_actions_type()
    # create_user()
    # create_transaction()


class Account(ABC):
  """Esta clase representa una cuenta donde se guarda o extre montos de dinero en distitnas divisas."""

  def add_child(self, account: 'Account'):
    account.parent = self
    self.children.append(account)

  def income(self, amount: float, origin: bool = True):
    # if origin:
    #   t = Transaction(id="123", user_id=4004, movement="I", account_id=self.__class__.__name__, date="21/10/21", amount=amount, category=self.category)
    #   t.register()
    
    self.total += amount
    
    if self.parent:
      self.parent.income(amount, False)

  def withdraw(self, amount: float, origin: bool = True):
    # if origin:
    #   t = Transaction(id="123", user_id=4005, movement="E", account_id=self.__class__.__name__, date="21/10/21", amount=amount, category=self.category)
    #   t.register()

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
    def add_income(self, amount: float) -> str:
      print(f'Adding {amount}')
      with db.Session(db.engine) as session:
        trans1 = models.Transaction(
            amount=amount,
            user_id=1,
            movement='I',
            category='Ganancia',
            account_id=11,
            id='123'
        )
        session.add(trans1)
        session.commit()

      return "ok"
        
def add_income() -> models.TransactionReadGraph:
  with db.Session(db.engine) as session:
    transactions = session.exec(select(models.Transaction)).all()
    data = models.TransactionReadGraph.from_pydantic(transactions)
    return data
@strawberry.type
class Query:
  transactions: models.TransactionRead = strawberry.field(resolver=add_income)


graphql_app = GraphQL(strawberry.Schema(mutation=Mutation, query=Query))
app = FastAPI()

# origins = [
#     "http://localhost",
#     "http://localhost:8080",
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app.add_route("/graphql", graphql_app)

@app.on_event("startup")
def on_startup():
    db.create_db_and_tables()


# @app.get("/")
# def test_endpoint():
#     return {
#         'msg': 'connection ok'
#     }

# # TODO: Move endpoints to Routes and create CRUD module.
# @app.post("/transactions/", response_model=models.TransactionRead)
# def transaction_add(*, session: db.Session = Depends(db.get_session), transaction: models.TransactionCreate):
#     actions_type: models.ActionTypeRead = session.get(models.ActionType, transaction.action_type_id)
#     user: models.UserRead = session.get(models.User, transaction.user_id)

#     if not actions_type:
#         raise HTTPException(status_code=404, detail="Invalid Action Type")
#     if not user:
#         raise HTTPException(status_code=404, detail="Invalid User ID")

#     db_transaction = models.Transaction.from_orm(transaction)
#     session.add(db_transaction)
#     session.commit()
#     session.refresh(db_transaction)
#     return db_transaction

# @app.get("/transactions/", response_model=List[models.TransactionRead])
# def transactions_read(*, session: db.Session = Depends(db.get_session)):
#     transactions = session.exec(select(models.Transaction)).all()
#     return transactions

# @app.get("/transactions/{transaction_id}", response_model=models.TransactionReadWithUser)
# def transaction_read(*, session: db.Session = Depends(db.get_session), transaction_id: int):
#     transaction = session.get(models.Transaction, transaction_id)
#     return transaction


# @app.get("/actions_type", response_model=List[models.ActionTypeRead])
# def action_type_read(*, session: db.Session = Depends(db.get_session)):
#     actions_type = session.exec(select(models.ActionType)).all()
#     return actions_type

# @app.post("/users/", response_model=models.UserRead)
# def user_add(*, session: db.Session = Depends(db.get_session), user: models.UserCreate):
#     db_user = models.User.from_orm(user)
#     session.add(db_user)
#     session.commit()
#     session.refresh(db_user)
#     return db_user

# @app.get('/users/', response_model=List[models.UserRead])
# def users_read(*, session: db.Session = Depends(db.get_session)):
#     users = session.exec(select(models.User)).all()
#     return users

# @app.get("/users/{user_id}", response_model=models.UserReadWithTransactions)
# def user_read(*, session: db.Session = Depends(db.get_session), user_id: int):
#     user = session.get(models.User, user_id)
#     return user

# if __name__ == "__main__":
#     main()