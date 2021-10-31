import strawberry

from typing import Optional, List

from strawberry.field import field

from .new_transaction import TransactionRead
from .user import UserRead
from .account import AccountRead
from .. import db, crud

@strawberry.experimental.pydantic.type(model=AccountRead, fields=["id","children","transactions","parent_id","user_id","total","name","account_type"])
class AccountReadGraph:
  children: List[strawberry.LazyType["AccountReadGraph", __module__]] = field(default_factory=list)
  transactions: List[strawberry.LazyType["TransactionReadGraph", __module__]] = field(default_factory=list)
  parent_id: Optional[int] = field(default=None)
@strawberry.experimental.pydantic.type(model=TransactionRead, fields=["user_id", "account_id", "movement", "account_id", "amount", "category", "id", "user", "accounts"])
class TransactionReadGraph:
  pass

@strawberry.experimental.pydantic.type(model=UserRead, fields=["id", "name", "email", "username", "transactions"])
class UserReadGraph:
  # accounts: List["AccountReadGraph"] = None
  # transactions: List["TransactionReadGraph"] = None
  @strawberry.field
  def accounts(self, account_id: Optional[int] = None) -> List[AccountReadGraph]:
    with db.Session(db.engine) as session: # Using session to avoid Parent Lazy bounce
      childrens = []
      def get_children(children, childrens):
        if len(children) == 0:
          return childrens
        for child in children:
          childrens.append(child)
          get_children(child.children, childrens)

      if account_id:
        results = crud.get_accounts(session, account_id=account_id, user_id=self.id)
      else:
        results = crud.get_accounts(session, user_id=self.id)

      accounts = []
      for account in results:
        a = AccountReadGraph(**account.dict())
        a.transactions = account.transactions
        a.children = account.children
        
        accounts.append(a)

      return accounts