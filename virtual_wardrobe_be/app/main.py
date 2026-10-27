from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.routes import router
from app.core.config import settings

settings.upload_dir.mkdir(parents=True, exist_ok=True)
app = FastAPI(title='Wardrobe Intelligence API', version='0.1.0')
app.add_middleware(CORSMiddleware, allow_origins=[s.strip() for s in settings.cors_origins.split(',')],
                   allow_credentials=True, allow_methods=['*'], allow_headers=['*'])
app.mount('/uploads', StaticFiles(directory=settings.upload_dir), name='uploads')
app.include_router(router)


@app.get('/health')
def health():
    return {'status': 'ok'}
