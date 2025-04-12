DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'mytestdb') THEN
        CREATE DATABASE mytestdb;
    END IF;
END
$$;