import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.v1.endpoints import tasks
from src.api.v1.endpoints.auth import router as auth_router
from src.api.chat_endpoint import router as chat_router
from src.config.settings import settings
from src.database.connection import create_tables
from src.utils.logging_config import get_logger

# Configure logging
logger = get_logger(__name__)

# Create tables on startup
logger.info("Creating database tables on startup...")
create_tables()
logger.info("Database tables created successfully")

# Create FastAPI app instance
app = FastAPI(
    title="Todo API",
    description="A secure, multi-user todo management API with JWT authentication",
    version="1.0.0",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Expose authorization header to allow frontend to access JWT tokens
    expose_headers=["Authorization"]
)

# Include API routes
app.include_router(tasks.router, prefix="/api/v1", tags=["tasks"])
# Include authentication routes
app.include_router(auth_router, prefix="/api/v1", tags=["authentication"])
# Include chat routes
app.include_router(chat_router, prefix="/api", tags=["chat"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Todo API"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "todo-backend"}