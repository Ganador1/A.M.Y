#!/bin/bash

# AXIOM Database Backup Configuration Script - ROADMAP 6 Implementation
# Sets up automated backup scheduling and configuration

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

# Configuration variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_SCRIPT="$SCRIPT_DIR/automated_backup.sh"
CRON_JOB="0 2 * * * $BACKUP_SCRIPT"  # Daily at 2 AM
CRON_FILE="axiom_backup_cron"

# Check if running as root (needed for some operations)
check_permissions() {
    if [ "$EUID" -eq 0 ]; then
        warn "Running as root - be careful with permissions"
    fi
}

# Install PostgreSQL client tools if needed
install_postgresql_client() {
    if ! command -v psql &> /dev/null; then
        info "PostgreSQL client not found. Installing..."

        # Detect OS and install accordingly
        if command -v apt-get &> /dev/null; then
            # Debian/Ubuntu
            sudo apt-get update
            sudo apt-get install -y postgresql-client
        elif command -v yum &> /dev/null; then
            # RHEL/CentOS
            sudo yum install -y postgresql
        elif command -v brew &> /dev/null; then
            # macOS
            brew install postgresql
        else
            warn "Could not detect package manager. Please install PostgreSQL client manually."
            return 1
        fi
    fi

    log "✅ PostgreSQL client installed/verified"
}

# Setup backup directory with proper permissions
setup_backup_directory() {
    local backup_dir="/var/backups/axiom"

    info "Setting up backup directory..."

    if [ ! -d "$backup_dir" ]; then
        info "Creating backup directory: $backup_dir"
        sudo mkdir -p "$backup_dir"
    fi

    # Set proper ownership (adjust user as needed)
    sudo chown $(whoami):$(whoami) "$backup_dir"

    # Set secure permissions
    chmod 700 "$backup_dir"

    log "✅ Backup directory configured: $backup_dir"
}

# Setup cron job for automated backups
setup_cron_job() {
    info "Setting up automated backup cron job..."

    # Check if cron job already exists
    if crontab -l 2>/dev/null | grep -q "$BACKUP_SCRIPT"; then
        warn "Cron job already exists for backup script"
        read -p "Do you want to update it? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            info "Keeping existing cron job"
            return 0
        fi
    fi

    # Create temporary cron file
    crontab -l 2>/dev/null > "$CRON_FILE" || echo "# AXIOM backup cron jobs" > "$CRON_FILE"

    # Remove existing backup cron job if present
    grep -v "$BACKUP_SCRIPT" "$CRON_FILE" > "${CRON_FILE}.tmp" 2>/dev/null || true
    mv "${CRON_FILE}.tmp" "$CRON_FILE"

    # Add new cron job
    echo "$CRON_JOB" >> "$CRON_FILE"

    # Install new crontab
    if crontab "$CRON_FILE"; then
        log "✅ Automated backup scheduled: Daily at 2:00 AM"
        info "You can modify the schedule by editing the cron job above"
    else
        error "Failed to install crontab"
        return 1
    fi

    # Clean up
    rm -f "$CRON_FILE"
}

# Create log rotation for backup logs
setup_log_rotation() {
    local log_file="/var/log/axiom_backup.log"

    info "Setting up log rotation..."

    # Create log directory if needed
    sudo mkdir -p /var/log

    # Create logrotate configuration
    local logrotate_conf="/etc/logrotate.d/axiom-backup"

    if [ ! -f "$logrotate_conf" ]; then
        cat > "$logrotate_conf" << EOF
$log_file {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 $(whoami) $(whoami)
    postrotate
        # Signal to backup script to reopen log file
        kill -HUP \$(cat /var/run/axiom_backup.pid 2>/dev/null) 2>/dev/null || true
    endscript
}
EOF
        log "✅ Log rotation configured: $logrotate_conf"
    else
        info "Log rotation already configured"
    fi
}

# Test backup configuration
test_backup_config() {
    info "Testing backup configuration..."

    # Test if backup script exists and is executable
    if [ ! -x "$BACKUP_SCRIPT" ]; then
        error "Backup script not found or not executable: $BACKUP_SCRIPT"
        return 1
    fi

    # Test database connection
    if ! command -v pg_isready &> /dev/null; then
        warn "pg_isready command not found - install PostgreSQL client tools"
        return 1
    fi

    if ! pg_isready > /dev/null 2>&1; then
        warn "Cannot connect to PostgreSQL server - check connection"
        return 1
    fi

    log "✅ Backup configuration test passed"
}

# Display configuration summary
show_summary() {
    echo
    echo "📋 AXIOM Database Backup Configuration Summary"
    echo "=" * 50
    echo "Backup Script: $BACKUP_SCRIPT"
    echo "Backup Directory: /var/backups/axiom"
    echo "Schedule: Daily at 2:00 AM"
    echo "Retention: 7 days for full backups, 3 latest for schema"
    echo "Log File: /var/log/axiom_backup.log"
    echo "Log Rotation: Daily with 30 days retention"
    echo
    echo "💡 Next Steps:"
    echo "1. Verify database connection and permissions"
    echo "2. Test manual backup: $BACKUP_SCRIPT"
    echo "3. Monitor logs: tail -f /var/log/axiom_backup.log"
    echo "4. Test restore procedure with a test database"
}

# Main setup process
main() {
    log "🚀 Setting up AXIOM automated database backup system..."

    check_permissions
    install_postgresql_client
    setup_backup_directory
    setup_cron_job
    setup_log_rotation
    test_backup_config
    show_summary

    log "🎉 Automated backup system setup completed!"
    info "Your database will be backed up automatically every day at 2:00 AM"
}

# Run main function
main "$@"
