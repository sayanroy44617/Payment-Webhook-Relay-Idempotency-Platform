from datetime import datetime
import uuid
from typing import Optional

from sqlalchemy import UUID, String, Integer, DateTime, func, Text
from sqlalchemy.dialects.postgresql import JSONB

from sqlalchemy.orm import Mapped , mapped_column

from payment_webhook_relay_idempotency_platform.database.database import Base


class Webhook(Base):

    __tablename__ = "webhooks_event"

    id : Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4)

    idempotency_key : Mapped[str] = mapped_column(String(255),
                                                  index=True,
                                                  nullable=False,
                                                  unique=True)

    provider : Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )

    event_status : Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="PENDING",
    )

    payload : Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    retry_count : Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    max_retry_count : Mapped[int] = mapped_column(
        Integer,
        default=3,
    )

    next_retry_at : Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    last_error : Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )

    destination_url : Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    response_code : Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    response_body : Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    created_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    updated_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )