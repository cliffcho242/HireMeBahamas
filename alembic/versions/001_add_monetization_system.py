"""Add monetization system tables

Revision ID: 001_monetization
Revises: 
Create Date: 2025-12-18 00:41:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_monetization'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create subscription_tier enum
    subscription_tier = postgresql.ENUM('free', 'basic', 'professional', 'business', 'enterprise', name='subscriptiontier')
    subscription_tier.create(op.get_bind(), checkfirst=True)
    
    # Create subscriptions table
    op.create_table('subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('tier', subscription_tier, nullable=False),
        sa.Column('price_paid', sa.Float(), nullable=True),
        sa.Column('starts_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('auto_renew', sa.Boolean(), nullable=True),
        sa.Column('payment_provider', sa.String(length=50), nullable=True),
        sa.Column('payment_provider_subscription_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_subscriptions_user_id'), 'subscriptions', ['user_id'], unique=True)

    # Create job_posting_packages table
    op.create_table('job_posting_packages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('package_name', sa.String(length=100), nullable=False),
        sa.Column('credits_purchased', sa.Integer(), nullable=False),
        sa.Column('credits_remaining', sa.Integer(), nullable=False),
        sa.Column('price_paid', sa.Float(), nullable=False),
        sa.Column('purchased_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('payment_provider', sa.String(length=50), nullable=True),
        sa.Column('payment_provider_transaction_id', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_job_posting_packages_user_id'), 'job_posting_packages', ['user_id'], unique=False)

    # Create boosted_posts table
    op.create_table('boosted_posts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('post_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('boost_type', sa.String(length=50), nullable=False),
        sa.Column('price_paid', sa.Float(), nullable=False),
        sa.Column('impressions_target', sa.Integer(), nullable=True),
        sa.Column('impressions_actual', sa.Integer(), nullable=True),
        sa.Column('starts_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('payment_provider', sa.String(length=50), nullable=True),
        sa.Column('payment_provider_transaction_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_boosted_posts_post_id'), 'boosted_posts', ['post_id'], unique=False)
    op.create_index(op.f('ix_boosted_posts_user_id'), 'boosted_posts', ['user_id'], unique=False)

    # Create advertisements table
    op.create_table('advertisements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.Column('link_url', sa.String(length=500), nullable=False),
        sa.Column('ad_type', sa.String(length=50), nullable=False),
        sa.Column('targeting_location', sa.String(length=200), nullable=True),
        sa.Column('targeting_category', sa.String(length=100), nullable=True),
        sa.Column('budget_total', sa.Float(), nullable=False),
        sa.Column('budget_spent', sa.Float(), nullable=True),
        sa.Column('cost_per_click', sa.Float(), nullable=True),
        sa.Column('cost_per_impression', sa.Float(), nullable=True),
        sa.Column('impressions', sa.Integer(), nullable=True),
        sa.Column('clicks', sa.Integer(), nullable=True),
        sa.Column('starts_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_approved', sa.Boolean(), nullable=True),
        sa.Column('payment_provider', sa.String(length=50), nullable=True),
        sa.Column('payment_provider_transaction_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_advertisements_user_id'), 'advertisements', ['user_id'], unique=False)

    # Create enterprise_accounts table
    op.create_table('enterprise_accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('company_name', sa.String(length=200), nullable=False),
        sa.Column('contract_value', sa.Float(), nullable=False),
        sa.Column('starts_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('max_job_posts', sa.Integer(), nullable=True),
        sa.Column('max_users', sa.Integer(), nullable=True),
        sa.Column('dedicated_support', sa.Boolean(), nullable=True),
        sa.Column('custom_branding', sa.Boolean(), nullable=True),
        sa.Column('api_access', sa.Boolean(), nullable=True),
        sa.Column('analytics_access', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('account_manager', sa.String(length=200), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_enterprise_accounts_user_id'), 'enterprise_accounts', ['user_id'], unique=True)


def downgrade():
    # Drop tables
    op.drop_index(op.f('ix_enterprise_accounts_user_id'), table_name='enterprise_accounts')
    op.drop_table('enterprise_accounts')
    
    op.drop_index(op.f('ix_advertisements_user_id'), table_name='advertisements')
    op.drop_table('advertisements')
    
    op.drop_index(op.f('ix_boosted_posts_user_id'), table_name='boosted_posts')
    op.drop_index(op.f('ix_boosted_posts_post_id'), table_name='boosted_posts')
    op.drop_table('boosted_posts')
    
    op.drop_index(op.f('ix_job_posting_packages_user_id'), table_name='job_posting_packages')
    op.drop_table('job_posting_packages')
    
    op.drop_index(op.f('ix_subscriptions_user_id'), table_name='subscriptions')
    op.drop_table('subscriptions')
    
    # Drop enum
    sa.Enum(name='subscriptiontier').drop(op.get_bind(), checkfirst=True)
