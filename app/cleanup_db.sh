#!/bin/bash

# Variables
DB_NAME="chatdb"
PG_USER="yourusername"  # Replace with your PostgreSQL username
PG_HOST="localhost"
PG_PORT="5432"

# Path to the SQL script
SQL_SCRIPT_PATH="./db/drop_table.sql"

# Run the SQL script to drop the database, connecting to the 'postgres' database
psql -h $PG_HOST -p $PG_PORT -U $PG_USER -d $DB_NAME -f $SQL_SCRIPT_PATH

# Check if psql command was successful
if [ $? -eq 0 ]; then
    echo "Database $DB_NAME cleaned up successfully."
else
    echo "Failed to clean up database $DB_NAME."
fi