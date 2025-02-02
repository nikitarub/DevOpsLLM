#!/bin/bash

# Variables
DB_NAME="chatdb"
DB_USER="yourusername"
DB_PASSWORD="yourpass"

# Export DATABASE_URL environment variable
export DATABASE_URL="postgresql://${DB_USER}:${DB_PASSWORD}@localhost/${DB_NAME}"

# Create the database if it doesn't exist
if ! psql -U $DB_USER -lqt | cut -d \| -f 1 | grep -qw $DB_NAME; then
    echo "Creating database $DB_NAME..."
    createdb -U $DB_USER $DB_NAME
else
    echo "Database $DB_NAME already exists."
fi

# Create tables if they don't exist
psql -U $DB_USER -d $DB_NAME -f ./db/create.sql

# Start the FastAPI application using Uvicorn
echo "Starting FastAPI application..."
cd backend
uvicorn main:app --reload
