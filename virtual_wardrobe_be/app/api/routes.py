from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.ai.providers import EmbeddingProvider, MockEmbeddingProvider, MockVisionProvider, VisionProvider
from app.core.config import settings
from app.core.db import get_db
from app.core.security import hash_password, make_token, token_subject, verify_password
from app.models.entities import Outfit, Product, User, WardrobeItem
from app.repositories.wardrobe import category_counts, items, owned
from app.schemas.contracts import (AuthRead, ClothingFields, ClothingRead, ClothingUpdate, GenerateRequest,
    GapRead, Login, OutfitCreate, OutfitRead, ProductAnalysis, ProductAnalyzeRequest, ProductFields, ProductRead,
    Register, ShoppingRead, ShoppingRequest, UserRead)
from app.services.intelligence import gaps, generate
from app.services.shopping import analyze_product as analyze_product_service, analyze_shopping

router = APIRouter(prefix='/api/v1')
bearer = HTTPBearer()


def vision_provider() -> VisionProvider:
    return MockVisionProvider()


def embedding_provider() -> EmbeddingProvider:
    return MockEmbeddingProvider()


def current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)) -> User:
    try:
        user_id = token_subject(credentials.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail='Invalid or expired token') from None
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail='User not found')
    return user


def required(db, model, user, object_id):
    value = owned(db, model, user.id, object_id)
    if not value:
        raise HTTPException(status_code=404, detail=f'{model.__name__} not found')
    return value


def save_product(db, user, data: ProductFields, embedding: EmbeddingProvider):
    product = Product(user_id=user.id, **data.model_dump())
    product.embedding = embedding.embed(product)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def resolve_product(db, user, product_id, product_data, embedding):
    if product_id:
        return required(db, Product, user, product_id)
    if product_data:
        return save_product(db, user, product_data, embedding)
    raise HTTPException(status_code=422, detail='Provide product_id or product')


@router.post('/auth/register', response_model=AuthRead, status_code=201)
def register(data: Register, db: Session = Depends(get_db)):
    user = User(name=data.name, email=data.email.lower(), password_hash=hash_password(data.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail='Email already registered') from None
    db.refresh(user)
    return AuthRead(access_token=make_token(user.id), user=UserRead.model_validate(user))


@router.post('/auth/login', response_model=AuthRead)
def login(data: Login, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == data.email.lower()))
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail='Invalid credentials')
    return AuthRead(access_token=make_token(user.id), user=UserRead.model_validate(user))


@router.get('/auth/me', response_model=UserRead)
def me(user: User = Depends(current_user)):
    return user


async def store_image(file: UploadFile) -> str:
    allowed = {'image/jpeg': '.jpg', 'image/png': '.png', 'image/webp': '.webp'}
    if file.content_type not in allowed:
        raise HTTPException(status_code=415, detail='Upload a JPEG, PNG or WebP image')
    data = await file.read(settings.max_upload_bytes + 1)
    if len(data) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail='Image is too large')
    if not data:
        raise HTTPException(status_code=400, detail='Image is empty')
    signatures = {'image/jpeg': data.startswith(b'\xff\xd8\xff'),
                  'image/png': data.startswith(b'\x89PNG\r\n\x1a\n'),
                  'image/webp': data.startswith(b'RIFF') and data[8:12] == b'WEBP'}
    if not signatures[file.content_type]:
        raise HTTPException(status_code=415, detail='Invalid image content')
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    filename = f'{uuid4().hex}{allowed[file.content_type]}'
    (settings.upload_dir / filename).write_bytes(data)
    return f'{settings.public_base_url}/uploads/{filename}'


@router.post('/wardrobe/upload')
async def upload_wardrobe(file: UploadFile = File(...), user: User = Depends(current_user)):
    return {'image_url': await store_image(file)}


@router.post('/wardrobe/analyze')
async def analyze_upload(file: UploadFile = File(...), user: User = Depends(current_user),
                         vision: VisionProvider = Depends(vision_provider)):
    url = await store_image(file)
    return {'image_url': url, **vision.analyze(url)}


@router.get('/wardrobe/items', response_model=list[ClothingRead])
def list_items(category: str | None = None, subcategory: str | None = None, color: str | None = None,
               style: str | None = None, season: str | None = None, occasion: str | None = None,
               limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0),
               user: User = Depends(current_user), db: Session = Depends(get_db)):
    return items(db, user.id, {'category': category, 'subcategory': subcategory, 'color': color,
                              'style': style, 'season': season, 'occasion': occasion}, offset, limit)


@router.post('/wardrobe/items', response_model=ClothingRead, status_code=201)
def create_item(data: ClothingFields, user: User = Depends(current_user), db: Session = Depends(get_db),
                embedding: EmbeddingProvider = Depends(embedding_provider)):
    item = WardrobeItem(user_id=user.id, **data.model_dump())
    item.embedding = embedding.embed(item)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get('/wardrobe/items/{item_id}', response_model=ClothingRead)
def get_item(item_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return required(db, WardrobeItem, user, item_id)


@router.patch('/wardrobe/items/{item_id}', response_model=ClothingRead)
def update_item(item_id: str, data: ClothingUpdate, user: User = Depends(current_user),
                db: Session = Depends(get_db), embedding: EmbeddingProvider = Depends(embedding_provider)):
    item = required(db, WardrobeItem, user, item_id)
    changes = data.model_dump(exclude_unset=True)
    for field, value in changes.items():
        if value is None and field in {'name', 'category', 'color', 'image_url', 'formality'}:
            raise HTTPException(status_code=422, detail=f'{field} cannot be null')
        setattr(item, field, value)
    item.embedding = embedding.embed(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete('/wardrobe/items/{item_id}', status_code=204)
def delete_item(item_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    db.delete(required(db, WardrobeItem, user, item_id))
    db.commit()


@router.post('/wardrobe/items/{item_id}/analyze', response_model=ClothingRead)
def analyze_item(item_id: str, user: User = Depends(current_user), db: Session = Depends(get_db),
                 vision: VisionProvider = Depends(vision_provider), embedding: EmbeddingProvider = Depends(embedding_provider)):
    item = required(db, WardrobeItem, user, item_id)
    # Explicit analysis refreshes metadata. Users can edit it afterward.
    for field, value in vision.analyze(item.image_url).items():
        if hasattr(item, field): setattr(item, field, value)
    item.embedding = embedding.embed(item)
    db.commit()
    db.refresh(item)
    return item


@router.get('/wardrobe/stats')
def stats(user: User = Depends(current_user), db: Session = Depends(get_db)):
    counts = category_counts(db, user.id)
    return {'total_items': sum(counts.values()), 'by_category': counts}


@router.get('/wardrobe/gaps', response_model=list[GapRead])
def wardrobe_gaps(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return gaps(db, user.id)


@router.post('/products/analyze', response_model=ProductAnalysis)
def analyze_product(data: ProductAnalyzeRequest, user: User = Depends(current_user), db: Session = Depends(get_db),
                    embedding: EmbeddingProvider = Depends(embedding_provider)):
    product = resolve_product(db, user, data.product_id, data.product, embedding)
    return analyze_product_service(db, user.id, product)


@router.get('/products/{product_id}', response_model=ProductRead)
def get_product(product_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return required(db, Product, user, product_id)


@router.post('/products/import', response_model=ProductRead, status_code=201)
def import_product(data: dict, user: User = Depends(current_user), db: Session = Depends(get_db),
                   embedding: EmbeddingProvider = Depends(embedding_provider)):
    url = data.get('url')
    if not isinstance(url, str) or not url.startswith(('http://', 'https://')):
        raise HTTPException(status_code=422, detail='A valid product URL is required')
    # No arbitrary URL fetch: the user can edit mock analysis metadata.
    product = ProductFields(name='Imported product', category='Tops', color='Neutral', image_url=url, url=url)
    return save_product(db, user, product, embedding)


@router.post('/products/upload', response_model=ProductRead, status_code=201)
async def upload_product(file: UploadFile = File(...), user: User = Depends(current_user),
                         db: Session = Depends(get_db), vision: VisionProvider = Depends(vision_provider),
                         embedding: EmbeddingProvider = Depends(embedding_provider)):
    url = await store_image(file)
    product = ProductFields(name='Uploaded product', image_url=url, **vision.analyze(url))
    return save_product(db, user, product, embedding)


@router.get('/outfits', response_model=list[OutfitRead])
def list_outfits(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return list(db.scalars(select(Outfit).where(Outfit.user_id == user.id).order_by(Outfit.created_at.desc())))


@router.post('/outfits/generate', response_model=list[OutfitRead])
def generate_outfits(data: GenerateRequest, user: User = Depends(current_user), db: Session = Depends(get_db),
                     embedding: EmbeddingProvider = Depends(embedding_provider)):
    if data.item_id:
        anchor = required(db, WardrobeItem, user, data.item_id)
    else:
        anchor = resolve_product(db, user, data.product_id, data.product, embedding)
    return generate(db, user.id, anchor, data.limit)


@router.post('/outfits', response_model=OutfitRead, status_code=201)
def save_outfit(data: OutfitCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if not data.item_ids or any(not owned(db, WardrobeItem, user.id, i) for i in data.item_ids):
        raise HTTPException(status_code=422, detail='Outfit contains unknown wardrobe items')
    outfit = Outfit(user_id=user.id, name=data.name, item_ids=data.item_ids, occasion=data.occasion,
                    description=data.description, saved=True)
    db.add(outfit)
    db.commit()
    db.refresh(outfit)
    return outfit


@router.delete('/outfits/{outfit_id}', status_code=204)
def delete_outfit(outfit_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    db.delete(required(db, Outfit, user, outfit_id))
    db.commit()


@router.post('/shopping/analyze', response_model=ShoppingRead)
def shopping_analysis(data: ShoppingRequest, user: User = Depends(current_user), db: Session = Depends(get_db),
                      embedding: EmbeddingProvider = Depends(embedding_provider)):
    product = resolve_product(db, user, data.product_id, data.product, embedding)
    return analyze_shopping(db, user.id, product)
