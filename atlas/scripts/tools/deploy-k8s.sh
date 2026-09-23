#!/bin/bash

# AXIOM META 4 - Kubernetes Deployment Script
# ===========================================
# Script para desplegar AXIOM en Kubernetes

set -e

echo "🚀 AXIOM META 4 - Despliegue en Kubernetes"
echo "=========================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes coloreados
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar si kubectl está instalado
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl no está instalado. Por favor instala kubectl primero."
    exit 1
fi

# Verificar conexión a cluster
if ! kubectl cluster-info &> /dev/null; then
    print_error "No se puede conectar al cluster de Kubernetes."
    print_error "Asegúrate de que kubectl esté configurado correctamente."
    exit 1
fi

print_status "Conexión al cluster verificada"

# Crear namespace
print_status "Creando namespace axiom-system..."
kubectl apply -f kubernetes/namespace.yml

# Esperar a que el namespace esté listo
kubectl wait --for=condition=Ready --timeout=60s namespace/axiom-system || true

# Aplicar ConfigMaps y Secrets
print_status "Aplicando configuraciones..."
kubectl apply -f kubernetes/configmap.yml
kubectl apply -f kubernetes/secret.yml

# Desplegar PostgreSQL
print_status "Desplegando PostgreSQL..."
kubectl apply -f kubernetes/postgres.yml

print_status "Esperando que PostgreSQL esté listo..."
kubectl wait --for=condition=available --timeout=300s deployment/axiom-postgres -n axiom-system

# Desplegar Redis
print_status "Desplegando Redis..."
kubectl apply -f kubernetes/redis.yml

print_status "Esperando que Redis esté listo..."
kubectl wait --for=condition=available --timeout=120s deployment/axiom-redis -n axiom-system

# Construir y desplegar imagen de AXIOM
print_status "Construyendo imagen de AXIOM..."
if command -v docker &> /dev/null; then
    docker build -t axiom-api:latest .
    print_success "Imagen construida exitosamente"
else
    print_warning "Docker no está disponible. Asegúrate de que la imagen axiom-api:latest esté disponible en el registry."
fi

# Desplegar AXIOM API
print_status "Desplegando AXIOM API..."
kubectl apply -f kubernetes/api.yml

print_status "Esperando que AXIOM API esté listo..."
kubectl wait --for=condition=available --timeout=300s deployment/axiom-api -n axiom-system

# Configurar Ingress
print_status "Configurando Ingress..."
kubectl apply -f kubernetes/ingress.yml

# Verificar estado de los deployments
print_status "Verificando estado de los deployments..."
kubectl get deployments -n axiom-system
kubectl get pods -n axiom-system
kubectl get services -n axiom-system

# Mostrar información de acceso
print_success "Despliegue completado!"
echo ""
echo "📊 Información del despliegue:"
echo "=============================="
echo "Namespace: axiom-system"
echo "API Service: axiom-api"
echo "Database: axiom-postgres"
echo "Cache: axiom-redis"
echo ""
echo "🔗 URLs de acceso:"
echo "=================="
echo "API: http://axiom.yourdomain.com"
echo "Health Check: http://axiom.yourdomain.com/health"
echo "Documentation: http://axiom.yourdomain.com/docs"
echo ""
echo "📈 Monitoreo:"
echo "=============="
echo "Pods: kubectl get pods -n axiom-system"
echo "Logs API: kubectl logs -f deployment/axiom-api -n axiom-system"
echo "Logs DB: kubectl logs -f deployment/axiom-postgres -n axiom-system"
echo ""
echo "🔧 Comandos útiles:"
echo "==================="
echo "Escalar API: kubectl scale deployment axiom-api --replicas=5 -n axiom-system"
echo "Ver HPA: kubectl get hpa -n axiom-system"
echo "Ver eventos: kubectl get events -n axiom-system"
echo ""
print_success "AXIOM META 4 desplegado exitosamente en Kubernetes!"
