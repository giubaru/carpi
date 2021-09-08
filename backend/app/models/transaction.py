from typing import TYPE_CHECKING, Optional
from sqlmodel import SQLModel, Field, Column, DateTime, Relationship
from datetime import datetime


if TYPE_CHECKING:
    from .user import User, UserRead


class TransactionBase(SQLModel):
    category_id: int
    currency_id: int
    amount: float
    description: str
    date: datetime = Field(sa_column=Column(
        DateTime(timezone=True),
        nullable=False
    ))

    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    action_type_id: Optional[int] = Field(default=None, foreign_key="action_type.id")

class Transaction(TransactionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    user: Optional["User"] = Relationship(back_populates="transactions")

class TransactionCreate(TransactionBase):
    pass

class TransactionRead(TransactionBase):
    id: int
