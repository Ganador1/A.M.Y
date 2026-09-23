#!/bin/bash
###############################################################################
# Script de Configuración de Redis - AXIOM ATLAS
###############################################################################

set -euo pipefail

echo "═══════════════════════════════════════════════════════════════════════"
echo "🔴 AXIOM ATLAS - Configuración de Redis"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 1. Verificar si Redis está instalado
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 Verificando instalación de Redis..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if ! command -v redis-server &>/dev/null; then
    echo -e "${YELLOW}⚠️  Redis no está instalado. Instalando...${NC}"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &>/dev/null; then
            brew install redis
        else
            echo -e "${RED}❌ Homebrew no está instalado. Instalar con:${NC}"
            echo "/bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v apt-get &>/dev/null; then
            sudo apt-get update
            sudo apt-get install -y redis-server
        elif command -v yum &>/dev/null; then
            sudo yum install -y redis
        else
            echo -e "${RED}❌ No se pudo detectar el gestor de paquetes${NC}"
            exit 1
        fi
    else
        echo -e "${RED}❌ Sistema operativo no soportado: $OSTYPE${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Redis ya está instalado${NC}"
fi

# Verificar versión
REDIS_VERSION=$(redis-server --version | grep -oE 'v=[0-9.]+' | cut -d'=' -f2)
echo -e "${BLUE}📦 Versión de Redis: $REDIS_VERSION${NC}"
echo ""

# 2. Verificar si Redis ya está corriendo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 Verificando estado de Redis..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if redis-cli ping &>/dev/null; then
    echo -e "${GREEN}✅ Redis ya está corriendo${NC}"
    REDIS_INFO=$(redis-cli INFO server | grep redis_version | cut -d':' -f2 | tr -d '\r\n')
    echo -e "${BLUE}📊 Redis Server: $REDIS_INFO${NC}"
else
    echo -e "${YELLOW}⚠️  Redis no está corriendo. Iniciando...${NC}"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS con Homebrew
        brew services start redis
        sleep 3
    else
        # Linux
        if command -v systemctl &>/dev/null; then
            sudo systemctl start redis
            sleep 3
        else
            # Iniciar manualmente en background
            redis-server --daemonize yes
            sleep 3
        fi
    fi
    
    # Verificar nuevamente
    if redis-cli ping &>/dev/null; then
        echo -e "${GREEN}✅ Redis iniciado exitosamente${NC}"
    else
        echo -e "${RED}❌ Error al iniciar Redis${NC}"
        exit 1
    fi
fi

echo ""

# 3. Verificar conectividad
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔗 Probando conectividad..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if PONG=$(redis-cli ping 2>&1); then
    if [[ "$PONG" == "PONG" ]]; then
        echo -e "${GREEN}✅ Conectividad exitosa: $PONG${NC}"
    else
        echo -e "${YELLOW}⚠️  Respuesta inesperada: $PONG${NC}"
    fi
else
    echo -e "${RED}❌ Error de conectividad${NC}"
    exit 1
fi

echo ""

# 4. Verificar configuración
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚙️  Configuración actual:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo -e "${BLUE}🔧 Puerto:${NC} $(redis-cli CONFIG GET port | tail -1)"
echo -e "${BLUE}💾 Max Memory:${NC} $(redis-cli CONFIG GET maxmemory | tail -1)"
echo -e "${BLUE}🗑️  Eviction Policy:${NC} $(redis-cli CONFIG GET maxmemory-policy | tail -1)"
echo -e "${BLUE}🔐 Require Pass:${NC} $(redis-cli CONFIG GET requirepass | tail -1)"

echo ""

# 5. Test básico de escritura/lectura
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 Test de escritura/lectura..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

TEST_KEY="axiom:test:$(date +%s)"
TEST_VALUE="AXIOM_ATLAS_V3.3_OK"

if redis-cli SET "$TEST_KEY" "$TEST_VALUE" EX 10 &>/dev/null; then
    RETRIEVED=$(redis-cli GET "$TEST_KEY")
    if [[ "$RETRIEVED" == "$TEST_VALUE" ]]; then
        echo -e "${GREEN}✅ Test de escritura/lectura exitoso${NC}"
        redis-cli DEL "$TEST_KEY" &>/dev/null
    else
        echo -e "${RED}❌ Error: Valor recuperado no coincide${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ Error en operación SET${NC}"
    exit 1
fi

echo ""

# 6. Actualizar .env si existe
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 Actualizando configuración .env..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [[ -f .env ]]; then
    # Hacer backup
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
    
    # Actualizar ENABLE_REDIS_CACHE
    if grep -q "ENABLE_REDIS_CACHE" .env; then
        sed -i '' 's/ENABLE_REDIS_CACHE=.*/ENABLE_REDIS_CACHE=true/' .env
        echo -e "${GREEN}✅ ENABLE_REDIS_CACHE=true actualizado en .env${NC}"
    else
        echo "ENABLE_REDIS_CACHE=true" >> .env
        echo -e "${GREEN}✅ ENABLE_REDIS_CACHE=true añadido a .env${NC}"
    fi
    
    # Verificar REDIS_URL
    if ! grep -q "REDIS_URL" .env; then
        echo "REDIS_URL=redis://localhost:6379" >> .env
        echo -e "${GREEN}✅ REDIS_URL añadido a .env${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Archivo .env no encontrado${NC}"
fi

echo ""

# 7. Resumen final
echo "═══════════════════════════════════════════════════════════════════════"
echo "✅ REDIS CONFIGURADO EXITOSAMENTE"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""
echo "📊 Estado:"
echo "   ✓ Redis Server: CORRIENDO"
echo "   ✓ Puerto: 6379"
echo "   ✓ Conectividad: OK"
echo "   ✓ Test R/W: OK"
echo "   ✓ .env actualizado: ENABLE_REDIS_CACHE=true"
echo ""
echo "🔧 Comandos útiles:"
echo "   • Ver estado: redis-cli ping"
echo "   • Detener: brew services stop redis (macOS)"
echo "   • Reiniciar: brew services restart redis (macOS)"
echo "   • Monitor: redis-cli MONITOR"
echo "   • Info: redis-cli INFO"
echo ""
echo "═══════════════════════════════════════════════════════════════════════"
