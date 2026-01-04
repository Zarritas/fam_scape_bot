# Bot de Atletismo Madrid

Bot de Telegram para notificar sobre competiciones de la Federación de Atletismo de Madrid.

## 🚀 Inicio Rápido

### Requisitos
- Python 3.11+
- Token de bot de Telegram (de @BotFather)

### Instalación

```bash
# Clonar repositorio
git clone <repo-url>
cd bot-telegram

# Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tu token y configuración
```

### Variables de Entorno

| Variable | Descripción | Requerida |
|----------|-------------|-----------|
| `TELEGRAM_BOT_TOKEN` | Token del bot de Telegram | ✅ |
| `ADMIN_USER_ID` | ID de Telegram del administrador | ✅ |
| `DATABASE_URL` | URL de la base de datos | ❌ (SQLite por defecto) |
| `LOG_LEVEL` | Nivel de logging | ❌ (INFO) |

### Ejecutar

```bash
# Desarrollo
python -m src.main

# Con Docker
docker-compose up -d
```

## 📋 Comandos del Bot

### Usuario
- `/start` - Iniciar bot y registrarse
- `/suscribir` - Suscribirse a pruebas
- `/desuscribir` - Cancelar suscripciones
- `/mis_pruebas` - Ver suscripciones actuales
- `/proximas` - Ver próximas competiciones
- `/ayuda` - Mostrar ayuda

### Administrador
- `/status` - Estado del sistema
- `/force_scrape` - Ejecutar scraping manual
- `/last_errors` - Ver últimos errores

## 🔄 Jobs Automáticos

| Hora | Job | Descripción |
|------|-----|-------------|
| 09:00 | Scraping | Descarga y procesa competiciones |
| 10:00 | Notificaciones | Envía alertas a usuarios suscritos |

## 🧪 Tests

```bash
# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt

# Ejecutar tests
pytest tests/ -v

# Con cobertura
pytest --cov=src --cov-report=html
```

## 🐳 Docker

```bash
# Construir imagen
docker build -f docker/Dockerfile -t atletismo-bot .

# Ejecutar con docker-compose
docker-compose -f docker/docker-compose.yml up -d
```

## 📁 Estructura del Proyecto

```
src/
├── bot/           # Handlers de Telegram
├── database/      # Modelos y repositorios
├── scheduler/     # Jobs automáticos
├── scraper/       # Scraping web y PDF
├── notifications/ # Servicio de notificaciones
├── utils/         # Utilidades
├── config.py      # Configuración
└── main.py        # Entry point
```

## 📄 Licencia

MIT
