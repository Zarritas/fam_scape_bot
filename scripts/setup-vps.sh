#!/bin/bash
# Script de configuración inicial para el VPS de IONOS
# Ejecutar como root en el servidor

set -e

echo "🚀 Configurando servidor para Bot de Atletismo..."

# Actualizar sistema
echo "📦 Actualizando sistema..."
apt update && apt upgrade -y

# Instalar Python 3.11 si no está instalado
if ! command -v python3.11 &> /dev/null; then
    echo "📦 Instalando Python 3.11..."
    apt install -y software-properties-common
    add-apt-repository -y ppa:deadsnakes/ppa
    apt install -y python3.11 python3.11-venv python3.11-pip
fi

# Instalar git si no está instalado
if ! command -v git &> /dev/null; then
    echo "📦 Instalando git..."
    apt install -y git
fi

# Crear directorio del proyecto
echo "📁 Creando directorio del proyecto..."
mkdir -p /opt/atletismo-bot
cd /opt/atletismo-bot

# Crear directorio para datos
mkdir -p data

# Crear archivo .env básico (se sobrescribirá en el despliegue)
if [ ! -f .env ]; then
    echo "📝 Creando archivo .env básico..."
    cat > .env << EOF
# Configuración del bot (se sobrescribirá automáticamente en el despliegue)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
ADMIN_USER_ID=your_admin_telegram_id_here

# Base de datos
DATABASE_URL=sqlite+aiosqlite:///./data/bot.db

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=text
EOF
    echo "⚠️  NOTA: Este archivo .env se sobrescribirá automáticamente durante el despliegue"
fi

echo "✅ Configuración inicial completada!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Configura los secrets en GitHub Actions"
echo "2. Haz push a la rama 'production' para desplegar automáticamente"
echo ""
echo "🔍 Para verificar: python3.11 --version && git --version"