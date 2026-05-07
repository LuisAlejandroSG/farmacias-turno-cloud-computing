#!/bin/bash

# ============ INSTALACIÓN INSTANCIA 1: API + BD ============
# Este script debe ejecutarse en la instancia EC2 que alojará la API y BD

set -e

echo "================================"
echo "  INSTALACIÓN FARMACIAS API"
echo "================================"
echo ""

# Actualizar sistema
echo "📦 Actualizando sistema..."
sudo apt-get update
sudo apt-get upgrade -y

# Instalar Docker
echo "🐳 Instalando Docker..."
sudo apt-get install -y docker.io docker-compose
sudo usermod -aG docker $USER
sudo systemctl start docker
sudo systemctl enable docker

# Instalar Nginx (se usará también localmente)
echo "🌐 Instalando Nginx..."
sudo apt-get install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Instalar herramientas útiles
echo "🛠️ Instalando herramientas..."
sudo apt-get install -y curl wget net-tools postgresql-client git

# Crear directorio del proyecto
echo "📁 Creando estructura de directorios..."
mkdir -p ~/farmacias-turnos/{api,database,nginx}
cd ~/farmacias-turnos

# Crear archivos Docker Compose (el usuario debe copiar los archivos)
echo "⚙️ Configurando Docker..."

# Crear red Docker
docker network create farmacias_network 2>/dev/null || true

# Comenzar servicios
echo "🚀 Iniciando servicios con Docker Compose..."
cd ~/farmacias-turnos

# Esperar confirmación del usuario
echo ""
echo "⚠️ IMPORTANTE:"
echo "1. Copia los archivos del proyecto a ~/farmacias-turnos/"
echo "2. Ejecuta: docker-compose up -d"
echo ""
echo "Para verificar que está todo funcionando:"
echo "  curl http://localhost/health"
echo "  curl http://localhost/api/farmacias"
echo ""
echo "Documentación interactiva en: http://IP_INSTANCIA/docs"
echo ""

# Configurar permisos
echo "🔐 Configurando permisos..."
chmod +x ~/farmacias-turnos/database/*.sql 2>/dev/null || true

echo "✅ Instalación completada"
echo ""
echo "Próximos pasos:"
echo "1. Copiar archivos a ~/farmacias-turnos/"
echo "2. docker-compose up -d"
echo "3. Verificar logs: docker-compose logs -f"
