"""disable autoincrement

Revision ID: b0b0e34060ab
Revises: 4ac6afa0aec2
Create Date: 2020-01-14 12:35:20.763385

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'b0b0e34060ab'
down_revision = '4ac6afa0aec2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(
        op.f('ix_bangumi_bilibili_season_id'),
        'bangumi_bilibili', ['season_id'],
        unique=False
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_bangumi_bilibili_season_id'), table_name='bangumi_bilibili')
    # ### end Alembic commands ###