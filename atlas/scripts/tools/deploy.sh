#!/bin/bash

# Script de Despliegue AXIOM Services
# ===================================

set -e

echo "🚀 Iniciando despliegue de AXIOM Services..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Verificar dependencias
check_dependencies() {
    log "Verificando dependencias..."
    
    if ! command -v docker &> /dev/null; then
        error "Docker no está instalado"
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose no está instalado"
    fi
    
    success "Dependencias verificadas"
}

# Crear directorios necesarios
create_directories() {
    log "Creando directorios necesarios..."
    
    mkdir -p logs
    mkdir -p data
    mkdir -p models
    mkdir -p monitoring/grafana/dashboards
    mkdir -p monitoring/grafana/datasources
    mkdir -p nginx/ssl
    
    success "Directorios creados"
}

# Configurar variables de entorno
setup_environment() {
    log "Configurando variables de entorno..."
    
    if [ ! -f .env ]; then
        cat > .env << EOF
# AXIOM Environment Configuration
ENVIRONMENT=production
SECRET_KEY=$(openssl rand -hex 32)
REDIS_URL=redis://redis:6379
MONGODB_URL=mongodb://mongodb:27017/axiom
LOG_LEVEL=INFO
WORKERS=4

# Database
MONGO_INITDB_ROOT_USERNAME=axiom
MONGO_INITDB_ROOT_PASSWORD=$(openssl rand -hex 16)
MONGO_INITDB_DATABASE=axiom

# Monitoring
GRAFANA_ADMIN_PASSWORD=$(openssl rand -hex 12)
EOF
        success "Archivo .env creado"
    else
        warning "Archivo .env ya existe"
    fi
}

# Construir imágenes
build_images() {
    log "Construyendo imágenes Docker..."
    
    docker-compose build --no-cache axiom-api
    
    success "Imágenes construidas"
}

# Ejecutar pruebas
run_tests() {
    log "Ejecutando pruebas..."
    
    # Ejecutar pruebas básicas
    if python -m pytest tests/test_basic_services.py::test_service_files_exist -v; then
        success "Pruebas básicas pasaron"
    else
        warning "Algunas pruebas básicas fallaron, continuando..."
    fi
}

# Desplegar servicios
deploy_services() {
    log "Desplegando servicios..."
    
    # Detener servicios existentes
    docker-compose down
    
    # Iniciar servicios de infraestructura primero
    docker-compose up -d redis mongodb prometheus
    
    # Esperar a que estén listos
    sleep 10
    
    # Iniciar servicios principales
    docker-compose up -d axiom-api axiom-worker axiom-scheduler
    
    # Iniciar servicios de monitoreo
    docker-compose up -d grafana nginx
    
    success "Servicios desplegados"
}

# Verificar salud de servicios
health_check() {
    log "Verificando salud de servicios..."
    
    # Esperar a que los servicios estén listos
    sleep 30
    
    # Verificar API principal
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        success "API principal está funcionando"
    else
        error "API principal no responde"
    fi
    
    # Verificar Redis
    if docker-compose exec -T redis redis-cli ping | grep -q PONG; then
        success "Redis está funcionando"
    else
        warning "Redis no responde"
    fi
    
    # Verificar MongoDB
    if docker-compose exec -T mongodb mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
        success "MongoDB está funcionando"
    else
        warning "MongoDB no responde"
    fi
    
    # Verificar Prometheus
    if curl -f http://localhost:9090/-/healthy > /dev/null 2>&1; then
        success "Prometheus está funcionando"
    else
        warning "Prometheus no responde"
    fi
    
    # Verificar Grafana
    if curl -f http://localhost:3000/api/health > /dev/null 2>&1; then
        success "Grafana está funcionando"
    else
        warning "Grafana no responde"
    fi
}

# Mostrar información de despliegue
show_deployment_info() {
    log "Información de despliegue:"
    echo ""
    echo "🌐 Servicios disponibles:"
    echo "   • API Principal: http://localhost:8000"
    echo "   • Documentación: http://localhost:8000/docs"
    echo "   • Métricas: http://localhost:8000/metrics"
    echo "   • Prometheus: http://localhost:9090"
    echo "   • Grafana: http://localhost:3000"
    echo ""
    echo "📊 Monitoreo:"
    echo "   • Health Check: http://localhost:8000/health"
    echo "   • Logs: docker-compose logs -f"
    echo ""
    echo "🔧 Comandos útiles:"
    echo "   • Ver logs: docker-compose logs -f [servicio]"
    echo "   • Reiniciar: docker-compose restart [servicio]"
    echo "   • Detener: docker-compose down"
    echo "   • Actualizar: ./scripts/deploy.sh"
    echo ""
}

# Función principal
main() {
    log "🚀 Iniciando despliegue de AXIOM Services"
    
    check_dependencies
    create_directories
    setup_environment
    build_images
    run_tests
    deploy_services
    health_check
    show_deployment_info
    
    success "🎉 Despliegue completado exitosamente!"
}

# Ejecutar función principal
main "$@"