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
								CEIL(B.VL_DATASET_ROW_SIZE/(CEIL((B.VL_DATASET_SIZE*numeric_iterator)/B.VL_DATASET_ROW_SIZE))) AS VL_GRID_COLUMN_SIZE,
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

								INSERT INTO PARAMETER(CD_PARAMETER,CD_CONFIGURATION,CD_ALGORITHM,CD_FUNCTION,ID_DEVICE,CD_DATASET,CD_RESOURCE,NR_ITERATIONS,DS_TP_PARAMETER,VL_DATASET_ROW_SIZE,VL_DATASET_COLUMN_SIZE,VL_GRID_ROW_SIZE,VL_GRID_COLUMN_SIZE,VL_BLOCK_ROW_SIZE,VL_BLOCK_COLUMN_SIZE,DS_STATUS_PARALLELISM,VL_BLOCK_SIZE_PERCENT_DATASET)
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
									CEIL(B.VL_DATASET_ROW_SIZE/(CEIL((B.VL_DATASET_SIZE*numeric_iterator)/B.VL_DATASET_ROW_SIZE))) AS VL_GRID_COLUMN_SIZE,
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
								
									INSERT INTO PARAMETER(CD_PARAMETER,CD_CONFIGURATION,CD_ALGORITHM,CD_FUNCTION,ID_DEVICE,CD_DATASET,CD_RESOURCE,NR_ITERATIONS,DS_TP_PARAMETER,VL_DATASET_ROW_SIZE,VL_DATASET_COLUMN_SIZE,VL_GRID_ROW_SIZE,VL_GRID_COLUMN_SIZE,VL_BLOCK_ROW_SIZE,VL_BLOCK_COLUMN_SIZE,DS_STATUS_PARALLELISM,VL_BLOCK_SIZE_PERCENT_DATASET)
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
							
								INSERT INTO PARAMETER(CD_PARAMETER,CD_CONFIGURATION,CD_ALGORITHM,CD_FUNCTION,ID_DEVICE,CD_DATASET,CD_RESOURCE,NR_ITERATIONS,DS_TP_PARAMETER,VL_DATASET_ROW_SIZE,VL_DATASET_COLUMN_SIZE,VL_GRID_ROW_SIZE,VL_GRID_COLUMN_SIZE,VL_BLOCK_ROW_SIZE,VL_BLOCK_COLUMN_SIZE,DS_STATUS_PARALLELISM,VL_BLOCK_SIZE_PERCENT_DATASET)
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