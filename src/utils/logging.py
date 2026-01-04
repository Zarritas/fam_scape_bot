"""
Sistema de logging estructurado para el bot.

Soporta:
- Formato JSON para producción (fácil de parsear en CloudWatch/ELK)
- Formato texto para desarrollo local
- Nivel configurable via variable de entorno
"""

import json
import logging
import sys
from datetime import datetime
from typing import Any

from src.config import settings


class JSONFormatter(logging.Formatter):
    """Formateador que produce logs en formato JSON."""

    def format(self, record: logging.LogRecord) -> str:
        log_data: dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Añadir información de excepción si existe
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Añadir campos extra si se proporcionan
        if hasattr(record, "extra_data"):
            log_data["data"] = record.extra_data

        return json.dumps(log_data, ensure_ascii=False)


class TextFormatter(logging.Formatter):
    """Formateador legible para desarrollo local."""

    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, "")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        message = (
            f"{color}[{timestamp}] "
            f"{record.levelname:8s}{self.RESET} "
            f"{record.name}: {record.getMessage()}"
        )

        if record.exc_info:
            message += f"\n{self.formatException(record.exc_info)}"

        return message


def setup_logging() -> None:
    """
    Configura el sistema de logging según las variables de entorno.
    
    Debe llamarse al inicio de la aplicación.
    """
    # Determinar el nivel de log
    level = getattr(logging, settings.log_level)

    # Seleccionar el formateador según configuración
    if settings.log_format == "json":
        formatter = JSONFormatter()
    else:
        formatter = TextFormatter()

    # Configurar handler para stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(level)

    # Configurar el logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # Reducir verbosidad de librerías externas
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.WARNING)
    logging.getLogger("apscheduler").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger configurado para el módulo especificado.
    
    Args:
        name: Nombre del módulo (usar __name__)
        
    Returns:
        Logger configurado
    """
    return logging.getLogger(name)


class LoggerAdapter(logging.LoggerAdapter):
    """Adapter para añadir contexto extra a los logs."""

    def process(
        self, msg: str, kwargs: dict[str, Any]
    ) -> tuple[str, dict[str, Any]]:
        # Añadir extra_data al record para uso por JSONFormatter
        extra = kwargs.get("extra", {})
        if self.extra:
            extra["extra_data"] = {**self.extra, **extra.get("extra_data", {})}
        kwargs["extra"] = extra
        return msg, kwargs


def get_logger_with_context(name: str, **context: Any) -> LoggerAdapter:
    """
    Obtiene un logger con contexto adicional incluido en cada mensaje.
    
    Útil para incluir IDs de usuario, competición, etc.
    
    Args:
        name: Nombre del módulo
        **context: Contexto adicional a incluir en los logs
        
    Returns:
        LoggerAdapter con el contexto configurado
    """
    logger = get_logger(name)
    return LoggerAdapter(logger, context)
