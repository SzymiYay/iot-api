#!/bin/bash

# Create virtual environment
python -m venv venv

# Check the operating system
if [[ "$OSTYPE" == "linux-gnu"* || "$OSTYPE" == "darwin"* ]]; then
    # Unix-based system (Linux or MacOS)
    source venv/bin/activate
elif [[ "$OSTYPE" == "cygwin" || "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows system
    source venv/Scripts/activate
else
    echo "Unknown operating system"
    exit 1
fi

# Install dependencies
pip install fastapi fastapi-sqlalchemy pydantic alembic psycopg2 uvicorn python-dotenv python-multipart python-jose[cryptography] passlib[bcrypt] python-multipart

# Run 
docker-compose up -d

# Create version folder in alembic
cd alembic
mkdir versions

# Migration
docker-compose run app alembic revision --autogenerate -m "New Migration"
docker-compose run app alembic upgrade head
