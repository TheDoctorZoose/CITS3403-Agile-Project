"""Add GameEntry table

Revision ID: a2a13a9edfa5
Revises: e87dfb2e12c0
Create Date: 2025-05-02 18:21:18.476715

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a2a13a9edfa5'
down_revision = 'e87dfb2e12c0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('game_entry',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('game_title', sa.String(length=100), nullable=True),
    sa.Column('date_played', sa.Date(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('game_entry')
    # ### end Alembic commands ###
