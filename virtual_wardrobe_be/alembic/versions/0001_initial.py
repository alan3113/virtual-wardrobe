"""Initial wardrobe schema with pgvector embeddings.

Revision ID: 0001
Revises:
"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    op.create_table('users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(120), nullable=False),
        sa.Column('email', sa.String(320), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False))
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    common = [sa.Column('id', sa.String(36), primary_key=True),
              sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
              sa.Column('name', sa.String(160), nullable=False),
              sa.Column('category', sa.String(50), nullable=False),
              sa.Column('subcategory', sa.String(80)),
              sa.Column('color', sa.String(60), nullable=False),
              sa.Column('pattern', sa.String(60)),
              sa.Column('material', sa.String(80)),
              sa.Column('style', sa.String(80)),
              sa.Column('season', sa.String(50)),
              sa.Column('occasion', sa.String(80)),
              sa.Column('formality', sa.Integer(), nullable=False),
              sa.Column('image_url', sa.Text(), nullable=False),
              sa.Column('embedding', Vector(32)),
              sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)]
    op.create_table('wardrobe_items', *common, sa.Column('notes', sa.Text()))
    op.create_index('ix_wardrobe_items_user_id', 'wardrobe_items', ['user_id'])
    op.create_index('ix_wardrobe_items_category', 'wardrobe_items', ['category'])
    product_columns = [sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(160), nullable=False), sa.Column('brand', sa.String(100)),
        sa.Column('price', sa.String(60)), sa.Column('url', sa.Text()),
        sa.Column('image_url', sa.Text(), nullable=False), sa.Column('category', sa.String(50), nullable=False),
        sa.Column('subcategory', sa.String(80)), sa.Column('color', sa.String(60), nullable=False),
        sa.Column('pattern', sa.String(60)), sa.Column('material', sa.String(80)),
        sa.Column('style', sa.String(80)), sa.Column('season', sa.String(50)),
        sa.Column('occasion', sa.String(80)), sa.Column('formality', sa.Integer(), nullable=False),
        sa.Column('embedding', Vector(32)), sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)]
    op.create_table('products', *product_columns)
    op.create_index('ix_products_user_id', 'products', ['user_id'])
    op.create_table('outfits', sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(160), nullable=False), sa.Column('item_ids', sa.JSON(), nullable=False),
        sa.Column('occasion', sa.String(80), nullable=False), sa.Column('description', sa.Text(), nullable=False),
        sa.Column('saved', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False))
    op.create_index('ix_outfits_user_id', 'outfits', ['user_id'])


def downgrade():
    op.drop_table('outfits')
    op.drop_table('products')
    op.drop_table('wardrobe_items')
    op.drop_table('users')
