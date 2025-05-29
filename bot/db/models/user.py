from uuid import uuid4
from datetime import datetime
from sqlalchemy import Boolean, String, DateTime, Integer, BigInteger
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID 
from db.sessions import Base

class User(Base):
    __tablename__ = "users"
    
    uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False), 
        primary_key=True,
        unique=True, 
        index=True, 
        default=lambda: str(uuid4()),
    )
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str] = mapped_column(String, nullable=True)
    first_name: Mapped[str] = mapped_column(String, nullable=True)
    last_name: Mapped[str] = mapped_column(String, nullable=True)
    language_code: Mapped[str] = mapped_column(String, nullable=True)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    is_bot: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )
    gk_user: Mapped["GkUser"] = relationship(
        "GkUser", 
        back_populates="user", 
        uselist=False,
        cascade="all, delete-orphan"
    )

class GkUser(Base):
    __tablename__ = "gk_users"
    uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        unique=True,
        index=True,
        default=lambda: str(uuid4()),
    )
    user_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.uuid", ondelete="CASCADE"),
        unique=True,
        index=True,
    )
    gk_user_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=True)
    first_name: Mapped[str] = mapped_column(String, nullable=True)
    last_name: Mapped[str] = mapped_column(String, nullable=True)
    email: Mapped[str] = mapped_column(String, nullable=True)
    phone: Mapped[str] = mapped_column(String, nullable=True)
    password: Mapped[str] = mapped_column(String, nullable=True)
    token: Mapped[str] = mapped_column(String, nullable=True)
    role: Mapped[int] = mapped_column(Integer, nullable=True)
    sber_id: Mapped[str] = mapped_column(String, nullable=True)
    gazprom_id: Mapped[str] = mapped_column(String, nullable=True)
    aeroflot_id: Mapped[str] = mapped_column(String, nullable=True)
    card_id: Mapped[str] = mapped_column(String, nullable=True)
    passes_amount: Mapped[int] = mapped_column(Integer, default=0)
    user_qr: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    user: Mapped["User"] = relationship("User", back_populates="gk_user")