import strawberry

from typing import Optional, TYPE_CHECKING, List

from sqlmodel import SQLModel, Field, Column, DateTime, Relationship
from datetime import datetime

from sqlalchemy.orm import backref
from uuid import uuid4


from .new_transaction import Transaction
if TYPE_CHECKING:
    from .user import User, UserRead

class AccountBase(SQLModel):
  user_id: Optional[int] = Field(default=None, foreign_key="user.id")
  total: float = 0.0
  name: str
  account_type: str


  # date: Field(sa_column=Column(
  #     DateTime(timezone=True),
  #     nullable=False
  # ))
  
class AccountLink(SQLModel, table=True):
  parent_id: Optional[int] = Field(
      default=None, foreign_key="accounts.id", primary_key=True
  )
  child_id: Optional[int] = Field(
      default=None, foreign_key="accounts.id", primary_key=True
  )

class Account(AccountBase, table=True):
  __tablename__ = "accounts"
  id: Optional[int] = Field(default=None, primary_key=True)
  user: Optional["User"] = Relationship(back_populates="accounts")
  parent_id: Optional[int] = Field(default=None, foreign_key="accounts.id")
  # parent: Optional["Account"] = None
  children: List["Account"] = Relationship(
    sa_relationship_kwargs=dict(
      cascade="all",
      backref=backref("parent", remote_side="Account.id"),
    )  
  )
  transactions: List["Transaction"] = Relationship(back_populates="accounts")

  def append(self, child: "Account"):
    self.children.append(child)

  def income(self, amount: float, origin: bool = True) -> "Transaction":
    if origin:
      transaction = Transaction(
        amount=amount,
        user_id=self.user_id,
        movement='I',
        category='Ganancia',
        account_id=self.id,
        id=str(uuid4())
      )
      self.transactions.append(transaction)

    self.total += amount
    
    if self.parent:
      self.parent.income(amount, origin=False)

  def withdraw(self, amount: float, origin: bool = True) -> "Transaction":
    if origin:
      transaction = Transaction(
        amount=amount,
        user_id=self.user_id,
        movement='E',
        category='Perdida',
        account_id=self.id,
        id=str(uuid4())
      )
      self.transactions.append(transaction)
    
    if amount > self.total: 
      raise Exception("Amount greater than available")

    self.total -= amount

    if self.parent:
      self.parent.withdraw(amount, origin=False)

  def transfer(self, amount: float, destination: "Account"):
    self.withdraw(amount)
    destination.income(amount)
class AccountCreate(AccountBase):
  pass

class AccountRead(AccountBase):
  id: int

@strawberry.experimental.pydantic.type(model=AccountRead, fields=["id","user","parent_id","children","transactions","user_id","total","name","account_type"])
class AccountReadGraph:
  pass

