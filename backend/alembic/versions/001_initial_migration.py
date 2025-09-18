"""Initial migration with all tables

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import pgvector

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Create data_source table
    op.create_table('data_source',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('type', sa.String(length=50), nullable=False),
    sa.Column('url', sa.String(length=1000), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_data_source_id'), 'data_source', ['id'], unique=False)
    
    # Create organization table
    op.create_table('organization',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('ticker', sa.String(length=20), nullable=True),
    sa.Column('sector', sa.String(length=100), nullable=True),
    sa.Column('country', sa.String(length=100), nullable=True),
    sa.Column('website', sa.String(length=500), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_organization_id'), 'organization', ['id'], unique=False)
    
    # Create kpi_definition table
    op.create_table('kpi_definition',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('code', sa.String(length=50), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('unit', sa.String(length=50), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('category', sa.String(length=100), nullable=True),
    sa.Column('framework_tags', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('is_higher_better', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_kpi_definition_id'), 'kpi_definition', ['id'], unique=False)
    
    # Create peer_group table
    op.create_table('peer_group',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('criteria', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_peer_group_id'), 'peer_group', ['id'], unique=False)
    
    # Create user table
    op.create_table('user',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('roles', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('provider', sa.String(length=50), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_user_id'), 'user', ['id'], unique=False)
    
    # Create ingestion_job table
    op.create_table('ingestion_job',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('kind', sa.String(length=50), nullable=False),
    sa.Column('params', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=True),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('logs', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ingestion_job_id'), 'ingestion_job', ['id'], unique=False)
    
    # Create report table
    op.create_table('report',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('organization_id', sa.BigInteger(), nullable=False),
    sa.Column('source_id', sa.BigInteger(), nullable=True),
    sa.Column('title', sa.String(length=500), nullable=False),
    sa.Column('year', sa.Integer(), nullable=False),
    sa.Column('period_start', sa.DateTime(), nullable=True),
    sa.Column('period_end', sa.DateTime(), nullable=True),
    sa.Column('file_path', sa.String(length=1000), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=True),
    sa.Column('checksum', sa.String(length=64), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
    sa.ForeignKeyConstraint(['source_id'], ['data_source.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_report_id'), 'report', ['id'], unique=False)
    
    # Create benchmark_snapshot table
    op.create_table('benchmark_snapshot',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('peer_group_id', sa.BigInteger(), nullable=False),
    sa.Column('kpi_id', sa.BigInteger(), nullable=False),
    sa.Column('period', sa.String(length=20), nullable=False),
    sa.Column('stats', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['kpi_id'], ['kpi_definition.id'], ),
    sa.ForeignKeyConstraint(['peer_group_id'], ['peer_group.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_benchmark_snapshot_id'), 'benchmark_snapshot', ['id'], unique=False)
    
    # Create audit_log table
    op.create_table('audit_log',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('actor_user_id', sa.BigInteger(), nullable=True),
    sa.Column('action', sa.String(length=100), nullable=False),
    sa.Column('entity_type', sa.String(length=50), nullable=False),
    sa.Column('entity_id', sa.BigInteger(), nullable=True),
    sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['actor_user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_log_id'), 'audit_log', ['id'], unique=False)
    
    # Create kpi_value table
    op.create_table('kpi_value',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('organization_id', sa.BigInteger(), nullable=False),
    sa.Column('kpi_id', sa.BigInteger(), nullable=False),
    sa.Column('report_id', sa.BigInteger(), nullable=True),
    sa.Column('year', sa.Integer(), nullable=False),
    sa.Column('value_numeric', sa.Float(), nullable=True),
    sa.Column('unit', sa.String(length=50), nullable=True),
    sa.Column('normalized_to_base_unit', sa.Float(), nullable=True),
    sa.Column('confidence', sa.Float(), nullable=True),
    sa.Column('extraction_method', sa.String(length=50), nullable=True),
    sa.Column('evidence_span', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['kpi_id'], ['kpi_definition.id'], ),
    sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
    sa.ForeignKeyConstraint(['report_id'], ['report.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_kpi_values', 'kpi_value', ['organization_id', 'kpi_id', 'year'], unique=False)
    op.create_index(op.f('ix_kpi_value_id'), 'kpi_value', ['id'], unique=False)
    
    # Create recommendation table
    op.create_table('recommendation',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('organization_id', sa.BigInteger(), nullable=False),
    sa.Column('kpi_id', sa.BigInteger(), nullable=True),
    sa.Column('title', sa.String(length=500), nullable=False),
    sa.Column('rationale', sa.Text(), nullable=True),
    sa.Column('actions', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('confidence', sa.Float(), nullable=True),
    sa.Column('sources', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['kpi_id'], ['kpi_definition.id'], ),
    sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recommendation_id'), 'recommendation', ['id'], unique=False)
    
    # Create embedding table
    op.create_table('embedding',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('report_id', sa.BigInteger(), nullable=True),
    sa.Column('kpi_definition_id', sa.BigInteger(), nullable=True),
    sa.Column('chunk_text', sa.Text(), nullable=False),
    sa.Column('vector', pgvector.sqlalchemy.Vector(dim=1536), nullable=False),
    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['kpi_definition_id'], ['kpi_definition.id'], ),
    sa.ForeignKeyConstraint(['report_id'], ['report.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_embedding_vector', 'embedding', ['vector'], unique=False, postgresql_using='ivfflat', postgresql_with={'lists': 64}, postgresql_ops={'vector': 'vector_cosine_ops'})
    op.create_index(op.f('ix_embedding_id'), 'embedding', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_embedding_id'), table_name='embedding')
    op.drop_index('idx_embedding_vector', table_name='embedding')
    op.drop_table('embedding')
    op.drop_index(op.f('ix_recommendation_id'), table_name='recommendation')
    op.drop_table('recommendation')
    op.drop_index(op.f('ix_kpi_value_id'), table_name='kpi_value')
    op.drop_index('idx_kpi_values', table_name='kpi_value')
    op.drop_table('kpi_value')
    op.drop_index(op.f('ix_audit_log_id'), table_name='audit_log')
    op.drop_table('audit_log')
    op.drop_index(op.f('ix_benchmark_snapshot_id'), table_name='benchmark_snapshot')
    op.drop_table('benchmark_snapshot')
    op.drop_index(op.f('ix_report_id'), table_name='report')
    op.drop_table('report')
    op.drop_index(op.f('ix_ingestion_job_id'), table_name='ingestion_job')
    op.drop_table('ingestion_job')
    op.drop_index(op.f('ix_user_id'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_peer_group_id'), table_name='peer_group')
    op.drop_table('peer_group')
    op.drop_index(op.f('ix_kpi_definition_id'), table_name='kpi_definition')
    op.drop_table('kpi_definition')
    op.drop_index(op.f('ix_organization_id'), table_name='organization')
    op.drop_table('organization')
    op.drop_index(op.f('ix_data_source_id'), table_name='data_source')
    op.drop_table('data_source')
    op.execute('DROP EXTENSION IF EXISTS vector')
