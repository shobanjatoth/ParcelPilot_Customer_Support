



from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.data.models import (
    Account,
    Action,
    AuditLog,
    Order,
    Ticket,
)


class Repository:
    def __init__(self, db: Session):
        self.db = db

    def get_account(
        self,
        account_id: str,
        user_account_id: Optional[str] = None,
    ) -> Optional[Account]:

        if user_account_id and user_account_id != account_id:
            return None

        stmt = select(Account).where(
            Account.account_id == account_id
        )

        return self.db.scalar(stmt)

    def get_order(
        self,
        order_id: str,
        user_account_id: Optional[str] = None,
    ) -> Optional[Order]:

        stmt = select(Order).where(
            Order.order_id == order_id
        )

        order = self.db.scalar(stmt)

        if (
            order
            and user_account_id
            and order.account_id != user_account_id
        ):
            return None

        return order

    def get_orders_by_account(
        self,
        account_id: str,
        user_account_id: Optional[str] = None,
    ) -> list[Order]:

        if user_account_id and user_account_id != account_id:
            return []

        stmt = select(Order).where(
            Order.account_id == account_id
        )

        return list(self.db.scalars(stmt).all())

    def get_ticket(
        self,
        ticket_id: str,
        user_account_id: Optional[str] = None,
    ) -> Optional[Ticket]:

        stmt = select(Ticket).where(
            Ticket.ticket_id == ticket_id
        )

        ticket = self.db.scalar(stmt)

        if (
            ticket
            and user_account_id
            and ticket.account_id != user_account_id
        ):
            return None

        return ticket

    def get_tickets_by_account(
        self,
        account_id: str,
        user_account_id: Optional[str] = None,
    ) -> list[Ticket]:

        if user_account_id and user_account_id != account_id:
            return []

        stmt = select(Ticket).where(
            Ticket.account_id == account_id
        )

        return list(self.db.scalars(stmt).all())

    def get_all_accounts(self) -> list[Account]:
        stmt = select(Account)
        return list(self.db.scalars(stmt).all())

    def get_all_orders(self) -> list[Order]:
        stmt = select(Order)
        return list(self.db.scalars(stmt).all())

    def get_all_tickets(self) -> list[Ticket]:
        stmt = select(Ticket)
        return list(self.db.scalars(stmt).all())

    def get_open_tickets(self) -> list[Ticket]:
        stmt = select(Ticket).where(
            Ticket.status == "open"
        )

        return list(self.db.scalars(stmt).all())

    def get_action(
        self,
        action_id: str,
    ) -> Optional[Action]:

        stmt = select(Action).where(
            Action.action_id == action_id
        )

        return self.db.scalar(stmt)

    def create_action(self, action: Action) -> Action:
        self.db.add(action)
        self.db.commit()
        self.db.refresh(action)

        return action

    def confirm_action(
        self,
        action_id: str,
    ) -> Optional[Action]:

        action = self.get_action(action_id)

        if not action or action.status != "pending":
            return None

        action.status = "confirmed"
        self.db.commit()
        self.db.refresh(action)

        return action

    def execute_action(
        self,
        action_id: str,
    ) -> Optional[Action]:

        action = self.get_action(action_id)

        if not action or action.status != "confirmed":
            return None

        action.status = "executed"
        self.db.commit()
        self.db.refresh(action)

        return action

    def get_pending_actions_for_account(
        self,
        account_id: str,
    ) -> list[Action]:

        stmt = select(Action).where(
            Action.account_id == account_id,
            Action.status.in_(["pending", "confirmed"]),
        )

        return list(self.db.scalars(stmt).all())

    def log_audit(
        self,
        audit: AuditLog,
    ) -> AuditLog:

        self.db.add(audit)
        self.db.commit()
        self.db.refresh(audit)

        return audit