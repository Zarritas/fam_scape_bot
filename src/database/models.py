"""
Modelos ORM de SQLAlchemy para la base de datos.

Define todas las tablas y relaciones del sistema.
"""

from datetime import datetime, date, time
from typing import Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
    UniqueConstraint,
    Index,
    func,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    """Base para todos los modelos ORM."""
    pass


class Competition(Base):
    """
    Competición de atletismo.
    
    Representa una competición completa con su PDF asociado.
    """
    __tablename__ = "competitions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    competition_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    pdf_url: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
    pdf_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    has_modifications: Mapped[bool] = mapped_column(Boolean, default=False)
    competition_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False, 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False, 
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # Relaciones
    events: Mapped[list["Event"]] = relationship(
        "Event",
        back_populates="competition",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    
    def __repr__(self) -> str:
        return f"<Competition(id={self.id}, name='{self.name}', date={self.competition_date})>"


class Event(Base):
    """
    Prueba individual dentro de una competición.
    
    Ej: 400m masculino, Pértiga femenino.
    """
    __tablename__ = "events"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    competition_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("competitions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    discipline: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(
        String(20),  # "carrera" o "concurso"
        nullable=False,
    )
    sex: Mapped[str] = mapped_column(
        String(1),  # "M" o "F"
        nullable=False,
        index=True,
    )
    scheduled_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    category: Mapped[str] = mapped_column(String(50), default="")
    
    # Relaciones
    competition: Mapped["Competition"] = relationship(
        "Competition",
        back_populates="events",
    )
    notification_logs: Mapped[list["NotificationLog"]] = relationship(
        "NotificationLog",
        back_populates="event",
        cascade="all, delete-orphan",
    )
    
    # Índice compuesto para búsquedas de suscripciones
    __table_args__ = (
        Index("ix_events_discipline_sex", "discipline", "sex"),
    )
    
    @property
    def subscription_key(self) -> str:
        """Clave para matching con suscripciones."""
        return f"{self.discipline.lower()}_{self.sex}"
    
    def __repr__(self) -> str:
        return f"<Event(id={self.id}, discipline='{self.discipline}', sex='{self.sex}')>"


class User(Base):
    """
    Usuario de Telegram.
    
    Almacena información básica y estado de actividad.
    """
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(
        Integer,  # BigInt en PostgreSQL, Integer en SQLite
        nullable=False,
        unique=True,
        index=True,
    )
    first_name: Mapped[str] = mapped_column(String(100), default="")
    username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False, 
        server_default=func.now()
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relaciones
    subscriptions: Mapped[list["Subscription"]] = relationship(
        "Subscription",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    notification_logs: Mapped[list["NotificationLog"]] = relationship(
        "NotificationLog",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, telegram_id={self.telegram_id})>"


class Subscription(Base):
    """
    Suscripción de un usuario a una prueba específica.
    
    Ej: Usuario 123 suscrito a "pértiga_F" (Pértiga femenino).
    """
    __tablename__ = "subscriptions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    discipline: Mapped[str] = mapped_column(String(100), nullable=False)
    sex: Mapped[str] = mapped_column(String(1), nullable=False)  # "M" o "F"
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )
    
    # Relaciones
    user: Mapped["User"] = relationship("User", back_populates="subscriptions")
    
    # Evitar duplicados: un usuario solo puede suscribirse una vez a cada prueba
    __table_args__ = (
        UniqueConstraint("user_id", "discipline", "sex", name="uq_user_subscription"),
        Index("ix_subscriptions_discipline_sex", "discipline", "sex"),
    )
    
    @property
    def subscription_key(self) -> str:
        """Clave de suscripción para matching con eventos."""
        return f"{self.discipline.lower()}_{self.sex}"
    
    @property
    def display_name(self) -> str:
        """Nombre para mostrar: 'Disciplina Sexo'."""
        sex_label = "Masculino" if self.sex == "M" else "Femenino"
        return f"{self.discipline} {sex_label}"
    
    def __repr__(self) -> str:
        return f"<Subscription(user_id={self.user_id}, discipline='{self.discipline}', sex='{self.sex}')>"


class NotificationLog(Base):
    """
    Registro de notificaciones enviadas.
    
    Evita enviar notificaciones duplicadas al mismo usuario
    para el mismo evento.
    """
    __tablename__ = "notification_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sent_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )
    message_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    
    # Relaciones
    user: Mapped["User"] = relationship("User", back_populates="notification_logs")
    event: Mapped["Event"] = relationship("Event", back_populates="notification_logs")
    
    # Evitar notificaciones duplicadas
    __table_args__ = (
        UniqueConstraint("user_id", "event_id", name="uq_user_event_notification"),
    )
    
    def __repr__(self) -> str:
        return f"<NotificationLog(user_id={self.user_id}, event_id={self.event_id})>"


class ErrorLog(Base):
    """
    Registro de errores del sistema.
    
    Para que el admin pueda revisar errores recientes.
    """
    __tablename__ = "error_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        index=True,
    )
    component: Mapped[str] = mapped_column(String(100), nullable=False)
    error_type: Mapped[str] = mapped_column(String(100), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    stack_trace: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    def __repr__(self) -> str:
        return f"<ErrorLog(id={self.id}, component='{self.component}', error_type='{self.error_type}')>"
