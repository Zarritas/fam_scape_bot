"""
Templates de mensajes HTML para Telegram.

Todos los mensajes están en español.
"""

# Mensaje de bienvenida
WELCOME_MESSAGE = """
<b>🏃 ¡Bienvenido al Bot de Atletismo Madrid!</b>

Este bot te ayuda a encontrar competiciones de la Federación de Atletismo de Madrid que incluyan tus pruebas favoritas.

<b>¿Cómo funciona?</b>
1. Usa el comando /buscar
2. Selecciona el tipo de prueba (carrera o concurso)
3. Elige la prueba específica (ej: 100m, Longitud)
4. ¡El bot te mostrará todas las competiciones futuras que incluyen esa prueba!

<b>Comandos disponibles:</b>
/buscar - Buscar competiciones por prueba
/proximas - Ver todas las próximas competiciones
/ayuda - Ver esta ayuda

¡Empieza usando /buscar para encontrar tu próxima competición!
"""

# Mensaje de ayuda
HELP_MESSAGE = """
<b>📖 Ayuda - Bot de Atletismo Madrid</b>

<b>Comandos de usuario:</b>
• /start - Iniciar el bot y ver bienvenida
• /buscar - Buscar competiciones por prueba específica
• /proximas - Ver lista general de próximas competiciones
• /ayuda - Mostrar este mensaje

<b>Búsqueda de pruebas:</b>
Usa /buscar para encontrar competiciones. Puedes buscar:
1. <b>Por Prueba:</b> Buscando disciplina específica (ej: "400m", "Pértiga")
2. <b>Por Fecha:</b> Seleccionando una fecha del calendario para ver qué pruebas hay.

<b>¿Tienes problemas?</b>
Si algo no funciona correctamente, espera unos minutos y vuelve a intentarlo.
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
