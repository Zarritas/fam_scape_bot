# 🤖 Bot de Telegram - Competiciones de Atletismo FAM

Bot de Telegram que informa automáticamente sobre las competiciones de atletismo de la Federación de Atletismo de Madrid (FAM).

## 📋 Funcionalidades

### 🔔 **Notificaciones Automáticas** ✨
- **ACTIVADO**: Recibe alertas automáticas diarias a las 10:00
- Notificaciones del día siguiente con tus pruebas suscritas
- Mensajes personalizados agrupados por competición
- Evita notificaciones duplicadas inteligentemente

### 🔍 **Búsqueda Interactiva**
- Comando `/buscar` para buscar competiciones por criterios
- Filtros por: método de búsqueda, fecha, tipo de prueba, disciplina, sexo
- Resultados paginados con navegación intuitiva

### 📅 **Calendario de Competiciones**
- Comando `/proximas` para ver próximas competiciones
- Información completa: fecha, lugar, tipo de competición
- Enlaces directos a PDFs de convocatoria

### 👑 **Funciones de Administrador**
- `/status` - Estado del sistema y estadísticas
- `/force_scrape` - Ejecutar scraping manual
- `/last_errors` - Ver últimos errores del sistema

### ⚙️ **Sistema Automático**
- **Scraping diario** a las 09:00 - obtiene nuevas competiciones del sitio FAM
- **Limpieza automática** - elimina competiciones pasadas para mantener BD limpia
- **Deduplicación inteligente** - evita duplicados pero permite múltiples competiciones del mismo PDF

## 🚀 Instalación y Despliegue

### **Requisitos**
- Python 3.11+
- PostgreSQL o SQLite
- Token de Bot de Telegram (de @BotFather)

### **Desarrollo Local**
```bash
# Instalar dependencias
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# Ejecutar
python -m src.main
```

### **Despliegue en VPS**
```bash
# 1. Preparar servidor
curl -fsSL https://raw.githubusercontent.com/tu-usuario/bot-telegram/main/scripts/setup-vps.sh | bash

# 2. Configurar secrets en GitHub Actions
# - TELEGRAM_BOT_TOKEN
# - ADMIN_USER_ID
# - VPS_HOST, VPS_USER, VPS_SSH_KEY

# 3. Push a rama production
git checkout -b production
git push origin production
```

## 📖 Uso del Bot

### **Primeros Pasos**
1. **Inicia el bot**: Envía `/start`
2. **Regístrate**: El bot te registra automáticamente
3. **Configura notificaciones**: Usa `/buscar` para encontrar pruebas de interés

### **Comandos Disponibles**

#### **Usuario Normal**
```
/start - Iniciar bot y registrarse
/ayuda - Ver ayuda completa
/buscar - Buscar competiciones interactivamente
/proximas - Ver próximas competiciones
```

#### **Administrador**
```
/status - Estado del sistema
/force_scrape - Ejecutar scraping manual
/last_errors - Ver últimos errores
```

### **Flujo de Búsqueda**
1. `/buscar` → Seleccionar método
2. Elegir fecha/tipo/disciplina/sexo
3. Ver resultados paginados
4. Suscribirse a notificaciones automáticas

## 🏗️ Arquitectura del Sistema

### **Componentes Principales**

```
src/
├── bot/              # Handlers de comandos de Telegram
│   ├── handlers/     # Lógica de cada comando
│   └── keyboards/    # Teclados inline para navegación
├── database/         # Capa de datos
│   ├── models/       # Definición de tablas
│   ├── repositories/ # Lógica de acceso a datos
│   └── engine.py     # Configuración de BD
├── scraper/          # Extracción de datos del sitio FAM
│   ├── web_scraper.py    # Scraping del calendario HTML
│   └── pdf_parser.py     # Parsing de PDFs de convocatoria
├── scheduler/        # Tareas programadas
│   ├── jobs.py       # Lógica de scraping y notificaciones
│   └── runner.py     # Configuración del scheduler
└── notifications/    # Sistema de notificaciones
    └── service.py    # Envío de mensajes a usuarios
```

### **Base de Datos**

#### **Tablas Principales**
- **users** - Usuarios registrados
- **competitions** - Competiciones scrapeadas
- **events** - Pruebas individuales dentro de competiciones
- **subscriptions** - Suscripciones de usuarios a disciplinas
- **notification_logs** - Historial de notificaciones enviadas

#### **Relaciones**
```
User 1:N Subscription
Competition 1:N Event
User 1:N NotificationLog
Event 1:N NotificationLog
```

### **Flujo de Datos**

1. **Scraping** (09:00): Sitio FAM → BD
2. **Notificaciones** (10:00): BD → Telegram
3. **Interacción usuario**: Telegram → BD → Respuesta

## 🔧 Configuración

### **Variables de Entorno**
```bash
# Bot de Telegram
TELEGRAM_BOT_TOKEN=tu_token_aqui
ADMIN_USER_ID=tu_id_telegram

# Base de datos
DATABASE_URL=sqlite+aiosqlite:///./data/bot.db

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=text

# Scheduler
SCRAPE_HOUR=9
SCRAPE_MINUTE=0
NOTIFY_HOUR=10
NOTIFY_MINUTE=0
```

### **Configuración FAM**
```python
# En src/config.py
FAM_BASE_URL = "https://www.atletismomadrid.org"
FAM_CALENDAR_PATH = "/calendario-de-competiciones"
TIMEZONE = "Europe/Madrid"
```

## 📊 Monitoreo y Mantenimiento

### **Comandos de Monitoreo**
```bash
# Ver logs del bot
journalctl -u atletismo-bot -f

# Ver estado del servicio
systemctl status atletismo-bot

# Reiniciar servicio
systemctl restart atletismo-bot
```

### **Estadísticas del Sistema**
- Competiciones activas
- Usuarios registrados
- Notificaciones enviadas
- Errores del sistema

### **Limpieza Automática**
- **Diaria**: Eliminación de competiciones pasadas
- **Deduplicación**: Evita competiciones duplicadas
- **Optimización**: Mantiene BD limpia y eficiente

## 🐛 Solución de Problemas

### **Problemas Comunes**

#### **Bot no responde**
```bash
# Verificar estado
systemctl status atletismo-bot

# Ver logs recientes
journalctl -u atletismo-bot -n 50
```

#### **Scraping falla**
```bash
# Ejecutar manualmente
python -c "from src.scheduler.jobs import scraping_job; import asyncio; asyncio.run(scraping_job())"
```

#### **Notificaciones no llegan**
- Verificar token del bot
- Comprobar permisos de administrador
- Revisar logs de errores

### **Debugging**
```bash
# Ejecutar con debug
LOG_LEVEL=DEBUG python -m src.main

# Verificar conectividad FAM
curl -I https://www.atletismomadrid.org/calendario-de-competiciones
```

## 🤝 Contribución

### **Desarrollo**
```bash
# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt

# Ejecutar tests
pytest tests/ -v

# Formatear código
ruff format src/
ruff check src/ --fix

# Type checking
mypy src/
```

### **Estructura de Commits**
```
feat: nueva funcionalidad
fix: corrección de bug
docs: cambios en documentación
style: formateo y linting
refactor: refactorización de código
test: agregar o modificar tests
```

## 📄 Licencia

MIT License - ver archivo LICENSE para detalles.

---

**Desarrollado con ❤️ para la comunidad de atletismo de Madrid**