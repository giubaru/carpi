import strawberry

from typing import Optional, List

from strawberry.field import field

from .new_transaction import TransactionRead
from .user import UserRead
from .account import AccountRead
from .. import db, crud

@strawberry.experimental.pydantic.type(model=AccountRead, fields=["id","user","parent_id","children","transactions","user_id","total","name","account_type"])
class AccountReadGraph:
  children: List[strawberry.LazyType["AccountReadGraph", __module__]] = field(default_factory=list)
  parent_id: Optional[int] = None
  transactions: List[strawberry.LazyType["TransactionReadGraph", __module__]] = field(default_factory=list)

@strawberry.experimental.pydantic.type(model=TransactionRead, fields=["user_id", "account_id", "movement", "account_id", "amount", "category", "id", "user", "accounts"])
class TransactionReadGraph:
  pass

@strawberry.experimental.pydantic.type(model=UserRead, fields=["id", "name", "email", "username", "transactions", "accounts"])
class UserReadGraph:
  # accounts: List["AccountReadGraph"] = None
  # transactions: List["TransactionReadGraph"] = None
  @strawberry.field
  def accounts(self, account_id: Optional[int] = None) -> List[AccountReadGraph]:
    with db.Session(db.engine) as session: # Using session to avoid Parent Lazy bounce
      
      if account_id:
        results = crud.get_accounts(session, account_id=account_id, user_id=self.id)
      else:
        results = crud.get_accounts(session, user_id=self.id)

      accounts = [AccountReadGraph.from_pydantic(account) for account in results]
      return accounts