# 🗄️ AXIOM Database Backup & Recovery Strategy - ROADMAP 6

## Overview

This document outlines the comprehensive database backup and recovery strategy implemented as part of ROADMAP 6: Database Integrity & Migrations.

## 🎯 Objectives

- **Automated Backups**: Daily automated backups with retention management
- **Quick Recovery**: Fast and reliable database restoration procedures
- **Data Safety**: Multiple backup types and verification mechanisms
- **Monitoring**: Health checks and alerting for backup operations

## 📁 Backup Structure

```
scripts/database/
├── automated_backup.sh      # Main backup script
├── restore_backup.sh        # Database restoration script
├── setup_backup_config.sh   # Configuration and setup script
└── README.md               # This documentation
```

## 🚀 Quick Start

### 1. Setup Automated Backups

```bash
# Run the setup script (requires sudo for some operations)
./scripts/database/setup_backup_config.sh
```

This will:
- Install PostgreSQL client tools if needed
- Create backup directory (`/var/backups/axiom`)
- Setup daily cron job (2:00 AM)
- Configure log rotation

### 2. Manual Backup

```bash
# Create immediate backup
./scripts/database/automated_backup.sh
```

### 3. Restore Database

```bash
# Restore from backup file
./scripts/database/restore_backup.sh /var/backups/axiom/full_20231201_120000.sql.gz

# Restore to specific database
./scripts/database/restore_backup.sh backup.sql.gz --database my_restored_db

# Only verify backup integrity
./scripts/database/restore_backup.sh backup.sql.gz --verify-only
```

## 🔧 Configuration

### Backup Types

1. **Full Backups** (`full_YYYYMMDD_HHMMSS.sql.gz`)
   - Complete database dump with compression
   - Retention: 7 days
   - Stored in: `/var/backups/axiom/`

2. **Schema Backups** (`schema_YYYYMMDD_HHMMSS.sql`)
   - Schema-only dumps for migration tracking
   - Retention: 3 latest backups
   - Useful for troubleshooting schema issues

### Scheduling

- **Frequency**: Daily at 2:00 AM
- **Retention**: 7 days for full backups, 3 for schema
- **Log Rotation**: Daily with 30-day retention

### Security

- Backup directory: `chmod 700` (owner only)
- Log files: `chmod 644` (readable by owner and group)
- Cron jobs run as the user who set them up

## 📊 Monitoring

### Health Checks

The backup system includes verification steps:

```bash
# Check backup integrity
gunzip -t /var/backups/axiom/full_20231201_120000.sql.gz

# Test database connectivity
pg_isready -d axiom_meta4

# Monitor backup logs
tail -f /var/log/axiom_backup.log
```

### Database Health Integration

The backup system integrates with the database health checker:

```bash
# Check database health via API
curl http://localhost:8000/health/database | jq '.backup_status'
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Permission Denied

```bash
# Fix backup directory permissions
sudo chown $(whoami):$(whoami) /var/backups/axiom
chmod 700 /var/backups/axiom
```

#### 2. PostgreSQL Connection Failed

```bash
# Check PostgreSQL service
sudo systemctl status postgresql

# Verify connection
pg_isready -d axiom_meta4
```

#### 3. Disk Space Issues

```bash
# Check available space
df -h /var/backups

# Clean old backups manually
find /var/backups/axiom -name "*.sql.gz" -mtime +14 -delete
```

#### 4. Cron Job Not Running

```bash
# Check cron service
sudo systemctl status cron

# Verify cron job exists
crontab -l | grep axiom

# Check cron logs
sudo tail -f /var/log/cron.log
```

### Emergency Procedures

#### Quick Recovery

```bash
# 1. Identify latest backup
ls -la /var/backups/axiom/ | grep full | tail -1

# 2. Restore to temporary database
./scripts/database/restore_backup.sh latest_backup.sql.gz --database emergency_restore

# 3. Verify data integrity
psql emergency_restore -c "SELECT COUNT(*) FROM users;"

# 4. Switch production database if needed
```

#### Point-in-Time Recovery (if using WAL archiving)

```bash
# Restore to specific point in time
psql -c "SELECT pg_stop_backup();" target_db
# Follow PostgreSQL PITR documentation
```

## 📈 Best Practices

### Regular Testing

1. **Monthly Restore Test**: Restore to a test database monthly
2. **Backup Verification**: Test backup integrity after creation
3. **Space Monitoring**: Monitor disk usage for backup directory

### Performance Optimization

1. **Backup Window**: Schedule during low-traffic periods
2. **Compression**: Use gzip compression (default)
3. **Parallel Jobs**: Consider pg_dump parallel options for large databases

### Security Considerations

1. **Encryption**: Consider encrypting backups for sensitive data
2. **Off-site Storage**: Copy backups to remote storage
3. **Access Control**: Limit backup script access to authorized users

## 🔗 Integration Points

### Application Integration

The backup system integrates with:

- **Database Health Checks**: `/health/database` endpoint
- **Monitoring Systems**: Log aggregation and alerting
- **Deployment Pipelines**: Pre-deployment backup verification

### Cloud Integration

For production deployments, consider:

```bash
# AWS S3 Integration
aws s3 cp /var/backups/axiom/*.sql.gz s3://axiom-backups/

# Google Cloud Storage
gsutil cp /var/backups/axiom/*.sql.gz gs://axiom-backups/

# Azure Blob Storage
az storage blob upload-batch \
  --destination axiom-backups \
  --source /var/backups/axiom/
```

## 📞 Support

For issues or questions:

1. Check logs: `/var/log/axiom_backup.log`
2. Verify configuration: `./scripts/database/setup_backup_config.sh`
3. Test manually: `./scripts/database/automated_backup.sh`
4. Community support: GitHub Issues

## 🔄 Maintenance

### Regular Tasks

- **Weekly**: Verify backup integrity and available space
- **Monthly**: Test restore procedures
- **Quarterly**: Review and update retention policies
- **Annually**: Audit backup strategy effectiveness

### Updates

When updating the backup system:

1. Test new scripts in staging environment
2. Verify cron jobs after updates
3. Update documentation for any new features
4. Communicate changes to operations team

---

*This backup strategy ensures data safety and quick recovery capabilities for the AXIOM Mathematics AI Engine.*
