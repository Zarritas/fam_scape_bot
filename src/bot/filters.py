"""
Filtros personalizados para handlers del bot.
"""

from telegram.ext import filters

from src.config import settings


class IsAdmin(filters.MessageFilter):
    """Filtro que verifica si el usuario es administrador."""

    def filter(self, message) -> bool:
        if message.from_user is None:
            return False
        return message.from_user.id == settings.admin_user_id


# Instancia del filtro para uso en handlers
is_admin = IsAdmin()
