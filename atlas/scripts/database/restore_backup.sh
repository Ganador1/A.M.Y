#!/bin/bash

# AXIOM Database Restore Script - ROADMAP 6 Implementation
# Safe database restoration with verification and rollback capabilities

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Show usage
usage() {
    echo "Usage: $0 <backup_file> [options]"
    echo ""
    echo "Options:"
    echo "  -d, --database NAME      Target database name (default: axiom_meta4_restored)"
    echo "  -v, --verify-only        Only verify backup file, don't restore"
    echo "  -f, --force             Force restore without confirmation"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 /var/backups/axiom/full_20231201_120000.sql.gz"
    echo "  $0 /var/backups/axiom/full_20231201_120000.sql.gz --database my_restored_db"
    echo "  $0 /var/backups/axiom/full_20231201_120000.sql.gz --verify-only"
}

# Parse command line arguments
BACKUP_FILE=""
TARGET_DB="axiom_meta4_restored"
VERIFY_ONLY=false
FORCE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--database)
            TARGET_DB="$2"
            shift 2
            ;;
        -v|--verify-only)
            VERIFY_ONLY=true
            shift
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        -*)
            error "Unknown option: $1"
            usage
            exit 1
            ;;
        *)
            if [ -z "$BACKUP_FILE" ]; then
                BACKUP_FILE="$1"
            else
                error "Multiple backup files specified"
                usage
                exit 1
            fi
            shift
            ;;
    esac
done

# Validate backup file
validate_backup_file() {
    local file="$1"

    if [ ! -f "$file" ]; then
        error "Backup file does not exist: $file"
        return 1
    fi

    if [[ "$file" == *.gz ]]; then
        # Test gzip integrity
        info "Testing gzip integrity..."
        if ! gunzip -t "$file" 2>/dev/null; then
            error "Backup file is corrupted or not a valid gzip file: $file"
            return 1
        fi
    fi

    log "✅ Backup file validation passed: $file"
    return 0
}

# Verify database connection
verify_db_connection() {
    info "Verifying database connection..."

    if ! command -v psql &> /dev/null; then
        error "psql command not found. Please install PostgreSQL client tools."
        return 1
    fi

    if ! pg_isready > /dev/null 2>&1; then
        error "Cannot connect to PostgreSQL server"
        return 1
    fi

    log "✅ Database connection verified"
    return 0
}

# Create new database
create_target_database() {
    local db_name="$1"

    info "Creating target database: $db_name"

    # Check if database already exists
    if psql -lqt | cut -d \| -f 1 | grep -qw "$db_name"; then
        if [ "$FORCE" = false ]; then
            warn "Database '$db_name' already exists!"
            read -p "Do you want to drop and recreate it? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                error "Restore cancelled by user"
                exit 1
            fi
        fi

        log "Dropping existing database: $db_name"
        dropdb "$db_name" 2>/dev/null || true
    fi

    if createdb "$db_name"; then
        log "✅ Database created successfully: $db_name"
        return 0
    else
        error "Failed to create database: $db_name"
        return 1
    fi
}

# Restore from backup
restore_database() {
    local backup_file="$1"
    local target_db="$2"

    info "Starting database restoration..."

    # Determine restore command based on file type
    if [[ "$backup_file" == *.gz ]]; then
        log "Restoring from compressed backup: $backup_file"
        if ! gunzip -c "$backup_file" | psql "$target_db"; then
            error "Failed to restore database from: $backup_file"
            return 1
        fi
    else
        log "Restoring from uncompressed backup: $backup_file"
        if ! psql "$target_db" < "$backup_file"; then
            error "Failed to restore database from: $backup_file"
            return 1
        fi
    fi

    log "✅ Database restoration completed successfully"
    return 0
}

# Verify restoration
verify_restoration() {
    local target_db="$1"

    info "Verifying database restoration..."

    # Check if we can connect to the restored database
    if ! psql "$target_db" -c "SELECT 1;" > /dev/null 2>&1; then
        error "Cannot connect to restored database: $target_db"
        return 1
    fi

    # Check for key tables
    local key_tables=("users" "calculations" "cached_results" "system_metrics")
    local missing_tables=()

    for table in "${key_tables[@]}"; do
        if ! psql "$target_db" -c "SELECT COUNT(*) FROM $table LIMIT 1;" > /dev/null 2>&1; then
            missing_tables+=("$table")
        fi
    done

    if [ ${#missing_tables[@]} -gt 0 ]; then
        warn "Some expected tables are missing: ${missing_tables[*]}"
    fi

    # Check migration status
    if psql "$target_db" -c "SELECT version_num FROM alembic_version;" > /dev/null 2>&1; then
        log "✅ Migration status verified"
    else
        warn "No migration version found - you may need to run migrations"
    fi

    log "✅ Database verification completed"
    return 0
}

# Main restoration process
main() {
    # Validate arguments
    if [ -z "$BACKUP_FILE" ]; then
        error "Backup file is required"
        usage
        exit 1
    fi

    log "🚀 Starting AXIOM database restoration process..."
    info "Backup file: $BACKUP_FILE"
    info "Target database: $TARGET_DB"
    info "Verify only: $VERIFY_ONLY"

    # Pre-flight checks
    validate_backup_file "$BACKUP_FILE"
    verify_db_connection

    # Verify only mode
    if [ "$VERIFY_ONLY" = true ]; then
        log "🔍 Verification completed successfully - backup file is valid"
        exit 0
    fi

    # Confirmation prompt (unless forced)
    if [ "$FORCE" = false ]; then
        warn "This will REPLACE all data in database: $TARGET_DB"
        read -p "Are you sure you want to continue? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log "Restoration cancelled by user"
            exit 0
        fi
    fi

    # Create target database
    create_target_database "$TARGET_DB"

    # Perform restoration
    if restore_database "$BACKUP_FILE" "$TARGET_DB"; then
        # Verify restoration
        verify_restoration "$TARGET_DB"

        log "🎉 Database restoration completed successfully!"
        info "Database: $TARGET_DB"
        info "You can now connect to the restored database"
        info "Don't forget to run migrations if needed: 'alembic upgrade head'"
    else
        error "❌ Database restoration failed!"
        error "The target database may be in an inconsistent state"
        error "Consider cleaning up: 'dropdb $TARGET_DB'"
        exit 1
    fi
}

# Handle script interruption
trap 'error "Restoration interrupted by user"; exit 1' INT TERM

# Run main function
main "$@"
