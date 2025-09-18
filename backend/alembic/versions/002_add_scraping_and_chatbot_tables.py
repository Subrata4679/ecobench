"""Add scraping and chatbot tables

Revision ID: 002
Revises: 001
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Create regulatory_report table
    op.create_table('regulatory_report',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('organization_id', sa.BigInteger(), nullable=False),
        sa.Column('report_type', sa.String(length=100), nullable=False),
        sa.Column('filing_date', sa.DateTime(), nullable=True),
        sa.Column('period_end_date', sa.DateTime(), nullable=True),
        sa.Column('url', sa.String(length=1000), nullable=False),
        sa.Column('file_path', sa.String(length=1000), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('raw_content', sa.Text(), nullable=True),
        sa.Column('extracted_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('last_scraped', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_regulatory_reports', 'regulatory_report', ['organization_id', 'report_type', 'filing_date'], unique=False)
    op.create_index(op.f('ix_regulatory_report_id'), 'regulatory_report', ['id'], unique=False)

    # Create it_company table
    op.create_table('it_company',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('ticker', sa.String(length=20), nullable=True),
        sa.Column('exchange', sa.String(length=50), nullable=True),
        sa.Column('sector', sa.String(length=100), nullable=True),
        sa.Column('website', sa.String(length=500), nullable=True),
        sa.Column('sec_cik', sa.String(length=20), nullable=True),
        sa.Column('market_cap', sa.BigInteger(), nullable=True),
        sa.Column('employees', sa.Integer(), nullable=True),
        sa.Column('headquarters', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('scraping_enabled', sa.Boolean(), nullable=True),
        sa.Column('last_scraped', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_it_company_id'), 'it_company', ['id'], unique=False)

    # Create scraping_job table
    op.create_table('scraping_job',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('company_id', sa.BigInteger(), nullable=False),
        sa.Column('job_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('results_summary', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['it_company.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scraping_job_id'), 'scraping_job', ['id'], unique=False)

    # Create chat_session table
    op.create_table('chat_session',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('session_name', sa.String(length=255), nullable=True),
        sa.Column('context_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chat_session_id'), 'chat_session', ['id'], unique=False)

    # Create user_esg_data table
    op.create_table('user_esg_data',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('company_name', sa.String(length=255), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('scope1_emissions', sa.Float(), nullable=True),
        sa.Column('scope2_emissions', sa.Float(), nullable=True),
        sa.Column('scope3_emissions', sa.Float(), nullable=True),
        sa.Column('water_consumption', sa.Float(), nullable=True),
        sa.Column('waste_generated', sa.Float(), nullable=True),
        sa.Column('energy_consumption', sa.Float(), nullable=True),
        sa.Column('renewable_energy_percentage', sa.Float(), nullable=True),
        sa.Column('employee_count', sa.Integer(), nullable=True),
        sa.Column('revenue', sa.Float(), nullable=True),
        sa.Column('additional_metrics', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_user_esg_data', 'user_esg_data', ['user_id', 'year'], unique=False)
    op.create_index(op.f('ix_user_esg_data_id'), 'user_esg_data', ['id'], unique=False)

    # Create chat_message table
    op.create_table('chat_message',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('session_id', sa.BigInteger(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['chat_session.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chat_message_id'), 'chat_message', ['id'], unique=False)


def downgrade():
    # Drop tables in reverse order
    op.drop_index(op.f('ix_chat_message_id'), table_name='chat_message')
    op.drop_table('chat_message')
    
    op.drop_index('idx_user_esg_data', table_name='user_esg_data')
    op.drop_index(op.f('ix_user_esg_data_id'), table_name='user_esg_data')
    op.drop_table('user_esg_data')
    
    op.drop_index(op.f('ix_chat_session_id'), table_name='chat_session')
    op.drop_table('chat_session')
    
    op.drop_index(op.f('ix_scraping_job_id'), table_name='scraping_job')
    op.drop_table('scraping_job')
    
    op.drop_index(op.f('ix_it_company_id'), table_name='it_company')
    op.drop_table('it_company')
    
    op.drop_index('idx_regulatory_reports', table_name='regulatory_report')
    op.drop_index(op.f('ix_regulatory_report_id'), table_name='regulatory_report')
    op.drop_table('regulatory_report')
