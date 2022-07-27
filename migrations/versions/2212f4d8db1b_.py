"""empty message

Revision ID: 2212f4d8db1b
Revises: 04bdf575d06d
Create Date: 2022-07-27 14:40:05.733089

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '2212f4d8db1b'
down_revision = '04bdf575d06d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # op.drop_table('dept')
    op.create_foreign_key(None, 'comment', 'guests', ['comment_guest'], ['guest_id'])
    op.create_foreign_key(None, 'guest_gift', 'gifts', ['g_giftid'], ['gift_id'])
    op.create_foreign_key(None, 'guest_gift', 'guests', ['g_guestid'], ['guest_id'])
    op.create_foreign_key(None, 'lga', 'state', ['state_id'], ['state_id'])
    op.create_foreign_key(None, 'order_details', 'uniform', ['det_itemid'], ['uni_id'])
    op.create_foreign_key(None, 'order_details', 'orders', ['det_orderid'], ['order_id'])
    op.create_foreign_key(None, 'orders', 'guests', ['order_by'], ['guest_id'])
    op.create_foreign_key(None, 'payment', 'orders', ['pay_orderid'], ['order_id'])
    op.create_foreign_key(None, 'payment', 'guests', ['pay_guestid'], ['guest_id'])
    op.add_column('state', sa.Column('state_slogan', sa.String(length=100), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('state', 'state_slogan')
    op.drop_constraint(None, 'payment', type_='foreignkey')
    op.drop_constraint(None, 'payment', type_='foreignkey')
    op.drop_constraint(None, 'orders', type_='foreignkey')
    op.drop_constraint(None, 'order_details', type_='foreignkey')
    op.drop_constraint(None, 'order_details', type_='foreignkey')
    op.drop_constraint(None, 'lga', type_='foreignkey')
    op.drop_constraint(None, 'guest_gift', type_='foreignkey')
    op.drop_constraint(None, 'guest_gift', type_='foreignkey')
    op.drop_constraint(None, 'comment', type_='foreignkey')
    op.create_table('dept',
    sa.Column('dept_id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('dept_name', mysql.VARCHAR(length=100), nullable=False),
    sa.PrimaryKeyConstraint('dept_id'),
    mysql_default_charset='latin1',
    mysql_engine='MyISAM'
    )
    # ### end Alembic commands ###