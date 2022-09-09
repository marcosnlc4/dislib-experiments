-- SERVER
SERVER NAME: DEV
HOST: localhost
PORT: 5432

-- DATABASE
CREATE DATABASE project_dev;
GRANT ALL PRIVILEGES ON database project_dev TO postgres; 

-- USERS
CREATE USER user_dev WITH PASSWORD '';

-- SCHEMAS
CREATE SCHEMA schema_dev;

-- DATABASE CONNECTION USING NEW USER
GRANT ALL ON SCHEMA schema_dev TO user_dev;
GRANT ALL ON SCHEMA schema_dev TO postgres;
GRANT ALL ON SCHEMA schema_dev TO public;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA schema_dev TO user_dev;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA schema_dev TO user_dev;
GRANT ALL ON DATABASE project_dev TO user_dev;


-- SET SCHEMA SEARCH PATH TO USER
SET search_path = user_dev,schema_dev;
SHOW search_path;
