-- Create schemas for data warehouse architecture
-- STG (Staging): Raw data from external sources
-- ODS (Operational Data Store): Cleaned and validated data
-- DM (Data Mart): Aggregated and business-ready data

-- Create schemas
CREATE SCHEMA IF NOT EXISTS stg;
CREATE SCHEMA IF NOT EXISTS ods;
CREATE SCHEMA IF NOT EXISTS dm;

-- Grant permissions to puzzle_user
GRANT ALL PRIVILEGES ON SCHEMA stg TO puzzle_user;
GRANT ALL PRIVILEGES ON SCHEMA ods TO puzzle_user;
GRANT ALL PRIVILEGES ON SCHEMA dm TO puzzle_user;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA stg GRANT ALL ON TABLES TO puzzle_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA ods GRANT ALL ON TABLES TO puzzle_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA dm GRANT ALL ON TABLES TO puzzle_user;

-- Set default privileges for sequences
ALTER DEFAULT PRIVILEGES IN SCHEMA stg GRANT ALL ON SEQUENCES TO puzzle_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA ods GRANT ALL ON SEQUENCES TO puzzle_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA dm GRANT ALL ON SEQUENCES TO puzzle_user;

-- Create comments for documentation
COMMENT ON SCHEMA stg IS 'Staging schema for raw data from external sources';
COMMENT ON SCHEMA ods IS 'Operational Data Store schema for cleaned and validated data';
COMMENT ON SCHEMA dm IS 'Data Mart schema for aggregated and business-ready data';

-- Create a metadata table to track ETL processes
CREATE TABLE IF NOT EXISTS public.etl_metadata (
    id SERIAL PRIMARY KEY,
    process_name VARCHAR(100) NOT NULL,
    schema_name VARCHAR(50) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Grant permissions on metadata table
GRANT ALL PRIVILEGES ON TABLE public.etl_metadata TO puzzle_user;
GRANT ALL PRIVILEGES ON SEQUENCE public.etl_metadata_id_seq TO puzzle_user; 