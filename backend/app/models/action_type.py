from typing import Optional
from sqlmodel import SQLModel, Field


class ActionTypeBase(SQLModel):
    name: str
    code: str
    description: str

class ActionType(ActionTypeBase, table=True):
    __tablename__ = 'action_type'
    id: Optional[int] = Field(default=None, primary_key=True)

class ActionTypeCreate(ActionTypeBase):
    ...

class ActionTypeRead(ActionTypeBase):
    id: int
