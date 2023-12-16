-- PROCEDURES


-- INSERT DATA
CREATE OR REPLACE PROCEDURE INSERT_DATA()
LANGUAGE plpgsql
AS $BODY$
DECLARE
	-- ARRAYS
	arr_ds_device text[] := '{
								{CPU,
								GPU}
							 }'; -- Device description
	-- Algorithm parameters (DS_ALGORITHM)
	arr_algorithm_data text[] := '{
									{MATMUL_DISLIB}
								  }';
	-- Function parameters (CD_FUNCTION, DS_FUNCTION, ID_ALGORITHM)
	arr_function_data text[] := '{
									{1,MATMUL_FUNC,1},
									{2,ADD_FUNC,1}
								 }';
	arr_id_device bigint[];
	arr_id_algorithm bigint[];
	arr_device_config bigint[];
	-- Resource parameters (DS_RESOURCE, NR_NODES, NR_COMPUTING_UNITS_CPU, NR_COMPUTING_UNITS_GPU, VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT, VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT)
	arr_resource_data text[] := '{
									{MINOTAURO_9_NODES_1_CORE,9,1,1,128000000000,12000000000}
								 }';
	-- Data set parameters (DS_DATASET, VL_DATASET_MEMORY_SIZE, DS_DATA_TYPE, VL_DATA_TYPE_MEMORY_SIZE, VL_DATASET_DIMENSION, VL_DATASET_ROW_DIMENSION, VL_DATASET_COLUMN_DIMENSION, NR_RANDOM_STATE, VL_DATA_SPARSITY, VL_DATA_SKEWNESS)
	arr_dataset_data text[] := '{	
									{S_128MB_1,128000000,FLOAT64,8,16000000,4000,4000,170,0.0,0.0},
									{S_512MB_1,512000000,FLOAT64,8,64000000,8000,8000,170,0.0,0.0},
									{S_2GB_1,2048000000,FLOAT64,8,256000000,16000,16000,170,0.0,0.0},
									{S_8GB_1,8192000000,FLOAT64,8,1024000000,32000,32000,170,0.0,0.0},
									{S_32GB_1,32768000000,FLOAT64,8,4096000000,64000,64000,170,0.0,0.0},
									{S_128MB_2,128000000,FLOAT64,8,16000000,4000,4000,170,1.0,0.0},
									{S_512MB_2,512000000,FLOAT64,8,64000000,8000,8000,170,1.0,0.0},
									{S_2GB_2,2048000000,FLOAT64,8,256000000,16000,16000,170,1.0,0.0},
									{S_8GB_2,8192000000,FLOAT64,8,1024000000,32000,32000,170,1.0,0.0},
									{S_32GB_2,32768000000,FLOAT64,8,4096000000,64000,64000,170,1.0,0.0},
									{S_128MB_3,128000000,FLOAT64,8,16000000,4000,4000,170,0.0,1.0},
									{S_512MB_3,512000000,FLOAT64,8,64000000,8000,8000,170,0.0,1.0},
									{S_2GB_3,2048000000,FLOAT64,8,256000000,16000,16000,170,0.0,1.0},
									{S_8GB_3,8192000000,FLOAT64,8,1024000000,32000,32000,170,0.0,1.0},
									{S_32GB_3,32768000000,FLOAT64,8,4096000000,64000,64000,170,0.0,1.0}
								}';
	-- Number of repetitions for each parameter set
	arr_nr_iteration bigint[] := '{
									{5}
								  }';

	-- Parameter type (DS_PARAMETER_TYPE, DS_PARAMETER_ATTRIBUTE)
	-- VAR_BLOCK_CAPACITY_SIZE: percentage of the data set size
	-- VAR_PARALLELISM_LEVEL: minimize inter parallelism and maximize intra parallelism (grid_row = 1) or maximize inter parallelism and minimize intra parallelism (single-element blocks (1x1))
	-- VAR_GRID_ROW: max_grid_rows__fixed_grid_columns
	-- VAR_GRID_COLUMN: fixed_grid_rows__increment_pct_grid_columns
	-- VAR_CORES_CLUSTER_1: grid_row_dimension__grid_column_dimension
	-- VAR_CORES_SINGLE_NODE_1: grid_row_dimension__grid_column_dimension
	arr_parameter_type_data text[] := '{
									{VAR_GRID_SHAPE_MATMUL_1,32MAXCORES_1,TrunkCT,0.6.4,es.bsc.compss.scheduler.orderstrict.fifo.FifoTS,NULL,GPFS,FALSE},
									{VAR_GRID_SHAPE_MATMUL_2,32MAXCORES_1,TrunkCT,0.6.4,es.bsc.compss.scheduler.lookahead.successors.fifolocality.FifoLocalityTS,NULL,LOCAL_DISK,FALSE},
									{VAR_GRID_SHAPE_MATMUL_3,32MAXCORES_1,TrunkCT,0.6.4,es.bsc.compss.scheduler.orderstrict.fifo.FifoTS,NULL,GPFS,TRUE},
									{VAR_GRID_SHAPE_MATMUL_4,32MAXCORES_1,TrunkCT,0.6.4,es.bsc.compss.scheduler.lookahead.successors.fifolocality.FifoLocalityTS,NULL,LOCAL_DISK,TRUE},
									{VAR_GRID_SHAPE_MATMUL_5,32MAXCORES_1,TrunkCT,0.6.4,es.bsc.compss.scheduler.lookahead.successors.fifolocality.FifoLocalityTS,NULL,GPFS,FALSE},
									{VAR_GRID_SHAPE_MATMUL_6,32MAXCORES_1,TrunkCT,0.6.4,es.bsc.compss.scheduler.orderstrict.fifo.FifoTS,NULL,LOCAL_DISK,FALSE}
								}';
								
	arr_id_resource bigint[];
	arr_id_dataset bigint[];
	arr_cd_configuration bigint[];
	arr_id_parameter_type bigint[];
	
	-- variables
	var_id_algorithm bigint;
	var_nr_function_config bigint;
	var_id_parameter_type bigint;
	var_ds_parameter_type text;
	var_ds_parameter_attribute text;
	
	-- iterators
	arr_text_iterator text[];
	text_iterator text;
	bigint_iterator bigint;
	id_algorithm_iterator bigint;

BEGIN
	
	SET search_path = user_dev,schema_dev_matmul;

	--DEVICE TABLE
	FOREACH text_iterator IN ARRAY arr_ds_device
	LOOP
		IF EXISTS(SELECT FROM DEVICE WHERE DS_DEVICE = text_iterator)
		THEN
		
			CONTINUE;
			
		ELSE
		
			INSERT INTO DEVICE(ID_DEVICE,DS_DEVICE)
			VALUES
			(DEFAULT,text_iterator);
			
		END IF;	
	END LOOP;
	
	
	-- ALGORITHM TABLE
	FOREACH text_iterator IN ARRAY arr_algorithm_data
	LOOP
		IF EXISTS(SELECT FROM ALGORITHM WHERE DS_ALGORITHM = text_iterator)
		THEN
		
			CONTINUE;
			
		ELSE
		
			INSERT INTO ALGORITHM(ID_ALGORITHM,DS_ALGORITHM)
			VALUES
			(DEFAULT,text_iterator);
		
		END IF;
	END LOOP;
	
	
	-- FUNCTION TABLE
	arr_id_device := ARRAY(SELECT DISTINCT ID_DEVICE FROM DEVICE ORDER BY ID_DEVICE);
	FOREACH arr_text_iterator SLICE 1 IN ARRAY arr_function_data
	LOOP
		
		var_id_algorithm := (SELECT DISTINCT ID_ALGORITHM FROM ALGORITHM WHERE ID_ALGORITHM = cast(arr_text_iterator[3] AS BIGINT) ORDER BY ID_ALGORITHM);
		
		FOREACH bigint_iterator IN ARRAY arr_id_device
		LOOP
		
			IF EXISTS(SELECT FROM FUNCTION WHERE CD_FUNCTION = cast(arr_text_iterator[1] AS BIGINT) AND DS_FUNCTION = arr_text_iterator[2] AND ID_DEVICE = bigint_iterator AND ID_ALGORITHM = var_id_algorithm)
			THEN

				CONTINUE;

			ELSE
			
					INSERT INTO FUNCTION(ID_FUNCTION,CD_FUNCTION,DS_FUNCTION,ID_DEVICE,ID_ALGORITHM)
					VALUES
					(DEFAULT,cast(arr_text_iterator[1] AS BIGINT), arr_text_iterator[2],bigint_iterator,var_id_algorithm);

			END IF;
			
		END LOOP;
		
	END LOOP;
	
	
	-- CONFIGURATION TABLE
	
	-- REMOVE PREVIOUS CONFIGURATIONS
	DELETE FROM CONFIGURATION;
	ALTER SEQUENCE configuration_id_configuration_seq RESTART WITH 1;
		
	-- SELECT AVAILABLE ALGORITHMS
	arr_id_algorithm := ARRAY(SELECT DISTINCT A.ID_ALGORITHM FROM ALGORITHM A ORDER BY A.ID_ALGORITHM);
	
	-- FOR EACH ALGORITHM
	FOREACH bigint_iterator IN ARRAY arr_id_algorithm
	LOOP
								
		-- GET THE TOTAL NUMBER OF FUNCTIONS OF AN ALGORITHM
		var_nr_function_config := (
									SELECT
									COUNT(DISTINCT CD_FUNCTION)
									FROM
									ALGORITHM A 
									INNER JOIN FUNCTION B ON (A.ID_ALGORITHM = B.ID_ALGORITHM)
									INNER JOIN DEVICE C ON (B.ID_DEVICE = C.ID_DEVICE)
									WHERE
									A.ID_ALGORITHM = bigint_iterator
								);
		
		CALL RECURSIVE_CONFIGURATION_PERMUTATION(var_nr_function_config, arr_device_config, 0, bigint_iterator);

	END LOOP;
	
	
	-- RESOURCE TABLE
	FOREACH arr_text_iterator SLICE 1 IN ARRAY arr_resource_data
	LOOP
		IF EXISTS(SELECT FROM RESOURCE
				  WHERE DS_RESOURCE = arr_text_iterator[1]
				  AND NR_NODES = CAST(arr_text_iterator[2] AS BIGINT)
				  AND NR_COMPUTING_UNITS_CPU = CAST(arr_text_iterator[3] AS BIGINT)
				  AND NR_COMPUTING_UNITS_GPU = CAST(arr_text_iterator[4] AS BIGINT)
				  AND VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT = CAST(arr_text_iterator[5] AS BIGINT)
				  AND VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT = CAST(arr_text_iterator[6] AS BIGINT)									
				 )
		THEN
			
			CONTINUE;
			
		ELSE
		
			INSERT INTO RESOURCE(ID_RESOURCE,
								 DS_RESOURCE,
								 NR_NODES,
								 NR_COMPUTING_UNITS_CPU,
								 NR_COMPUTING_UNITS_GPU,
								 VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
								 VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT)
			VALUES
			(DEFAULT,
			 arr_text_iterator[1],
			 CAST(arr_text_iterator[2] AS BIGINT),
			 CAST(arr_text_iterator[3] AS BIGINT),
			 CAST(arr_text_iterator[4] AS BIGINT),
			 CAST(arr_text_iterator[5] AS BIGINT),
			 CAST(arr_text_iterator[6] AS BIGINT));
			 
		END IF;
		
	END LOOP;

	
	-- DATASET TABLE
	FOREACH arr_text_iterator SLICE 1 IN ARRAY arr_dataset_data
	LOOP
		
		IF EXISTS(SELECT FROM DATASET
				  WHERE DS_DATASET = arr_text_iterator[1]
				  AND VL_DATASET_MEMORY_SIZE = CAST(arr_text_iterator[2] AS BIGINT)
				  AND DS_DATA_TYPE = arr_text_iterator[3]
				  AND VL_DATA_TYPE_MEMORY_SIZE = CAST(arr_text_iterator[4] AS BIGINT)
				  AND VL_DATASET_DIMENSION = CAST(arr_text_iterator[5] AS BIGINT)
				  AND VL_DATASET_ROW_DIMENSION = CAST(arr_text_iterator[6] AS BIGINT)
				  AND VL_DATASET_COLUMN_DIMENSION = CAST(arr_text_iterator[7] AS BIGINT)
				  AND NR_RANDOM_STATE = CAST(arr_text_iterator[8] AS BIGINT)
				  AND VL_DATA_SPARSITY = CAST(arr_text_iterator[9] AS DOUBLE PRECISION)
				  AND VL_DATA_SKEWNESS = CAST(arr_text_iterator[10] AS DOUBLE PRECISION)
				 )
		THEN
		
			CONTINUE;
		
		ELSE
		
			INSERT INTO DATASET(ID_DATASET,
								DS_DATASET,
								VL_DATASET_MEMORY_SIZE,
								DS_DATA_TYPE,
								VL_DATA_TYPE_MEMORY_SIZE,
								VL_DATASET_DIMENSION,
								VL_DATASET_ROW_DIMENSION,
								VL_DATASET_COLUMN_DIMENSION,
								NR_RANDOM_STATE,
								VL_DATA_SPARSITY,
								VL_DATA_SKEWNESS)
			VALUES
			(DEFAULT,
			 arr_text_iterator[1],
			 CAST(arr_text_iterator[2] AS BIGINT),
			 arr_text_iterator[3],
			 CAST(arr_text_iterator[4] AS BIGINT),
			 CAST(arr_text_iterator[5] AS BIGINT),
			 CAST(arr_text_iterator[6] AS BIGINT),
			 CAST(arr_text_iterator[7] AS BIGINT),
			 CAST(arr_text_iterator[8] AS BIGINT),
			 CAST(arr_text_iterator[9] AS DOUBLE PRECISION),
			 CAST(arr_text_iterator[10] AS DOUBLE PRECISION));
		
		END IF;
	
	END LOOP;


	-- PARAMETER TYPE TABLE
	FOREACH arr_text_iterator SLICE 1 IN ARRAY arr_parameter_type_data
	LOOP
		IF EXISTS(SELECT FROM PARAMETER_TYPE
				  WHERE DS_PARAMETER_TYPE = arr_text_iterator[1]
				  AND DS_PARAMETER_ATTRIBUTE = arr_text_iterator[2]
				  AND DS_COMPSS_VERSION = arr_text_iterator[3]
				  AND DS_DISLIB_VERSION = arr_text_iterator[4]
				  AND DS_SCHDEULER = arr_text_iterator[5]
				  --AND NR_CLUSTER = CAST(arr_text_iterator[6] AS BIGINT) --ONLY FOR KMEANS VERSION
				  AND DS_STORAGE = arr_text_iterator[7]
				  AND BL_TRANSPOSE_MATRIX = CAST(arr_text_iterator[8] AS BOOLEAN)
				 )
		THEN
			
			CONTINUE;
			
		ELSE
		
			INSERT INTO PARAMETER_TYPE(ID_PARAMETER_TYPE,
										DS_PARAMETER_TYPE,
										DS_PARAMETER_ATTRIBUTE,
										DS_COMPSS_VERSION,
										DS_DISLIB_VERSION,
										DS_SCHDEULER,
										NR_CLUSTER,
										DS_STORAGE,
										BL_TRANSPOSE_MATRIX)
			VALUES
			(DEFAULT,
			 arr_text_iterator[1],
			 arr_text_iterator[2],
			 arr_text_iterator[3],
			 arr_text_iterator[4],
			 arr_text_iterator[5],
			 CAST(arr_text_iterator[6] AS BIGINT),
			 arr_text_iterator[7],
			 CAST(arr_text_iterator[8] AS BOOLEAN));
			 
		END IF;
		
	END LOOP;
	
	
	-- PARAMETER TABLE
	-- SELECT AVAILABLE RESOURCES
	arr_id_algorithm := ARRAY(SELECT DISTINCT A.ID_ALGORITHM FROM ALGORITHM A ORDER BY A.ID_ALGORITHM);
	arr_id_resource := ARRAY(SELECT DISTINCT ID_RESOURCE FROM RESOURCE ORDER BY ID_RESOURCE);
	arr_id_dataset := ARRAY(SELECT DISTINCT ID_DATASET FROM DATASET ORDER BY ID_DATASET);
	arr_id_parameter_type := ARRAY(SELECT DISTINCT ID_PARAMETER_TYPE FROM PARAMETER_TYPE ORDER BY ID_PARAMETER_TYPE);
	
	-- INSERT NEW PARAMETERS
	-- FOR EACH ALGORITHM
	FOREACH id_algorithm_iterator IN ARRAY arr_id_algorithm
	LOOP
		arr_cd_configuration := ARRAY(SELECT DISTINCT CD_CONFIGURATION FROM CONFIGURATION WHERE ID_ALGORITHM = id_algorithm_iterator ORDER BY CD_CONFIGURATION);
		-- FOR EACH "NUMBER ITERATIONS"
		FOREACH bigint_iterator IN ARRAY arr_nr_iteration
		LOOP

			-- FOR EACH PARAMETER TYPE
			FOREACH var_id_parameter_type IN ARRAY arr_id_parameter_type
			LOOP

				var_ds_parameter_type := (SELECT DISTINCT DS_PARAMETER_TYPE FROM PARAMETER_TYPE WHERE ID_PARAMETER_TYPE = var_id_parameter_type);
				var_ds_parameter_attribute := (SELECT DISTINCT DS_PARAMETER_ATTRIBUTE FROM PARAMETER_TYPE WHERE ID_PARAMETER_TYPE = var_id_parameter_type);

				CALL PARAMETER_INSERT(id_algorithm_iterator, bigint_iterator, var_id_parameter_type, var_ds_parameter_type, var_ds_parameter_attribute, arr_id_resource, arr_id_dataset, arr_cd_configuration);

			END LOOP;

		END LOOP;
		
	END LOOP;
	
END; 
$BODY$;



-- DELETE TABLES AND RESET SEQUENCES
CREATE OR REPLACE PROCEDURE DELETE_TABLES()
LANGUAGE plpgsql
AS $BODY$
BEGIN

	SET search_path = user_dev,schema_dev_matmul;

	-- DELETE TABLES
	DELETE FROM EXPERIMENT_RAW;
	DELETE FROM EXPERIMENT;
	DELETE FROM PARAMETER;
	DELETE FROM PARAMETER_TYPE;
	DELETE FROM DATASET;
	DELETE FROM RESOURCE;
	DELETE FROM CONFIGURATION;
	DELETE FROM FUNCTION;
	DELETE FROM ALGORITHM;
	DELETE FROM DEVICE;

	-- RESET SEQUENCES
	ALTER SEQUENCE experiment_raw_id_experiment_seq RESTART WITH 1;
	ALTER SEQUENCE experiment_id_experiment_seq RESTART WITH 1;
	ALTER SEQUENCE parameter_id_parameter_seq RESTART WITH 1;
	ALTER SEQUENCE parameter_type_id_parameter_type_seq RESTART WITH 1;
	ALTER SEQUENCE dataset_id_dataset_seq RESTART WITH 1;
	ALTER SEQUENCE resource_id_resource_seq RESTART WITH 1;
	ALTER SEQUENCE configuration_id_configuration_seq RESTART WITH 1;
	ALTER SEQUENCE function_id_function_seq RESTART WITH 1;
	ALTER SEQUENCE algorithm_id_algorithm_seq RESTART WITH 1;
	ALTER SEQUENCE device_id_device_seq RESTART WITH 1;
END; 
$BODY$;


-- CREATE TABLES
CREATE OR REPLACE PROCEDURE CREATE_TABLES()
LANGUAGE plpgsql
AS $BODY$
BEGIN

	SET search_path = user_dev,schema_dev_matmul;

	CREATE TABLE DEVICE
	(
		ID_DEVICE BIGSERIAL PRIMARY KEY,
		DS_DEVICE VARCHAR
	);

	CREATE TABLE ALGORITHM
	(
		ID_ALGORITHM BIGSERIAL PRIMARY KEY,
		DS_ALGORITHM VARCHAR
	);

	CREATE TABLE FUNCTION
	(
		ID_FUNCTION BIGSERIAL PRIMARY KEY,
		CD_FUNCTION BIGINT,
		DS_FUNCTION VARCHAR,
		ID_DEVICE BIGINT REFERENCES DEVICE(ID_DEVICE),
		ID_ALGORITHM BIGINT REFERENCES ALGORITHM(ID_ALGORITHM)
	);
	
	CREATE TABLE CONFIGURATION
	(
		ID_CONFIGURATION BIGSERIAL PRIMARY KEY,
		CD_CONFIGURATION BIGINT,
		ID_ALGORITHM BIGINT,
		CD_FUNCTION BIGINT,
		ID_DEVICE BIGINT
	);
	
	CREATE TABLE RESOURCE
	(
		ID_RESOURCE BIGSERIAL PRIMARY KEY,
		DS_RESOURCE VARCHAR,
		NR_NODES BIGINT,
		NR_COMPUTING_UNITS_CPU BIGINT,
		NR_COMPUTING_UNITS_GPU BIGINT,
		VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT BIGINT,
		VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT BIGINT
	);

	CREATE TABLE DATASET
	(
		ID_DATASET BIGSERIAL PRIMARY KEY,
		DS_DATASET VARCHAR,
		VL_DATASET_MEMORY_SIZE BIGINT,
		DS_DATA_TYPE VARCHAR,
		VL_DATA_TYPE_MEMORY_SIZE BIGINT,
		VL_DATASET_DIMENSION BIGINT,
		VL_DATASET_ROW_DIMENSION BIGINT,
		VL_DATASET_COLUMN_DIMENSION BIGINT,
		NR_RANDOM_STATE BIGINT,
		VL_DATA_SPARSITY DOUBLE PRECISION,
		VL_DATA_SKEWNESS DOUBLE PRECISION
	);

	CREATE TABLE PARAMETER_TYPE
	(
		ID_PARAMETER_TYPE BIGSERIAL PRIMARY KEY,
		DS_PARAMETER_TYPE VARCHAR,
		DS_PARAMETER_ATTRIBUTE VARCHAR,
		DS_COMPSS_VERSION VARCHAR,
		DS_DISLIB_VERSION VARCHAR,
		DS_SCHDEULER VARCHAR,
		NR_CLUSTER BIGINT,
		DS_STORAGE VARCHAR,
		BL_TRANSPOSE_MATRIX BOOLEAN
	);
	
	CREATE TABLE PARAMETER
	(
		ID_PARAMETER BIGSERIAL PRIMARY KEY,
		CD_PARAMETER BIGINT,
		CD_CONFIGURATION BIGINT,
		ID_ALGORITHM BIGINT REFERENCES ALGORITHM(ID_ALGORITHM),
		ID_FUNCTION BIGINT REFERENCES FUNCTION(ID_FUNCTION),
		ID_DATASET BIGINT REFERENCES DATASET(ID_DATASET),
		ID_RESOURCE BIGINT REFERENCES RESOURCE(ID_RESOURCE),
		ID_PARAMETER_TYPE BIGINT REFERENCES PARAMETER_TYPE(ID_PARAMETER_TYPE),
		NR_ITERATIONS BIGINT,
		VL_GRID_ROW_DIMENSION BIGINT,
		VL_GRID_COLUMN_DIMENSION BIGINT,
		VL_BLOCK_ROW_DIMENSION BIGINT,
		VL_BLOCK_COLUMN_DIMENSION BIGINT,
		VL_BLOCK_MEMORY_SIZE BIGINT,
		VL_BLOCK_MEMORY_SIZE_PERCENT_CPU DOUBLE PRECISION,
		VL_BLOCK_MEMORY_SIZE_PERCENT_GPU DOUBLE PRECISION
	);
	
	CREATE TABLE EXPERIMENT
	(
		ID_EXPERIMENT BIGSERIAL PRIMARY KEY,
		ID_PARAMETER BIGINT REFERENCES PARAMETER(ID_PARAMETER),
		VL_TOTAL_EXECUTION_TIME DOUBLE PRECISION,
		VL_INTER_TASK_EXECUTION_TIME DOUBLE PRECISION,
		VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC DOUBLE PRECISION,
		VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC DOUBLE PRECISION,
		VL_COMMUNICATION_TIME DOUBLE PRECISION,
		DT_PROCESSING TIMESTAMP
	);

	CREATE UNIQUE INDEX idx_experiment ON EXPERIMENT (ID_PARAMETER,VL_TOTAL_EXECUTION_TIME,VL_INTER_TASK_EXECUTION_TIME,VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,VL_COMMUNICATION_TIME,DT_PROCESSING);

	CREATE TABLE EXPERIMENT_RAW
	(
		ID_EXPERIMENT BIGSERIAL PRIMARY KEY,
		ID_PARAMETER BIGINT REFERENCES PARAMETER(ID_PARAMETER),
		NR_ALGORITHM_ITERATION BIGINT,
		NR_FUNCTION_ITERATION BIGINT,
		NR_TASK BIGINT,
		VL_TOTAL_EXECUTION_TIME DOUBLE PRECISION,
		VL_INTER_TASK_EXECUTION_TIME DOUBLE PRECISION,
		VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC DOUBLE PRECISION,
		VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC DOUBLE PRECISION,
		VL_COMMUNICATION_TIME_1 DOUBLE PRECISION,
		VL_COMMUNICATION_TIME_2 DOUBLE PRECISION,
		VL_ADDITIONAL_TIME_1 DOUBLE PRECISION,
		VL_ADDITIONAL_TIME_2 DOUBLE PRECISION,
		DT_PROCESSING TIMESTAMP
	);

	CREATE UNIQUE INDEX idx_experiment_raw ON EXPERIMENT_RAW (ID_PARAMETER,NR_ALGORITHM_ITERATION,NR_FUNCTION_ITERATION,NR_TASK,VL_TOTAL_EXECUTION_TIME,VL_INTER_TASK_EXECUTION_TIME,VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,VL_COMMUNICATION_TIME_1,VL_COMMUNICATION_TIME_2,VL_ADDITIONAL_TIME_1,VL_ADDITIONAL_TIME_2,DT_PROCESSING);


END; 
$BODY$;



-- DROP TABLES
CREATE OR REPLACE PROCEDURE DROP_TABLES()
LANGUAGE plpgsql
AS $BODY$
BEGIN

	SET search_path = user_dev,schema_dev_matmul;
	
	DROP TABLE EXPERIMENT_RAW;
	DROP TABLE EXPERIMENT;
	DROP TABLE PARAMETER;
	DROP TABLE PARAMETER_TYPE;
	DROP TABLE DATASET;
	DROP TABLE RESOURCE;
	DROP TABLE CONFIGURATION;
	DROP TABLE FUNCTION;
	DROP TABLE ALGORITHM;
	DROP TABLE DEVICE;
END; 
$BODY$;





-- RECURSIVE_CONFIGURATION_INSERT
CREATE OR REPLACE PROCEDURE RECURSIVE_CONFIGURATION_PERMUTATION(var_nr_function_config bigint, arr_device_config bigint[], var_i bigint, var_id_algorithm bigint)
LANGUAGE plpgsql
AS $BODY$

BEGIN

	SET search_path = user_dev,schema_dev_matmul;
	
    IF var_i = var_nr_function_config THEN
        -- insert item
        CALL CONFIGURATION_INSERT(var_nr_function_config, arr_device_config, var_i, var_id_algorithm);
		RETURN;
    END IF;
	
    arr_device_config[var_i] := 1;
    CALL RECURSIVE_CONFIGURATION_PERMUTATION(var_nr_function_config, arr_device_config, var_i + 1, var_id_algorithm);
 
    arr_device_config[var_i] := 2;
    CALL RECURSIVE_CONFIGURATION_PERMUTATION(var_nr_function_config, arr_device_config, var_i + 1, var_id_algorithm);

END;
$BODY$;



-- CONFIGURATION_INSERT
CREATE OR REPLACE PROCEDURE CONFIGURATION_INSERT(var_nr_function_config bigint, arr_device_config bigint[], var_i bigint, var_id_algorithm bigint)
LANGUAGE plpgsql
AS $BODY$
DECLARE
    var_cd_function bigint := 1;
    var_id_device_config bigint;
    var_cd_configuration_2 bigint;

BEGIN

	SET search_path = user_dev,schema_dev_matmul;

    var_cd_configuration_2 := 
    (
        COALESCE(
            (SELECT
            MAX(CD_CONFIGURATION)
            FROM
            CONFIGURATION A
            WHERE
            A.ID_ALGORITHM = var_id_algorithm),0
            )
            
    );

    var_cd_configuration_2 := var_cd_configuration_2 + 1;

    FOREACH var_id_device_config IN ARRAY arr_device_config
    LOOP
	
		INSERT INTO CONFIGURATION(CD_CONFIGURATION,ID_ALGORITHM,CD_FUNCTION,ID_DEVICE)
		(
			SELECT
			var_cd_configuration_2 AS CD_CONFIGURATION,
			A.ID_ALGORITHM,
			B.CD_FUNCTION,
			C.ID_DEVICE
			FROM
			ALGORITHM A 
			INNER JOIN FUNCTION B ON (A.ID_ALGORITHM = B.ID_ALGORITHM)
			INNER JOIN DEVICE C ON (B.ID_DEVICE = C.ID_DEVICE)
			WHERE
			A.ID_ALGORITHM = var_id_algorithm
			AND B.CD_FUNCTION = var_cd_function
			AND C.ID_DEVICE = var_id_device_config
		);
		
        var_cd_function = var_cd_function + 1;
		
    END LOOP;
END;
$BODY$;



-- PARAMETER_INSERT
CREATE OR REPLACE PROCEDURE PARAMETER_INSERT(id_algorithm_iterator bigint, bigint_iterator bigint, var_id_parameter_type bigint, var_ds_parameter_type text, var_ds_parameter_attribute text, arr_id_resource bigint[], arr_id_dataset bigint[], arr_cd_configuration bigint[])
LANGUAGE plpgsql
AS $BODY$
#variable_conflict use_column
DECLARE
	var_ds_parameter_attribute_numeric numeric;
	id_resource_iterator bigint;
	id_dataset_iterator bigint;
	cd_configuration_iterator bigint;
	id_parameter_type bigint;
	id_configuration bigint;
	arr_id_configuration bigint[];
	var_cd_parameter bigint;
	flag_increment_cd_parameter boolean default TRUE;
	flag_insert boolean default TRUE;
	param_grid_row_dimension text;
	param_grid_column_dimension text;
	grid_row_dimension bigint;
	grid_column_dimension bigint;

	-- VAR_GRID_ROW
	increment_exp_grid_row_dimension bigint;
	arr_grid_row_dimension bigint[];
	max_grid_row_dimension bigint;
	i_grid_row_dimension bigint;

	-- VAR_GRID_COLUMN
	increment_percent_grid_col_dataset_col numeric;
	percent_grid_col_dataset_col numeric;
	arr_percent_grid_col_dataset_col numeric[];
	i_percent_grid_col_dataset_col numeric;

BEGIN

	SET search_path = user_dev,schema_dev_matmul;
	
	-- SET INITIAL VALUE FOR CD_PARAMETER
	var_cd_parameter := (SELECT COALESCE(MAX(CD_PARAMETER),0) FROM PARAMETER);

	IF (var_ds_parameter_type = 'VAR_GRID_SHAPE_MATMUL_1' or var_ds_parameter_type = 'VAR_GRID_SHAPE_MATMUL_2' or var_ds_parameter_type = 'VAR_GRID_SHAPE_MATMUL_3' or var_ds_parameter_type = 'VAR_GRID_SHAPE_MATMUL_4' or var_ds_parameter_type = 'VAR_GRID_SHAPE_MATMUL_5' or var_ds_parameter_type = 'VAR_GRID_SHAPE_MATMUL_6')
	THEN

		arr_id_resource := ARRAY(SELECT DISTINCT ID_RESOURCE FROM RESOURCE ORDER BY ID_RESOURCE);
		-- arr_id_dataset := ARRAY(SELECT DISTINCT ID_DATASET FROM DATASET WHERE DS_DATASET IN ('S_128MB_1','S_512MB_1','S_2GB_1','S_8GB_1','S_32GB_1') ORDER BY ID_DATASET);
		-- arr_id_dataset := ARRAY(SELECT DISTINCT ID_DATASET FROM DATASET WHERE DS_DATASET IN ('S_128MB_2','S_512MB_2','S_2GB_2','S_8GB_2','S_32GB_2') ORDER BY ID_DATASET);
		arr_id_dataset := ARRAY(SELECT DISTINCT ID_DATASET FROM DATASET WHERE DS_DATASET IN ('S_128MB_3','S_512MB_3','S_2GB_3','S_8GB_3','S_32GB_3') ORDER BY ID_DATASET);
		param_grid_row_dimension := split_part(var_ds_parameter_attribute,'_',1);

		-- FOR EACH RESOURCE
		FOREACH id_resource_iterator IN ARRAY arr_id_resource
		LOOP

			-- FOR EACH DATASET
			FOREACH id_dataset_iterator IN ARRAY arr_id_dataset
			LOOP
			
				IF (flag_increment_cd_parameter = TRUE)
				THEN

					var_cd_parameter := var_cd_parameter + 1;

				END IF;

				-- GRID ROW PARAMETERS
				IF (param_grid_row_dimension = '2MAXCORES')
				THEN

					increment_exp_grid_row_dimension := 0;
					grid_row_dimension = 1;
					arr_grid_row_dimension := '{}';
					
					max_grid_row_dimension := (SELECT 2*MAX((NR_NODES-1) * NR_COMPUTING_UNITS_CPU) AS NR_TOTAL_CORES FROM RESOURCE WHERE ID_RESOURCE = id_resource_iterator);

					WHILE grid_row_dimension < max_grid_row_dimension
					LOOP
						grid_row_dimension := CAST(POWER(2,increment_exp_grid_row_dimension) AS BIGINT);
						arr_grid_row_dimension := array_append(arr_grid_row_dimension, grid_row_dimension);
						
						increment_exp_grid_row_dimension := increment_exp_grid_row_dimension + 1;
					END LOOP;

				END IF;

				-- GRID ROW PARAMETERS
				IF (param_grid_row_dimension = '32MAXCORES')
				THEN

					increment_exp_grid_row_dimension := 0;
					grid_row_dimension = 1;
					arr_grid_row_dimension := '{}';
					
					max_grid_row_dimension := (SELECT 32*MAX((NR_NODES-1) * NR_COMPUTING_UNITS_CPU) AS NR_TOTAL_CORES FROM RESOURCE WHERE ID_RESOURCE = id_resource_iterator);

					WHILE grid_row_dimension < max_grid_row_dimension
					LOOP
						grid_row_dimension := CAST(POWER(2,increment_exp_grid_row_dimension) AS BIGINT);
						arr_grid_row_dimension := array_append(arr_grid_row_dimension, grid_row_dimension);
						
						increment_exp_grid_row_dimension := increment_exp_grid_row_dimension + 1;
					END LOOP;

				END IF;

				-- FOR EACH GRID ROW
				FOREACH i_grid_row_dimension IN ARRAY arr_grid_row_dimension
				LOOP
		
					-- FOR EACH CONFIGURATION
					FOREACH cd_configuration_iterator IN ARRAY arr_cd_configuration
					LOOP
						
						arr_id_configuration := ARRAY(SELECT C.ID_CONFIGURATION FROM CONFIGURATION C WHERE C.CD_CONFIGURATION = cd_configuration_iterator AND C.ID_ALGORITHM = id_algorithm_iterator);
						flag_insert := CHECK_PARAMETER_EXISTENCE(arr_id_configuration, var_ds_parameter_type, var_ds_parameter_attribute, var_cd_parameter, cd_configuration_iterator, id_algorithm_iterator, id_resource_iterator, id_dataset_iterator, var_id_parameter_type, bigint_iterator, var_ds_parameter_attribute_numeric);
						
						
						-- COMBINE ALL ELEMENTS FROM "CONFIGURATION", "RESOURCE" AND "DATASET" TABLES AND INSERT INTO "PARAMETER" TABLE
						--IF (flag_insert = TRUE)
						IF EXISTS(
								WITH T_CONFIGURATION AS (
												SELECT
												var_cd_parameter AS CD_PARAMETER,
												A.CD_CONFIGURATION,
												A.ID_ALGORITHM,
												A.CD_FUNCTION,
												A.ID_DEVICE
												FROM CONFIGURATION  A
												WHERE
												A.CD_CONFIGURATION IN (1,4)--= cd_configuration_iterator
												AND A.ID_ALGORITHM = id_algorithm_iterator
												),
								T_RESOURCE AS (
												SELECT
												var_cd_parameter AS CD_PARAMETER,
												A.ID_RESOURCE,
												VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
												VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT
												FROM RESOURCE A
												WHERE A.ID_RESOURCE = id_resource_iterator
												),
								T_DATASET AS (
												SELECT
												var_cd_parameter AS CD_PARAMETER,
												A.ID_DATASET,
												A.VL_DATASET_DIMENSION,
												A.VL_DATASET_ROW_DIMENSION,
												A.VL_DATASET_COLUMN_DIMENSION,
												A.VL_DATA_TYPE_MEMORY_SIZE
												FROM DATASET A
												WHERE A.ID_DATASET = id_dataset_iterator
												)
							
								SELECT
								CD_CONFIGURATION,
								ID_ALGORITHM,
								ID_FUNCTION,
								ID_DATASET,
								ID_RESOURCE,
								ID_PARAMETER_TYPE,
								NR_ITERATIONS,
								VL_GRID_ROW_DIMENSION,
								VL_GRID_COLUMN_DIMENSION,
								VL_BLOCK_ROW_DIMENSION,
								VL_BLOCK_COLUMN_DIMENSION,
								VL_BLOCK_MEMORY_SIZE,
								VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
								VL_BLOCK_MEMORY_SIZE_PERCENT_GPU
								FROM PARAMETER

							
									INTERSECT
							
							
								SELECT
								A.CD_CONFIGURATION,
								A.ID_ALGORITHM,
								(SELECT DISTINCT ID_FUNCTION FROM FUNCTION Z WHERE Z.ID_ALGORITHM = A.ID_ALGORITHM AND Z.CD_FUNCTION = A.CD_FUNCTION AND Z.ID_DEVICE = A.ID_DEVICE) AS ID_FUNCTION,
								B.ID_DATASET,
								C.ID_RESOURCE,
								var_id_parameter_type AS ID_PARAMETER_TYPE,
								bigint_iterator AS NR_ITERATIONS,
								i_grid_row_dimension AS VL_GRID_ROW_DIMENSION,
								i_grid_row_dimension AS VL_GRID_COLUMN_DIMENSION,
								CEIL(B.VL_DATASET_ROW_DIMENSION/i_grid_row_dimension) AS VL_BLOCK_ROW_DIMENSION,
								CEIL(B.VL_DATASET_COLUMN_DIMENSION/i_grid_row_dimension) AS VL_BLOCK_COLUMN_DIMENSION,
								CEIL(B.VL_DATASET_ROW_DIMENSION/i_grid_row_dimension) * CEIL(B.VL_DATASET_COLUMN_DIMENSION/i_grid_row_dimension) * B.VL_DATA_TYPE_MEMORY_SIZE AS VL_BLOCK_MEMORY_SIZE,
								(CEIL(B.VL_DATASET_ROW_DIMENSION/i_grid_row_dimension) * CEIL(B.VL_DATASET_COLUMN_DIMENSION/i_grid_row_dimension) * B.VL_DATA_TYPE_MEMORY_SIZE) / VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT AS VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
								(CEIL(B.VL_DATASET_ROW_DIMENSION/i_grid_row_dimension) * CEIL(B.VL_DATASET_COLUMN_DIMENSION/i_grid_row_dimension) * B.VL_DATA_TYPE_MEMORY_SIZE) / VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT AS VL_BLOCK_MEMORY_SIZE_PERCENT_GPU
								FROM T_CONFIGURATION A
								INNER JOIN T_DATASET B ON (A.CD_PARAMETER = B.CD_PARAMETER)
								INNER JOIN T_RESOURCE C ON (A.CD_PARAMETER = C.CD_PARAMETER)
						)
						THEN

							flag_increment_cd_parameter := FALSE;

							CONTINUE;

						ELSE

							flag_increment_cd_parameter := TRUE;

							INSERT INTO PARAMETER(CD_PARAMETER,CD_CONFIGURATION,ID_ALGORITHM,ID_FUNCTION,ID_DATASET,ID_RESOURCE,ID_PARAMETER_TYPE,NR_ITERATIONS,VL_GRID_ROW_DIMENSION,VL_GRID_COLUMN_DIMENSION,VL_BLOCK_ROW_DIMENSION,VL_BLOCK_COLUMN_DIMENSION,VL_BLOCK_MEMORY_SIZE,VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,VL_BLOCK_MEMORY_SIZE_PERCENT_GPU)
							(
									WITH T_CONFIGURATION AS (
													SELECT
													var_cd_parameter AS CD_PARAMETER,
													A.CD_CONFIGURATION,
													A.ID_ALGORITHM,
													A.CD_FUNCTION,
													A.ID_DEVICE
													FROM CONFIGURATION  A
													WHERE
													A.CD_CONFIGURATION IN (1,4)--= cd_configuration_iterator
													AND A.ID_ALGORITHM = id_algorithm_iterator
													),
									T_RESOURCE AS (
													SELECT
													var_cd_parameter AS CD_PARAMETER,
													A.ID_RESOURCE,
													VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
													VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT
													FROM RESOURCE A
													WHERE A.ID_RESOURCE = id_resource_iterator
													),
									T_DATASET AS (
													SELECT
													var_cd_parameter AS CD_PARAMETER,
													A.ID_DATASET,
													A.VL_DATASET_DIMENSION,
													A.VL_DATASET_ROW_DIMENSION,
													A.VL_DATASET_COLUMN_DIMENSION,
													A.VL_DATA_TYPE_MEMORY_SIZE
													FROM DATASET A
													WHERE A.ID_DATASET = id_dataset_iterator
													)
									SELECT
									A.CD_PARAMETER,
									A.CD_CONFIGURATION,
									A.ID_ALGORITHM,
									(SELECT DISTINCT ID_FUNCTION FROM FUNCTION Z WHERE Z.ID_ALGORITHM = A.ID_ALGORITHM AND Z.CD_FUNCTION = A.CD_FUNCTION AND Z.ID_DEVICE = A.ID_DEVICE) AS ID_FUNCTION,
									B.ID_DATASET,
									C.ID_RESOURCE,
									var_id_parameter_type AS ID_PARAMETER_TYPE,
									bigint_iterator AS NR_ITERATIONS,
									i_grid_row_dimension AS VL_GRID_ROW_DIMENSION,
									i_grid_row_dimension AS VL_GRID_COLUMN_DIMENSION,
									CEIL(B.VL_DATASET_ROW_DIMENSION/i_grid_row_dimension) AS VL_BLOCK_ROW_DIMENSION,
									CEIL(B.VL_DATASET_COLUMN_DIMENSION/i_grid_row_dimension) AS VL_BLOCK_COLUMN_DIMENSION,
									CEIL(B.VL_DATASET_ROW_DIMENSION/i_grid_row_dimension) * CEIL(B.VL_DATASET_COLUMN_DIMENSION/i_grid_row_dimension) * B.VL_DATA_TYPE_MEMORY_SIZE AS VL_BLOCK_MEMORY_SIZE,
									(CEIL(B.VL_DATASET_ROW_DIMENSION/i_grid_row_dimension) * CEIL(B.VL_DATASET_COLUMN_DIMENSION/i_grid_row_dimension) * B.VL_DATA_TYPE_MEMORY_SIZE) / VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT AS VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
									(CEIL(B.VL_DATASET_ROW_DIMENSION/i_grid_row_dimension) * CEIL(B.VL_DATASET_COLUMN_DIMENSION/i_grid_row_dimension) * B.VL_DATA_TYPE_MEMORY_SIZE) / VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT AS VL_BLOCK_MEMORY_SIZE_PERCENT_GPU
									FROM T_CONFIGURATION A
									INNER JOIN T_DATASET B ON (A.CD_PARAMETER = B.CD_PARAMETER)
									INNER JOIN T_RESOURCE C ON (A.CD_PARAMETER = C.CD_PARAMETER)
							);

						END IF;
						
					END LOOP;

				END LOOP;

			END LOOP;

		END LOOP;

	END IF;

END;
$BODY$;



CREATE OR REPLACE FUNCTION CHECK_PARAMETER_EXISTENCE(arr_id_configuration bigint[], var_ds_parameter_type TEXT, var_ds_parameter_attribute TEXT, var_cd_parameter BIGINT, cd_configuration_iterator BIGINT, id_algorithm_iterator BIGINT, id_resource_iterator BIGINT, id_dataset_iterator BIGINT, var_id_parameter_type BIGINT, bigint_iterator BIGINT, var_ds_parameter_attribute_numeric NUMERIC)
returns boolean
language plpgsql
as
$$
declare
   flag_insert boolean default TRUE;
   id_configuration_iterator bigint;
begin

	SET search_path = user_dev,schema_dev_matmul;

	-- FOR EACH CONFIGURATION ID
	FOREACH id_configuration_iterator IN ARRAY arr_id_configuration
	LOOP

		flag_insert := (select exists(

						SELECT
						P.CD_CONFIGURATION,
						P.ID_ALGORITHM,
						P.ID_FUNCTION,
						P.ID_DATASET,
						P.ID_RESOURCE,
						P.ID_PARAMETER_TYPE,
						P.NR_ITERATIONS,
						P.VL_GRID_ROW_DIMENSION,
						P.VL_GRID_COLUMN_DIMENSION,
						P.VL_BLOCK_ROW_DIMENSION,
						P.VL_BLOCK_COLUMN_DIMENSION,
						P.VL_BLOCK_MEMORY_SIZE,
						P.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
						P.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU
						FROM PARAMETER P
						WHERE
						P.CD_CONFIGURATION IN (SELECT C.CD_CONFIGURATION FROM CONFIGURATION C WHERE C.ID_CONFIGURATION = id_configuration_iterator)
						AND P.ID_ALGORITHM = id_algorithm_iterator
						AND P.ID_RESOURCE = id_resource_iterator
						AND P.ID_DATASET = id_dataset_iterator
						AND P.ID_PARAMETER_TYPE = var_id_parameter_type
						AND P.NR_ITERATIONS = bigint_iterator

		));

   
   END LOOP;
   
   return flag_insert;
end;
$$;