#!/bin/bash
# AXIOM Database Migration Status Script
# This script shows the current status of database migrations
# Ethics & Safety: No imprimas credenciales ni variables sensibles. Uso local de desarrollo.
# Seguridad: valida herramientas y usa timeouts para evitar bloqueos.

set -euo pipefail

echo "AXIOM Database Migration Status"
echo "==============================="

cd .
if [ -f .venv/bin/activate ]; then
	# shellcheck disable=SC1091
	source .venv/bin/activate
fi

if ! command -v alembic >/dev/null 2>&1; then
	echo "ERROR: alembic no está instalado en el entorno actual."
	exit 1
fi

echo "Current migration:"
timeout 10s alembic current || true
echo ""

echo "Migration history:"
timeout 10s alembic history || true
echo ""

echo "Migration heads:"
timeout 10s alembic heads || true
