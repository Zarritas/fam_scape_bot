"""
Templates de mensajes HTML para Telegram.

Todos los mensajes están en español.
"""

# Mensaje de bienvenida
WELCOME_MESSAGE = """
<b>🏃 ¡Bienvenido al Bot de Atletismo Madrid!</b>

Este bot te notificará sobre las competiciones de la Federación de Atletismo de Madrid.

<b>¿Cómo funciona?</b>
1. Suscríbete a las pruebas que te interesan
2. Cada día a las 10:00 recibirás notificaciones de nuevas competiciones
3. Solo recibirás información de tus pruebas suscritas

<b>Comandos disponibles:</b>
/suscribir - Suscribirse a una prueba
/desuscribir - Cancelar una suscripción
/mis_pruebas - Ver tus suscripciones actuales
/proximas - Ver próximas competiciones
/revisar - Ver competiciones de tus pruebas
/ayuda - Ver esta ayuda

¡Empieza usando /suscribir para elegir tus pruebas!
"""

# Mensaje de ayuda
HELP_MESSAGE = """
<b>📖 Ayuda - Bot de Atletismo Madrid</b>

<b>Comandos de usuario:</b>
• /start - Iniciar el bot
• /suscribir - Suscribirse a pruebas
• /desuscribir - Cancelar suscripciones
• /mis_pruebas - Ver tus suscripciones
• /proximas - Ver próximas competiciones
• /revisar - Ver competiciones de tus pruebas
• /ayuda - Mostrar este mensaje

<b>¿Cómo funcionan las suscripciones?</b>
Puedes suscribirte a pruebas específicas como "400m Masculino" o "Pértiga Femenino". 
Cada día a las 10:00 recibirás un mensaje con las nuevas competiciones que incluyan tus pruebas.

<b>¿Tienes problemas?</b>
Si algo no funciona correctamente, espera unos minutos y vuelve a intentarlo.
"""

# Plantilla para lista de suscripciones
SUBSCRIPTIONS_LIST = """
<b>📋 Tus suscripciones actuales:</b>

{subscriptions}

<i>Usa /desuscribir para cancelar alguna suscripción</i>
"""

# Sin suscripciones
NO_SUBSCRIPTIONS = """
<b>📭 No tienes suscripciones activas</b>

Usa /suscribir para elegir las pruebas que te interesan.
"""

# Plantilla para próximas competiciones
UPCOMING_COMPETITIONS = """
<b>📅 Próximas competiciones:</b>

{competitions}
"""

# Sin competiciones próximas
NO_UPCOMING = """
<b>📅 No hay competiciones próximas programadas</b>

Vuelve a consultar más adelante.
"""

# Suscripción exitosa
SUBSCRIPTION_SUCCESS = """
✅ <b>¡Suscripción exitosa!</b>

Te has suscrito a: <b>{discipline} {sex}</b>

Recibirás notificaciones cuando haya nuevas competiciones con esta prueba.
"""

# Ya suscrito
ALREADY_SUBSCRIBED = """
ℹ️ Ya estás suscrito a <b>{discipline} {sex}</b>

Usa /mis_pruebas para ver todas tus suscripciones.
"""

# Desuscripción exitosa
UNSUBSCRIPTION_SUCCESS = """
✅ Te has desuscrito de <b>{discipline} {sex}</b>
"""

# No suscrito
NOT_SUBSCRIBED = """
ℹ️ No estabas suscrito a <b>{discipline} {sex}</b>
"""

# Error genérico para usuarios
GENERIC_ERROR = """
🔧 Ha ocurrido un error inesperado.

Por favor, inténtalo de nuevo en unos minutos.
"""

# Admin: Status del sistema
ADMIN_STATUS = """
<b>📊 Estado del Sistema</b>

<b>Scheduler:</b> {scheduler_status}

<b>Últimos jobs:</b>
• Último scraping: {last_scrape}
• Última notificación: {last_notify}

<b>Estadísticas:</b>
• Usuarios activos: {users_count}
• Competiciones futuras: {competitions_count}
• Errores (24h): {errors_count}

<b>Próximas ejecuciones:</b>
{next_jobs}
"""

# Admin: Error log
ADMIN_ERROR_LOG = """
<b>🚨 Últimos errores del sistema</b>

{errors}
"""

# Admin: Force scrape
ADMIN_FORCE_SCRAPE_START = """
⏳ Iniciando scraping manual...

Te notificaré cuando termine.
"""

ADMIN_FORCE_SCRAPE_RESULT = """
✅ <b>Scraping completado</b>

<b>Resultados:</b>
• Meses procesados: {months_scraped}
• Competiciones encontradas: {competitions_found}
• Nuevas/actualizadas: {competitions_new}
• Errores: {errors}
"""
