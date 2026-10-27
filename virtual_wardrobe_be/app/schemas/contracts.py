from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


def canonical_category(value: str | None) -> str | None:
    if value is None: return None
    categories = {'tops': 'Tops', 'bottoms': 'Bottoms', 'shoes': 'Shoes',
                  'outerwear': 'Outerwear', 'accessories': 'Accessories'}
    return categories.get(value.strip().lower(), value.strip())


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Register(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class Login(BaseModel):
    email: EmailStr
    password: str


class UserRead(ORMModel):
    id: str
    name: str
    email: str


class AuthRead(BaseModel):
    access_token: str
    token_type: str = 'bearer'
    user: UserRead


class ClothingFields(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    category: str = Field(min_length=1, max_length=50)
    subcategory: str | None = None
    color: str = Field(min_length=1, max_length=60)
    pattern: str | None = None
    material: str | None = None
    style: str | None = None
    season: str | None = None
    occasion: str | None = None
    formality: int = Field(default=2, ge=1, le=5)
    image_url: str = Field(min_length=1)
    notes: str | None = None

    @field_validator('category')
    @classmethod
    def normalize_category(cls, value: str) -> str:
        return canonical_category(value)


class ClothingUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    subcategory: str | None = None
    color: str | None = None
    pattern: str | None = None
    material: str | None = None
    style: str | None = None
    season: str | None = None
    occasion: str | None = None
    formality: int | None = Field(default=None, ge=1, le=5)
    image_url: str | None = None
    notes: str | None = None

    @field_validator('category')
    @classmethod
    def normalize_category(cls, value: str | None) -> str | None:
        return canonical_category(value)

    @field_validator('name', 'category', 'color', 'image_url')
    @classmethod
    def nonempty(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError('must not be empty')
        return value


class ClothingRead(ClothingFields, ORMModel):
    id: str
    created_at: datetime


class ProductFields(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    brand: str | None = None
    price: str | None = None
    url: str | None = None
    image_url: str = Field(min_length=1)
    category: str = Field(min_length=1)
    subcategory: str | None = None
    color: str = Field(min_length=1)
    pattern: str | None = None
    material: str | None = None
    style: str | None = None
    season: str | None = None
    occasion: str | None = None
    formality: int = Field(default=2, ge=1, le=5)

    @field_validator('category')
    @classmethod
    def normalize_category(cls, value: str) -> str:
        return canonical_category(value)


class ProductRead(ProductFields, ORMModel):
    id: str


class ProductAnalyzeRequest(BaseModel):
    product_id: str | None = None
    product: ProductFields | None = None


class SimilarItem(BaseModel):
    item: ClothingRead
    similarity_score: float
    classification: str


class ProductAnalysis(BaseModel):
    product: ProductRead
    similar_items: list[SimilarItem]
    duplicate_risk: str


class GenerateRequest(BaseModel):
    item_id: str | None = None
    product_id: str | None = None
    product: ProductFields | None = None
    limit: int = Field(default=3, ge=1, le=10)


class OutfitCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    item_ids: list[str] = Field(min_length=1)
    occasion: str = 'Everyday'
    description: str = ''


class OutfitRead(ORMModel):
    id: str
    name: str
    item_ids: list[str]
    occasion: str
    description: str
    saved: bool
    created_at: datetime


class GapRead(BaseModel):
    id: str
    category: str
    title: str
    description: str
    priority: str
    image_url: str = ''
    pairs_with: list[str] = []
    count: int
    target: int


class ShoppingRequest(BaseModel):
    product_id: str | None = None
    product: ProductFields | None = None


class ShoppingRead(BaseModel):
    id: str
    product: ProductRead
    wardrobe_match: int
    similar_item_owned: int
    compatible_items: int
    new_outfits: int
    duplicate_risk: str
    wardrobe_gap: bool
    explanation: str
    outfit_item_ids: list[list[str]]
    similar_items: list[SimilarItem]
    compatibility_score: int
    compatible_wardrobe_items: list[ClothingRead]
    possible_new_outfits: list[OutfitRead]
