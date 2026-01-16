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

   # Ejecutar script de configuración automática
   curl -fsSL https://raw.githubusercontent.com/tu-usuario/bot-telegram/production/scripts/setup-vps.sh | bash

   # O manualmente:
   # Instalar Docker y Docker Compose
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   apt-get install -y docker-compose-plugin

    # Crear directorio del proyecto
    mkdir -p /opt/atletismo-bot
    cd /opt/atletismo-bot
    ```

    **Nota:** El archivo `.env` se crea automáticamente durante el despliegue desde las secrets de GitHub. No necesitas crearlo manualmente.

2. **Configurar variables de entorno:**
   Editar `.env` en el servidor con tus credenciales reales.

3. **Configurar Docker Hub:**
   - Crea una cuenta en [Docker Hub](https://hub.docker.com/)
   - Ve a Account Settings → Security → New Access Token
   - Crea un token con permisos de read/write

4. **Configurar SSH Key:**
   ```bash
   # En tu máquina local, generar clave SSH
   ssh-keygen -t rsa -b 4096 -C "tu-email@ejemplo.com"

   # Copiar clave pública al servidor
   ssh-copy-id root@tu-servidor-ionos

   # O manualmente agregar al authorized_keys del servidor
   cat ~/.ssh/id_rsa.pub  # Copiar esta línea
   # Pegar en /root/.ssh/authorized_keys en el servidor
   ```

5. **Secrets de GitHub (para CI/CD):**
   En tu repositorio de GitHub, configura estos secrets:
   - `DOCKERHUB_USERNAME`: Tu usuario de Docker Hub
   - `DOCKERHUB_TOKEN`: Token de acceso de Docker Hub
   - `TELEGRAM_BOT_TOKEN`: Token de tu bot de Telegram
   - `ADMIN_USER_ID`: Tu ID de Telegram como administrador
   - `VPS_HOST`: IP o dominio de tu servidor IONOS
   - `VPS_USER`: Usuario SSH (normalmente `root`)
   - `VPS_SSH_KEY`: Contenido de tu clave privada SSH (`cat ~/.ssh/id_rsa`)

### Despliegue Automático

Los pushes a la rama `production` activarán automáticamente el despliegue:
1. Construcción de imagen Docker
2. Push a Docker Hub
3. Despliegue en el VPS via SSH

## 🐳 Docker

### Desarrollo Local
```bash
# Construir imagen
docker build -f docker/Dockerfile -t atletismo-bot .

# Ejecutar con docker-compose
docker-compose -f docker/docker-compose.yml up -d
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
