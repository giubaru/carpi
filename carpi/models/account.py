import strawberry

from typing import Optional, TYPE_CHECKING, List

from sqlmodel import SQLModel, Field, Column, DateTime, Relationship
from datetime import datetime


if TYPE_CHECKING:
    from .user import User, UserRead
    from .new_transaction import Transaction

class AccountBase(SQLModel):
  user_id: Optional[int] = Field(default=None, foreign_key="user.id")
  total: float = 0.0
  name: str
  account_type: str


  # date: Field(sa_column=Column(
  #     DateTime(timezone=True),
  #     nullable=False
  # ))
  

class Account(AccountBase, table=True):
  __tablename__ = 'accounts'

  id: Optional[int] = Field(default=None, primary_key=True)
  user: Optional["User"] = Relationship(back_populates="accounts")
  parent_id: Optional[int] = Field(default=None, foreign_key="accounts.id")
  children: List["Account"] = Relationship()
  transactions: List["Transaction"] = Relationship(back_populates="accounts")


class AccountCreate(AccountBase):
  pass

class AccountRead(AccountBase):
  id: int

@strawberry.experimental.pydantic.type(model=AccountRead, fields=["id","user","parent_id","children","transactions","user_id","total","name","account_type"])
class AccountReadGraph:
  pass

