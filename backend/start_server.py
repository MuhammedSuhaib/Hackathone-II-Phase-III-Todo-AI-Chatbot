import os
import subprocess
import sys

# Set the environment variables
os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_JDbCa6ELqGQ2@ep-withered-shape-a7bd9hif-pooler.ap-southeast-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
os.environ['NEON_DB_URL'] = 'postgresql://neondb_owner:npg_JDbCa6ELqGQ2@ep-withered-shape-a7bd9hif-pooler.ap-southeast-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
os.environ['BETTER_AUTH_SECRET'] = 'pohwuyqoVn683bmFDoVzmtQq50Zn3bFV'
os.environ['SECRET_KEY'] = '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'
os.environ['OPENAI_API_KEY'] = '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'
os.environ['OPEN_ROUTER_API_KEY'] = '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'
os.environ['BACKEND_URL'] = 'https://muhammedsuhaib-raheel.hf.space'

print("Environment variables set.")

# First, create the tables
print("Creating database tables...")
try:
    from src.database.connection import create_tables
    create_tables()
    print("Tables created successfully.")
except Exception as e:
    print(f"Error creating tables: {e}")
    sys.exit(1)

# Then start the server
print("Starting the backend server...")
try:
    import uvicorn
    from main import app
    uvicorn.run(app, host="0.0.0.0", port=8001)
except Exception as e:
    print(f"Error starting server: {e}")
    sys.exit(1)