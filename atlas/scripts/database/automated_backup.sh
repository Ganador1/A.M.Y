#!/bin/bash

# AXIOM Database Automated Backup Script - ROADMAP 6 Implementation
# Automated backup system for PostgreSQL database with retention management

set -e  # Exit on any error

# Configuration
BACKUP_DIR="/var/backups/axiom"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="axiom_meta4"
RETENTION_DAYS=7

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Create backup directory if it doesn't exist
create_backup_dir() {
    if [ ! -d "$BACKUP_DIR" ]; then
        log "Creating backup directory: $BACKUP_DIR"
        sudo mkdir -p "$BACKUP_DIR"
        sudo chown $(whoami):$(whoami) "$BACKUP_DIR"
    fi
}

# Verify database connection
verify_db_connection() {
    log "Verifying database connection..."
    if ! pg_isready -d "$DB_NAME" > /dev/null 2>&1; then
        error "Cannot connect to database: $DB_NAME"
        exit 1
    fi
    log "Database connection verified"
}

# Create full backup
create_full_backup() {
    local backup_file="$BACKUP_DIR/full_${DATE}.sql.gz"

    log "Creating full database backup: $backup_file"

    # Create the backup with compression
    if pg_dump "$DB_NAME" | gzip > "$backup_file"; then
        local size=$(du -h "$backup_file" | cut -f1)
        log "✅ Full backup completed successfully: $backup_file (${size})"
        return 0
    else
        error "Failed to create full backup"
        return 1
    fi
}

# Create schema-only backup (for migrations)
create_schema_backup() {
    local backup_file="$BACKUP_DIR/schema_${DATE}.sql"

    log "Creating schema-only backup: $backup_file"

    # Create schema-only backup
    if pg_dump "$DB_NAME" --schema-only > "$backup_file"; then
        local size=$(du -h "$backup_file" | cut -f1)
        log "✅ Schema backup completed successfully: $backup_file (${size})"
        return 0
    else
        error "Failed to create schema backup"
        return 1
    fi
}

# Cleanup old backups
cleanup_old_backups() {
    log "Cleaning up backups older than $RETENTION_DAYS days..."

    local deleted_count=0

    # Clean full backups
    while IFS= read -r -d '' file; do
        if [ -f "$file" ]; then
            log "Removing old backup: $(basename "$file")"
            rm "$file"
            ((deleted_count++))
        fi
    done < <(find "$BACKUP_DIR" -name "full_*.sql.gz" -mtime +$RETENTION_DAYS -print0)

    # Clean schema backups (keep only last 3)
    local schema_files=($(find "$BACKUP_DIR" -name "schema_*.sql" -mtime +$RETENTION_DAYS | sort))
    if [ ${#schema_files[@]} -gt 3 ]; then
        local to_delete=$((${#schema_files[@]} - 3))
        for ((i=0; i<to_delete; i++)); do
            log "Removing old schema backup: $(basename "${schema_files[i]}")"
            rm "${schema_files[i]}"
            ((deleted_count++))
        done
    fi

    log "✅ Cleanup completed: $deleted_count files removed"
}

# Verify backup integrity
verify_backup() {
    local backup_file="$1"

    log "Verifying backup integrity: $backup_file"

    if [[ "$backup_file" == *.gz ]]; then
        # Test gzip integrity
        if ! gunzip -t "$backup_file" 2>/dev/null; then
            error "Backup file is corrupted: $backup_file"
            return 1
        fi
    fi

    log "✅ Backup verification passed"
    return 0
}

# Upload to remote storage (placeholder for cloud backup)
upload_backup() {
    local backup_file="$1"

    # Placeholder for cloud upload (AWS S3, Google Cloud, etc.)
    # Uncomment and configure based on your cloud provider

    # Example for AWS S3:
    # aws s3 cp "$backup_file" "s3://axiom-backups/$(basename "$backup_file")"

    # Example for Google Cloud Storage:
    # gsutil cp "$backup_file" "gs://axiom-backups/$(basename "$backup_file")"

    warn "Remote upload not configured - backup stored locally only"
}

# Main backup process
main() {
    log "🚀 Starting AXIOM database backup process..."

    # Pre-flight checks
    create_backup_dir
    verify_db_connection

    local backup_success=true

    # Create full backup
    if ! create_full_backup; then
        backup_success=false
    fi

    # Create schema backup
    if ! create_schema_backup; then
        backup_success=false
    fi

    # Verify latest backup
    local latest_backup="$BACKUP_DIR/full_${DATE}.sql.gz"
    if [ -f "$latest_backup" ]; then
        if ! verify_backup "$latest_backup"; then
            backup_success=false
        fi
    fi

    # Cleanup old backups
    cleanup_old_backups

    # Upload to remote storage (if configured)
    if [ -f "$latest_backup" ] && [ "$backup_success" = true ]; then
        upload_backup "$latest_backup"
    fi

    # Final status
    if [ "$backup_success" = true ]; then
        log "🎉 Database backup process completed successfully!"
        return 0
    else
        error "❌ Database backup process failed!"
        return 1
    fi
}

# Handle script interruption
trap 'error "Backup interrupted by user"; exit 1' INT TERM

# Run main function
main "$@"
