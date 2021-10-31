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
  
class AccountLink(SQLModel, table=True):
  parent_id: Optional[int] = Field(
      default=None, foreign_key="accounts.id", primary_key=True
  )
  child_id: Optional[int] = Field(
      default=None, foreign_key="accounts.id", primary_key=True
  )

class Account(AccountBase, table=True):
  __tablename__ = 'accounts'

  id: Optional[int] = Field(default=None, primary_key=True)
  user: Optional["User"] = Relationship(back_populates="accounts")
  parents: Optional["Account"] = Relationship(
    back_populates="children", 
    link_model=AccountLink,
    sa_relationship_kwargs=dict(
      primaryjoin="Account.id == AccountLink.child_id", 
      secondaryjoin="Account.id == AccountLink.parent_id"))
  children: List["Account"] = Relationship(
    back_populates="parents", 
    link_model=AccountLink,
    sa_relationship_kwargs=dict(
      primaryjoin="Account.id == AccountLink.parent_id", 
      secondaryjoin="Account.id == AccountLink.child_id"))
  transactions: List["Transaction"] = Relationship(back_populates="accounts")


class AccountCreate(AccountBase):
  pass

class AccountRead(AccountBase):
  id: int

@strawberry.experimental.pydantic.type(model=AccountRead, fields=["id","user","parents","children","transactions","user_id","total","name","account_type"])
class AccountReadGraph:
  pass

