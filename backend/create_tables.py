#!/usr/bin/env python
"""
Script to create database tables in PostgreSQL.
"""
from src.database.connection import create_tables

if __name__ == "__main__":
    print("Creating database tables...")
    create_tables()
    print("Tables created successfully!")