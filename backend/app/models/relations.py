from pydantic.fields import Field
from sqlalchemy.util.langhelpers import safe_reraise
import strawberry
from typing import TYPE_CHECKING, Optional, List


from .new_transaction import TransactionRead
from .user import UserRead
from .account import AccountRead, Account
from .. import db
from sqlmodel import select

from app.models import account

@strawberry.experimental.pydantic.type(model=AccountRead, all_fields=True)
class AccountReadGraph:
  
  children: List[strawberry.LazyType["AccountReadGraph", __module__]] = None
  parent_id: Optional[int] = None
  transactions: List[strawberry.LazyType["TransactionReadGraph", __module__]] = None

@strawberry.experimental.pydantic.type(model=TransactionRead, all_fields=True)
class TransactionReadGraph:
  # account: "AccountReadGraph" = None
  pass

@strawberry.experimental.pydantic.type(model=UserRead, fields=['id', 'name', 'email', 'transactions', 'username', "accounts"])
class UserReadGraph:
  # accounts: List["AccountReadGraph"] = None
  # transactions: List["TransactionReadGraph"] = None
  @strawberry.field
  def accounts(self, account_id: Optional[int] = None) -> List[AccountReadGraph]:
    with db.Session(db.engine) as session:
      if account_id:
        results = session.exec(select(Account).where(Account.id == account_id)).all()
      else:
        results = session.exec(select(Account).where(Account.user_id == self.id)).all()

      accounts = [AccountReadGraph.from_pydantic(account) for account in results]
      return accounts