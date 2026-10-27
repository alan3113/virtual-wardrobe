# Wardrobe Intelligence API

FastAPI backend for the virtual wardrobe frontend. Clothing and product embeddings use PostgreSQL with pgvector. The included vision and embedding providers are deterministic mocks, so the API runs without paid AI services.

## Start with Docker

```bash
cp .env.example .env
# Set SECRET_KEY in .env to a long random value before deploying.
docker compose up --build
```

The API is at `http://localhost:8000/api/v1`; interactive docs are at `http://localhost:8000/docs`. Compose waits for PostgreSQL, runs `alembic upgrade head`, then starts the API. Uploaded images are served from `/uploads` and persisted in a Docker volume.

## Local development

Python 3.10+ and PostgreSQL 16 with pgvector are required. Start only the database with `docker compose up -d db`, then:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

Set `DATABASE_URL` for another PostgreSQL instance. Set `CORS_ORIGINS` to a comma-separated list of frontend origins. The existing frontend uses `http://localhost:8000/api/v1` when `VITE_DEMO_MODE=false`.

Run tests without PostgreSQL:

```bash
python -m pytest -q
```

Tests use in-memory SQLite with JSON storage for the vector column. Production uses `vector(32)` and pgvector cosine ordering. Mock provider dependencies can be overridden via FastAPI's `app.dependency_overrides`.

## API

All routes below use the `/api/v1` prefix. Send the JWT from register or login as `Authorization: Bearer <token>` on protected routes.

| Method | Route | Purpose |
| --- | --- | --- |
| POST | `/auth/register`, `/auth/login` | Create account or get JWT |
| GET | `/auth/me` | Current account |
| POST | `/wardrobe/upload`, `/wardrobe/analyze` | Upload an image or get editable mock metadata; multipart field `file` |
| GET, POST | `/wardrobe/items` | List or create clothing |
| GET, PATCH, DELETE | `/wardrobe/items/{id}` | Read, edit or delete owned clothing |
| POST | `/wardrobe/items/{id}/analyze` | Refresh an item's metadata and embedding |
| GET | `/wardrobe/stats`, `/wardrobe/gaps` | Category counts and underrepresented categories |
| POST | `/products/analyze` | Compare a product with owned items |
| GET | `/products/{id}` | Read a previously analyzed product |
| POST | `/products/upload`, `/products/import` | Create a product from an image or URL |
| GET, POST | `/outfits` | List or save outfits |
| DELETE | `/outfits/{id}` | Delete a saved outfit |
| POST | `/outfits/generate` | Generate combinations from `item_id`, `product_id`, or `product` |
| POST | `/shopping/analyze` | Combined duplicate, gap, compatibility and outfit analysis |

`GET /wardrobe/items` accepts `category`, `subcategory`, `color`, `style`, `season`, `occasion`, `limit` and `offset` query parameters. Product and shopping analysis accept either `product_id` or an inline `product` object. An inline product is stored under the current user and can then be referenced by ID. Example:

```json
{
  "product": {
    "name": "Blue linen shirt",
    "category": "Tops",
    "color": "Blue",
    "image_url": "https://example.com/shirt.jpg",
    "style": "Casual",
    "season": "Summer"
  }
}
```

Similarity labels are `likely_duplicate` (score ≥ 0.90), `similar` (≥ 0.72), `related` (≥ 0.48), and `different`. Outfit compatibility is a transparent score using category, color, style, occasion, season and formality. These are MVP heuristics, not model predictions. `VisionProvider` and `EmbeddingProvider` in `app/ai/providers.py` can be replaced by implementations that return the same contracts; embeddings must remain 32-dimensional until the column and migration are changed.
