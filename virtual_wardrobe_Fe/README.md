# Wardrobe AI

A fashion focused virtual wardrobe frontend built with React, TypeScript, Vite, Tailwind CSS, React Router, TanStack Query, Axios, and Lucide.

## Run locally

```bash
npm install
cp .env.example .env
npm run dev
```

Demo mode is enabled by default. It includes sample wardrobe pieces, outfits, gaps, and a shopping analysis. Changes to wardrobe items and saved outfits are stored in browser local storage. Use the landing page or go directly to `/dashboard`.

## Backend integration

Set `VITE_DEMO_MODE=false` and point `VITE_API_BASE_URL` at the FastAPI API. The Axios client attaches `wardrobe_token` as a bearer token. API calls and shared TypeScript types live under `src/api` and `src/types.ts`.

The frontend currently expects these REST paths:

| Area | Endpoints |
| --- | --- |
| Auth | `POST /auth/login`, `POST /auth/register`, `GET /auth/me` |
| Wardrobe | `GET/POST /wardrobe/items`, `GET/PATCH/DELETE /wardrobe/items/:id`, `POST /wardrobe/analyze`, `POST /wardrobe/upload`, `GET /wardrobe/gaps` |
| Outfits | `GET/POST /outfits`, `POST /outfits/generate`, `DELETE /outfits/:id` |
| Products | `GET /products/:id`, `POST /products/import`, `POST /products/upload` |
| Shopping | `POST /shopping/analyze` |

The backend schemas were not included in this repository. Align the endpoint paths and types with the FastAPI OpenAPI spec when connecting the service. Image upload endpoints use multipart form data with a `file` field.

## Checks

```bash
npm run lint
npm run typecheck
npm run build
```
