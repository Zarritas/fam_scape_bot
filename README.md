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
# Desarrollo local
python -m src.main
```

## 📋 Comandos del Bot

### Usuario
- `/start` - Iniciar bot y registrarse
- `/buscar` - Buscar pruebas
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

## 🚀 Despliegue

### Configuración del VPS (IONOS)

1. **Preparar el servidor:**
   ```bash
   # Conectarse al VPS
   ssh root@tu-servidor-ionos

   # Actualizar sistema
   apt update && apt upgrade -y

   # Instalar Python 3.11 y git
   apt install -y software-properties-common git
   add-apt-repository -y ppa:deadsnakes/ppa
   apt install -y python3.11 python3.11-venv python3.11-pip

   # Crear directorio del proyecto
   mkdir -p /opt/atletismo-bot
   cd /opt/atletismo-bot
   ```

2. **Configurar SSH Key:**
   ```bash
   # En tu máquina local, generar clave SSH
   ssh-keygen -t rsa -b 4096 -C "tu-email@ejemplo.com"

   # Copiar clave pública al servidor
   ssh-copy-id root@tu-servidor-ionos

   # O manualmente agregar al authorized_keys del servidor
   cat ~/.ssh/id_rsa.pub  # Copiar esta línea
   # Pegar en /root/.ssh/authorized_keys en el servidor

   # CODIFICAR la clave privada para GitHub Secrets (IMPORTANTE)
   cat ~/.ssh/id_rsa | base64 -w 0
   # Copia la salida completa y pégala en el secret VPS_SSH_KEY
   ```

3. **Secrets de GitHub (para CI/CD):**
   En tu repositorio de GitHub, configura estos secrets:
   - `TELEGRAM_BOT_TOKEN`: Token de tu bot de Telegram
   - `ADMIN_USER_ID`: Tu ID de Telegram como administrador
   - `VPS_HOST`: IP o dominio de tu servidor IONOS
   - `VPS_USER`: Usuario SSH (normalmente `root`)
   - `VPS_SSH_KEY`: Contenido de tu clave privada SSH (`cat ~/.ssh/id_rsa`)

### Despliegue Automático

Los pushes a la rama `production` activarán automáticamente el despliegue:
1. Clonación del código desde GitHub
2. Instalación de dependencias Python
3. Configuración del archivo `.env`
4. Configuración del servicio systemd
5. Reinicio del bot

### Producción
El despliegue se maneja automáticamente via GitHub Actions ejecutando directamente en el servidor.

### Monitoreo
```bash
# Ver estado del servicio
systemctl status atletismo-bot

# Ver logs del servicio
journalctl -u atletismo-bot -f

# Reiniciar el servicio
systemctl restart atletismo-bot

# Ver logs recientes
journalctl -u atletismo-bot -n 50 --no-pager

# Ver uso de recursos
top -p $(pgrep -f "python -m src.main")
```

### Producción
El despliegue se maneja automáticamente via GitHub Actions usando `docker-compose.prod.yml`.

### Monitoreo
```bash
# Ver logs del contenedor
docker logs atletismo-bot

# Ver estado de contenedores
docker ps

# Reiniciar servicios
docker compose restart

# Ver uso de recursos
docker stats atletismo-bot
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
