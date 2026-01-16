"""
Tests del sistema de notificaciones automáticas.
Prueba el job de notificaciones, repositorios y lógica completa.
"""

import pytest
from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock

from src.database.repositories.notification import NotificationRepository
from src.database.repositories.subscription import SubscriptionRepository
from src.scheduler.jobs import notification_job


@pytest.mark.asyncio
class TestNotificationJob:
    """Tests del job de notificaciones diario."""

    async def test_notification_job_no_bot(self):
        """Test que el job maneja correctamente cuando no hay bot."""
        stats = await notification_job(bot=None)

        expected_stats = {
            "users_notified": 0,
            "notifications_sent": 0,
            "notifications_skipped": 0,
            "errors": 0,
        }

        assert stats == expected_stats


@pytest.mark.asyncio
class TestNotificationRepository:
    """Tests del repositorio de notificaciones."""

    @pytest.fixture
    async def repo(self, db_session):
        """Repositorio para tests."""
        return NotificationRepository(db_session)

    async def test_was_notified_false_initially(self, repo):
        """Test que inicialmente no hay notificaciones registradas."""
        was_notified = await repo.was_notified(user_id=1, event_id=1)
        assert was_notified is False

    async def test_log_and_check_notification(self, repo):
        """Test registrar y verificar notificación."""
        # Registrar notificación
        log = await repo.log_notification(
            user_id=1,
            event_id=1,
            message_hash="test_hash_123"
        )

        assert log.user_id == 1
        assert log.event_id == 1
        assert log.message_hash == "test_hash_123"

        # Verificar que se registra como notificada
        was_notified = await repo.was_notified(user_id=1, event_id=1)
        assert was_notified is True

        # Pero no para otro evento
        was_notified_other = await repo.was_notified(user_id=1, event_id=2)
        assert was_notified_other is False

    async def test_get_by_user_empty_initially(self, repo):
        """Test que inicialmente no hay notificaciones para un usuario."""
        notifications = await repo.get_by_user(user_id=1)
        assert len(notifications) == 0

    async def test_get_by_user_with_notifications(self, repo):
        """Test obtener notificaciones de un usuario."""
        # Crear varias notificaciones
        await repo.log_notification(1, 1, "hash1")
        await repo.log_notification(1, 2, "hash2")
        await repo.log_notification(2, 1, "hash3")  # Otro usuario

        # Obtener notificaciones del usuario 1
        notifications = await repo.get_by_user(user_id=1)

        assert len(notifications) == 2
        event_ids = {n.event_id for n in notifications}
        assert event_ids == {1, 2}

    async def test_count_sent_today_initially_zero(self, repo):
        """Test que inicialmente no hay notificaciones enviadas hoy."""
        count = await repo.count_sent_today()
        assert count == 0

    async def test_cleanup_old_notifications(self, repo):
        """Test limpieza de notificaciones antiguas."""
        from datetime import datetime, timedelta

        # Crear notificación antigua (simular cambiando la fecha)
        old_log = await repo.create(
            user_id=1,
            event_id=1,
            message_hash="old_hash",
            sent_at=datetime.now() - timedelta(days=40)  # Más de 30 días
        )

        # Crear notificación reciente
        recent_log = await repo.create(
            user_id=1,
            event_id=2,
            message_hash="recent_hash",
            sent_at=datetime.now()  # Hoy
        )

        # Ejecutar limpieza (30 días por defecto)
        deleted_count = await repo.cleanup_old(days=30)

        # Debería eliminar la notificación antigua
        assert deleted_count == 1

        # Verificar que solo queda la reciente
        remaining = await repo.get_by_user(user_id=1)
        assert len(remaining) == 1
        assert remaining[0].event_id == 2


@pytest.mark.asyncio
class TestSubscriptionRepository:
    """Tests del repositorio de suscripciones."""

    @pytest.fixture
    async def repo(self, db_session):
        """Repositorio para tests."""
        return SubscriptionRepository(db_session)

    @pytest.fixture
    async def user(self, db_session):
        """Usuario de prueba."""
        from src.database.repositories.user import UserRepository
        user_repo = UserRepository(db_session)
        return await user_repo.create(telegram_id=123456789)

    async def test_get_users_for_event_no_subscriptions(self, repo):
        """Test que inicialmente no hay usuarios suscritos."""
        users = await repo.get_users_for_event("100m", "M")
        assert len(users) == 0

    async def test_subscribe_and_get_users(self, repo, user):
        """Test suscribir usuario y obtener lista de suscritos."""
        # Suscribir usuario
        subscription, is_new = await repo.subscribe(
            user_id=user.id,
            discipline="100m",
            sex="M"
        )

        assert is_new is True
        assert subscription.discipline == "100m"
        assert subscription.sex == "M"

        # Verificar que aparece en la lista
        users = await repo.get_users_for_event("100m", "M")
        assert len(users) == 1
        assert users[0] == user.id

    async def test_subscribe_duplicate_no_new(self, repo, user):
        """Test que suscribir duplicado no crea nueva suscripción."""
        # Primera suscripción
        sub1, is_new1 = await repo.subscribe(user.id, "100m", "M")
        assert is_new1 is True

        # Segunda suscripción igual
        sub2, is_new2 = await repo.subscribe(user.id, "100m", "M")
        assert is_new2 is False

        # Debería ser la misma suscripción
        assert sub1.id == sub2.id

    async def test_get_users_for_event_case_insensitive(self, repo, user):
        """Test que la búsqueda de disciplina es case insensitive."""
        await repo.subscribe(user.id, "100m", "M")

        # Buscar con diferente case
        users = await repo.get_users_for_event("100M", "m")
        assert len(users) == 1

        users = await repo.get_users_for_event("100m", "M")
        assert len(users) == 1

    async def test_get_by_user(self, repo, user):
        """Test obtener suscripciones de un usuario."""
        # Crear varias suscripciones
        await repo.subscribe(user.id, "100m", "M")
        await repo.subscribe(user.id, "200m", "F")
        await repo.subscribe(user.id, "pértiga", "M")

        subscriptions = await repo.get_by_user(user.id)

        assert len(subscriptions) == 3
        disciplines = {s.discipline for s in subscriptions}
        assert disciplines == {"100m", "200m", "pértiga"}

    async def test_unsubscribe(self, repo, user):
        """Test eliminar suscripción específica."""
        await repo.subscribe(user.id, "100m", "M")
        await repo.subscribe(user.id, "200m", "F")

        # Eliminar una suscripción
        deleted = await repo.unsubscribe(user.id, "100m", "M")
        assert deleted is True

        # Verificar que ya no está
        users = await repo.get_users_for_event("100m", "M")
        assert len(users) == 0

        # Pero la otra sigue
        users = await repo.get_users_for_event("200m", "F")
        assert len(users) == 1

    async def test_unsubscribe_all(self, repo, user):
        """Test eliminar todas las suscripciones de un usuario."""
        await repo.subscribe(user.id, "100m", "M")
        await repo.subscribe(user.id, "200m", "F")
        await repo.subscribe(user.id, "pértiga", "M")

        # Eliminar todas
        deleted_count = await repo.unsubscribe_all(user.id)
        assert deleted_count == 3

        # Verificar que no quedan
        subscriptions = await repo.get_by_user(user.id)
        assert len(subscriptions) == 0