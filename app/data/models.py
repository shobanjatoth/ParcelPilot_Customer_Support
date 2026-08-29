
# from __future__ import annotations

# from datetime import datetime, timezone
# from decimal import Decimal

# from sqlalchemy import (
#     Boolean,
#     DateTime,
#     ForeignKey,
#     Numeric,
#     String,
#     Text,
# )
# from sqlalchemy.orm import Mapped, mapped_column, relationship

# from app.data.database import Base


# # ============================================================
# # Helper
# # ============================================================

# def utc_now() -> datetime:
#     """Return a timezone-aware UTC datetime."""
#     return datetime.now(timezone.utc)


# # ============================================================
# # Account
# # ============================================================

# class Account(Base):
#     __tablename__ = "accounts"

#     account_id: Mapped[str] = mapped_column(
#         String(100),
#         primary_key=True,
#     )

#     account_name: Mapped[str] = mapped_column(
#         String(255),
#         nullable=False,
#     )

#     plan: Mapped[str] = mapped_column(
#         String(100),
#         nullable=False,
#     )

#     status: Mapped[str] = mapped_column(
#         String(50),
#         default="active",
#         nullable=False,
#     )

#     csm: Mapped[str | None] = mapped_column(
#         String(255),
#         nullable=True,
#     )

#     contract_file: Mapped[str | None] = mapped_column(
#         String(500),
#         nullable=True,
#     )

#     premium_support: Mapped[bool] = mapped_column(
#         Boolean,
#         default=False,
#         nullable=False,
#     )

#     notes: Mapped[str | None] = mapped_column(
#         Text,
#         nullable=True,
#     )

#     # --------------------------------------------------------
#     # Relationships
#     # --------------------------------------------------------

#     orders: Mapped[list["Order"]] = relationship(
#         "Order",
#         back_populates="account",
#         cascade="all, delete-orphan",
#     )

#     tickets: Mapped[list["Ticket"]] = relationship(
#         "Ticket",
#         back_populates="account",
#         cascade="all, delete-orphan",
#     )

#     actions: Mapped[list["Action"]] = relationship(
#         "Action",
#         back_populates="account",
#         cascade="all, delete-orphan",
#     )


# # ============================================================
# # Order
# # ============================================================

# class Order(Base):
#     __tablename__ = "orders"

#     order_id: Mapped[str] = mapped_column(
#         String(100),
#         primary_key=True,
#     )

#     account_id: Mapped[str] = mapped_column(
#         String(100),
#         ForeignKey("accounts.account_id"),
#         nullable=False,
#         index=True,
#     )

#     carrier: Mapped[str] = mapped_column(
#         String(100),
#         nullable=False,
#     )

#     status: Mapped[str] = mapped_column(
#         String(50),
#         nullable=False,
#     )

#     booked_at: Mapped[datetime | None] = mapped_column(
#         DateTime(timezone=True),
#         nullable=True,
#     )

#     pickup_window_start: Mapped[datetime | None] = mapped_column(
#         DateTime(timezone=True),
#         nullable=True,
#     )

#     pickup_window_end: Mapped[datetime | None] = mapped_column(
#         DateTime(timezone=True),
#         nullable=True,
#     )

#     pickup_actual_at: Mapped[datetime | None] = mapped_column(
#         DateTime(timezone=True),
#         nullable=True,
#     )

#     shipment_fee_inr: Mapped[Decimal] = mapped_column(
#         Numeric(12, 2),
#         default=Decimal("0.00"),
#         nullable=False,
#     )

#     carrier_fault: Mapped[bool] = mapped_column(
#         Boolean,
#         default=False,
#         nullable=False,
#     )

#     customer_fault: Mapped[bool] = mapped_column(
#         Boolean,
#         default=False,
#         nullable=False,
#     )

#     cancellation_requested_at: Mapped[datetime | None] = mapped_column(
#         DateTime(timezone=True),
#         nullable=True,
#     )

#     notes: Mapped[str | None] = mapped_column(
#         Text,
#         nullable=True,
#     )

#     # --------------------------------------------------------
#     # Relationship
#     # --------------------------------------------------------

#     account: Mapped["Account"] = relationship(
#         "Account",
#         back_populates="orders",
#     )


# # ============================================================
# # Ticket
# # ============================================================

# class Ticket(Base):
#     __tablename__ = "tickets"

#     ticket_id: Mapped[str] = mapped_column(
#         String(100),
#         primary_key=True,
#     )

#     account_id: Mapped[str] = mapped_column(
#         String(100),
#         ForeignKey("accounts.account_id"),
#         nullable=False,
#         index=True,
#     )

#     created_at: Mapped[datetime | None] = mapped_column(
#         DateTime(timezone=True),
#         nullable=True,
#     )

#     status: Mapped[str] = mapped_column(
#         String(50),
#         default="open",
#         nullable=False,
#     )

#     subject: Mapped[str | None] = mapped_column(
#         String(500),
#         nullable=True,
#     )

#     description: Mapped[str | None] = mapped_column(
#         Text,
#         nullable=True,
#     )

#     channel: Mapped[str | None] = mapped_column(
#         String(100),
#         nullable=True,
#     )

#     assigned_to: Mapped[str | None] = mapped_column(
#         String(255),
#         nullable=True,
#     )

#     last_customer_message_at: Mapped[datetime | None] = mapped_column(
#         DateTime(timezone=True),
#         nullable=True,
#     )

#     historical_resolution: Mapped[str | None] = mapped_column(
#         Text,
#         nullable=True,
#     )

#     # --------------------------------------------------------
#     # Relationship
#     # --------------------------------------------------------

#     account: Mapped["Account"] = relationship(
#         "Account",
#         back_populates="tickets",
#     )


# # ============================================================
# # Action
# # ============================================================

# class Action(Base):
#     __tablename__ = "actions"

#     action_id: Mapped[str] = mapped_column(
#         String(100),
#         primary_key=True,
#     )

#     action_type: Mapped[str] = mapped_column(
#         String(100),
#         nullable=False,
#     )

#     status: Mapped[str] = mapped_column(
#         String(50),
#         default="pending",
#         nullable=False,
#     )

#     requested_by: Mapped[str | None] = mapped_column(
#         String(100),
#         nullable=True,
#     )

#     account_id: Mapped[str | None] = mapped_column(
#         String(100),
#         ForeignKey("accounts.account_id"),
#         nullable=True,
#         index=True,
#     )

#     payload_json: Mapped[str | None] = mapped_column(
#         Text,
#         nullable=True,
#     )

#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         default=utc_now,
#         nullable=False,
#     )

#     confirmed_at: Mapped[datetime | None] = mapped_column(
#         DateTime(timezone=True),
#         nullable=True,
#     )

#     executed_at: Mapped[datetime | None] = mapped_column(
#         DateTime(timezone=True),
#         nullable=True,
#     )

#     # --------------------------------------------------------
#     # Relationship
#     # --------------------------------------------------------

#     account: Mapped["Account | None"] = relationship(
#         "Account",
#         back_populates="actions",
#     )


# # ============================================================
# # Audit Log
# # ============================================================

# class AuditLog(Base):
#     __tablename__ = "audit_log"

#     id: Mapped[str] = mapped_column(
#         String(100),
#         primary_key=True,
#     )

#     request_id: Mapped[str | None] = mapped_column(
#         String(100),
#         index=True,
#         nullable=True,
#     )

#     user_id: Mapped[str | None] = mapped_column(
#         String(100),
#         index=True,
#         nullable=True,
#     )

#     account_id: Mapped[str | None] = mapped_column(
#         String(100),
#         index=True,
#         nullable=True,
#     )

#     action: Mapped[str] = mapped_column(
#         String(100),
#         nullable=False,
#     )

#     details: Mapped[str | None] = mapped_column(
#         Text,
#         nullable=True,
#     )

#     timestamp: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         default=utc_now,
#         nullable=False,
#     )





from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, sessionmaker

from app.data.database import Base
from app.config import settings


# ============================================================
# Database Engine & Initialization
# ============================================================

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


# ============================================================
# Helper
# ============================================================

def utc_now() -> datetime:
    """Return a timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


# ============================================================
# Account
# ============================================================

class Account(Base):
    __tablename__ = "accounts"

    account_id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
    )

    account_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    plan: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="active",
        nullable=False,
    )

    csm: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    contract_file: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    premium_support: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # --------------------------------------------------------
    # Relationships
    # --------------------------------------------------------

    orders: Mapped[list["Order"]] = relationship(
        "Order",
        back_populates="account",
        cascade="all, delete-orphan",
    )

    tickets: Mapped[list["Ticket"]] = relationship(
        "Ticket",
        back_populates="account",
        cascade="all, delete-orphan",
    )

    actions: Mapped[list["Action"]] = relationship(
        "Action",
        back_populates="account",
        cascade="all, delete-orphan",
    )


# ============================================================
# Order
# ============================================================

class Order(Base):
    __tablename__ = "orders"

    order_id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
    )

    account_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("accounts.account_id"),
        nullable=False,
        index=True,
    )

    carrier: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    booked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    pickup_window_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    pickup_window_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    pickup_actual_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    shipment_fee_inr: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal("0.00"),
        nullable=False,
    )

    carrier_fault: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    customer_fault: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    cancellation_requested_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # --------------------------------------------------------
    # Relationship
    # --------------------------------------------------------

    account: Mapped["Account"] = relationship(
        "Account",
        back_populates="orders",
    )


# ============================================================
# Ticket
# ============================================================

class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
    )

    account_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("accounts.account_id"),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="open",
        nullable=False,
    )

    subject: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    channel: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    assigned_to: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    last_customer_message_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    historical_resolution: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # --------------------------------------------------------
    # Relationship
    # --------------------------------------------------------

    account: Mapped["Account"] = relationship(
        "Account",
        back_populates="tickets",
    )


# ============================================================
# Action
# ============================================================

class Action(Base):
    __tablename__ = "actions"

    action_id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
    )

    action_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
    )

    requested_by: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    account_id: Mapped[str | None] = mapped_column(
        String(100),
        ForeignKey("accounts.account_id"),
        nullable=True,
        index=True,
    )

    payload_json: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    confirmed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    executed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # --------------------------------------------------------
    # Relationship
    # --------------------------------------------------------

    account: Mapped["Account | None"] = relationship(
        "Account",
        back_populates="actions",
    )


# ============================================================
# Audit Log
# ============================================================

class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
    )

    request_id: Mapped[str | None] = mapped_column(
        String(100),
        index=True,
        nullable=True,
    )

    user_id: Mapped[str | None] = mapped_column(
        String(100),
        index=True,
        nullable=True,
    )

    account_id: Mapped[str | None] = mapped_column(
        String(100),
        index=True,
        nullable=True,
    )

    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    details: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )