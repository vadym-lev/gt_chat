"""Initial migration

Revision ID: 219388cb28fd
Revises: 
Create Date: 2024-10-29 04:20:30.983829

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '219388cb28fd'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tasks',
    sa.Column('task_id', sa.String(), nullable=False),
    sa.Column('original_text', sa.String(), nullable=True),
    sa.Column('processed_text', sa.String(), nullable=True),
    sa.Column('type', sa.String(), nullable=True),
    sa.Column('word_count', sa.Integer(), nullable=True),
    sa.Column('language', sa.String(), nullable=True),
    sa.Column('status', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('task_id')
    )
    op.create_index(op.f('ix_tasks_task_id'), 'tasks', ['task_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_tasks_task_id'), table_name='tasks')
    op.drop_table('tasks')
    # ### end Alembic commands ###