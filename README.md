# Virtual Wardrobe

A full-stack wardrobe organizer and shopping assistant. Virtual Wardrobe helps users catalog clothing, build outfits, identify wardrobe gaps, and compare potential purchases with items they already own.

The project includes a React frontend and a FastAPI backend backed by PostgreSQL and pgvector. It can also run as a frontend-only demo with sample data stored in the browser.

## Features

- Organize and filter wardrobe items
- Upload clothing and product images
- Generate and save outfit combinations
- Analyze wardrobe gaps and category coverage
- Compare products for similarity and outfit compatibility
- Register and sign in with JWT authentication
- Explore the UI without a backend using demo mode

## Tech stack

| Layer | Technologies |
| --- | --- |
| Frontend | React 19, TypeScript, Vite, Tailwind CSS, TanStack Query, Axios |
| Backend | FastAPI, SQLAlchemy, Alembic, Pydantic |
| Database | PostgreSQL 16, pgvector |
| Infrastructure | Docker Compose |

## Project structure

```text
virtual_wardrobe/
├── virtual_wardrobe_Fe/   # React frontend
└── virtual_wardrobe_be/   # FastAPI backend, migrations, and tests
```

## Quick start: demo mode

Demo mode runs entirely in the browser and does not require the backend.

```bash
cd virtual_wardrobe_Fe
npm install
cp .env.example .env
npm run dev
```

Open `http://localhost:5173`. Demo mode is enabled by default, and changes are stored in browser local storage.

## Run the full stack

### 1. Start the backend

Docker is the simplest way to start the API and its pgvector-enabled PostgreSQL database.

```bash
cd virtual_wardrobe_be
cp .env.example .env
docker compose up --build
```

Before deploying, replace the example `SECRET_KEY` in `.env` with a long random value. The local `.env` file is ignored by Git.

The API will be available at:

- API base URL: `http://localhost:8000/api/v1`
- Interactive documentation: `http://localhost:8000/docs`

### 2. Connect the frontend

In a second terminal:

```bash
cd virtual_wardrobe_Fe
npm install
cp .env.example .env
```

Set these values in `virtual_wardrobe_Fe/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_DEMO_MODE=false
```

Then start the development server:

```bash
npm run dev
```

## Development checks

Frontend:

```bash
cd virtual_wardrobe_Fe
npm run lint
npm run typecheck
npm run build
```

Backend:

```bash
cd virtual_wardrobe_be
. .venv/bin/activate
python -m pytest -q
```

For more detail, see the [frontend documentation](virtual_wardrobe_Fe/README.md) and [backend documentation](virtual_wardrobe_be/README.md).
