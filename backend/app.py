#!/usr/bin/env python
"""
Entry point for Hugging Face Spaces deployment.
This script sets up the environment and starts the FastAPI application.
"""

import os
import sys
import subprocess
import time
from threading import Thread

# Set default environment variables for Hugging Face Space if not provided
if not os.getenv("DATABASE_URL"):
    os.environ["DATABASE_URL"] = "postgresql://neondb_owner:npg_JDbCa6ELqGQ2@ep-withered-shape-a7bd9hif-pooler.ap-southeast-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

if not os.getenv("NEON_DB_URL"):
    os.environ["NEON_DB_URL"] = "postgresql://neondb_owner:npg_JDbCa6ELqGQ2@ep-withered-shape-a7bd9hif-pooler.ap-southeast-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

if not os.getenv("SECRET_KEY"):
    os.environ["SECRET_KEY"] = "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"

if not os.getenv("BETTER_AUTH_SECRET"):
    os.environ["BETTER_AUTH_SECRET"] = "pohwuyqoVn683bmFDoVzmtQq50Zn3bFV"

if not os.getenv("BETTER_AUTH_URL"):
    os.environ["BETTER_AUTH_URL"] = "http://localhost:8000"

if not os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = "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"

if not os.getenv("OPEN_ROUTER_API_KEY"):
    os.environ["OPEN_ROUTER_API_KEY"] = "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"

if not os.getenv("ALGORITHM"):
    os.environ["ALGORITHM"] = "HS256"

if not os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"):
    os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"

if not os.getenv("ALLOWED_ORIGINS"):
    os.environ["ALLOWED_ORIGINS"] = '["*"]'

if not os.getenv("BACKEND_URL"):
    os.environ["BACKEND_URL"] = "https://muhammedsuhaib-raheel.hf.space"

# Late import to ensure environment variables are loaded before settings validation
from src.utils.logging_config import get_logger
logger = get_logger(__name__)

def create_tables():
    """Create database tables."""
    try:
        from src.database.connection import create_tables
        logger.info("Creating database tables...")
        create_tables()
        logger.info("Database tables created successfully.")
        return True
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        return False

def start_server():
    """Start the FastAPI server."""
    try:
        import uvicorn
        from main import app

        port = int(os.getenv("PORT", 7860))
        logger.info(f"Starting server on port {port}...")

        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    logger.info("Initializing Todo API for Hugging Face Spaces...")

    if not create_tables():
        logger.error("Failed to create database tables. Exiting.")
        sys.exit(1)

    logger.info("Starting the server...")
    start_server()