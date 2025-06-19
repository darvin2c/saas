from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.api import auth, users, tenants, roles, permissions
from app.services.permission_service import PermissionService

app = FastAPI(
    title=settings.APP_NAME,
    description="Multi-tenant Authentication Service with Dynamic Roles",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(tenants.router)
app.include_router(roles.router)
app.include_router(permissions.router)


@app.get("/")
def read_root():
    """Root endpoint."""
    return {
        "message": "Auth Service API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event():
    """Initialize default permissions on startup."""
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        # Create default permissions
        PermissionService.create_default_permissions(db)
        print("Default permissions initialized")
    except Exception as e:
        print(f"Error initializing default permissions: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
