-- drop_table.sql

DO $$
BEGIN
    -- Check if the database exists and drop it if it does
    IF EXISTS (SELECT 1 FROM pg_database WHERE datname = 'chatdb') THEN
        RAISE NOTICE 'Dropping tables in chatdb';

        -- Connect to the 'chatdb' database and drop the 'messages' table
        EXECUTE 'DROP TABLE IF EXISTS messages CASCADE;';
    ELSE
        RAISE NOTICE 'Database chatdb does not exist';
    END IF;
END $$;