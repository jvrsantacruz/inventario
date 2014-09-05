"""Initial database model

Revision ID: 32007559b6c
Revises: None
Create Date: 2014-09-02 01:03:12.521582

"""

# revision identifiers, used by Alembic.
revision = '32007559b6c'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'books',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('identified', sa.Boolean(), nullable=False),
        sa.Column('first_entry_id', sa.Integer(), sa.ForeignKey('book_entries.id'), nullable=True),
        sa.Column('last_entry_id', sa.Integer(), sa.ForeignKey('book_entries.id'), nullable=True)
    )

    op.create_table(
        'listings',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('year', sa.Integer(), index=True, nullable=False)
    )

    op.create_table(
        'book_entries',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('title', sa.Unicode(2048), index=True, nullable=False),
        sa.Column('pos', sa.Integer(), index=True, nullable=False),
        sa.Column('lang', sa.Unicode(128)),
        sa.Column('format', sa.Unicode(128)),
        sa.Column('error', sa.Boolean()),

        sa.Column('book_id', sa.Integer(), sa.ForeignKey('books.id'), nullable=False),
        sa.Column('listing_id', sa.Integer(), sa.ForeignKey('listings.id'), nullable=False)
    )


def downgrade():
    op.drop_table('book_entries')
    op.drop_table('books')
    op.drop_table('listings')
