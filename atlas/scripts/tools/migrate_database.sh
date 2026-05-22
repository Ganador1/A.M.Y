#!/bin/bash
# AXIOM Database Migration Script
# This script applies database migrations for the AXIOM Mathematics AI Engine
# Ethics & Safety: No imprimas credenciales ni secretos. Usa solo entornos locales de desarrollo.
# Seguridad: usa timeouts razonables y verifica herramientas antes de ejecutar.

set -euo pipefail

echo "AXIOM Database Migration Script"
echo "==============================="

# Check if PostgreSQL is running
if ! command -v pg_isready >/dev/null 2>&1; then
        echo "ERROR: pg_isready no está instalado en el PATH. Instala PostgreSQL cliente."
        exit 1
fi

if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "ERROR: PostgreSQL is not running on localhost:5432"
    echo "Please start PostgreSQL service first:"
    echo "  brew services start postgresql"
    echo "  OR"
    echo "  pg_ctl -D /usr/local/var/postgres start"
    exit 1
fi

# Check if database exists
if ! command -v psql >/dev/null 2>&1; then
        echo "ERROR: psql no está instalado en el PATH. Instala PostgreSQL cliente."
        exit 1
fi

if ! timeout 10s psql -h localhost -p 5432 -U axiom_user -d axiom_db -c "SELECT 1;" > /dev/null 2>&1; then
    echo "Creating AXIOM database..."
        if ! command -v createdb >/dev/null 2>&1; then
                echo "ERROR: createdb no está instalado en el PATH."
                exit 1
        fi
        timeout 10s createdb -h localhost -p 5432 -U axiom_user axiom_db
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create database. Please check PostgreSQL credentials."
        exit 1
    fi
fi

echo "Applying database migrations..."
cd .
if [ -f .venv/bin/activate ]; then
    # shellcheck disable=SC1091
    source .venv/bin/activate
else
    echo "WARNING: .venv no encontrado. Usando interprete del sistema."
fi

# Apply migrations
if ! command -v alembic >/dev/null 2>&1; then
    echo "ERROR: alembic no está instalado en el entorno actual."
    exit 1
fi

timeout 30s alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✅ Database migrations applied successfully!"
    echo ""
    echo "Current migration status:"
        timeout 10s alembic current || true
else
    echo "❌ Failed to apply migrations"
    exit 1
fi
