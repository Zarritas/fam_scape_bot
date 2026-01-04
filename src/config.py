"""
Configuración centralizada del bot usando Pydantic Settings.

Carga las variables de entorno desde .env y valida los tipos.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración del bot de Telegram para Atletismo Madrid."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Telegram
    telegram_bot_token: str = Field(..., description="Token del bot de Telegram")
    admin_user_id: int = Field(..., description="ID de Telegram del usuario administrador")

    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./data/bot.db",
        description="URL de conexión a la base de datos",
    )

    # Scheduler
    scrape_hour: int = Field(default=9, ge=0, le=23)
    scrape_minute: int = Field(default=0, ge=0, le=59)
    notify_hour: int = Field(default=10, ge=0, le=23)
    notify_minute: int = Field(default=0, ge=0, le=59)

    # FAM URLs
    fam_base_url: str = Field(
        default="https://www.atletismomadrid.com",
        description="URL base de la Federación de Atletismo de Madrid",
    )
    fam_calendar_path: str = Field(
        default="/index.php?option=com_content&view=article&id=3292&Itemid=111",
        description="Ruta al calendario de competiciones",
    )

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(default="INFO")
    log_format: Literal["json", "text"] = Field(default="json")

    # Timezone
    timezone: str = Field(default="Europe/Madrid")

    @property
    def fam_calendar_url(self) -> str:
        """URL completa del calendario de competiciones."""
        return f"{self.fam_base_url}{self.fam_calendar_path}"

    @property
    def is_sqlite(self) -> bool:
        """Retorna True si la base de datos es SQLite."""
        return self.database_url.startswith("sqlite")

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Valida que la URL de la base de datos tenga un formato válido."""
        valid_prefixes = ("sqlite", "postgresql", "postgres")
        if not any(v.startswith(prefix) for prefix in valid_prefixes):
            raise ValueError(f"DATABASE_URL debe empezar con uno de: {valid_prefixes}")
        return v


@lru_cache
def get_settings() -> Settings:
    """
    Obtiene la configuración del bot.

    Usa lru_cache para evitar cargar el archivo .env múltiples veces.
    """
    return Settings()


# Alias para acceso rápido
settings = get_settings()
