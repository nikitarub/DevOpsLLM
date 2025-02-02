-- drop_database.sql

DO $$
BEGIN
    -- Check if the database exists and drop it if it does
    IF EXISTS (SELECT 1 FROM pg_database WHERE datname = 'chatdb') THEN
        RAISE NOTICE 'Dropping database chatdb';
        EXECUTE 'DROP DATABASE "chatdb"';
    ELSE
        RAISE NOTICE 'Database chatdb does not exist';
    END IF;
END $$;
