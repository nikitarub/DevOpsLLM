-- Connect to the 'chatdb' database
\c chatdb;

-- Create a table for storing messages
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
