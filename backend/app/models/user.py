from typing import TYPE_CHECKING, Optional, List
from sqlmodel import SQLModel, Field, Relationship


if TYPE_CHECKING:
  from .new_transaction import Transaction
  from .account import Account


class UserBase(SQLModel):
  name: str
  email: str
  username: str

class User(UserBase, table=True):
  id: Optional[int] = Field(default=None, primary_key=True)
  
  transactions: List["Transaction"] = Relationship(back_populates="user")
  accounts: List["Account"] = Relationship(back_populates="user")

class UserCreate(UserBase):
  pass

class UserRead(UserBase):
  id: int
