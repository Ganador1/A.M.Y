"""Add workflows v1.1 tables

Revision ID: 0b1c2d3e4f56
Revises: f905ab334d30
Create Date: 2025-09-02 10:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0b1c2d3e4f56'
down_revision: Union[str, Sequence[str], None] = 'f905ab334d30'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: add workflows and related tables."""
    op.create_table(
        'workflows',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('workflow_id', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workflows_id'), 'workflows', ['id'], unique=False)
    op.create_index(op.f('ix_workflows_workflow_id'), 'workflows', ['workflow_id'], unique=True)
    op.create_index(op.f('ix_workflows_status'), 'workflows', ['status'], unique=False)

    op.create_table(
        'workflow_steps',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('workflow_id', sa.Integer(), nullable=False),
        sa.Column('step_id', sa.String(length=64), nullable=False),
        sa.Column('service_type', sa.String(length=64), nullable=False),
        sa.Column('operation', sa.String(length=128), nullable=False),
        sa.Column('parameters', sa.JSON(), nullable=True),
        sa.Column('dependencies', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('result', sa.JSON(), nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('execution_time', sa.Float(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['workflow_id'], ['workflows.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workflow_steps_id'), 'workflow_steps', ['id'], unique=False)
    op.create_index(op.f('ix_workflow_steps_workflow_id'), 'workflow_steps', ['workflow_id'], unique=False)
    op.create_index(op.f('ix_workflow_steps_status'), 'workflow_steps', ['status'], unique=False)

    op.create_table(
        'workflow_step_executions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('workflow_step_id', sa.Integer(), nullable=False),
        sa.Column('attempt', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_sec', sa.Float(), nullable=True),
        sa.Column('cache_hit', sa.Boolean(), nullable=True),
        sa.Column('timeout_sec', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['workflow_step_id'], ['workflow_steps.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workflow_step_executions_id'), 'workflow_step_executions', ['id'], unique=False)
    op.create_index(op.f('ix_workflow_step_executions_workflow_step_id'), 'workflow_step_executions', ['workflow_step_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema: drop workflows and related tables."""
    op.drop_index(op.f('ix_workflow_step_executions_workflow_step_id'), table_name='workflow_step_executions')
    op.drop_index(op.f('ix_workflow_step_executions_id'), table_name='workflow_step_executions')
    op.drop_table('workflow_step_executions')

    op.drop_index(op.f('ix_workflow_steps_status'), table_name='workflow_steps')
    op.drop_index(op.f('ix_workflow_steps_workflow_id'), table_name='workflow_steps')
    op.drop_index(op.f('ix_workflow_steps_id'), table_name='workflow_steps')
    op.drop_table('workflow_steps')

    op.drop_index(op.f('ix_workflows_status'), table_name='workflows')
    op.drop_index(op.f('ix_workflows_workflow_id'), table_name='workflows')
    op.drop_index(op.f('ix_workflows_id'), table_name='workflows')
    op.drop_table('workflows')
