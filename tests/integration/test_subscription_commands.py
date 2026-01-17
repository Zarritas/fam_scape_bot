"""
Tests de integración para comandos de suscripción.

Estos tests verifican el flujo completo de comandos, no solo el repositorio.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from telegram import Update, User as TelegramUser, Message, CallbackQuery
from telegram.ext import ContextTypes

from src.bot.handlers.subscriptions import (
    subscribe_command,
    subscriptions_command,
    unsubscribe_callback,
    smart_subscribe_callback,
)


class TestSubscriptionCommands:
    """Tests de integración para comandos de suscripción."""

    @pytest.fixture
    def mock_update(self):
        """Update mock para tests."""
        update = MagicMock(spec=Update)
        update.effective_user = MagicMock(spec=TelegramUser)
        update.effective_user.id = 123456789
        update.message = MagicMock(spec=Message)
        update.message.reply_text = AsyncMock()
        return update

    @pytest.fixture
    def mock_context(self):
        """Context mock para tests."""
        context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
        context.args = []
        return context

    @pytest.fixture
    def mock_query_update(self):
        """Update mock para callback queries."""
        update = MagicMock(spec=Update)
        update.callback_query = MagicMock(spec=CallbackQuery)
        update.callback_query.from_user = MagicMock(spec=TelegramUser)
        update.callback_query.from_user.id = 123456789
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()
        update.callback_query.data = ""
        return update

    async def test_subscribe_command_no_args(self, mock_update, mock_context, db_session):
        """Test comando /suscribirse sin argumentos."""
        # Setup
        mock_context.args = []

        # Execute
        await subscribe_command(mock_update, mock_context)

        # Assert
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Sintaxis incorrecta" in call_args

    async def test_subscribe_command_invalid_sex(self, mock_update, mock_context, db_session):
        """Test comando /suscribirse con sexo inválido."""
        # Setup
        mock_context.args = ["400m", "X"]

        # Execute
        await subscribe_command(mock_update, mock_context)

        # Assert
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Sexo inválido" in call_args

    async def test_subscriptions_command_no_subscriptions(self, mock_update, mock_context, db_session):
        """Test comando /suscripciones sin suscripciones activas."""
        # Setup - usuario sin suscripciones

        # Execute
        await subscriptions_command(mock_update, mock_context)

        # Assert
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "No tienes suscripciones activas" in call_args

    async def test_unsubscribe_callback_invalid_data(self, mock_query_update, db_session):
        """Test callback de desuscripción con datos inválidos."""
        # Setup
        mock_query_update.callback_query.data = "invalid"

        # Execute
        await unsubscribe_callback(mock_query_update, MagicMock())

        # Assert
        mock_query_update.callback_query.edit_message_text.assert_called_once()
        call_args = mock_query_update.callback_query.edit_message_text.call_args[0][0]
        assert "Callback inválido" in call_args