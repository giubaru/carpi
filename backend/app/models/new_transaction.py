from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Column, DateTime, Relationship
from datetime import datetime
import strawberry

if TYPE_CHECKING:
    from .user import User, UserRead
    from .account import Account

class TransactionBase(SQLModel):
  user_id: Optional[int] = Field(default=None, foreign_key="user.id")
  account_id: Optional[int] = Field(default=None, foreign_key="accounts.id")
  movement: str
  account_id: int
  amount: float
  category: str
  # date: Field(sa_column=Column(
  #     DateTime(timezone=True),
  #     nullable=False
  # ))
  

class Transaction(TransactionBase, table=True):
  __tablename__ = 'transactions'

  id: Optional[int] = Field(default=None, primary_key=True)
  user: Optional["User"] = Relationship(back_populates="transactions")
  accounts: Optional["Account"] = Relationship(back_populates="transactions")

class TransactionCreate(TransactionBase):
  pass

class TransactionRead(TransactionBase):
  id: int

@strawberry.experimental.pydantic.type(model=TransactionRead, fields=["user_id", "account_id", "movement", "account_id", "amount", "category", "id", "user", "accounts"])
class TransactionReadGraph:
  pass
