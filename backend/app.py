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
from src.utils.logging_config import get_logger

# Configure logging
logger = get_logger(__name__)

# Set default environment variables for Hugging Face Space if not provided
if not os.getenv("DATABASE_URL"):
    # In a real deployment, you would use a persistent database service
    # For demo purposes only, using a SQLite database
    os.environ["DATABASE_URL"] = "sqlite:///./todo_app_hf.db"
    logger.debug("Set DATABASE_URL to default SQLite database")

if not os.getenv("SECRET_KEY"):
    # Generate a random secret key for JWT tokens
    import secrets
    os.environ["SECRET_KEY"] = secrets.token_hex(32)
    logger.debug("Generated random SECRET_KEY for JWT tokens")

if not os.getenv("BETTER_AUTH_SECRET"):
    os.environ["BETTER_AUTH_SECRET"] = "hf_space_demo_secret_change_in_production"
    logger.debug("Set BETTER_AUTH_SECRET to default value")

if not os.getenv("ALGORITHM"):
    os.environ["ALGORITHM"] = "HS256"
    logger.debug("Set ALGORITHM to HS256")

if not os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"):
    os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
    logger.debug("Set ACCESS_TOKEN_EXPIRE_MINUTES to 30")

if not os.getenv("ALLOWED_ORIGINS"):
    os.environ["ALLOWED_ORIGINS"] = '["*"]'
    logger.debug("Set ALLOWED_ORIGINS to allow all origins")

# Set the backend URL to work in Hugging Face environment
if not os.getenv("BACKEND_URL"):
    # For Hugging Face Space deployment
    os.environ["BACKEND_URL"] = "https://muhammedsuhaib-raheel.hf.space"
    logger.debug("Set BACKEND_URL for Hugging Face Space deployment")

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

        # Hugging Face Spaces typically use port 7860
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

    # Create tables
    if not create_tables():
        logger.error("Failed to create database tables. Exiting.")
        sys.exit(1)

    # Start the server
    logger.info("Starting the server...")
    start_server()