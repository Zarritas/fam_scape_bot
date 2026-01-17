"""
Templates de mensajes HTML para Telegram.

Todos los mensajes están en español.
"""

# Mensaje de bienvenida
WELCOME_MESSAGE = """
<b>🏃 ¡Bienvenido al Bot de Atletismo Madrid!</b>

Este bot te ayuda a encontrar competiciones de la Federación de Atletismo de Madrid y recibir notificaciones automáticas.

<b>¿Cómo funciona?</b>
1. Usa el comando /buscar para encontrar pruebas
2. Suscríbete a tus pruebas favoritas con ⭐
3. Recibe notificaciones diarias a las 10:00 cuando haya nuevas competiciones

<b>Comandos disponibles:</b>
/buscar - Buscar competiciones por prueba
/proximas - Ver todas las próximas competiciones
/suscripciones - Gestionar tus suscripciones
/suscribirse [prueba] [sexo] - Suscripción rápida
/ayuda - Ver esta ayuda

<b>💡 Consejos:</b>
• Busca una prueba y haz click en "⭐ Suscribirse" para activar notificaciones
• Usa /suscripciones para ver y gestionar todas tus suscripciones
• Recibirás alertas automáticas cuando se publiquen nuevas competiciones

¡Empieza usando /buscar para encontrar tus pruebas favoritas!
"""

# Mensaje de ayuda
HELP_MESSAGE = """
<b>📖 Ayuda - Bot de Atletismo Madrid</b>

<b>Comandos principales:</b>
• /start - Iniciar el bot y ver bienvenida
• /buscar - Buscar competiciones por prueba específica
• /proximas - Ver lista general de próximas competiciones
• /suscripciones - Ver y gestionar tus suscripciones activas
• /ayuda - Mostrar este mensaje

<b>Suscripciones y notificaciones:</b>
• <code>/suscribirse 400m F</code> - Suscripción directa a una prueba
• En resultados de búsqueda: click ⭐ para suscribirte
• Recibirás notificaciones automáticas diarias a las 10:00
• Usa /suscripciones para desuscribirte con ❌

<b>Búsqueda de pruebas:</b>
Usa /buscar para encontrar competiciones. Puedes buscar:
1. <b>Por Prueba:</b> Disciplina específica (ej: "400m", "Pértiga")
2. <b>Por Fecha:</b> Ver qué pruebas hay un día específico

<b>Sintaxis de suscripción:</b>
• <code>/suscribirse 100m M</code> - 100m Masculino
• <code>/suscribirse pértiga F</code> - Pértiga Femenino
• <code>/suscribirse 400m B</code> - 400m Ambos sexos

<b>¿Tienes problemas?</b>
Si algo no funciona, espera unos minutos y vuelve a intentarlo.
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

# Error genérico para usuarios
GENERIC_ERROR = """
🔧 Ha ocurrido un error inesperado.

Por favor, inténtalo de nuevo en unos minutos.
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
