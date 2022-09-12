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
	-- Algorithm parameters (CD_ALGORITHM, DS_ALGORITHM)
	arr_algorithm_data text[] := '{
										{1,KMEANS}
								  }';
	-- Function parameters (CD_FUNCTION, DS_FUNCTION, CD_ALGORITHM)
	arr_function_data text[] := '{
									{1,_PARTIAL_SUM,1}
								 }';
	arr_id_device bigint[];
	arr_cd_algorithm bigint[];
	arr_device_config bigint[];
	-- Resource parameters (CD_RESOURCE, DS_RESOURCE, NR_NODES, NR_COMPUTING_UNITS_CPU, NR_COMPUTING_UNITS_GPU, VL_MEMORY_PER_CPU_COMPUTING_UNIT, VL_MEMORY_PER_GPU_COMPUTING_UNIT)
	arr_resource_data text[] := '{
									{1,MINOTAURO_1,2,8,1,128000000000,12000000000}
								 }';
	-- Data set parameters (CD_DATASET, DS_DATASET, VL_DATASET_MEMORY_SIZE, DS_DATA_TYPE, VL_DATA_TYPE_MEMORY_SIZE, VL_DATASET_SIZE, VL_DATASET_ROW_SIZE, VL_DATASET_COLUMN_SIZE, NR_RANDOM_STATE)
	arr_dataset_data text[] := '{
									{1,SYNTHETIC_SMALL_400B_1,400,FLOAT64,8,50,50,1,170},
									{2,SYNTHETIC_SMALL_400B_2,400,FLOAT64,8,50,10,5,170},
									{3,SYNTHETIC_SMALL_400B_3,400,FLOAT64,8,50,5,10,170},
									{4,SYNTHETIC_SMALL_400B_4,400,FLOAT64,8,50,7,7,170},
							  		{5,SYNTHETIC_MEDIUM_400KB_1,400000,FLOAT64,8,50000,50000,1,170},
									{6,SYNTHETIC_MEDIUM_400KB_2,400000,FLOAT64,8,50000,10000,5,170},
									{7,SYNTHETIC_MEDIUM_400KB_3,400000,FLOAT64,8,50000,5000,10,170},
									{8,SYNTHETIC_MEDIUM_400KB_4,400000,FLOAT64,8,50000,224,224,170},
							  		{9,SYNTHETIC_BIG_400MB_1,400000000,FLOAT64,8,50000000,50000000,1,170},
									{10,SYNTHETIC_BIG_400MB_2,400000000,FLOAT64,8,50000000,10000000,5,170},
									{11,SYNTHETIC_BIG_400MB_3,400000000,FLOAT64,8,50000000,5000000,10,170},
									{12,SYNTHETIC_BIG_400MB_4,400000000,FLOAT64,8,50000000,7071,7071,170}
								}';
	-- Number of repetitions for each parameter set
	arr_nr_iteration bigint[] := '{
									{5}
								  }';
	-- Parameter type description
	arr_ds_tp_parameter text[] := '{
									{VAR_BLOCK_CAPACITY_SIZE,VAR_PARALLELISM_LEVEL}
								}';
	-- Percentage of data set for each parameter (for VAR_BLOCK_CAPACITY_SIZE only)
	arr_percent_dataset numeric[] := '{
										{0.25,0.50,0.75,1.00}
									  }';
									  
	-- Description of Status of Parallelism (MIN_INTER_MAX_INTRA or MAX_INTER_MIN_INTRA) (for VAR_PARALLELISM_LEVEL only)
	arr_ds_parallelism_data text[] := '{
									{MIN_INTER_MAX_INTRA,MAX_INTER_MIN_INTRA}
								}';
								
	arr_cd_resource bigint[];
	arr_cd_dataset bigint[];
	arr_cd_configuration bigint[];
	
	-- variables
	var_id_algorithm bigint;
	var_repetition_config bigint;
	var_nr_function_config bigint;
	
	-- iterators
	arr_text_iterator text[];
	text_iterator text;
	text_iterator_2 text;
	numeric_iterator numeric;
	bigint_iterator bigint;
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
	FOREACH arr_text_iterator SLICE 1 IN ARRAY arr_algorithm_data
	LOOP
		IF EXISTS(SELECT FROM ALGORITHM WHERE CD_ALGORITHM = CAST(arr_text_iterator[1] AS BIGINT) AND DS_ALGORITHM = arr_text_iterator[2])
		THEN
		
			CONTINUE;
			
		ELSE
		
			INSERT INTO ALGORITHM(ID_ALGORITHM,CD_ALGORITHM,DS_ALGORITHM)
			VALUES
			(DEFAULT,CAST(arr_text_iterator[1] AS BIGINT), arr_text_iterator[2]);
		
		END IF;
	END LOOP;
	
	
	-- FUNCTION TABLE
	arr_id_device := ARRAY(SELECT DISTINCT ID_DEVICE FROM DEVICE ORDER BY ID_DEVICE);
	FOREACH arr_text_iterator SLICE 1 IN ARRAY arr_function_data
	LOOP
		
		var_id_algorithm := (SELECT DISTINCT ID_ALGORITHM FROM ALGORITHM WHERE CD_ALGORITHM = cast(arr_text_iterator[3] AS BIGINT));
		
		IF EXISTS(SELECT FROM FUNCTION WHERE CD_FUNCTION = cast(arr_text_iterator[1] AS BIGINT) AND DS_FUNCTION = arr_text_iterator[2] AND ID_DEVICE = var_id_algorithm AND ID_ALGORITHM = var_id_algorithm)
		THEN
		
			CONTINUE;
			
		ELSE
		
			FOREACH bigint_iterator IN ARRAY arr_id_device
			LOOP
				INSERT INTO FUNCTION(ID_FUNCTION,CD_FUNCTION,DS_FUNCTION,ID_DEVICE,ID_ALGORITHM)
				VALUES
				(DEFAULT,cast(arr_text_iterator[1] AS BIGINT), arr_text_iterator[2],bigint_iterator,var_id_algorithm);
			END LOOP;
		END IF;
	END LOOP;
	
	
	-- CONFIGURATION TABLE
	
	-- REMOVE PREVIOUS CONFIGURATIONS
	DELETE FROM CONFIGURATION;
	ALTER SEQUENCE configuration_id_configuration_seq RESTART WITH 1;
		
	-- SELECT AVAILABLE ALGORITHMS
	arr_cd_algorithm := ARRAY(SELECT DISTINCT A.CD_ALGORITHM FROM ALGORITHM A ORDER BY A.CD_ALGORITHM);
	
	-- FOR EACH ALGORITHM
	FOREACH bigint_iterator IN ARRAY arr_cd_algorithm
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
									A.CD_ALGORITHM = bigint_iterator
								);
		
		CALL RECURSIVE_CONFIGURATION_PERMUTATION(var_nr_function_config, arr_device_config, 0, bigint_iterator);

	END LOOP;
	
	
	-- RESOURCE TABLE
	FOREACH arr_text_iterator SLICE 1 IN ARRAY arr_resource_data
	LOOP
		IF EXISTS(SELECT FROM RESOURCE
				  WHERE CD_RESOURCE = CAST(arr_text_iterator[1] AS BIGINT)
				  AND DS_RESOURCE = arr_text_iterator[2]
				  AND NR_NODES = CAST(arr_text_iterator[3] AS BIGINT)
				  AND NR_COMPUTING_UNITS_CPU = CAST(arr_text_iterator[4] AS BIGINT)
				  AND NR_COMPUTING_UNITS_GPU = CAST(arr_text_iterator[5] AS BIGINT)
				  AND VL_MEMORY_PER_CPU_COMPUTING_UNIT = CAST(arr_text_iterator[6] AS BIGINT)
				  AND VL_MEMORY_PER_GPU_COMPUTING_UNIT = CAST(arr_text_iterator[7] AS BIGINT)									
				 )
		THEN
			
			CONTINUE;
			
		ELSE
		
			INSERT INTO RESOURCE(ID_RESOURCE,
								 CD_RESOURCE,
								 DS_RESOURCE,
								 NR_NODES,
								 NR_COMPUTING_UNITS_CPU,
								 NR_COMPUTING_UNITS_GPU,
								 VL_MEMORY_PER_CPU_COMPUTING_UNIT,
								 VL_MEMORY_PER_GPU_COMPUTING_UNIT)
			VALUES
			(DEFAULT,
			 CAST(arr_text_iterator[1] AS BIGINT),
			 arr_text_iterator[2],
			 CAST(arr_text_iterator[3] AS BIGINT),
			 CAST(arr_text_iterator[4] AS BIGINT),
			 CAST(arr_text_iterator[5] AS BIGINT),
			 CAST(arr_text_iterator[6] AS BIGINT),
			 CAST(arr_text_iterator[7] AS BIGINT));
			 
		END IF;
		
	END LOOP;
	
	
	-- DATASET TABLE
	FOREACH arr_text_iterator SLICE 1 IN ARRAY arr_dataset_data
	LOOP
		
		IF EXISTS(SELECT FROM DATASET
				  WHERE CD_DATASET = CAST(arr_text_iterator[1] AS BIGINT)
				  AND DS_DATASET = arr_text_iterator[2]
				  AND VL_DATASET_MEMORY_SIZE = CAST(arr_text_iterator[3] AS BIGINT)
				  AND DS_DATA_TYPE = arr_text_iterator[4]
				  AND VL_DATA_TYPE_MEMORY_SIZE = CAST(arr_text_iterator[5] AS BIGINT)
				  AND VL_DATASET_SIZE = CAST(arr_text_iterator[6] AS BIGINT)
				  AND VL_DATASET_ROW_SIZE = CAST(arr_text_iterator[7] AS BIGINT)
				  AND VL_DATASET_COLUMN_SIZE = CAST(arr_text_iterator[8] AS BIGINT)
				  AND NR_RANDOM_STATE = CAST(arr_text_iterator[9] AS BIGINT)
				 )
		THEN
		
			CONTINUE;
		
		ELSE
		
			INSERT INTO DATASET(ID_DATASET,
								CD_DATASET,
								DS_DATASET,
								VL_DATASET_MEMORY_SIZE,
								DS_DATA_TYPE,
								VL_DATA_TYPE_MEMORY_SIZE,
								VL_DATASET_SIZE,
								VL_DATASET_ROW_SIZE,
								VL_DATASET_COLUMN_SIZE,
								NR_RANDOM_STATE)
			VALUES
			(DEFAULT,
			 CAST(arr_text_iterator[1] AS BIGINT),
			 arr_text_iterator[2],
			 CAST(arr_text_iterator[3] AS BIGINT),
			 arr_text_iterator[4],
			 CAST(arr_text_iterator[5] AS BIGINT),
			 CAST(arr_text_iterator[6] AS BIGINT),
			 CAST(arr_text_iterator[7] AS BIGINT),
			 CAST(arr_text_iterator[8] AS BIGINT),
			 CAST(arr_text_iterator[9] AS BIGINT));
		
		END IF;
	
	END LOOP;
	
	
	-- PARAMETER TABLE
	-- SELECT AVAILABLE RESOURCES
	arr_cd_resource := ARRAY(SELECT DISTINCT CD_RESOURCE FROM RESOURCE ORDER BY CD_RESOURCE);
	arr_cd_dataset := ARRAY(SELECT DISTINCT CD_DATASET FROM DATASET ORDER BY CD_DATASET);
	arr_cd_configuration := ARRAY(SELECT DISTINCT CD_CONFIGURATION FROM CONFIGURATION ORDER BY CD_CONFIGURATION);
	
	-- INSERT NEW PARAMETERS
	-- FOR EACH "NUMBER ITERATIONS"
	FOREACH bigint_iterator IN ARRAY arr_nr_iteration
	LOOP
	
		-- FOR EACH PARAMETER TYPE DESCRIPTION
		FOREACH text_iterator IN ARRAY arr_ds_tp_parameter
		LOOP
		
			 CALL PARAMETER_INSERT(bigint_iterator, text_iterator, arr_percent_dataset, arr_ds_parallelism_data, arr_cd_resource, arr_cd_dataset, arr_cd_configuration);
	
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
	DELETE FROM DATASET;
	DELETE FROM RESOURCE;
	DELETE FROM CONFIGURATION;
	DELETE FROM FUNCTION;
	DELETE FROM ALGORITHM;
	DELETE FROM DEVICE;

	-- RESET SEQUENCES
	ALTER SEQUENCE experiment_id_experiment_seq RESTART WITH 1;
	ALTER SEQUENCE parameter_id_parameter_seq RESTART WITH 1;
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
		CD_ALGORITHM BIGINT,
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
		CD_ALGORITHM BIGINT,
		CD_FUNCTION BIGINT,
		ID_DEVICE BIGINT
	);
	
	CREATE TABLE RESOURCE
	(
		ID_RESOURCE BIGSERIAL PRIMARY KEY,
		CD_RESOURCE BIGINT,
		DS_RESOURCE VARCHAR,
		NR_NODES BIGINT,
		NR_COMPUTING_UNITS_CPU BIGINT,
		NR_COMPUTING_UNITS_GPU BIGINT,
		VL_MEMORY_PER_CPU_COMPUTING_UNIT BIGINT,
		VL_MEMORY_PER_GPU_COMPUTING_UNIT BIGINT
	);

	CREATE TABLE DATASET
	(
		ID_DATASET BIGSERIAL PRIMARY KEY,
		CD_DATASET BIGINT,
		DS_DATASET VARCHAR,
		VL_DATASET_MEMORY_SIZE BIGINT,
		DS_DATA_TYPE VARCHAR,
		VL_DATA_TYPE_MEMORY_SIZE BIGINT,
		VL_DATASET_SIZE BIGINT,
		VL_DATASET_ROW_SIZE BIGINT,
		VL_DATASET_COLUMN_SIZE BIGINT,
		NR_RANDOM_STATE BIGINT
	);
	
	CREATE TABLE PARAMETER
	(
		ID_PARAMETER BIGSERIAL PRIMARY KEY,
		CD_PARAMETER BIGINT,
		CD_CONFIGURATION BIGINT,
		CD_ALGORITHM BIGINT,
		CD_FUNCTION BIGINT,
		ID_DEVICE BIGINT,
		CD_DATASET BIGINT,
		CD_RESOURCE BIGINT,
		NR_ITERATIONS BIGINT,
		DS_TP_PARAMETER VARCHAR,
		VL_DATASET_ROW_SIZE BIGINT,
		VL_DATASET_COLUMN_SIZE BIGINT,
		VL_GRID_ROW_SIZE BIGINT,
		VL_GRID_COLUMN_SIZE BIGINT,
		VL_BLOCK_ROW_SIZE BIGINT,
		VL_BLOCK_COLUMN_SIZE BIGINT,
		VL_BLOCK_MEMORY_SIZE BIGINT,
		VL_BLOCK_MEMORY_SIZE_PERCENT_CPU DOUBLE PRECISION,
		VL_BLOCK_MEMORY_SIZE_PERCENT_GPU DOUBLE PRECISION,
		DS_STATUS_PARALLELISM VARCHAR,
		VL_BLOCK_SIZE_PERCENT_DATASET DOUBLE PRECISION
	);

	CREATE TABLE EXPERIMENT
	(
		ID_EXPERIMENT BIGSERIAL PRIMARY KEY,
		ID_PARAMETER BIGINT REFERENCES PARAMETER(ID_PARAMETER),
		VL_TOTAL_EXECUTION_TIME DOUBLE PRECISION,
		VL_INTER_TASK_EXECUTION_TIME DOUBLE PRECISION,
		VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC DOUBLE PRECISION,
		VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC DOUBLE PRECISION,
		VL_COMMUNICATION_TIME DOUBLE PRECISION,
		DT_PROCESSING DATE
	);
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
	DROP TABLE DATASET;
	DROP TABLE RESOURCE;
	DROP TABLE CONFIGURATION;
	DROP TABLE FUNCTION;
	DROP TABLE ALGORITHM;
	DROP TABLE DEVICE;
END; 
$BODY$;





-- RECURSIVE_CONFIGURATION_INSERT
CREATE OR REPLACE PROCEDURE RECURSIVE_CONFIGURATION_PERMUTATION(var_nr_function_config bigint, arr_device_config bigint[], var_i bigint, var_cd_algorithm bigint)
LANGUAGE plpgsql
AS $BODY$

BEGIN
    IF var_i = var_nr_function_config THEN
        -- insert item
        CALL CONFIGURATION_INSERT(var_nr_function_config, arr_device_config, var_i, var_cd_algorithm);
		RETURN;
    END IF;
	
    arr_device_config[var_i] := 1;
    CALL RECURSIVE_CONFIGURATION_PERMUTATION(var_nr_function_config, arr_device_config, var_i + 1, var_cd_algorithm);
 
    arr_device_config[var_i] := 2;
    CALL RECURSIVE_CONFIGURATION_PERMUTATION(var_nr_function_config, arr_device_config, var_i + 1, var_cd_algorithm);

END;
$BODY$;



-- CONFIGURATION_INSERT
CREATE OR REPLACE PROCEDURE CONFIGURATION_INSERT(var_nr_function_config bigint, arr_device_config bigint[], var_i bigint, var_cd_algorithm bigint)
LANGUAGE plpgsql
AS $BODY$
DECLARE
    var_cd_function bigint := 1;
    var_id_device_config bigint;
    var_cd_configuration_2 bigint;

BEGIN

    var_cd_configuration_2 := 
    (
        COALESCE(
            (SELECT
            MAX(CD_CONFIGURATION)
            FROM
            CONFIGURATION A
            WHERE
            A.CD_ALGORITHM = var_cd_algorithm),0
            )
            
    );

    var_cd_configuration_2 := var_cd_configuration_2 + 1;

    FOREACH var_id_device_config IN ARRAY arr_device_config
    LOOP
	
		INSERT INTO CONFIGURATION(CD_CONFIGURATION,CD_ALGORITHM,CD_FUNCTION,ID_DEVICE)
		(
			SELECT
			var_cd_configuration_2 AS CD_CONFIGURATION,
			A.CD_ALGORITHM,
			B.CD_FUNCTION,
			C.ID_DEVICE
			FROM
			ALGORITHM A 
			INNER JOIN FUNCTION B ON (A.ID_ALGORITHM = B.ID_ALGORITHM)
			INNER JOIN DEVICE C ON (B.ID_DEVICE = C.ID_DEVICE)
			WHERE
			A.CD_ALGORITHM = var_cd_algorithm
			AND B.CD_FUNCTION = var_cd_function
			AND C.ID_DEVICE = var_id_device_config
		);
		

        var_cd_function = var_cd_function + 1;
		
    END LOOP;
END;
$BODY$;




-- PARAMETER_INSERT
CREATE OR REPLACE PROCEDURE PARAMETER_INSERT(bigint_iterator bigint, text_iterator text, arr_percent_dataset numeric[], arr_ds_parallelism_data text[], arr_cd_resource bigint[], arr_cd_dataset bigint[], arr_cd_configuration bigint[])
LANGUAGE plpgsql
AS $BODY$
DECLARE
	numeric_iterator numeric;
	text_iterator_2 text;
	cd_resource_iterator bigint;
	cd_dataset_iterator bigint;
	cd_configuration_iterator bigint;
	
	var_cd_parameter bigint;

BEGIN
	
	-- SET INITIAL VALUE FOR CD_PARAMETER
	var_cd_parameter := (SELECT COALESCE(MAX(CD_PARAMETER),0) FROM PARAMETER);

	IF (text_iterator = 'VAR_BLOCK_CAPACITY_SIZE')
	THEN

		-- FOR EACH % AMOUNT OF THE DATA SET 
		FOREACH numeric_iterator IN ARRAY arr_percent_dataset
		LOOP
		
			-- FOR EACH RESOURCE
			FOREACH cd_resource_iterator IN ARRAY arr_cd_resource
			LOOP
			
				-- FOR EACH DATASET
				FOREACH cd_dataset_iterator IN ARRAY arr_cd_dataset
				LOOP
				
					var_cd_parameter := var_cd_parameter + 1;
				
					-- FOR EACH CONFIGURATION
					FOREACH cd_configuration_iterator IN ARRAY arr_cd_configuration
					LOOP

						-- COMBINE ALL ELEMENTS FROM "CONFIGURATION", "RESOURCE" AND "DATASET" TABLES AND INSERT INTO "PARAMETER" TABLE
						IF EXISTS(
							WITH T_CONFIGURATION AS (
												SELECT
												var_cd_parameter AS CD_PARAMETER,
												A.CD_CONFIGURATION,
												A.CD_ALGORITHM,
												A.CD_FUNCTION,
												A.ID_DEVICE
												FROM CONFIGURATION  A
												WHERE A.CD_CONFIGURATION = cd_configuration_iterator
												),
							T_RESOURCE AS (
											SELECT
											var_cd_parameter AS CD_PARAMETER,
											A.CD_RESOURCE,
											VL_MEMORY_PER_CPU_COMPUTING_UNIT,
											VL_MEMORY_PER_GPU_COMPUTING_UNIT
											FROM RESOURCE A
											WHERE A.CD_RESOURCE = cd_resource_iterator
											),
							T_DATASET AS (
											SELECT
											var_cd_parameter AS CD_PARAMETER,
											A.CD_DATASET,
											A.VL_DATASET_SIZE,
											A.VL_DATASET_ROW_SIZE,
											A.VL_DATASET_COLUMN_SIZE,
											A.VL_DATA_TYPE_MEMORY_SIZE
											FROM DATASET A
											WHERE A.CD_DATASET = cd_dataset_iterator
											)
							
								SELECT
								CD_CONFIGURATION,
								CD_ALGORITHM,
								CD_FUNCTION,
								ID_DEVICE,
								CD_DATASET,
								CD_RESOURCE,
								NR_ITERATIONS,
								DS_TP_PARAMETER,
								VL_DATASET_ROW_SIZE,
								VL_DATASET_COLUMN_SIZE,
								VL_GRID_ROW_SIZE,
								VL_GRID_COLUMN_SIZE,
								VL_BLOCK_ROW_SIZE,
								VL_BLOCK_COLUMN_SIZE,
								VL_BLOCK_MEMORY_SIZE,
								VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
								VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
								DS_STATUS_PARALLELISM,
								VL_BLOCK_SIZE_PERCENT_DATASET
								FROM PARAMETER
								
									INTERSECT
								
								SELECT
								A.CD_CONFIGURATION,
								A.CD_ALGORITHM,
								A.CD_FUNCTION,
								A.ID_DEVICE,
								B.CD_DATASET,
								C.CD_RESOURCE,
								bigint_iterator AS NR_ITERATIONS,
								text_iterator AS DS_TP_PARAMETER,
								B.VL_DATASET_ROW_SIZE AS VL_DATASET_ROW_SIZE,
								B.VL_DATASET_COLUMN_SIZE AS VL_DATASET_COLUMN_SIZE,
								CEIL(B.VL_DATASET_ROW_SIZE/(CEIL((B.VL_DATASET_SIZE*numeric_iterator)/B.VL_DATASET_COLUMN_SIZE))) AS VL_GRID_ROW_SIZE,
								CEIL(B.VL_DATASET_COLUMN_SIZE/(CEIL((B.VL_DATASET_SIZE*numeric_iterator)/B.VL_DATASET_ROW_SIZE))) AS VL_GRID_COLUMN_SIZE,
								CEIL((B.VL_DATASET_SIZE*numeric_iterator)/B.VL_DATASET_COLUMN_SIZE) AS VL_BLOCK_ROW_SIZE,
								CEIL((B.VL_DATASET_SIZE*numeric_iterator)/B.VL_DATASET_ROW_SIZE) AS VL_BLOCK_COLUMN_SIZE,
								CEIL((B.VL_DATASET_SIZE*numeric_iterator)/B.VL_DATASET_COLUMN_SIZE) * CEIL((B.VL_DATASET_SIZE*numeric_iterator)/B.VL_DATASET_ROW_SIZE) * B.VL_DATA_TYPE_MEMORY_SIZE AS VL_BLOCK_MEMORY_SIZE,
								(CEIL((B.VL_DATASET_SIZE*numeric_iterator)/B.VL_DATASET_COLUMN_SIZE) * CEIL((B.VL_DATASET_SIZE*numeric_iterator)/B.VL_DATASET_ROW_SIZE) * B.VL_DATA_TYPE_MEMORY_SIZE) / VL_MEMORY_PER_CPU_COMPUTING_UNIT AS VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
								(CEIL((B.VL_DATASET_SIZE*numeric_iterator)/B.VL_DATASET_COLUMN_SIZE) * CEIL((B.VL_DATASET_SIZE*numeric_iterator)/B.VL_DATASET_ROW_SIZE) * B.VL_DATA_TYPE_MEMORY_SIZE) / VL_MEMORY_PER_GPU_COMPUTING_UNIT AS VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
								NULL AS DS_STATUS_PARALLELISM,
								numeric_iterator AS VL_BLOCK_SIZE_PERCENT_DATASET
								FROM T_CONFIGURATION A
								INNER JOIN T_DATASET B ON (A.CD_PARAMETER = B.CD_PARAMETER)
								INNER JOIN T_RESOURCE C ON (A.CD_PARAMETER = C.CD_PARAMETER)
							)
							THEN

								CONTINUE;

							ELSE

								INSERT INTO PARAMETER(CD_PARAMETER,CD_CONFIGURATION,CD_ALGORITHM,CD_FUNCTION,ID_DEVICE,CD_DATASET,CD_RESOURCE,NR_ITERATIONS,DS_TP_PARAMETER,VL_DATASET_ROW_SIZE,VL_DATASET_COLUMN_SIZE,VL_GRID_ROW_SIZE,VL_GRID_COLUMN_SIZE,VL_BLOCK_ROW_SIZE,VL_BLOCK_COLUMN_SIZE,VL_BLOCK_MEMORY_SIZE,VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,DS_STATUS_PARALLELISM,VL_BLOCK_SIZE_PERCENT_DATASET)
								(

									WITH T_CONFIGURATION AS (
													SELECT
													var_cd_parameter AS CD_PARAMETER,
													A.CD_CONFIGURATION,
													A.CD_ALGORITHM,
													A.CD_FUNCTION,
													A.ID_DEVICE
													FROM CONFIGURATION  A
													WHERE A.CD_CONFIGURATION = cd_configuration_iterator
													),
									T_RESOURCE AS (
													SELECT
													var_cd_parameter AS CD_PARAMETER,
													A.CD_RESOURCE,
													VL_MEMORY_PER_CPU_COMPUTING_UNIT,
													VL_MEMORY_PER_GPU_COMPUTING_UNIT
													FROM RESOURCE A
													WHERE A.CD_RESOURCE = cd_resource_iterator
													),
									T_DATASET AS (
													SELECT
													var_cd_parameter AS CD_PARAMETER,
													A.CD_DATASET,
													A.VL_DATASET_SIZE,
													A.VL_DATASET_ROW_SIZE,
													A.VL_DATASET_COLUMN_SIZE,
													A.VL_DATA_TYPE_MEMORY_SIZE
													FROM DATASET A
													WHERE A.CD_DATASET = cd_dataset_iterator
													)

									SELECT
									A.CD_PARAMETER,
									A.CD_CONFIGURATION,
									A.CD_ALGORITHM,
									A.CD_FUNCTION,
									A.ID_DEVICE,
									B.CD_DATASET,
									C.CD_RESOURCE,
									bigint_iterator AS NR_ITERATIONS,
									text_iterator AS DS_TP_PARAMETER,
									B.VL_DATASET_ROW_SIZE AS VL_DATASET_ROW_SIZE,
									B.VL_DATASET_COLUMN_SIZE AS VL_DATASET_COLUMN_SIZE,
									CEIL(B.VL_DATASET_ROW_SIZE/(CEIL((B.VL_DATASET_SIZE*numeric_iterator)/B.VL_DATASET_COLUMN_SIZE))) AS VL_GRID_ROW_SIZE,
									CEIL(B.VL_DATASET_COLUMN_SIZE/(CEIL((B.VL_DATASET_SIZE*numeric_iterator)/B.VL_DATASET_ROW_SIZE))) AS VL_GRID_COLUMN_SIZE,
									CEIL((B.VL_DATASET_SIZE*numeric_iterator)/B.VL_DATASET_COLUMN_SIZE) AS VL_BLOCK_ROW_SIZE,
									CEIL((B.VL_DATASET_SIZE*numeric_iterator)/B.VL_DATASET_ROW_SIZE) AS VL_BLOCK_COLUMN_SIZE,
									CEIL((B.VL_DATASET_SIZE*numeric_iterator)/B.VL_DATASET_COLUMN_SIZE) * CEIL((B.VL_DATASET_SIZE*numeric_iterator)/B.VL_DATASET_ROW_SIZE) * B.VL_DATA_TYPE_MEMORY_SIZE AS VL_BLOCK_MEMORY_SIZE,
									(CEIL((B.VL_DATASET_SIZE*numeric_iterator)/B.VL_DATASET_COLUMN_SIZE) * CEIL((B.VL_DATASET_SIZE*numeric_iterator)/B.VL_DATASET_ROW_SIZE) * B.VL_DATA_TYPE_MEMORY_SIZE) / VL_MEMORY_PER_CPU_COMPUTING_UNIT AS VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
									(CEIL((B.VL_DATASET_SIZE*numeric_iterator)/B.VL_DATASET_COLUMN_SIZE) * CEIL((B.VL_DATASET_SIZE*numeric_iterator)/B.VL_DATASET_ROW_SIZE) * B.VL_DATA_TYPE_MEMORY_SIZE) / VL_MEMORY_PER_GPU_COMPUTING_UNIT AS VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
									NULL AS DS_STATUS_PARALLELISM,
									numeric_iterator AS VL_BLOCK_SIZE_PERCENT_DATASET
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

		-- FOR EACH PARALLELISM LEVEL
		FOREACH text_iterator_2 IN ARRAY arr_ds_parallelism_data
		LOOP

			IF (text_iterator_2 = 'MIN_INTER_MAX_INTRA')
			THEN
			
				
				-- FOR EACH RESOURCE
				FOREACH cd_resource_iterator IN ARRAY arr_cd_resource
				LOOP
			
					-- FOR EACH DATASET
					FOREACH cd_dataset_iterator IN ARRAY arr_cd_dataset
					LOOP
					
						var_cd_parameter := var_cd_parameter + 1;
				
						-- FOR EACH CONFIGURATION
						FOREACH cd_configuration_iterator IN ARRAY arr_cd_configuration
						LOOP
				
							-- COMBINE ALL ELEMENTS FROM "CONFIGURATION", "RESOURCE" AND "DATASET" TABLES AND INSERT INTO "PARAMETER" TABLE
							IF EXISTS(
									WITH T_CONFIGURATION AS (
														SELECT
														var_cd_parameter AS CD_PARAMETER,
														A.CD_CONFIGURATION,
														A.CD_ALGORITHM,
														A.CD_FUNCTION,
														A.ID_DEVICE
														FROM CONFIGURATION  A
														WHERE A.CD_CONFIGURATION = cd_configuration_iterator
														),
										T_RESOURCE AS (
														SELECT
														var_cd_parameter AS CD_PARAMETER,
														A.CD_RESOURCE,
														VL_MEMORY_PER_CPU_COMPUTING_UNIT,
														VL_MEMORY_PER_GPU_COMPUTING_UNIT
														FROM RESOURCE A
														WHERE A.CD_RESOURCE = cd_resource_iterator
														),
										T_DATASET AS (
														SELECT
														var_cd_parameter AS CD_PARAMETER,
														A.CD_DATASET,
														A.VL_DATASET_SIZE,
														A.VL_DATASET_ROW_SIZE,
														A.VL_DATASET_COLUMN_SIZE,
														A.VL_DATA_TYPE_MEMORY_SIZE
														FROM DATASET A
														WHERE A.CD_DATASET = cd_dataset_iterator
														)
								
										SELECT
										CD_CONFIGURATION,
										CD_ALGORITHM,
										CD_FUNCTION,
										ID_DEVICE,
										CD_DATASET,
										CD_RESOURCE,
										NR_ITERATIONS,
										DS_TP_PARAMETER,
										VL_DATASET_ROW_SIZE,
										VL_DATASET_COLUMN_SIZE,
										VL_GRID_ROW_SIZE,
										VL_GRID_COLUMN_SIZE,
										VL_BLOCK_ROW_SIZE,
										VL_BLOCK_COLUMN_SIZE,
										VL_BLOCK_MEMORY_SIZE,
										VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
										VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
										DS_STATUS_PARALLELISM,
										VL_BLOCK_SIZE_PERCENT_DATASET
										FROM PARAMETER

											INTERSECT
										
										SELECT
										A.CD_CONFIGURATION,
										A.CD_ALGORITHM,
										A.CD_FUNCTION,
										A.ID_DEVICE,
										B.CD_DATASET,
										C.CD_RESOURCE,
										bigint_iterator AS NR_ITERATIONS,
										text_iterator AS DS_TP_PARAMETER,
										B.VL_DATASET_ROW_SIZE AS VL_DATASET_ROW_SIZE,
										B.VL_DATASET_COLUMN_SIZE AS VL_DATASET_COLUMN_SIZE,
										1 AS VL_GRID_ROW_SIZE,
										1 AS VL_GRID_COLUMN_SIZE,
										CEIL(B.VL_DATASET_ROW_SIZE/1) AS VL_BLOCK_ROW_SIZE,
										CEIL(B.VL_DATASET_COLUMN_SIZE/1) AS VL_BLOCK_COLUMN_SIZE,
										CEIL(B.VL_DATASET_ROW_SIZE/1) * CEIL(B.VL_DATASET_COLUMN_SIZE/1) * VL_DATA_TYPE_MEMORY_SIZE AS VL_BLOCK_MEMORY_SIZE,
										(CEIL(B.VL_DATASET_ROW_SIZE/1) * CEIL(B.VL_DATASET_COLUMN_SIZE/1) * VL_DATA_TYPE_MEMORY_SIZE) / VL_MEMORY_PER_CPU_COMPUTING_UNIT AS VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
										(CEIL(B.VL_DATASET_ROW_SIZE/1) * CEIL(B.VL_DATASET_COLUMN_SIZE/1) * VL_DATA_TYPE_MEMORY_SIZE) / VL_MEMORY_PER_GPU_COMPUTING_UNIT AS VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
										text_iterator_2 AS DS_STATUS_PARALLELISM,
										NULL AS VL_BLOCK_SIZE_PERCENT_DATASET
										FROM T_CONFIGURATION A
										INNER JOIN T_DATASET B ON (A.CD_PARAMETER = B.CD_PARAMETER)
										INNER JOIN T_RESOURCE C ON (A.CD_PARAMETER = C.CD_PARAMETER)
								
								)
								THEN
								
									CONTINUE;
									
								ELSE
								
									INSERT INTO PARAMETER(CD_PARAMETER,CD_CONFIGURATION,CD_ALGORITHM,CD_FUNCTION,ID_DEVICE,CD_DATASET,CD_RESOURCE,NR_ITERATIONS,DS_TP_PARAMETER,VL_DATASET_ROW_SIZE,VL_DATASET_COLUMN_SIZE,VL_GRID_ROW_SIZE,VL_GRID_COLUMN_SIZE,VL_BLOCK_ROW_SIZE,VL_BLOCK_COLUMN_SIZE,VL_BLOCK_MEMORY_SIZE,VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,DS_STATUS_PARALLELISM,VL_BLOCK_SIZE_PERCENT_DATASET)
									(
											WITH T_CONFIGURATION AS (
																SELECT
																var_cd_parameter AS CD_PARAMETER,
																A.CD_CONFIGURATION,
																A.CD_ALGORITHM,
																A.CD_FUNCTION,
																A.ID_DEVICE
																FROM CONFIGURATION  A
																WHERE A.CD_CONFIGURATION = cd_configuration_iterator
																),
											T_RESOURCE AS (
															SELECT
															var_cd_parameter AS CD_PARAMETER,
															A.CD_RESOURCE,
															VL_MEMORY_PER_CPU_COMPUTING_UNIT,
															VL_MEMORY_PER_GPU_COMPUTING_UNIT
															FROM RESOURCE A
															WHERE A.CD_RESOURCE = cd_resource_iterator
															),
											T_DATASET AS (
															SELECT
															var_cd_parameter AS CD_PARAMETER,
															A.CD_DATASET,
															A.VL_DATASET_SIZE,
															A.VL_DATASET_ROW_SIZE,
															A.VL_DATASET_COLUMN_SIZE,
															A.VL_DATA_TYPE_MEMORY_SIZE
															FROM DATASET A
															WHERE A.CD_DATASET = cd_dataset_iterator
															)
											SELECT
											A.CD_PARAMETER,
											A.CD_CONFIGURATION,
											A.CD_ALGORITHM,
											A.CD_FUNCTION,
											A.ID_DEVICE,
											B.CD_DATASET,
											C.CD_RESOURCE,
											bigint_iterator AS NR_ITERATIONS,
											text_iterator AS DS_TP_PARAMETER,
											B.VL_DATASET_ROW_SIZE AS VL_DATASET_ROW_SIZE,
											B.VL_DATASET_COLUMN_SIZE AS VL_DATASET_COLUMN_SIZE,
											1 AS VL_GRID_ROW_SIZE,
											1 AS VL_GRID_COLUMN_SIZE,
											CEIL(B.VL_DATASET_ROW_SIZE/1) AS VL_BLOCK_ROW_SIZE,
											CEIL(B.VL_DATASET_COLUMN_SIZE/1) AS VL_BLOCK_COLUMN_SIZE,
											CEIL(B.VL_DATASET_ROW_SIZE/1) * CEIL(B.VL_DATASET_COLUMN_SIZE/1) * VL_DATA_TYPE_MEMORY_SIZE AS VL_BLOCK_MEMORY_SIZE,
											(CEIL(B.VL_DATASET_ROW_SIZE/1) * CEIL(B.VL_DATASET_COLUMN_SIZE/1) * VL_DATA_TYPE_MEMORY_SIZE) / VL_MEMORY_PER_CPU_COMPUTING_UNIT AS VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
											(CEIL(B.VL_DATASET_ROW_SIZE/1) * CEIL(B.VL_DATASET_COLUMN_SIZE/1) * VL_DATA_TYPE_MEMORY_SIZE) / VL_MEMORY_PER_GPU_COMPUTING_UNIT AS VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
											text_iterator_2 AS DS_STATUS_PARALLELISM,
											NULL AS VL_BLOCK_SIZE_PERCENT_DATASET
											FROM T_CONFIGURATION A
											INNER JOIN T_DATASET B ON (A.CD_PARAMETER = B.CD_PARAMETER)
											INNER JOIN T_RESOURCE C ON (A.CD_PARAMETER = C.CD_PARAMETER)
									);
									
								END IF;
							
						END LOOP;

					END LOOP;

				END LOOP;

			ELSE

				-- FOR EACH RESOURCE
				FOREACH cd_resource_iterator IN ARRAY arr_cd_resource
				LOOP
			
					-- FOR EACH DATASET
					FOREACH cd_dataset_iterator IN ARRAY arr_cd_dataset
					LOOP
				
						var_cd_parameter := var_cd_parameter + 1;
						
						-- FOR EACH CONFIGURATION
						FOREACH cd_configuration_iterator IN ARRAY arr_cd_configuration
						LOOP

							-- COMBINE ALL ELEMENTS FROM "CONFIGURATION", "RESOURCE" AND "DATASET" TABLES AND INSERT INTO "PARAMETER" TABLE
							IF EXISTS(
								
								WITH T_CONFIGURATION AS (
													SELECT
													var_cd_parameter AS CD_PARAMETER,
													A.CD_CONFIGURATION,
													A.CD_ALGORITHM,
													A.CD_FUNCTION,
													A.ID_DEVICE
													FROM CONFIGURATION  A
													WHERE A.CD_CONFIGURATION = cd_configuration_iterator
													),
									T_RESOURCE AS (
													SELECT
													var_cd_parameter AS CD_PARAMETER,
													A.CD_RESOURCE,
													VL_MEMORY_PER_CPU_COMPUTING_UNIT,
													VL_MEMORY_PER_GPU_COMPUTING_UNIT
													FROM RESOURCE A
													WHERE A.CD_RESOURCE = cd_resource_iterator
													),
									T_DATASET AS (
													SELECT
													var_cd_parameter AS CD_PARAMETER,
													A.CD_DATASET,
													A.VL_DATASET_SIZE,
													A.VL_DATASET_ROW_SIZE,
													A.VL_DATASET_COLUMN_SIZE,
													A.VL_DATA_TYPE_MEMORY_SIZE
													FROM DATASET A
													WHERE A.CD_DATASET = cd_dataset_iterator
													)
								
									SELECT
									CD_CONFIGURATION,
									CD_ALGORITHM,
									CD_FUNCTION,
									ID_DEVICE,
									CD_DATASET,
									CD_RESOURCE,
									NR_ITERATIONS,
									DS_TP_PARAMETER,
									VL_DATASET_ROW_SIZE,
									VL_DATASET_COLUMN_SIZE,
									VL_GRID_ROW_SIZE,
									VL_GRID_COLUMN_SIZE,
									VL_BLOCK_ROW_SIZE,
									VL_BLOCK_COLUMN_SIZE,
									VL_BLOCK_MEMORY_SIZE,
									VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
									VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
									DS_STATUS_PARALLELISM,
									VL_BLOCK_SIZE_PERCENT_DATASET
									FROM PARAMETER

										INTERSECT
								
									SELECT
									A.CD_CONFIGURATION,
									A.CD_ALGORITHM,
									A.CD_FUNCTION,
									A.ID_DEVICE,
									B.CD_DATASET,
									C.CD_RESOURCE,
									bigint_iterator AS NR_ITERATIONS,
									text_iterator AS DS_TP_PARAMETER,
									B.VL_DATASET_ROW_SIZE AS VL_DATASET_ROW_SIZE,
									B.VL_DATASET_COLUMN_SIZE AS VL_DATASET_COLUMN_SIZE,
									B.VL_DATASET_ROW_SIZE AS VL_GRID_ROW_SIZE,
									B.VL_DATASET_COLUMN_SIZE AS VL_GRID_COLUMN_SIZE,
									CEIL(B.VL_DATASET_ROW_SIZE/B.VL_DATASET_ROW_SIZE) AS VL_BLOCK_ROW_SIZE,
									CEIL(B.VL_DATASET_COLUMN_SIZE/B.VL_DATASET_COLUMN_SIZE) AS VL_BLOCK_COLUMN_SIZE,
									CEIL(B.VL_DATASET_ROW_SIZE/B.VL_DATASET_ROW_SIZE) * CEIL(B.VL_DATASET_COLUMN_SIZE/B.VL_DATASET_COLUMN_SIZE) * VL_DATA_TYPE_MEMORY_SIZE AS VL_BLOCK_MEMORY_SIZE,
									(CEIL(B.VL_DATASET_ROW_SIZE/B.VL_DATASET_ROW_SIZE) * CEIL(B.VL_DATASET_COLUMN_SIZE/B.VL_DATASET_COLUMN_SIZE) * VL_DATA_TYPE_MEMORY_SIZE) / VL_MEMORY_PER_CPU_COMPUTING_UNIT AS VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
									(CEIL(B.VL_DATASET_ROW_SIZE/B.VL_DATASET_ROW_SIZE) * CEIL(B.VL_DATASET_COLUMN_SIZE/B.VL_DATASET_COLUMN_SIZE) * VL_DATA_TYPE_MEMORY_SIZE) / VL_MEMORY_PER_GPU_COMPUTING_UNIT AS VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
									text_iterator_2 AS DS_STATUS_PARALLELISM,
									NULL AS VL_BLOCK_SIZE_PERCENT_DATASET
									FROM T_CONFIGURATION A
									INNER JOIN T_DATASET B ON (A.CD_PARAMETER = B.CD_PARAMETER)
									INNER JOIN T_RESOURCE C ON (A.CD_PARAMETER = C.CD_PARAMETER)
								
							)
							THEN
								
								CONTINUE;
								
							ELSE
							
								INSERT INTO PARAMETER(CD_PARAMETER,CD_CONFIGURATION,CD_ALGORITHM,CD_FUNCTION,ID_DEVICE,CD_DATASET,CD_RESOURCE,NR_ITERATIONS,DS_TP_PARAMETER,VL_DATASET_ROW_SIZE,VL_DATASET_COLUMN_SIZE,VL_GRID_ROW_SIZE,VL_GRID_COLUMN_SIZE,VL_BLOCK_ROW_SIZE,VL_BLOCK_COLUMN_SIZE,VL_BLOCK_MEMORY_SIZE,VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,DS_STATUS_PARALLELISM,VL_BLOCK_SIZE_PERCENT_DATASET)
								(
										WITH T_CONFIGURATION AS (
															SELECT
															var_cd_parameter AS CD_PARAMETER,
															A.CD_CONFIGURATION,
															A.CD_ALGORITHM,
															A.CD_FUNCTION,
															A.ID_DEVICE
															FROM CONFIGURATION  A
															WHERE A.CD_CONFIGURATION = cd_configuration_iterator
															),
										T_RESOURCE AS (
														SELECT
														var_cd_parameter AS CD_PARAMETER,
														A.CD_RESOURCE,
														VL_MEMORY_PER_CPU_COMPUTING_UNIT,
														VL_MEMORY_PER_GPU_COMPUTING_UNIT
														FROM RESOURCE A
														WHERE A.CD_RESOURCE = cd_resource_iterator
														),
										T_DATASET AS (
														SELECT
														var_cd_parameter AS CD_PARAMETER,
														A.CD_DATASET,
														A.VL_DATASET_SIZE,
														A.VL_DATASET_ROW_SIZE,
														A.VL_DATASET_COLUMN_SIZE,
														A.VL_DATA_TYPE_MEMORY_SIZE
														FROM DATASET A
														WHERE A.CD_DATASET = cd_dataset_iterator
														)
										SELECT
										A.CD_PARAMETER,
										A.CD_CONFIGURATION,
										A.CD_ALGORITHM,
										A.CD_FUNCTION,
										A.ID_DEVICE,
										B.CD_DATASET,
										C.CD_RESOURCE,
										bigint_iterator AS NR_ITERATIONS,
										text_iterator AS DS_TP_PARAMETER,
										B.VL_DATASET_ROW_SIZE AS VL_DATASET_ROW_SIZE,
										B.VL_DATASET_COLUMN_SIZE AS VL_DATASET_COLUMN_SIZE,
										B.VL_DATASET_ROW_SIZE AS VL_GRID_ROW_SIZE,
										B.VL_DATASET_COLUMN_SIZE AS VL_GRID_COLUMN_SIZE,
										CEIL(B.VL_DATASET_ROW_SIZE/B.VL_DATASET_ROW_SIZE) AS VL_BLOCK_ROW_SIZE,
										CEIL(B.VL_DATASET_COLUMN_SIZE/B.VL_DATASET_COLUMN_SIZE) AS VL_BLOCK_COLUMN_SIZE,
										CEIL(B.VL_DATASET_ROW_SIZE/B.VL_DATASET_ROW_SIZE) * CEIL(B.VL_DATASET_COLUMN_SIZE/B.VL_DATASET_COLUMN_SIZE) * VL_DATA_TYPE_MEMORY_SIZE AS VL_BLOCK_MEMORY_SIZE,
										(CEIL(B.VL_DATASET_ROW_SIZE/B.VL_DATASET_ROW_SIZE) * CEIL(B.VL_DATASET_COLUMN_SIZE/B.VL_DATASET_COLUMN_SIZE) * VL_DATA_TYPE_MEMORY_SIZE) / VL_MEMORY_PER_CPU_COMPUTING_UNIT AS VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
										(CEIL(B.VL_DATASET_ROW_SIZE/B.VL_DATASET_ROW_SIZE) * CEIL(B.VL_DATASET_COLUMN_SIZE/B.VL_DATASET_COLUMN_SIZE) * VL_DATA_TYPE_MEMORY_SIZE) / VL_MEMORY_PER_GPU_COMPUTING_UNIT AS VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
										text_iterator_2 AS DS_STATUS_PARALLELISM,
										NULL AS VL_BLOCK_SIZE_PERCENT_DATASET
										FROM T_CONFIGURATION A
										INNER JOIN T_DATASET B ON (A.CD_PARAMETER = B.CD_PARAMETER)
										INNER JOIN T_RESOURCE C ON (A.CD_PARAMETER = C.CD_PARAMETER)
								);
								
							END IF;
							
						END LOOP;

					END LOOP;

				END LOOP;

			END IF;

		END LOOP;	

	END IF;

END;
$BODY$;