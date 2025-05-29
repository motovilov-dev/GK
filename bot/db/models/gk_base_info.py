from uuid import uuid4
from datetime import datetime
from sqlalchemy import Boolean, String, DateTime, Integer, BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from db.sessions import Base

class City(Base):
    __tablename__ = "cities"

    uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        unique=True,
        index=True,
        default=lambda: str(uuid4()),
    )
    gk_id: Mapped[int] = mapped_column(BigInteger, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    code: Mapped[str] = mapped_column(String, nullable=True, index=True)
    foreign: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationship to Hall
    halls: Mapped[list["Hall"]] = relationship("Hall", back_populates="city_rel")

class Hall(Base):
    __tablename__ = "halls"
    
    uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False), 
        primary_key=True,
        unique=True, 
        index=True, 
        default=lambda: str(uuid4()),
    )
    gk_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    admin_name: Mapped[str] = mapped_column(String, nullable=True, index=True)
    working_time: Mapped[str] = mapped_column(String, nullable=True, index=True)
    location: Mapped[str] = mapped_column(String, nullable=True, index=True)
    is_hidden: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    htype_id: Mapped[int] = mapped_column(Integer, nullable=True, index=True)
    station_id: Mapped[int] = mapped_column(Integer, nullable=True, index=True)
    city_uuid: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("cities.uuid"), index=True)
    city_gk_id: Mapped[int] = mapped_column(Integer, nullable=True, index=True)
    city: Mapped[str] = mapped_column(String, nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )
    
    # Relationships
    city_rel: Mapped["City"] = relationship("City", back_populates="halls")
    media: Mapped[list["Media"]] = relationship("Media", back_populates="hall")
    services: Mapped[list["Services"]] = relationship("Services", back_populates="hall")

class Media(Base):
    __tablename__ = "medias"
    uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        unique=True,
        index=True,
        default=lambda: str(uuid4()),
    )
    hall_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("halls.uuid"),
        index=True
    )
    gk_id: Mapped[int] = mapped_column(BigInteger, index=True)
    hall_gk_id: Mapped[int] = mapped_column(BigInteger, index=True)
    url: Mapped[str] = mapped_column(String, index=True)
    
    # Relationship to Hall
    hall: Mapped["Hall"] = relationship("Hall", back_populates="media")

class Services(Base):
    __tablename__ = "services"
    uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        unique=True,
        index=True,
        default=lambda: str(uuid4()),
    )
    hall_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("halls.uuid"),
        index=True
    )
    gk_id: Mapped[int] = mapped_column(BigInteger, index=True)
    hall_gk_id: Mapped[int] = mapped_column(BigInteger, index=True)
    name: Mapped[str] = mapped_column(String, nullable=True, index=True)
    text: Mapped[str] = mapped_column(String, nullable=True, index=True)
    icon_url: Mapped[str] = mapped_column(String, nullable=True, index=True)
    service_type: Mapped[str] = mapped_column(String, nullable=True, index=True)
    content: Mapped[dict] = mapped_column(JSONB, nullable=True, index=True)
    
    # Relationship to Hall
    hall: Mapped["Hall"] = relationship("Hall", back_populates="services")

class Products(Base):
    __tablename__ = "products"
    uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        unique=True,
        index=True,
        default=lambda: str(uuid4()),
    )
    gk_id: Mapped[int] = mapped_column(BigInteger, index=True)
    name: Mapped[str] = mapped_column(String, nullable=True, index=True)
    price: Mapped[int] = mapped_column(Integer, nullable=True, index=True)
    prefix: Mapped[str] = mapped_column(String, nullable=True, index=True)
    display: Mapped[int] = mapped_column(Integer, nullable=True, index=True)
    count: Mapped[int] = mapped_column(Integer, nullable=True, index=True)
    foreign: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

class PromoServices(Base):
    __tablename__ = "promo_services"
    uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        unique=True,
        index=True,
        default=lambda: str(uuid4()),
    )
    gk_id: Mapped[int] = mapped_column(BigInteger, index=True)
    active: Mapped[int] = mapped_column(Integer, nullable=True, default=False)
    name: Mapped[str] = mapped_column(String, nullable=True, index=True)
    code: Mapped[str] = mapped_column(String, nullable=True, index=True)
    denomination: Mapped[str] = mapped_column(String, nullable=True, index=True)
    description: Mapped[str] = mapped_column(String, nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )