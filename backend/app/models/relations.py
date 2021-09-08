from pydantic.fields import Field
import strawberry
from typing import TYPE_CHECKING, Optional, List

from .transaction import TransactionRead
from .user import UserRead


class TransactionReadWithUser(TransactionRead):
    user: Optional["UserRead"] = None

class UserReadWithTransactions(UserRead):
    transactions: List["TransactionRead"] = []

@strawberry.experimental.pydantic.type(model=TransactionRead, fields=['category_id', 'currency_id', 'amount', 'description', 'user_id', 'date', 'action_type_id'])
class TransactionReadGraph: 
    pass

@strawberry.experimental.pydantic.type(model=UserRead, fields=['name', 'email', 'transactions', 'username'])
class UserReadGraph:
    transactions: List["TransactionReadGraph"] = None