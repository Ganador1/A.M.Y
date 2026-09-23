#!/bin/bash

echo "🔍 Database Schema Audit"
echo "======================="

# 1. Count migrations
MIGRATIONS=$(ls alembic/versions/*.py 2>/dev/null | wc -l)
echo "Migrations: $MIGRATIONS"

# 2. Count model files
MODELS=$(find app/models -name "*.py" -type f | wc -l)
echo "Model files: $MODELS"

# 3. Extract table names from models
echo -e "\nTables in models:"
grep -r "class.*Base\|__tablename__" app/models --include="*.py" | grep -v "BaseModel" | wc -l

# 4. Generate current migration (dry-run)
echo -e "\n📝 Generating autogenerate preview..."
alembic revision --autogenerate -m "schema_audit_dryrun" --sql > schema_diff.sql

echo -e "\n✅ Check schema_diff.sql for changes"
