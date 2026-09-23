"""add_audit_tables

Revision ID: 03185bfdf445
Revises: f1fd628cbe31
Create Date: 2025-10-06 20:30:35.374996

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '03185bfdf445'
down_revision: Union[str, Sequence[str], None] = 'f1fd628cbe31'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create audit_events table
    op.create_table(
        'audit_events',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('category', sa.String(length=30), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('username', sa.String(length=50), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=255), nullable=True),
        sa.Column('endpoint', sa.String(length=255), nullable=True),
        sa.Column('method', sa.String(length=10), nullable=True),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=False),
        sa.Column('status_code', sa.Integer(), nullable=True),
        sa.Column('duration_ms', sa.Float(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for audit_events
    op.create_index('ix_audit_events_timestamp', 'audit_events', ['timestamp'])
    op.create_index('ix_audit_events_event_type', 'audit_events', ['event_type'])
    op.create_index('ix_audit_events_category', 'audit_events', ['category'])
    op.create_index('ix_audit_events_severity', 'audit_events', ['severity'])
    op.create_index('ix_audit_events_user_id', 'audit_events', ['user_id'])
    op.create_index('ix_audit_events_username', 'audit_events', ['username'])
    op.create_index('ix_audit_events_ip_address', 'audit_events', ['ip_address'])
    op.create_index('ix_audit_events_endpoint', 'audit_events', ['endpoint'])
    op.create_index('ix_audit_timestamp_type', 'audit_events', ['timestamp', 'event_type'])
    op.create_index('ix_audit_user_timestamp', 'audit_events', ['user_id', 'timestamp'])
    op.create_index('ix_audit_category_severity', 'audit_events', ['category', 'severity'])
    op.create_index('ix_audit_ip_timestamp', 'audit_events', ['ip_address', 'timestamp'])

    # Create security_metrics table
    op.create_table(
        'security_metrics',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('window_start', sa.DateTime(), nullable=False),
        sa.Column('window_end', sa.DateTime(), nullable=False),
        sa.Column('window_size', sa.String(length=20), nullable=False),
        sa.Column('total_logins', sa.Integer(), default=0),
        sa.Column('successful_logins', sa.Integer(), default=0),
        sa.Column('failed_logins', sa.Integer(), default=0),
        sa.Column('unique_users', sa.Integer(), default=0),
        sa.Column('permission_checks', sa.Integer(), default=0),
        sa.Column('permission_denied', sa.Integer(), default=0),
        sa.Column('tokens_created', sa.Integer(), default=0),
        sa.Column('tokens_refreshed', sa.Integer(), default=0),
        sa.Column('tokens_revoked', sa.Integer(), default=0),
        sa.Column('rate_limit_hits', sa.Integer(), default=0),
        sa.Column('rate_limit_exceeded', sa.Integer(), default=0),
        sa.Column('critical_events', sa.Integer(), default=0),
        sa.Column('error_events', sa.Integer(), default=0),
        sa.Column('warning_events', sa.Integer(), default=0),
        sa.Column('avg_response_time', sa.Float(), nullable=True),
        sa.Column('max_response_time', sa.Float(), nullable=True),
        sa.Column('metrics_data', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for security_metrics
    op.create_index('ix_security_metrics_timestamp', 'security_metrics', ['timestamp'])
    op.create_index('ix_security_metrics_window_start', 'security_metrics', ['window_start'])
    op.create_index('ix_metrics_window', 'security_metrics', ['window_start', 'window_size'])

    # Create active_alerts table
    op.create_table(
        'active_alerts',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('alert_type', sa.String(length=50), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('username', sa.String(length=50), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('trigger_count', sa.Integer(), default=1),
        sa.Column('first_seen', sa.DateTime(), nullable=False),
        sa.Column('last_seen', sa.DateTime(), nullable=False),
        sa.Column('related_events', sa.JSON(), nullable=True),
        sa.Column('evidence', sa.JSON(), nullable=True),
        sa.Column('assigned_to', sa.String(), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('risk_score', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for active_alerts
    op.create_index('ix_active_alerts_created_at', 'active_alerts', ['created_at'])
    op.create_index('ix_active_alerts_alert_type', 'active_alerts', ['alert_type'])
    op.create_index('ix_active_alerts_severity', 'active_alerts', ['severity'])
    op.create_index('ix_active_alerts_status', 'active_alerts', ['status'])
    op.create_index('ix_active_alerts_user_id', 'active_alerts', ['user_id'])
    op.create_index('ix_active_alerts_ip_address', 'active_alerts', ['ip_address'])
    op.create_index('ix_alerts_status_severity', 'active_alerts', ['status', 'severity'])
    op.create_index('ix_alerts_type_status', 'active_alerts', ['alert_type', 'status'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop active_alerts
    op.drop_index('ix_alerts_type_status', table_name='active_alerts')
    op.drop_index('ix_alerts_status_severity', table_name='active_alerts')
    op.drop_index('ix_active_alerts_ip_address', table_name='active_alerts')
    op.drop_index('ix_active_alerts_user_id', table_name='active_alerts')
    op.drop_index('ix_active_alerts_status', table_name='active_alerts')
    op.drop_index('ix_active_alerts_severity', table_name='active_alerts')
    op.drop_index('ix_active_alerts_alert_type', table_name='active_alerts')
    op.drop_index('ix_active_alerts_created_at', table_name='active_alerts')
    op.drop_table('active_alerts')

    # Drop security_metrics
    op.drop_index('ix_metrics_window', table_name='security_metrics')
    op.drop_index('ix_security_metrics_window_start', table_name='security_metrics')
    op.drop_index('ix_security_metrics_timestamp', table_name='security_metrics')
    op.drop_table('security_metrics')

    # Drop audit_events
    op.drop_index('ix_audit_ip_timestamp', table_name='audit_events')
    op.drop_index('ix_audit_category_severity', table_name='audit_events')
    op.drop_index('ix_audit_user_timestamp', table_name='audit_events')
    op.drop_index('ix_audit_timestamp_type', table_name='audit_events')
    op.drop_index('ix_audit_events_endpoint', table_name='audit_events')
    op.drop_index('ix_audit_events_ip_address', table_name='audit_events')
    op.drop_index('ix_audit_events_username', table_name='audit_events')
    op.drop_index('ix_audit_events_user_id', table_name='audit_events')
    op.drop_index('ix_audit_events_severity', table_name='audit_events')
    op.drop_index('ix_audit_events_category', table_name='audit_events')
    op.drop_index('ix_audit_events_event_type', table_name='audit_events')
    op.drop_index('ix_audit_events_timestamp', table_name='audit_events')
    op.drop_table('audit_events')
