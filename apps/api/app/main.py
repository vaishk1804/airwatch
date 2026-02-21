from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.admin import router as admin_router
from app.api.locations import router as locations_router
from app.api.dashboard import router as dashboard_router

from app.core.config import settings

app = FastAPI(title="AirWatch API", version="0.1.0")

origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]

app.add_middleware(CORSMiddleware,
                   allow_origins=origins,
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=['*'],)

app.include_router(health_router)
app.include_router(admin_router)
app.include_router(locations_router)
app.include_router(dashboard_router)