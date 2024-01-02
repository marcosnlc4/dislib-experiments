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
SET search_path = user_dev,schema_dev; --KMEANS
SET search_path = user_dev,schema_dev_matmul; --MATMUL
SET search_path = user_dev,schema_dev_matmul_fma; --MATMUL FMA
SHOW search_path;















--TEST ONLY
-- SCHEMAS
CREATE SCHEMA schema_test;
SHOW search_path;

-- DATABASE CONNECTION USING NEW USER
GRANT ALL ON SCHEMA schema_test TO user_dev;
GRANT ALL ON SCHEMA schema_test TO postgres;
GRANT ALL ON SCHEMA schema_test TO public;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA schema_test TO user_dev;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA schema_test TO user_dev;
GRANT ALL ON DATABASE project_dev TO user_dev;


-- SET SCHEMA SEARCH PATH TO USER
SET search_path = user_dev,schema_test;
SHOW search_path;

--FILLING TEST TABLES WITH PRODUCTION TABLES
--SCHEMA_DEV
select * into schema_test.device from schema_dev.DEVICE
select * into schema_test.FUNCTION from schema_dev.FUNCTION
select * into schema_test.ALGORITHM from schema_dev.ALGORITHM
select * into schema_test.CONFIGURATION from schema_dev.CONFIGURATION
select * into schema_test.RESOURCE from schema_dev.RESOURCE WHERE ID_RESOURCE = 18
select * into schema_test.DATASET from schema_dev.DATASET WHERE ID_DATASET IN (27,28,29,39)
select * into schema_test.PARAMETER_TYPE from schema_dev.PARAMETER_TYPE WHERE ID_PARAMETER_TYPE BETWEEN 17 AND 28
select * into schema_test.PARAMETER from schema_dev.PARAMETER WHERE ID_RESOURCE = 18 AND ID_DATASET IN (27,28,29,39) AND ID_PARAMETER_TYPE BETWEEN 17 AND 28
select A.* into schema_test.EXPERIMENT_RAW from schema_dev.EXPERIMENT_RAW A INNER JOIN schema_dev.PARAMETER B ON (A.ID_PARAMETER = B.ID_PARAMETER) WHERE ID_RESOURCE = 18 AND ID_DATASET IN (27,28,29,39) AND ID_PARAMETER_TYPE BETWEEN 17 AND 28

--SCHEMA_DEV_MATMUL
select * into schema_test.device from schema_dev_matmul.DEVICE
select * into schema_test.FUNCTION from schema_dev_matmul.FUNCTION
select * into schema_test.ALGORITHM from schema_dev_matmul.ALGORITHM
select * into schema_test.CONFIGURATION from schema_dev_matmul.CONFIGURATION
select * into schema_test.RESOURCE from schema_dev_matmul.RESOURCE WHERE ID_RESOURCE = 1
select * into schema_test.DATASET from schema_dev_matmul.DATASET WHERE ID_DATASET IN (3,4,5,8) --DS_DATASET IN ('S_2GB_1','S_2GB_2','S_8GB_1','S_32GB_1')
select * into schema_test.PARAMETER_TYPE from schema_dev_matmul.PARAMETER_TYPE WHERE ID_PARAMETER_TYPE IN (1,2,5,6)
select * into schema_test.PARAMETER from schema_dev_matmul.PARAMETER WHERE ID_RESOURCE = 1 AND ID_DATASET IN (3,4,5,8) AND ID_PARAMETER_TYPE IN (1,2,5,6)
select A.* into schema_test.EXPERIMENT_RAW from schema_dev_matmul.EXPERIMENT_RAW A INNER JOIN schema_dev_matmul.PARAMETER B ON (A.ID_PARAMETER = B.ID_PARAMETER) WHERE ID_RESOURCE = 1 AND ID_DATASET IN (3,4,5,8) AND ID_PARAMETER_TYPE IN (1,2,5,6)


--SCHEMA_DEV_MATMUL_FMA
select * into schema_test.device from schema_dev_matmul_fma.DEVICE
select * into schema_test.FUNCTION from schema_dev_matmul_fma.FUNCTION
select * into schema_test.ALGORITHM from schema_dev_matmul_fma.ALGORITHM
select * into schema_test.CONFIGURATION from schema_dev_matmul_fma.CONFIGURATION
select * into schema_test.RESOURCE from schema_dev_matmul_fma.RESOURCE WHERE ID_RESOURCE = 1
select * into schema_test.DATASET from schema_dev_matmul_fma.DATASET WHERE ID_DATASET = 4--DS_DATASET = 'S_8GB_1'
select * into schema_test.PARAMETER_TYPE from schema_dev_matmul_fma.PARAMETER_TYPE WHERE ID_PARAMETER_TYPE = 1
select * into schema_test.PARAMETER from schema_dev_matmul_fma.PARAMETER WHERE ID_RESOURCE = 1 AND ID_DATASET = 4 AND ID_PARAMETER_TYPE = 1
select A.* into schema_test.EXPERIMENT_RAW from schema_dev_matmul_fma.EXPERIMENT_RAW A INNER JOIN schema_dev_matmul_fma.PARAMETER B ON (A.ID_PARAMETER = B.ID_PARAMETER) WHERE ID_RESOURCE = 1 AND ID_DATASET = 4 AND ID_PARAMETER_TYPE = 1


DROP TABLE schema_test.EXPERIMENT_RAW;
DROP TABLE schema_test.EXPERIMENT;
DROP TABLE schema_test.PARAMETER;
DROP TABLE schema_test.PARAMETER_TYPE;
DROP TABLE schema_test.DATASET;
DROP TABLE schema_test.RESOURCE;
DROP TABLE schema_test.CONFIGURATION;
DROP TABLE schema_test.FUNCTION;
DROP TABLE schema_test.ALGORITHM;
DROP TABLE schema_test.DEVICE;