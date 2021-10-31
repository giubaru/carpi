from typing import List, Optional
from sqlmodel import select
from sqlmodel.orm.session import Session
from . import db, models
from .models.account import Account, AccountRead


def get_transactions() -> List[models.TransactionRead]:
  with db.get_session() as session:
    transactions = session.exec(select(models.Transaction)).all()
    return transactions

def get_transactions_by_user_id(user_id: int) -> List[models.TransactionRead]:
  with db.Session(db.engine) as session:
    statement = select(models.Transaction).where(models.Transaction.user_id == user_id)
    transactions = session.exec(statement).all()
    return transactions

def get_total_income_by_user_id(user_id: int) -> float:
  with db.Session(db.engine) as session:
    statement = select(models.Transaction).where(models.Transaction.user_id == user_id, models.Transaction.movement == 'I')
    transactions = session.exec(statement).all()
    total = [ transaction.amount for transaction in transactions ]
    return sum(total)

def get_user(user_id: int) -> models.UserRead:
  with db.Session(db.engine) as session:
    user = session.get(models.User, user_id)
    return user

def get_user_by_username(username: str) -> models.UserRead:
  with db.Session(db.engine) as session:
    user = session.exec(select(models.User).where(models.User.username == username)).first()
    return user

def get_user_by_email(email: str) -> models.UserRead:
  with db.Session(db.engine) as session:
    user = session.exec(select(models.User).where(models.User.email == email)).first()
    return user

def get_accounts_by_user_id(user_id: int) -> List[models.AccountRead]:
  with db.Session(db.engine) as session:
    accounts = session.exec(select(models.Account).where(models.Account.user_id == user_id)).all()
    return accounts

def update_total(account_id: int, amount: float):
  with db.Session(db.engine) as session:
    account = session.get(models.Account, account_id)
    account.total += amount
    session.add(account)
    session.commit()
    if account.parent_id:
      update_total(account.parent_id, amount)

def get_accounts(session: Session, account_id: Optional[int] = None, user_id: Optional[int] = None) -> List[AccountRead]:
  statement = select(Account)

  if account_id:
    statement = statement.where(Account.user_id == user_id, Account.id == account_id)
  elif user_id:
    statement = statement.where(Account.user_id == user_id)
  
  accounts = session.exec(statement).all()
  return accounts