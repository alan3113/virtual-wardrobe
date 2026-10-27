from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models.entities import WardrobeItem, Product, Outfit


def owned(db: Session, model, user_id: str, object_id: str):
    return db.scalar(select(model).where(model.id == object_id, model.user_id == user_id))


def items(db: Session, user_id: str, filters: dict | None = None, offset: int = 0, limit: int = 100):
    query = select(WardrobeItem).where(WardrobeItem.user_id == user_id)
    for key, value in (filters or {}).items():
        if value:
            query = query.where(getattr(WardrobeItem, key).ilike(f'%{value}%'))
    return list(db.scalars(query.order_by(WardrobeItem.created_at.desc()).offset(offset).limit(limit)))


def category_counts(db: Session, user_id: str):
    return dict(db.execute(select(WardrobeItem.category, func.count()).where(
        WardrobeItem.user_id == user_id).group_by(WardrobeItem.category)).all())


def similar(db: Session, user_id: str, product: Product, limit: int = 5):
    query = select(WardrobeItem).where(WardrobeItem.user_id == user_id,
        WardrobeItem.category.ilike(product.category))
    if db.bind.dialect.name == 'postgresql' and product.embedding is not None:
        query = query.order_by(WardrobeItem.embedding.cosine_distance(product.embedding))
    return list(db.scalars(query.limit(limit if db.bind.dialect.name == 'postgresql' else 1000)))
