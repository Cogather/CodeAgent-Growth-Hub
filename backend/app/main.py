from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import get_settings
from app.database import engine
from app.db_init import init_tables
from app.routers import auth, departments, personnel, usage_stats, users, zone_permissions

init_tables()

settings = get_settings()

app = FastAPI(title="CodeAgent Growth Hub API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(departments.router, prefix="/api")
app.include_router(personnel.router, prefix="/api")
app.include_router(zone_permissions.router, prefix="/api")
app.include_router(usage_stats.router, prefix="/api")


@app.get("/api/health")
def health():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {
        "status": "ok",
        "database": settings.mysql_database if not settings.database_url else "configured",
    }
