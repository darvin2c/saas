from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.api.router import router
import logging
import time
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("gateway-service")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for the application."""
    # Startup event
    logger.info("API Gateway starting up")
    logger.info(f"Servicios configurados: {list(settings.SERVICES.keys())}")
    
    yield  # This is where the application runs
    
    # Shutdown event
    logger.info("API Gateway shutting down")

app = FastAPI(
    title=settings.APP_NAME,
    description="API Gateway para Microservicios SaaS",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    debug=settings.DEBUG    
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests and their processing time."""
    start_time = time.time()
    
    # Get client IP
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()
    else:
        client_ip = request.client.host if request.client else "unknown"
    
    # Log request details
    logger.info(f"Request: {request.method} {request.url.path} from {client_ip}")
    
    try:
        # Process the request
        response = await call_next(request)
        
        # Log response details
        process_time = time.time() - start_time
        logger.info(
            f"Response: {request.method} {request.url.path} - "
            f"Status: {response.status_code} - Time: {process_time:.3f}s"
        )
        
        return response
    except Exception as e:
        # Log any exceptions
        process_time = time.time() - start_time
        logger.error(
            f"Error: {request.method} {request.url.path} - "
            f"Error: {str(e)} - Time: {process_time:.3f}s"
        )
        
        # Return a 500 error response
        return Response(
            content=json.dumps({"detail": "Internal server error"}).encode(),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            media_type="application/json"
        )

# Include router dinámico para todos los servicios
app.include_router(router)

@app.get("/")
def read_root():
    """Root endpoint."""
    return {
        "message": "API Gateway Service",
        "version": "1.0.0",
        "docs": "/docs",
        "services": list(settings.SERVICES.keys())
    }

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.GATEWAY_HOST,
        port=settings.GATEWAY_PORT
    )
