"""create roi_records table

Revision ID: 3d7b3d740da8
Revises: 
Create Date: 2026-05-07 01:19:08.069261

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3d7b3d740da8'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'roi_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(), nullable=False),
        sa.Column('frame_id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('x', sa.Integer(), nullable=False),
        sa.Column('y', sa.Integer(), nullable=False),
        sa.Column('width', sa.Integer(), nullable=False),
        sa.Column('height', sa.Integer(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_roi_records_id', 'roi_records', ['id'])
    op.create_index('ix_roi_records_session_id', 'roi_records', ['session_id'])
    op.create_index('ix_roi_records_frame_id', 'roi_records', ['frame_id'])


def downgrade() -> None:
    op.drop_index('ix_roi_records_frame_id', table_name='roi_records')
    op.drop_index('ix_roi_records_session_id', table_name='roi_records')
    op.drop_index('ix_roi_records_id', table_name='roi_records')
    op.drop_table('roi_records')
