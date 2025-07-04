"""add_patient_guardians_table

Revision ID: 9836ccdbd8de
Revises: 4e3060f6dcbd
Create Date: 2025-07-02 15:50:12.982738

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9836ccdbd8de'
down_revision = '4e3060f6dcbd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('patient_guardians',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('patient_id', sa.UUID(), nullable=False),
    sa.Column('guardian_id', sa.UUID(), nullable=False),
    sa.Column('relationship', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['guardian_id'], ['dentist.patients.id'], ),
    sa.ForeignKeyConstraint(['patient_id'], ['dentist.patients.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='dentist'
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('patient_guardians', schema='dentist')
    # ### end Alembic commands ###
