
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import inspect

from backend.database import Base, engine

# Import models so SQLAlchemy registers them
from backend.models.supplier import Supplier
from backend.models.buyer import Buyer
from backend.models.product import Product
from backend.models.supplier_rate import SupplierRate

# Import routers
from backend.routers.supplier import router as supplier_router
from backend.routers.buyer import router as buyer_router
from backend.routers.product import router as product_router
from backend.routers.supplier_rate import router as supplier_rate_router
from backend.routers.dashboard import router as dashboard_router
from backend.routers.reports import router as reports_router
from backend.routers.report_archive import router as report_archive_router

# Import scheduler service
from backend.services.scheduler_service import (
    start_scheduler,
    stop_scheduler
)


# Create database tables
Base.metadata.create_all(bind=engine)


# FastAPI application lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):

    # Start daily report scheduler
    start_scheduler()

    yield

    # Stop scheduler during application shutdown
    stop_scheduler()


# Create FastAPI application
app = FastAPI(
    title="PPS Bitumen Intelligence",
    description="Bitumen Buyer, Supplier and Rate Management System",
    version="1.0.0",
    lifespan=lifespan
)


# Register API routers
app.include_router(supplier_router)
app.include_router(buyer_router)
app.include_router(product_router)
app.include_router(supplier_rate_router)
app.include_router(dashboard_router)
app.include_router(reports_router)
app.include_router(report_archive_router)


@app.get("/")
def home():
    return {
        "message": "Welcome to PPS Bitumen Intelligence",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "PPS Bitumen Intelligence"
    }


@app.get("/database-status")
def database_status():
    inspector = inspect(engine)

    tables = inspector.get_table_names()

    return {
        "database": "SQLite",
        "status": "connected",
        "tables": tables,
        "total_tables": len(tables)
    }
