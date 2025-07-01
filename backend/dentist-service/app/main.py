from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import SessionLocal
from app.api import patients

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for the application."""
    # Startup event
    db = SessionLocal()
    try:
        print("Dentist service started")
    except Exception as e:
        print(f"Error during startup: {e}")
    finally:
        db.close()
    
    yield  # This is where the application runs
    
    # Shutdown event: Clean up resources if needed

app = FastAPI(
    title=settings.APP_NAME,
    description="Dentist Service API for managing patients and appointments",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    debug=settings.DEBUG
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
app.include_router(patients.router)


@app.get("/")
def read_root():
    """Root endpoint."""
    return {
        "message": "Dentist Service API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)  # Using port 8001 to avoid conflict with auth service
