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
										{KMEANS}
								  }';
	-- Function parameters (CD_FUNCTION, DS_FUNCTION, ID_ALGORITHM)
	arr_function_data text[] := '{
									{1,_PARTIAL_SUM,1}
								 }';
	arr_id_device bigint[];
	arr_id_algorithm bigint[];
	arr_device_config bigint[];
	-- Resource parameters (DS_RESOURCE, NR_NODES, NR_COMPUTING_UNITS_CPU, NR_COMPUTING_UNITS_GPU, VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT, VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT)
	arr_resource_data text[] := '{
									{MINOTAURO_1,2,8,1,128000000000,12000000000},
									{MINOTAURO_2,2,8,1,12000000000,12000000000},
									{MINOTAURO_2_NODES_16_CORES,2,16,1,128000000000,12000000000},
									{MINOTAURO_3_NODES_16_CORES,3,16,1,128000000000,12000000000},
									{MINOTAURO_4_NODES_16_CORES,4,16,1,128000000000,12000000000},
									{MINOTAURO_5_NODES_16_CORES,5,16,1,128000000000,12000000000},
									{MINOTAURO_6_NODES_16_CORES,6,16,1,128000000000,12000000000},
									{MINOTAURO_7_NODES_16_CORES,7,16,1,128000000000,12000000000},
									{MINOTAURO_8_NODES_16_CORES,8,16,1,128000000000,12000000000},
									{MINOTAURO_9_NODES_16_CORES,9,16,1,128000000000,12000000000}
								 }';
	-- Data set parameters (DS_DATASET, VL_DATASET_MEMORY_SIZE, DS_DATA_TYPE, VL_DATA_TYPE_MEMORY_SIZE, VL_DATASET_DIMENSION, VL_DATASET_ROW_DIMENSION, VL_DATASET_COLUMN_DIMENSION, NR_RANDOM_STATE)
	arr_dataset_data text[] := '{
									{S_A_1,400,FLOAT64,8,50,50,1,170},
									{S_A_2,400,FLOAT64,8,50,10,5,170},
									{S_A_3,400,FLOAT64,8,50,5,10,170},
									{S_A_4,400,FLOAT64,8,50,7,7,170},
							  		{S_B_1,400000,FLOAT64,8,50000,50000,1,170},
									{S_B_2,400000,FLOAT64,8,50000,10000,5,170},
									{S_B_3,400000,FLOAT64,8,50000,5000,10,170},
									{S_B_4,400000,FLOAT64,8,50000,224,224,170},
							  		{S_C_1,400000000,FLOAT64,8,50000000,50000000,1,170},
									{S_C_2,400000000,FLOAT64,8,50000000,10000000,5,170},
									{S_C_3,400000000,FLOAT64,8,50000000,5000000,10,170},
									{S_C_4,400000000,FLOAT64,8,50000000,7071,7071,170},
									{S_AA_1,640,FLOAT64,8,80,80,1,170},
									{S_AA_2,640,FLOAT64,8,80,20,4,170},
									{S_AA_3,640,FLOAT64,8,80,5,16,170},
									{S_AA_4,640,FLOAT64,8,80,8,8,170},
							  		{S_BB_1,640000,FLOAT64,8,80000,80000,1,170},
									{S_BB_2,640000,FLOAT64,8,80000,20000,4,170},
									{S_BB_3,640000,FLOAT64,8,80000,5000,16,170},
									{S_BB_4,640000,FLOAT64,8,80000,282,282,170},
							  		{S_CC_1,640000000,FLOAT64,8,80000000,80000000,1,170},
									{S_CC_2,640000000,FLOAT64,8,80000000,20000000,4,170},
									{S_CC_3,640000000,FLOAT64,8,80000000,5000000,16,170},
									{S_CC_4,640000000,FLOAT64,8,80000000,8944,8944,170},
									{S_10MB_1,10000000,FLOAT64,8,1250000,12500,100,170},
									{S_100MB_1,100000000,FLOAT64,8,12500000,125000,100,170},
									{S_1GB_1,1000000000,FLOAT64,8,125000000,1250000,100,170},
									{S_10GB_1,10000000000,FLOAT64,8,1250000000,12500000,100,170},
									{S_100GB_1,10000000000,FLOAT64,8,12500000000,125000000,100,170},
									{S_1MB_1,1000000,FLOAT64,8,125000,1250000,100,170}
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
	arr_parameter_type_data text[] := '{
									{VAR_BLOCK_CAPACITY_SIZE,0.25},
									{VAR_BLOCK_CAPACITY_SIZE,0.50},
									{VAR_BLOCK_CAPACITY_SIZE,0.75},
									{VAR_BLOCK_CAPACITY_SIZE,1.00},
									{VAR_PARALLELISM_LEVEL,MIN_INTER_MAX_INTRA},
									{VAR_PARALLELISM_LEVEL,MAX_INTER_MIN_INTRA},
									{VAR_GRID_ROW,2MAXCORES_1},
									{VAR_GRID_COLUMN,MAXCORES_0.1}
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
	
	SET search_path = user_dev,schema_dev;

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
								NR_RANDOM_STATE)
			VALUES
			(DEFAULT,
			 arr_text_iterator[1],
			 CAST(arr_text_iterator[2] AS BIGINT),
			 arr_text_iterator[3],
			 CAST(arr_text_iterator[4] AS BIGINT),
			 CAST(arr_text_iterator[5] AS BIGINT),
			 CAST(arr_text_iterator[6] AS BIGINT),
			 CAST(arr_text_iterator[7] AS BIGINT),
			 CAST(arr_text_iterator[8] AS BIGINT));
		
		END IF;
	
	END LOOP;


	-- PARAMETER TYPE TABLE
	FOREACH arr_text_iterator SLICE 1 IN ARRAY arr_parameter_type_data
	LOOP
		IF EXISTS(SELECT FROM PARAMETER_TYPE
				  WHERE DS_PARAMETER_TYPE = arr_text_iterator[1]
				  AND DS_PARAMETER_ATTRIBUTE = arr_text_iterator[2]			
				 )
		THEN
			
			CONTINUE;
			
		ELSE
		
			INSERT INTO PARAMETER_TYPE(ID_PARAMETER_TYPE,
										DS_PARAMETER_TYPE,
										DS_PARAMETER_ATTRIBUTE)
			VALUES
			(DEFAULT,
			 arr_text_iterator[1],
			 arr_text_iterator[2]);
			 
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

	SET search_path = user_dev,schema_dev;

	-- DELETE TABLES
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

	SET search_path = user_dev,schema_dev;

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
		NR_RANDOM_STATE BIGINT
	);

	CREATE TABLE PARAMETER_TYPE
	(
		ID_PARAMETER_TYPE BIGSERIAL PRIMARY KEY,
		DS_PARAMETER_TYPE VARCHAR,
		DS_PARAMETER_ATTRIBUTE VARCHAR
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

END; 
$BODY$;



-- DROP TABLES
CREATE OR REPLACE PROCEDURE DROP_TABLES()
LANGUAGE plpgsql
AS $BODY$
BEGIN

	SET search_path = user_dev,schema_dev;
	
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

	SET search_path = user_dev,schema_dev;
	
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

	SET search_path = user_dev,schema_dev;

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

	SET search_path = user_dev,schema_dev;
	
	-- SET INITIAL VALUE FOR CD_PARAMETER
	var_cd_parameter := (SELECT COALESCE(MAX(CD_PARAMETER),0) FROM PARAMETER);

	IF (var_ds_parameter_type = 'VAR_BLOCK_CAPACITY_SIZE')
	THEN

		var_ds_parameter_attribute_numeric := cast(var_ds_parameter_attribute as numeric);
		
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
			
				-- FOR EACH CONFIGURATION
				FOREACH cd_configuration_iterator IN ARRAY arr_cd_configuration
				LOOP
				
				
					arr_id_configuration := ARRAY(SELECT C.ID_CONFIGURATION FROM CONFIGURATION C WHERE C.CD_CONFIGURATION = cd_configuration_iterator AND C.ID_ALGORITHM = id_algorithm_iterator);
					
					flag_insert := CHECK_PARAMETER_EXISTENCE(arr_id_configuration, var_ds_parameter_type, var_ds_parameter_attribute, var_cd_parameter, cd_configuration_iterator, id_algorithm_iterator, id_resource_iterator, id_dataset_iterator, var_id_parameter_type, bigint_iterator, var_ds_parameter_attribute_numeric);
					
					-- COMBINE ALL ELEMENTS FROM "CONFIGURATION", "RESOURCE" AND "DATASET" TABLES AND INSERT INTO "PARAMETER" TABLE					
					IF (flag_insert = TRUE)
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
											A.CD_CONFIGURATION = cd_configuration_iterator
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
							CEIL(B.VL_DATASET_ROW_DIMENSION/(CEIL(((B.VL_DATASET_ROW_DIMENSION*B.VL_DATASET_COLUMN_DIMENSION)*var_ds_parameter_attribute_numeric)/B.VL_DATASET_COLUMN_DIMENSION))) AS VL_GRID_ROW_DIMENSION,
							CEIL(B.VL_DATASET_COLUMN_DIMENSION/(CEIL(((B.VL_DATASET_ROW_DIMENSION*B.VL_DATASET_COLUMN_DIMENSION)*var_ds_parameter_attribute_numeric)/B.VL_DATASET_ROW_DIMENSION))) AS VL_GRID_COLUMN_DIMENSION,
							CEIL(((B.VL_DATASET_ROW_DIMENSION*B.VL_DATASET_COLUMN_DIMENSION)*var_ds_parameter_attribute_numeric)/B.VL_DATASET_COLUMN_DIMENSION) AS VL_BLOCK_ROW_DIMENSION,
							CEIL(((B.VL_DATASET_ROW_DIMENSION*B.VL_DATASET_COLUMN_DIMENSION)*var_ds_parameter_attribute_numeric)/B.VL_DATASET_ROW_DIMENSION) AS VL_BLOCK_COLUMN_DIMENSION,
							CEIL(((B.VL_DATASET_ROW_DIMENSION*B.VL_DATASET_COLUMN_DIMENSION)*var_ds_parameter_attribute_numeric)/B.VL_DATASET_COLUMN_DIMENSION) * CEIL(((B.VL_DATASET_ROW_DIMENSION*B.VL_DATASET_COLUMN_DIMENSION)*var_ds_parameter_attribute_numeric)/B.VL_DATASET_ROW_DIMENSION) * B.VL_DATA_TYPE_MEMORY_SIZE AS VL_BLOCK_MEMORY_SIZE,
							(CEIL(((B.VL_DATASET_ROW_DIMENSION*B.VL_DATASET_COLUMN_DIMENSION)*var_ds_parameter_attribute_numeric)/B.VL_DATASET_COLUMN_DIMENSION) * CEIL(((B.VL_DATASET_ROW_DIMENSION*B.VL_DATASET_COLUMN_DIMENSION)*var_ds_parameter_attribute_numeric)/B.VL_DATASET_ROW_DIMENSION) * B.VL_DATA_TYPE_MEMORY_SIZE) / VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT AS VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
							(CEIL(((B.VL_DATASET_ROW_DIMENSION*B.VL_DATASET_COLUMN_DIMENSION)*var_ds_parameter_attribute_numeric)/B.VL_DATASET_COLUMN_DIMENSION) * CEIL(((B.VL_DATASET_ROW_DIMENSION*B.VL_DATASET_COLUMN_DIMENSION)*var_ds_parameter_attribute_numeric)/B.VL_DATASET_ROW_DIMENSION) * B.VL_DATA_TYPE_MEMORY_SIZE) / VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT AS VL_BLOCK_MEMORY_SIZE_PERCENT_GPU
							FROM T_CONFIGURATION A
							INNER JOIN T_DATASET B ON (A.CD_PARAMETER = B.CD_PARAMETER)
							INNER JOIN T_RESOURCE C ON (A.CD_PARAMETER = C.CD_PARAMETER)

						);

					END IF;
						
				END LOOP;
				
			END LOOP;
			
		END LOOP;

	ELSIF (var_ds_parameter_type = 'VAR_PARALLELISM_LEVEL')
	THEN

		IF (var_ds_parameter_attribute = 'MIN_INTER_MAX_INTRA')
		THEN
			
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
			
					-- FOR EACH CONFIGURATION
					FOREACH cd_configuration_iterator IN ARRAY arr_cd_configuration
					LOOP
						
						arr_id_configuration := ARRAY(SELECT C.ID_CONFIGURATION FROM CONFIGURATION C WHERE C.CD_CONFIGURATION = cd_configuration_iterator AND C.ID_ALGORITHM = id_algorithm_iterator);
						flag_insert := CHECK_PARAMETER_EXISTENCE(arr_id_configuration, var_ds_parameter_type, var_ds_parameter_attribute, var_cd_parameter, cd_configuration_iterator, id_algorithm_iterator, id_resource_iterator, id_dataset_iterator, var_id_parameter_type, bigint_iterator, var_ds_parameter_attribute_numeric);
						
						
						-- COMBINE ALL ELEMENTS FROM "CONFIGURATION", "RESOURCE" AND "DATASET" TABLES AND INSERT INTO "PARAMETER" TABLE
						IF (flag_insert = TRUE)
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
													A.CD_CONFIGURATION = cd_configuration_iterator
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
									1 AS VL_GRID_ROW_DIMENSION,
									1 AS VL_GRID_COLUMN_DIMENSION,
									CEIL(B.VL_DATASET_ROW_DIMENSION/1) AS VL_BLOCK_ROW_DIMENSION,
									CEIL(B.VL_DATASET_COLUMN_DIMENSION/1) AS VL_BLOCK_COLUMN_DIMENSION,
									CEIL(B.VL_DATASET_ROW_DIMENSION/1) * CEIL(B.VL_DATASET_COLUMN_DIMENSION/1) * VL_DATA_TYPE_MEMORY_SIZE AS VL_BLOCK_MEMORY_SIZE,
									(CEIL(B.VL_DATASET_ROW_DIMENSION/1) * CEIL(B.VL_DATASET_COLUMN_DIMENSION/1) * VL_DATA_TYPE_MEMORY_SIZE) / VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT AS VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
									(CEIL(B.VL_DATASET_ROW_DIMENSION/1) * CEIL(B.VL_DATASET_COLUMN_DIMENSION/1) * VL_DATA_TYPE_MEMORY_SIZE) / VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT AS VL_BLOCK_MEMORY_SIZE_PERCENT_GPU
									FROM T_CONFIGURATION A
									INNER JOIN T_DATASET B ON (A.CD_PARAMETER = B.CD_PARAMETER)
									INNER JOIN T_RESOURCE C ON (A.CD_PARAMETER = C.CD_PARAMETER)
							);

						END IF;
						
					END LOOP;

				END LOOP;

			END LOOP;

		ELSIF (var_ds_parameter_attribute = 'MAX_INTER_MIN_INTRA')
		THEN
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
					
					-- FOR EACH CONFIGURATION
					FOREACH cd_configuration_iterator IN ARRAY arr_cd_configuration
					LOOP
						
						arr_id_configuration := ARRAY(SELECT C.ID_CONFIGURATION FROM CONFIGURATION C WHERE C.CD_CONFIGURATION = cd_configuration_iterator AND C.ID_ALGORITHM = id_algorithm_iterator);
						flag_insert := CHECK_PARAMETER_EXISTENCE(arr_id_configuration,var_ds_parameter_type, var_ds_parameter_attribute, var_cd_parameter, cd_configuration_iterator, id_algorithm_iterator, id_resource_iterator, id_dataset_iterator, var_id_parameter_type, bigint_iterator, var_ds_parameter_attribute_numeric);
						-- COMBINE ALL ELEMENTS FROM "CONFIGURATION", "RESOURCE" AND "DATASET" TABLES AND INSERT INTO "PARAMETER" TABLE
						IF (flag_insert = TRUE)
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
													A.CD_CONFIGURATION = cd_configuration_iterator
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
									B.VL_DATASET_ROW_DIMENSION AS VL_GRID_ROW_DIMENSION,
									B.VL_DATASET_COLUMN_DIMENSION AS VL_GRID_COLUMN_DIMENSION,
									CEIL(B.VL_DATASET_ROW_DIMENSION/B.VL_DATASET_ROW_DIMENSION) AS VL_BLOCK_ROW_DIMENSION,
									CEIL(B.VL_DATASET_COLUMN_DIMENSION/B.VL_DATASET_COLUMN_DIMENSION) AS VL_BLOCK_COLUMN_DIMENSION,
									CEIL(B.VL_DATASET_ROW_DIMENSION/B.VL_DATASET_ROW_DIMENSION) * CEIL(B.VL_DATASET_COLUMN_DIMENSION/B.VL_DATASET_COLUMN_DIMENSION) * VL_DATA_TYPE_MEMORY_SIZE AS VL_BLOCK_MEMORY_SIZE,
									(CEIL(B.VL_DATASET_ROW_DIMENSION/B.VL_DATASET_ROW_DIMENSION) * CEIL(B.VL_DATASET_COLUMN_DIMENSION/B.VL_DATASET_COLUMN_DIMENSION) * VL_DATA_TYPE_MEMORY_SIZE) / VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT AS VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
									(CEIL(B.VL_DATASET_ROW_DIMENSION/B.VL_DATASET_ROW_DIMENSION) * CEIL(B.VL_DATASET_COLUMN_DIMENSION/B.VL_DATASET_COLUMN_DIMENSION) * VL_DATA_TYPE_MEMORY_SIZE) / VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT AS VL_BLOCK_MEMORY_SIZE_PERCENT_GPU
									FROM T_CONFIGURATION A
									INNER JOIN T_DATASET B ON (A.CD_PARAMETER = B.CD_PARAMETER)
									INNER JOIN T_RESOURCE C ON (A.CD_PARAMETER = C.CD_PARAMETER)
							);

						END IF;
						
					END LOOP;

				END LOOP;

			END LOOP;

		ELSE


		END IF;
		
	ELSIF (var_ds_parameter_type = 'VAR_GRID_ROW')
	THEN
		
		param_grid_row_dimension := split_part(var_ds_parameter_attribute,'_',1);
		param_grid_column_dimension := split_part(var_ds_parameter_attribute,'_',2);

		-- GRID COLUMN PARAMETERS
		grid_column_dimension := CAST(param_grid_column_dimension AS BIGINT);

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
												A.CD_CONFIGURATION = cd_configuration_iterator
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
								grid_column_dimension AS VL_GRID_COLUMN_DIMENSION,
								CEIL(B.VL_DATASET_ROW_DIMENSION/i_grid_row_dimension) AS VL_BLOCK_ROW_DIMENSION,
								CEIL(B.VL_DATASET_COLUMN_DIMENSION/grid_column_dimension) AS VL_BLOCK_COLUMN_DIMENSION,
								CEIL(B.VL_DATASET_ROW_DIMENSION/i_grid_row_dimension) * CEIL(B.VL_DATASET_COLUMN_DIMENSION/grid_column_dimension) * B.VL_DATA_TYPE_MEMORY_SIZE AS VL_BLOCK_MEMORY_SIZE,
								(CEIL(B.VL_DATASET_ROW_DIMENSION/i_grid_row_dimension) * CEIL(B.VL_DATASET_COLUMN_DIMENSION/grid_column_dimension) * B.VL_DATA_TYPE_MEMORY_SIZE) / VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT AS VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
								(CEIL(B.VL_DATASET_ROW_DIMENSION/i_grid_row_dimension) * CEIL(B.VL_DATASET_COLUMN_DIMENSION/grid_column_dimension) * B.VL_DATA_TYPE_MEMORY_SIZE) / VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT AS VL_BLOCK_MEMORY_SIZE_PERCENT_GPU
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
													A.CD_CONFIGURATION = cd_configuration_iterator
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
									grid_column_dimension AS VL_GRID_COLUMN_DIMENSION,
									CEIL(B.VL_DATASET_ROW_DIMENSION/i_grid_row_dimension) AS VL_BLOCK_ROW_DIMENSION,
									CEIL(B.VL_DATASET_COLUMN_DIMENSION/grid_column_dimension) AS VL_BLOCK_COLUMN_DIMENSION,
									CEIL(B.VL_DATASET_ROW_DIMENSION/i_grid_row_dimension) * CEIL(B.VL_DATASET_COLUMN_DIMENSION/grid_column_dimension) * B.VL_DATA_TYPE_MEMORY_SIZE AS VL_BLOCK_MEMORY_SIZE,
									(CEIL(B.VL_DATASET_ROW_DIMENSION/i_grid_row_dimension) * CEIL(B.VL_DATASET_COLUMN_DIMENSION/grid_column_dimension) * B.VL_DATA_TYPE_MEMORY_SIZE) / VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT AS VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
									(CEIL(B.VL_DATASET_ROW_DIMENSION/i_grid_row_dimension) * CEIL(B.VL_DATASET_COLUMN_DIMENSION/grid_column_dimension) * B.VL_DATA_TYPE_MEMORY_SIZE) / VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT AS VL_BLOCK_MEMORY_SIZE_PERCENT_GPU
									FROM T_CONFIGURATION A
									INNER JOIN T_DATASET B ON (A.CD_PARAMETER = B.CD_PARAMETER)
									INNER JOIN T_RESOURCE C ON (A.CD_PARAMETER = C.CD_PARAMETER)
							);

						END IF;
						
					END LOOP;

				END LOOP;

			END LOOP;

		END LOOP;


	ELSIF (var_ds_parameter_type = 'VAR_GRID_COLUMN')
	THEN
	
		param_grid_row_dimension := split_part(var_ds_parameter_attribute,'_',1);
		param_grid_column_dimension := split_part(var_ds_parameter_attribute,'_',2);

		-- GRID COLUMN PARAMETERS
		increment_percent_grid_col_dataset_col := CAST(param_grid_column_dimension AS NUMERIC);
		percent_grid_col_dataset_col := increment_percent_grid_col_dataset_col;
		arr_percent_grid_col_dataset_col := '{}';

		WHILE percent_grid_col_dataset_col <= 1.00
		LOOP

			arr_percent_grid_col_dataset_col := array_append(arr_percent_grid_col_dataset_col, percent_grid_col_dataset_col);
			percent_grid_col_dataset_col := percent_grid_col_dataset_col + increment_percent_grid_col_dataset_col;

		END LOOP;


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
				IF (param_grid_row_dimension = 'MAXCORES')
				THEN

					grid_row_dimension := (SELECT MAX((NR_NODES-1) * NR_COMPUTING_UNITS_CPU) AS NR_TOTAL_CORES FROM RESOURCE WHERE ID_RESOURCE = id_resource_iterator);

				END IF;

				-- FOR EACH PERCENTAGE GRID COLUMN TO DATASET COLUMN
				FOREACH i_percent_grid_col_dataset_col IN ARRAY arr_percent_grid_col_dataset_col
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
												A.CD_CONFIGURATION = cd_configuration_iterator
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
								grid_row_dimension AS VL_GRID_ROW_DIMENSION,
								CEIL(B.VL_DATASET_COLUMN_DIMENSION * i_percent_grid_col_dataset_col) AS VL_GRID_COLUMN_DIMENSION,
								CEIL(B.VL_DATASET_ROW_DIMENSION/grid_row_dimension) AS VL_BLOCK_ROW_DIMENSION,
								CEIL(B.VL_DATASET_COLUMN_DIMENSION/(CEIL(B.VL_DATASET_COLUMN_DIMENSION * i_percent_grid_col_dataset_col))) AS VL_BLOCK_COLUMN_DIMENSION,
								CEIL(B.VL_DATASET_ROW_DIMENSION/grid_row_dimension) * CEIL(B.VL_DATASET_COLUMN_DIMENSION/(CEIL(B.VL_DATASET_COLUMN_DIMENSION * i_percent_grid_col_dataset_col))) * B.VL_DATA_TYPE_MEMORY_SIZE AS VL_BLOCK_MEMORY_SIZE,
								(CEIL(B.VL_DATASET_ROW_DIMENSION/grid_row_dimension) * CEIL(B.VL_DATASET_COLUMN_DIMENSION/(CEIL(B.VL_DATASET_COLUMN_DIMENSION * i_percent_grid_col_dataset_col))) * B.VL_DATA_TYPE_MEMORY_SIZE) / VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT AS VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
								(CEIL(B.VL_DATASET_ROW_DIMENSION/grid_row_dimension) * CEIL(B.VL_DATASET_COLUMN_DIMENSION/(CEIL(B.VL_DATASET_COLUMN_DIMENSION * i_percent_grid_col_dataset_col))) * B.VL_DATA_TYPE_MEMORY_SIZE) / VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT AS VL_BLOCK_MEMORY_SIZE_PERCENT_GPU
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
													A.CD_CONFIGURATION = cd_configuration_iterator
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
									grid_row_dimension AS VL_GRID_ROW_DIMENSION,
									CEIL(B.VL_DATASET_COLUMN_DIMENSION * i_percent_grid_col_dataset_col) AS VL_GRID_COLUMN_DIMENSION,
									CEIL(B.VL_DATASET_ROW_DIMENSION/grid_row_dimension) AS VL_BLOCK_ROW_DIMENSION,
									CEIL(B.VL_DATASET_COLUMN_DIMENSION/(CEIL(B.VL_DATASET_COLUMN_DIMENSION * i_percent_grid_col_dataset_col))) AS VL_BLOCK_COLUMN_DIMENSION,
									CEIL(B.VL_DATASET_ROW_DIMENSION/grid_row_dimension) * CEIL(B.VL_DATASET_COLUMN_DIMENSION/(CEIL(B.VL_DATASET_COLUMN_DIMENSION * i_percent_grid_col_dataset_col))) * B.VL_DATA_TYPE_MEMORY_SIZE AS VL_BLOCK_MEMORY_SIZE,
									(CEIL(B.VL_DATASET_ROW_DIMENSION/grid_row_dimension) * CEIL(B.VL_DATASET_COLUMN_DIMENSION/(CEIL(B.VL_DATASET_COLUMN_DIMENSION * i_percent_grid_col_dataset_col))) * B.VL_DATA_TYPE_MEMORY_SIZE) / VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT AS VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
									(CEIL(B.VL_DATASET_ROW_DIMENSION/grid_row_dimension) * CEIL(B.VL_DATASET_COLUMN_DIMENSION/(CEIL(B.VL_DATASET_COLUMN_DIMENSION * i_percent_grid_col_dataset_col))) * B.VL_DATA_TYPE_MEMORY_SIZE) / VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT AS VL_BLOCK_MEMORY_SIZE_PERCENT_GPU
									FROM T_CONFIGURATION A
									INNER JOIN T_DATASET B ON (A.CD_PARAMETER = B.CD_PARAMETER)
									INNER JOIN T_RESOURCE C ON (A.CD_PARAMETER = C.CD_PARAMETER)
							);

						END IF;
						
					END LOOP;

				END LOOP;

			END LOOP;

		END LOOP;
			
	ELSE


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

	SET search_path = user_dev,schema_dev;

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