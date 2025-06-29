"""remove_roles_and_permissions

Revision ID: 30a3248a3e9f
Revises: 7c4c8297b15e
Create Date: 2025-06-29 00:15:41.621611

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid


# revision identifiers, used by Alembic.
revision = '30a3248a3e9f'
down_revision = '7c4c8297b15e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create new user_tenants table
    op.create_table('user_tenants',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('assigned_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['tenant_id'], ['auth.tenants.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['auth.users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='auth'
    )
    
    # Create index on user_id and tenant_id for faster lookups
    op.create_index('ix_auth_user_tenants_user_id_tenant_id', 'user_tenants', ['user_id', 'tenant_id'], unique=True, schema='auth')
    op.create_index('ix_auth_user_tenants_tenant_id', 'user_tenants', ['tenant_id'], unique=False, schema='auth')
    op.create_index('ix_auth_user_tenants_user_id', 'user_tenants', ['user_id'], unique=False, schema='auth')
    
    # Drop tables related to roles and permissions
    # First drop user_tenant_roles as it has foreign keys to roles
    op.drop_table('user_tenant_roles', schema='auth')
    
    # Then drop role_permissions as it has foreign keys to roles and permissions
    op.drop_table('role_permissions', schema='auth')
    
    # Finally drop roles and permissions tables
    op.drop_table('roles', schema='auth')
    op.drop_table('permissions', schema='auth')


def downgrade() -> None:
    # Recreate roles and permissions tables
    op.create_table('permissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        schema='auth'
    )
    
    op.create_table('roles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        schema='auth'
    )
    
    # Create role_permissions table
    op.create_table('role_permissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('permission_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['permission_id'], ['auth.permissions.id'], ),
        sa.ForeignKeyConstraint(['role_id'], ['auth.roles.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('role_id', 'permission_id'),
        schema='auth'
    )
    
    # Create user_tenant_roles table
    op.create_table('user_tenant_roles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('assigned_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['auth.roles.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['auth.tenants.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['auth.users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='auth'
    )
    
    # Drop user_tenants table
    op.drop_index('ix_auth_user_tenants_user_id', table_name='user_tenants', schema='auth')
    op.drop_index('ix_auth_user_tenants_tenant_id', table_name='user_tenants', schema='auth')
    op.drop_index('ix_auth_user_tenants_user_id_tenant_id', table_name='user_tenants', schema='auth')
    op.drop_table('user_tenants', schema='auth')
