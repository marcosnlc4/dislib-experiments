--###################### MOTIVATIONAL CHARTS
-- PARAMETERS
SELECT
distinct
	(SELECT DISTINCT X.DS_ALGORITHM FROM ALGORITHM X WHERE X.ID_ALGORITHM = A.ID_ALGORITHM) AS DS_ALGORITHM,
	(SELECT DISTINCT Y.DS_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = A.ID_FUNCTION) AS DS_DEVICE,
	C.VL_DATASET_MEMORY_SIZE * 1*10^(-9) as VL_DATASET_MEMORY_SIZE,
	C.VL_DATASET_ROW_DIMENSION,
	C.VL_DATASET_COLUMN_DIMENSION,
	A.VL_BLOCK_MEMORY_SIZE * 1*10^(-6) AS VL_BLOCK_MEMORY_SIZE,
	A.VL_BLOCK_ROW_DIMENSION,
	A.VL_BLOCK_COLUMN_DIMENSION,
	ROUND((CAST(A.VL_BLOCK_MEMORY_SIZE AS NUMERIC)/CAST(C.VL_DATASET_MEMORY_SIZE AS NUMERIC)),3) AS VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
	(SELECT X.DS_STORAGE FROM PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = A.ID_PARAMETER_TYPE) AS DS_STORAGE
FROM PARAMETER A
INNER JOIN RESOURCE B ON (A.ID_RESOURCE = B.ID_RESOURCE)
INNER JOIN DATASET C ON (A.ID_DATASET = C.ID_DATASET)
WHERE
(SELECT DISTINCT X.DS_ALGORITHM FROM ALGORITHM X WHERE X.ID_ALGORITHM = A.ID_ALGORITHM) = 'KMEANS' -- FIXED VALUE
AND A.NR_ITERATIONS = 5 -- FIXED VALUE
AND C.DS_DATASET = 'S_10GB_1'
AND (SELECT X.DS_PARAMETER_TYPE FROM PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = A.ID_PARAMETER_TYPE) = 'VAR_GRID_ROW_5'
AND B.DS_RESOURCE = 'MINOTAURO_9_NODES_1_CORE'
--AND A.VL_BLOCK_MEMORY_SIZE NOT IN 
order by
ROUND((CAST(A.VL_BLOCK_MEMORY_SIZE AS NUMERIC)/CAST(C.VL_DATASET_MEMORY_SIZE AS NUMERIC)),3) desc,
(SELECT DISTINCT Y.DS_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = A.ID_FUNCTION)




-- SPEEDUPS KMEANS
--SET search_path = user_dev,schema_dev; --KMEANS
--SET search_path = user_dev,schema_dev_matmul; --MATMUL
--SHOW search_path;

-- SPEEDUPS KMEANS
-- CONSIDERING ONLY SERIAL FRACTION AS INTRA-TASK OVERHEAD (THIS WAS USED IN THE EXPERIMENTS FOR PAPER 1)
WITH T_CPU AS (
                                    SELECT
                                    A.VL_TOTAL_EXECUTION_TIME,
                                    A.VL_INTER_TASK_EXECUTION_TIME,
                                    A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
									A.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                                    A.VL_COMMUNICATION_TIME,
                                    (A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC + A.VL_COMMUNICATION_TIME) AS VL_INTRA_TASK_EXECUTION_TIME_FREE_ADDITIONAL,
									(A.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC-A.VL_COMMUNICATION_TIME) AS VL_INTRA_TASK_EXECUTION_TIME_FREE_COMMUNICATION,
                                    B.ID_PARAMETER,
                                    B.CD_PARAMETER,
                                    B.CD_CONFIGURATION,
                                    B.ID_ALGORITHM,
                                    (SELECT DISTINCT X.DS_ALGORITHM FROM schema_dev.ALGORITHM X WHERE X.ID_ALGORITHM = B.ID_ALGORITHM) AS DS_ALGORITHM,
                                    B.ID_FUNCTION,
                                    (SELECT DISTINCT X.DS_FUNCTION FROM schema_dev.FUNCTION X WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS DS_FUNCTION,
                                    (SELECT DISTINCT Y.ID_DEVICE FROM schema_dev.FUNCTION X INNER JOIN schema_dev.DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS ID_DEVICE,
                                    (SELECT DISTINCT Y.DS_DEVICE FROM schema_dev.FUNCTION X INNER JOIN schema_dev.DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS DS_DEVICE,
                                    B.ID_DATASET,
                                    B.ID_RESOURCE,
                                    B.ID_PARAMETER_TYPE,
                                    (SELECT X.DS_PARAMETER_TYPE FROM schema_dev.PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) AS DS_PARAMETER_TYPE,
                                    (SELECT X.DS_PARAMETER_ATTRIBUTE FROM schema_dev.PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) AS DS_PARAMETER_ATTRIBUTE,
                                    B.NR_ITERATIONS,
                                    B.VL_GRID_ROW_DIMENSION,
                                    B.VL_GRID_COLUMN_DIMENSION,
                                    B.VL_BLOCK_ROW_DIMENSION,
                                    B.VL_BLOCK_COLUMN_DIMENSION,
                                    B.VL_BLOCK_MEMORY_SIZE,
                                    B.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                                    B.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                                    ROUND((CAST(B.VL_BLOCK_MEMORY_SIZE AS NUMERIC)/CAST(D.VL_DATASET_MEMORY_SIZE AS NUMERIC))*100,2) AS VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                    C.DS_RESOURCE,
                                    C.NR_NODES,
                                    C.NR_COMPUTING_UNITS_CPU,
                                    C.NR_COMPUTING_UNITS_GPU,
                                    C.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                                    C.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
									(C.NR_NODES-1) || ' (' || (C.NR_NODES-1)*C.NR_COMPUTING_UNITS_CPU || ';' || (C.NR_NODES-1)*4 || ')' AS NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU_GPU,
                                    D.DS_DATASET,
                                    D.VL_DATASET_MEMORY_SIZE,
                                    D.DS_DATA_TYPE,
                                    D.VL_DATA_TYPE_MEMORY_SIZE,
                                    D.VL_DATASET_DIMENSION,
                                    D.VL_DATASET_ROW_DIMENSION,
                                    D.VL_DATASET_COLUMN_DIMENSION,
                                    D.NR_RANDOM_STATE
                                FROM schema_dev.EXPERIMENT A
                                INNER JOIN schema_dev.PARAMETER B ON (A.ID_PARAMETER = B.ID_PARAMETER)
                                INNER JOIN schema_dev.RESOURCE C ON (B.ID_RESOURCE = C.ID_RESOURCE)
                                INNER JOIN schema_dev.DATASET D ON (B.ID_DATASET = D.ID_DATASET)
                                WHERE
                                (SELECT DISTINCT Y.DS_DEVICE FROM schema_dev.FUNCTION X INNER JOIN schema_dev.DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) = 'CPU'
                                
                                UNION ALL
                        
                                    SELECT
                                    Y.VL_TOTAL_EXECUTION_TIME,
                                    Y.VL_INTER_TASK_EXECUTION_TIME,
                                    Y.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                                    Y.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                                    Y.VL_COMMUNICATION_TIME,
                                    (Y.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC + Y.VL_COMMUNICATION_TIME) AS VL_INTRA_TASK_EXECUTION_TIME_FREE_ADDITIONAL,
									(Y.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC+Y.VL_ADDITIONAL_TIME) AS VL_INTRA_TASK_EXECUTION_TIME_FREE_COMMUNICATION,
                                    Y.ID_PARAMETER,
                                    Y.CD_PARAMETER,
                                    Y.CD_CONFIGURATION,
                                    Y.ID_ALGORITHM,
                                    Y.DS_ALGORITHM,
                                    Y.ID_FUNCTION,
                                    Y.DS_FUNCTION,
                                    Y.ID_DEVICE,
                                    Y.DS_DEVICE,
                                    Y.ID_DATASET,
                                    Y.ID_RESOURCE,
                                    Y.ID_PARAMETER_TYPE,
                                    Y.DS_PARAMETER_TYPE,
                                    Y.DS_PARAMETER_ATTRIBUTE,
                                    Y.NR_ITERATIONS,
                                    Y.VL_GRID_ROW_DIMENSION,
                                    Y.VL_GRID_COLUMN_DIMENSION,
                                    Y.VL_BLOCK_ROW_DIMENSION,
                                    Y.VL_BLOCK_COLUMN_DIMENSION,
                                    Y.VL_BLOCK_MEMORY_SIZE,
                                    Y.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                                    Y.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                                    Y.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                    Y.DS_RESOURCE,
                                    Y.NR_NODES,
                                    Y.NR_COMPUTING_UNITS_CPU,
                                    Y.NR_COMPUTING_UNITS_GPU,
                                    Y.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                                    Y.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
									Y.NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU_GPU,
                                    Y.DS_DATASET,
                                    Y.VL_DATASET_MEMORY_SIZE,
                                    Y.DS_DATA_TYPE,
                                    Y.VL_DATA_TYPE_MEMORY_SIZE,
                                    Y.VL_DATASET_DIMENSION,
                                    Y.VL_DATASET_ROW_DIMENSION,
                                    Y.VL_DATASET_COLUMN_DIMENSION,
                                    Y.NR_RANDOM_STATE
                                    FROM
                                    (
                                        SELECT
                                        AVG(X.VL_TOTAL_EXECUTION_TIME) AS VL_TOTAL_EXECUTION_TIME,
                                        AVG(X.VL_INTER_TASK_EXECUTION_TIME) AS VL_INTER_TASK_EXECUTION_TIME,
                                        AVG(X.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC) AS VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                                        AVG(X.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC) AS VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                                        AVG(X.VL_COMMUNICATION_TIME_1) AS VL_COMMUNICATION_TIME_1,
                                        AVG(X.VL_COMMUNICATION_TIME_2) AS VL_COMMUNICATION_TIME_2,
                                        AVG(X.VL_COMMUNICATION_TIME) AS VL_COMMUNICATION_TIME,
                                        AVG(X.VL_ADDITIONAL_TIME_1) AS VL_ADDITIONAL_TIME_1,
                                        AVG(X.VL_ADDITIONAL_TIME_2) AS VL_ADDITIONAL_TIME_2,
                                        AVG(X.VL_ADDITIONAL_TIME) AS VL_ADDITIONAL_TIME,
                                        X.ID_PARAMETER,
                                        X.CD_PARAMETER,
                                        X.CD_CONFIGURATION,
                                        X.ID_ALGORITHM,
                                        X.DS_ALGORITHM,
                                        X.ID_FUNCTION,
                                        X.DS_FUNCTION,
                                        X.ID_DEVICE,
                                        X.DS_DEVICE,
                                        X.ID_DATASET,
                                        X.ID_RESOURCE,
                                        X.ID_PARAMETER_TYPE,
                                        X.DS_PARAMETER_TYPE,
                                        X.DS_PARAMETER_ATTRIBUTE,
                                        X.NR_ITERATIONS,
                                        X.VL_GRID_ROW_DIMENSION,
                                        X.VL_GRID_COLUMN_DIMENSION,
                                        X.VL_GRID_ROW_X_COLUMN_DIMENSION,
                                        X.VL_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                        X.VL_CONCAT_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                        X.VL_BLOCK_ROW_DIMENSION,
                                        X.VL_BLOCK_COLUMN_DIMENSION,
                                        X.VL_BLOCK_ROW_X_COLUMN_DIMENSION,
                                        X.VL_BLOCK_MEMORY_SIZE,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                        X.VL_CONCAT_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                        X.DS_RESOURCE,
                                        X.NR_NODES,
                                        X.NR_COMPUTING_UNITS_CPU,
                                        X.NR_COMPUTING_UNITS_GPU,
                                        X.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                                        X.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
										X.NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU_GPU,
                                        X.DS_DATASET,
                                        X.VL_DATASET_MEMORY_SIZE,
                                        X.DS_DATA_TYPE,
                                        X.VL_DATA_TYPE_MEMORY_SIZE,
                                        X.VL_DATASET_DIMENSION,
                                        X.VL_DATASET_ROW_DIMENSION,
                                        X.VL_DATASET_COLUMN_DIMENSION,
                                        X.VL_DATASET_ROW_X_COLUMN_DIMENSION,
                                        X.NR_RANDOM_STATE
                                        FROM
                                        (
                                            SELECT
                                                A.ID_EXPERIMENT,
                                                A.VL_TOTAL_EXECUTION_TIME,
                                                A.VL_INTER_TASK_EXECUTION_TIME,
                                                A.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                                                A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                                                A.VL_COMMUNICATION_TIME_1,
                                                A.VL_COMMUNICATION_TIME_2,
                                                A.VL_COMMUNICATION_TIME_1 + A.VL_COMMUNICATION_TIME_2 AS VL_COMMUNICATION_TIME,
                                                A.VL_ADDITIONAL_TIME_1,
                                                A.VL_ADDITIONAL_TIME_2,
                                                A.VL_ADDITIONAL_TIME_1 + A.VL_ADDITIONAL_TIME_2 AS VL_ADDITIONAL_TIME,
                                                A.DT_PROCESSING,
                                                B.ID_PARAMETER,
                                                B.CD_PARAMETER,
                                                B.CD_CONFIGURATION,
                                                B.ID_ALGORITHM,
                                                (SELECT DISTINCT X.DS_ALGORITHM FROM schema_dev.ALGORITHM X WHERE X.ID_ALGORITHM = B.ID_ALGORITHM) AS DS_ALGORITHM,
                                                B.ID_FUNCTION,
                                                (SELECT DISTINCT X.DS_FUNCTION FROM schema_dev.FUNCTION X WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS DS_FUNCTION,
                                                (SELECT DISTINCT Y.ID_DEVICE FROM schema_dev.FUNCTION X INNER JOIN schema_dev.DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS ID_DEVICE,
                                                (SELECT DISTINCT Y.DS_DEVICE FROM schema_dev.FUNCTION X INNER JOIN schema_dev.DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS DS_DEVICE,
                                                B.ID_DATASET,
                                                B.ID_RESOURCE,
                                                B.ID_PARAMETER_TYPE,
                                                (SELECT X.DS_PARAMETER_TYPE FROM schema_dev.PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) AS DS_PARAMETER_TYPE,
                                                (SELECT X.DS_PARAMETER_ATTRIBUTE FROM schema_dev.PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) AS DS_PARAMETER_ATTRIBUTE,
                                                B.NR_ITERATIONS,
                                                B.VL_GRID_ROW_DIMENSION,
                                                B.VL_GRID_COLUMN_DIMENSION,
                                                B.VL_GRID_ROW_DIMENSION || ' x ' || B.VL_GRID_COLUMN_DIMENSION AS VL_GRID_ROW_X_COLUMN_DIMENSION,
                                                ROUND((CAST(B.VL_GRID_COLUMN_DIMENSION AS NUMERIC)/CAST(D.VL_DATASET_COLUMN_DIMENSION AS NUMERIC))*100,2) AS VL_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                                B.VL_GRID_ROW_DIMENSION || ' x ' || B.VL_GRID_COLUMN_DIMENSION || ' (' || ROUND((CAST(B.VL_GRID_COLUMN_DIMENSION AS NUMERIC)/CAST(D.VL_DATASET_COLUMN_DIMENSION AS NUMERIC))*100,2) || '%)' AS VL_CONCAT_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                                B.VL_BLOCK_ROW_DIMENSION,
                                                B.VL_BLOCK_COLUMN_DIMENSION,
                                                B.VL_BLOCK_ROW_DIMENSION || ' x ' || B.VL_BLOCK_COLUMN_DIMENSION AS VL_BLOCK_ROW_X_COLUMN_DIMENSION,
                                                B.VL_BLOCK_MEMORY_SIZE,
                                                B.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                                                B.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                                                ROUND((CAST(B.VL_BLOCK_MEMORY_SIZE AS NUMERIC)/CAST(D.VL_DATASET_MEMORY_SIZE AS NUMERIC))*100,2) AS VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                                ROUND(B.VL_BLOCK_MEMORY_SIZE*1e-6,2) || ' (' || ROUND((CAST(B.VL_BLOCK_MEMORY_SIZE AS NUMERIC)/CAST(D.VL_DATASET_MEMORY_SIZE AS NUMERIC))*100,2) || '%)' AS VL_CONCAT_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                                C.DS_RESOURCE,
                                                C.NR_NODES,
                                                C.NR_COMPUTING_UNITS_CPU,
                                                C.NR_COMPUTING_UNITS_GPU,
                                                C.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                                                C.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
												(C.NR_NODES-1) || ' (' || (C.NR_NODES-1)*C.NR_COMPUTING_UNITS_CPU || ';' || (C.NR_NODES-1)*4 || ')' AS NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU_GPU,
                                                D.DS_DATASET,
                                                D.VL_DATASET_MEMORY_SIZE,
                                                D.DS_DATA_TYPE,
                                                D.VL_DATA_TYPE_MEMORY_SIZE,
                                                D.VL_DATASET_DIMENSION,
                                                D.VL_DATASET_ROW_DIMENSION,
                                                D.VL_DATASET_COLUMN_DIMENSION,
                                                D.VL_DATASET_ROW_DIMENSION || ' x ' || D.VL_DATASET_COLUMN_DIMENSION AS VL_DATASET_ROW_X_COLUMN_DIMENSION,
                                                D.NR_RANDOM_STATE
                                            FROM schema_dev.EXPERIMENT_RAW A
                                            INNER JOIN schema_dev.PARAMETER B ON (A.ID_PARAMETER = B.ID_PARAMETER)
                                            INNER JOIN schema_dev.RESOURCE C ON (B.ID_RESOURCE = C.ID_RESOURCE)
                                            INNER JOIN schema_dev.DATASET D ON (B.ID_DATASET = D.ID_DATASET)
                                            WHERE
                                            (SELECT DISTINCT Z.DS_DEVICE FROM schema_dev.FUNCTION W INNER JOIN schema_dev.DEVICE Z ON (W.ID_DEVICE = Z.ID_DEVICE) WHERE W.ID_FUNCTION = B.ID_FUNCTION) = 'CPU'
                                            AND A.NR_ALGORITHM_ITERATION <> 0
                                        ) X
                                        GROUP BY
                                        X.ID_PARAMETER,
                                        X.CD_PARAMETER,
                                        X.CD_CONFIGURATION,
                                        X.ID_ALGORITHM,
                                        X.DS_ALGORITHM,
                                        X.ID_FUNCTION,
                                        X.DS_FUNCTION,
                                        X.ID_DEVICE,
                                        X.DS_DEVICE,
                                        X.ID_DATASET,
                                        X.ID_RESOURCE,
                                        X.ID_PARAMETER_TYPE,
                                        X.DS_PARAMETER_TYPE,
                                        X.DS_PARAMETER_ATTRIBUTE,
                                        X.NR_ITERATIONS,
                                        X.VL_GRID_ROW_DIMENSION,
                                        X.VL_GRID_COLUMN_DIMENSION,
                                        X.VL_GRID_ROW_X_COLUMN_DIMENSION,
                                        X.VL_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                        X.VL_CONCAT_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                        X.VL_BLOCK_ROW_DIMENSION,
                                        X.VL_BLOCK_COLUMN_DIMENSION,
                                        X.VL_BLOCK_ROW_X_COLUMN_DIMENSION,
                                        X.VL_BLOCK_MEMORY_SIZE,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                        X.VL_CONCAT_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                        X.DS_RESOURCE,
                                        X.NR_NODES,
                                        X.NR_COMPUTING_UNITS_CPU,
                                        X.NR_COMPUTING_UNITS_GPU,
                                        X.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                                        X.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
										X.NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU_GPU,
                                        X.DS_DATASET,
                                        X.VL_DATASET_MEMORY_SIZE,
                                        X.DS_DATA_TYPE,
                                        X.VL_DATA_TYPE_MEMORY_SIZE,
                                        X.VL_DATASET_DIMENSION,
                                        X.VL_DATASET_ROW_DIMENSION,
                                        X.VL_DATASET_COLUMN_DIMENSION,
                                        X.VL_DATASET_ROW_X_COLUMN_DIMENSION,
                                        X.NR_RANDOM_STATE
                                    ) Y
                        
                                ),
                    T_GPU AS (
                                    SELECT
                                    A.VL_TOTAL_EXECUTION_TIME,
                                    A.VL_INTER_TASK_EXECUTION_TIME,
                                    A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                                    A.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                                    A.VL_COMMUNICATION_TIME,
                                    (A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC + A.VL_COMMUNICATION_TIME) AS VL_INTRA_TASK_EXECUTION_TIME_FREE_ADDITIONAL,
                                    (A.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC-A.VL_COMMUNICATION_TIME) AS VL_INTRA_TASK_EXECUTION_TIME_FREE_COMMUNICATION,
									B.ID_PARAMETER,
                                    B.CD_PARAMETER,
                                    B.CD_CONFIGURATION,
                                    B.ID_ALGORITHM,
                                    (SELECT DISTINCT X.DS_ALGORITHM FROM schema_dev.ALGORITHM X WHERE X.ID_ALGORITHM = B.ID_ALGORITHM) AS DS_ALGORITHM,
                                    B.ID_FUNCTION,
                                    (SELECT DISTINCT X.DS_FUNCTION FROM FUNCTION X WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS DS_FUNCTION,
                                    (SELECT DISTINCT Y.ID_DEVICE FROM FUNCTION X INNER JOIN schema_dev.DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS ID_DEVICE,
                                    (SELECT DISTINCT Y.DS_DEVICE FROM FUNCTION X INNER JOIN schema_dev.DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS DS_DEVICE,
                                    B.ID_DATASET,
                                    B.ID_RESOURCE,
                                    B.ID_PARAMETER_TYPE,
                                    (SELECT X.DS_PARAMETER_TYPE FROM schema_dev.PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) AS DS_PARAMETER_TYPE,
                                    (SELECT X.DS_PARAMETER_ATTRIBUTE FROM schema_dev.PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) AS DS_PARAMETER_ATTRIBUTE,
                                    B.NR_ITERATIONS,
                                    B.VL_GRID_ROW_DIMENSION,
                                    B.VL_GRID_COLUMN_DIMENSION,
                                    B.VL_BLOCK_ROW_DIMENSION,
                                    B.VL_BLOCK_COLUMN_DIMENSION,
                                    B.VL_BLOCK_MEMORY_SIZE,
                                    B.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                                    B.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                                    ROUND((CAST(B.VL_BLOCK_MEMORY_SIZE AS NUMERIC)/CAST(D.VL_DATASET_MEMORY_SIZE AS NUMERIC))*100,2) AS VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                    C.DS_RESOURCE,
                                    C.NR_NODES,
                                    C.NR_COMPUTING_UNITS_CPU,
                                    C.NR_COMPUTING_UNITS_GPU,
                                    C.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                                    C.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
									(C.NR_NODES-1) || ' (' || (C.NR_NODES-1)*C.NR_COMPUTING_UNITS_CPU || ';' || (C.NR_NODES-1)*4 || ')' AS NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU_GPU,
                                    D.DS_DATASET,
                                    D.VL_DATASET_MEMORY_SIZE,
                                    D.DS_DATA_TYPE,
                                    D.VL_DATA_TYPE_MEMORY_SIZE,
                                    D.VL_DATASET_DIMENSION,
                                    D.VL_DATASET_ROW_DIMENSION,
                                    D.VL_DATASET_COLUMN_DIMENSION,
                                    D.NR_RANDOM_STATE
                                    FROM schema_dev.EXPERIMENT A
                                    INNER JOIN schema_dev.PARAMETER B ON (A.ID_PARAMETER = B.ID_PARAMETER)
                                    INNER JOIN schema_dev.RESOURCE C ON (B.ID_RESOURCE = C.ID_RESOURCE)
                                    INNER JOIN schema_dev.DATASET D ON (B.ID_DATASET = D.ID_DATASET)
                                    WHERE
                                    (SELECT DISTINCT Y.DS_DEVICE FROM FUNCTION X INNER JOIN schema_dev.DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) = 'GPU'
                            
                                UNION ALL
                        
                                    SELECT
                                    Y.VL_TOTAL_EXECUTION_TIME,
                                    Y.VL_INTER_TASK_EXECUTION_TIME,
                                    Y.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                                    Y.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                                    Y.VL_COMMUNICATION_TIME,
                                    (Y.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC + Y.VL_COMMUNICATION_TIME) AS VL_INTRA_TASK_EXECUTION_TIME_FREE_ADDITIONAL,
                                    (Y.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC+Y.VL_ADDITIONAL_TIME) AS VL_INTRA_TASK_EXECUTION_TIME_FREE_COMMUNICATION,
									Y.ID_PARAMETER,
                                    Y.CD_PARAMETER,
                                    Y.CD_CONFIGURATION,
                                    Y.ID_ALGORITHM,
                                    Y.DS_ALGORITHM,
                                    Y.ID_FUNCTION,
                                    Y.DS_FUNCTION,
                                    Y.ID_DEVICE,
                                    Y.DS_DEVICE,
                                    Y.ID_DATASET,
                                    Y.ID_RESOURCE,
                                    Y.ID_PARAMETER_TYPE,
                                    Y.DS_PARAMETER_TYPE,
                                    Y.DS_PARAMETER_ATTRIBUTE,
                                    Y.NR_ITERATIONS,
                                    Y.VL_GRID_ROW_DIMENSION,
                                    Y.VL_GRID_COLUMN_DIMENSION,
                                    Y.VL_BLOCK_ROW_DIMENSION,
                                    Y.VL_BLOCK_COLUMN_DIMENSION,
                                    Y.VL_BLOCK_MEMORY_SIZE,
                                    Y.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                                    Y.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                                    Y.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                    Y.DS_RESOURCE,
                                    Y.NR_NODES,
                                    Y.NR_COMPUTING_UNITS_CPU,
                                    Y.NR_COMPUTING_UNITS_GPU,
                                    Y.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                                    Y.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
									Y.NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU_GPU,
                                    Y.DS_DATASET,
                                    Y.VL_DATASET_MEMORY_SIZE,
                                    Y.DS_DATA_TYPE,
                                    Y.VL_DATA_TYPE_MEMORY_SIZE,
                                    Y.VL_DATASET_DIMENSION,
                                    Y.VL_DATASET_ROW_DIMENSION,
                                    Y.VL_DATASET_COLUMN_DIMENSION,
                                    Y.NR_RANDOM_STATE
                                    FROM
                                    (
                                        SELECT
                                        AVG(X.VL_TOTAL_EXECUTION_TIME) AS VL_TOTAL_EXECUTION_TIME,
                                        AVG(X.VL_INTER_TASK_EXECUTION_TIME) AS VL_INTER_TASK_EXECUTION_TIME,
                                        AVG(X.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC) AS VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                                        AVG(X.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC) AS VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                                        AVG(X.VL_COMMUNICATION_TIME_1) AS VL_COMMUNICATION_TIME_1,
                                        AVG(X.VL_COMMUNICATION_TIME_2) AS VL_COMMUNICATION_TIME_2,
                                        AVG(X.VL_COMMUNICATION_TIME) AS VL_COMMUNICATION_TIME,
                                        AVG(X.VL_ADDITIONAL_TIME_1) AS VL_ADDITIONAL_TIME_1,
                                        AVG(X.VL_ADDITIONAL_TIME_2) AS VL_ADDITIONAL_TIME_2,
                                        AVG(X.VL_ADDITIONAL_TIME) AS VL_ADDITIONAL_TIME,
                                        X.ID_PARAMETER,
                                        X.CD_PARAMETER,
                                        X.CD_CONFIGURATION,
                                        X.ID_ALGORITHM,
                                        X.DS_ALGORITHM,
                                        X.ID_FUNCTION,
                                        X.DS_FUNCTION,
                                        X.ID_DEVICE,
                                        X.DS_DEVICE,
                                        X.ID_DATASET,
                                        X.ID_RESOURCE,
                                        X.ID_PARAMETER_TYPE,
                                        X.DS_PARAMETER_TYPE,
                                        X.DS_PARAMETER_ATTRIBUTE,
                                        X.NR_ITERATIONS,
                                        X.VL_GRID_ROW_DIMENSION,
                                        X.VL_GRID_COLUMN_DIMENSION,
                                        X.VL_GRID_ROW_X_COLUMN_DIMENSION,
                                        X.VL_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                        X.VL_CONCAT_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                        X.VL_BLOCK_ROW_DIMENSION,
                                        X.VL_BLOCK_COLUMN_DIMENSION,
                                        X.VL_BLOCK_ROW_X_COLUMN_DIMENSION,
                                        X.VL_BLOCK_MEMORY_SIZE,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                        X.VL_CONCAT_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                        X.DS_RESOURCE,
                                        X.NR_NODES,
                                        X.NR_COMPUTING_UNITS_CPU,
                                        X.NR_COMPUTING_UNITS_GPU,
                                        X.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                                        X.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
										X.NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU_GPU,
                                        X.DS_DATASET,
                                        X.VL_DATASET_MEMORY_SIZE,
                                        X.DS_DATA_TYPE,
                                        X.VL_DATA_TYPE_MEMORY_SIZE,
                                        X.VL_DATASET_DIMENSION,
                                        X.VL_DATASET_ROW_DIMENSION,
                                        X.VL_DATASET_COLUMN_DIMENSION,
                                        X.VL_DATASET_ROW_X_COLUMN_DIMENSION,
                                        X.NR_RANDOM_STATE
                                        FROM
                                        (
                                            SELECT
                                                A.ID_EXPERIMENT,
                                                A.VL_TOTAL_EXECUTION_TIME,
                                                A.VL_INTER_TASK_EXECUTION_TIME,
                                                A.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                                                A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                                                A.VL_COMMUNICATION_TIME_1,
                                                A.VL_COMMUNICATION_TIME_2,
                                                A.VL_COMMUNICATION_TIME_1 + A.VL_COMMUNICATION_TIME_2 AS VL_COMMUNICATION_TIME,
                                                A.VL_ADDITIONAL_TIME_1,
                                                A.VL_ADDITIONAL_TIME_2,
                                                A.VL_ADDITIONAL_TIME_1 + A.VL_ADDITIONAL_TIME_2 AS VL_ADDITIONAL_TIME,
                                                A.DT_PROCESSING,
                                                B.ID_PARAMETER,
                                                B.CD_PARAMETER,
                                                B.CD_CONFIGURATION,
                                                B.ID_ALGORITHM,
                                                (SELECT DISTINCT X.DS_ALGORITHM FROM schema_dev.ALGORITHM X WHERE X.ID_ALGORITHM = B.ID_ALGORITHM) AS DS_ALGORITHM,
                                                B.ID_FUNCTION,
                                                (SELECT DISTINCT X.DS_FUNCTION FROM FUNCTION X WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS DS_FUNCTION,
                                                (SELECT DISTINCT Y.ID_DEVICE FROM FUNCTION X INNER JOIN schema_dev.DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS ID_DEVICE,
                                                (SELECT DISTINCT Y.DS_DEVICE FROM FUNCTION X INNER JOIN schema_dev.DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS DS_DEVICE,
                                                B.ID_DATASET,
                                                B.ID_RESOURCE,
                                                B.ID_PARAMETER_TYPE,
                                                (SELECT X.DS_PARAMETER_TYPE FROM schema_dev.PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) AS DS_PARAMETER_TYPE,
                                                (SELECT X.DS_PARAMETER_ATTRIBUTE FROM schema_dev.PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) AS DS_PARAMETER_ATTRIBUTE,
                                                B.NR_ITERATIONS,
                                                B.VL_GRID_ROW_DIMENSION,
                                                B.VL_GRID_COLUMN_DIMENSION,
                                                B.VL_GRID_ROW_DIMENSION || ' x ' || B.VL_GRID_COLUMN_DIMENSION AS VL_GRID_ROW_X_COLUMN_DIMENSION,
                                                ROUND((CAST(B.VL_GRID_COLUMN_DIMENSION AS NUMERIC)/CAST(D.VL_DATASET_COLUMN_DIMENSION AS NUMERIC))*100,2) AS VL_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                                B.VL_GRID_ROW_DIMENSION || ' x ' || B.VL_GRID_COLUMN_DIMENSION || ' (' || ROUND((CAST(B.VL_GRID_COLUMN_DIMENSION AS NUMERIC)/CAST(D.VL_DATASET_COLUMN_DIMENSION AS NUMERIC))*100,2) || '%)' AS VL_CONCAT_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                                B.VL_BLOCK_ROW_DIMENSION,
                                                B.VL_BLOCK_COLUMN_DIMENSION,
                                                B.VL_BLOCK_ROW_DIMENSION || ' x ' || B.VL_BLOCK_COLUMN_DIMENSION AS VL_BLOCK_ROW_X_COLUMN_DIMENSION,
                                                B.VL_BLOCK_MEMORY_SIZE,
                                                B.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                                                B.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                                                ROUND((CAST(B.VL_BLOCK_MEMORY_SIZE AS NUMERIC)/CAST(D.VL_DATASET_MEMORY_SIZE AS NUMERIC))*100,2) AS VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                                ROUND(B.VL_BLOCK_MEMORY_SIZE*1e-6,2) || ' (' || ROUND((CAST(B.VL_BLOCK_MEMORY_SIZE AS NUMERIC)/CAST(D.VL_DATASET_MEMORY_SIZE AS NUMERIC))*100,2) || '%)' AS VL_CONCAT_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                                C.DS_RESOURCE,
                                                C.NR_NODES,
                                                C.NR_COMPUTING_UNITS_CPU,
                                                C.NR_COMPUTING_UNITS_GPU,
                                                C.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                                                C.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
												(C.NR_NODES-1) || ' (' || (C.NR_NODES-1)*C.NR_COMPUTING_UNITS_CPU || ';' || (C.NR_NODES-1)*4 || ')' AS NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU_GPU,
                                                D.DS_DATASET,
                                                D.VL_DATASET_MEMORY_SIZE,
                                                D.DS_DATA_TYPE,
                                                D.VL_DATA_TYPE_MEMORY_SIZE,
                                                D.VL_DATASET_DIMENSION,
                                                D.VL_DATASET_ROW_DIMENSION,
                                                D.VL_DATASET_COLUMN_DIMENSION,
                                                D.VL_DATASET_ROW_DIMENSION || ' x ' || D.VL_DATASET_COLUMN_DIMENSION AS VL_DATASET_ROW_X_COLUMN_DIMENSION,
                                                D.NR_RANDOM_STATE
                                            FROM schema_dev.EXPERIMENT_RAW A
                                            INNER JOIN schema_dev.PARAMETER B ON (A.ID_PARAMETER = B.ID_PARAMETER)
                                            INNER JOIN schema_dev.RESOURCE C ON (B.ID_RESOURCE = C.ID_RESOURCE)
                                            INNER JOIN schema_dev.DATASET D ON (B.ID_DATASET = D.ID_DATASET)
                                            WHERE
                                            (SELECT DISTINCT Z.DS_DEVICE FROM FUNCTION W INNER JOIN schema_dev.DEVICE Z ON (W.ID_DEVICE = Z.ID_DEVICE) WHERE W.ID_FUNCTION = B.ID_FUNCTION) = 'GPU'
                                            --AND A.ID_EXPERIMENT NOT IN (776778, 776777, 776780, 776779, 776776, 776794, 776793, 776795, 776792, 776791, 776784) --FILTERING OUTLIERS KMEANS EXTRA EXPERIMENTS
                                            AND A.NR_ALGORITHM_ITERATION <> 0
                                        ) X
                                        GROUP BY
                                        X.ID_PARAMETER,
                                        X.CD_PARAMETER,
                                        X.CD_CONFIGURATION,
                                        X.ID_ALGORITHM,
                                        X.DS_ALGORITHM,
                                        X.ID_FUNCTION,
                                        X.DS_FUNCTION,
                                        X.ID_DEVICE,
                                        X.DS_DEVICE,
                                        X.ID_DATASET,
                                        X.ID_RESOURCE,
                                        X.ID_PARAMETER_TYPE,
                                        X.DS_PARAMETER_TYPE,
                                        X.DS_PARAMETER_ATTRIBUTE,
                                        X.NR_ITERATIONS,
                                        X.VL_GRID_ROW_DIMENSION,
                                        X.VL_GRID_COLUMN_DIMENSION,
                                        X.VL_GRID_ROW_X_COLUMN_DIMENSION,
                                        X.VL_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                        X.VL_CONCAT_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                        X.VL_BLOCK_ROW_DIMENSION,
                                        X.VL_BLOCK_COLUMN_DIMENSION,
                                        X.VL_BLOCK_ROW_X_COLUMN_DIMENSION,
                                        X.VL_BLOCK_MEMORY_SIZE,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                        X.VL_CONCAT_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                        X.DS_RESOURCE,
                                        X.NR_NODES,
                                        X.NR_COMPUTING_UNITS_CPU,
                                        X.NR_COMPUTING_UNITS_GPU,
                                        X.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                                        X.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
										X.NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU_GPU,
                                        X.DS_DATASET,
                                        X.VL_DATASET_MEMORY_SIZE,
                                        X.DS_DATA_TYPE,
                                        X.VL_DATA_TYPE_MEMORY_SIZE,
                                        X.VL_DATASET_DIMENSION,
                                        X.VL_DATASET_ROW_DIMENSION,
                                        X.VL_DATASET_COLUMN_DIMENSION,
                                        X.VL_DATASET_ROW_X_COLUMN_DIMENSION,
                                        X.NR_RANDOM_STATE
                                    ) Y
                    )
                    SELECT
                    --T_CPU.ID_PARAMETER_TYPE,
                    --T_CPU.CD_PARAMETER,
                    T_CPU.DS_ALGORITHM,
                    --T_CPU.NR_ITERATIONS,
                    --CASE
                    --WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 0.3 THEN 0.4
                    --WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 0.7 THEN 0.8
                    --WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 1.5 THEN 1.6
                    --WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 3.0 THEN 3.1
                    --WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 6.2 THEN 6.3
                    --ELSE ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1)
					--END AS VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                    --CASE
                    --WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 0.3 THEN 0.4 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION || ' x ' || T_CPU.VL_GRID_COLUMN_DIMENSION  || ')'
                    --WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 0.7 THEN 0.8 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION || ' x ' || T_CPU.VL_GRID_COLUMN_DIMENSION  || ')'
                    --WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 1.5 THEN 1.6 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION || ' x ' || T_CPU.VL_GRID_COLUMN_DIMENSION  || ')'
                    --WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 3.0 THEN 3.1 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION || ' x ' || T_CPU.VL_GRID_COLUMN_DIMENSION  || ')'
                    --WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 6.2 THEN 6.3 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION || ' x ' || T_CPU.VL_GRID_COLUMN_DIMENSION  || ')'
                    --ELSE ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) || ' (' || T_CPU.VL_GRID_ROW_DIMENSION || ' x ' || T_CPU.VL_GRID_COLUMN_DIMENSION  || ')'
					--END AS CONCAT_BLOCK_PERCENT_DATASET_GRID_DIMENSION,
                    --ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) AS VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                    --T_CPU.DS_RESOURCE,
                    --T_CPU.DS_PARAMETER_TYPE,
                    --T_CPU.DS_PARAMETER_ATTRIBUTE,
                    T_CPU.DS_DATASET,
                    --CAST(T_CPU.VL_DATASET_MEMORY_SIZE*1e-6 AS BIGINT) as VL_DATASET_MEMORY_SIZE,
                    --T_CPU.VL_DATASET_DIMENSION,
                    --T_CPU.VL_DATASET_ROW_DIMENSION,
                    --T_CPU.VL_DATASET_COLUMN_DIMENSION,
                    --T_CPU.VL_GRID_ROW_DIMENSION,
                    --T_CPU.VL_GRID_COLUMN_DIMENSION,
                    --T_CPU.VL_BLOCK_ROW_DIMENSION,
                    --T_CPU.VL_BLOCK_COLUMN_DIMENSION,
                    --T_CPU.VL_BLOCK_MEMORY_SIZE,
                    --ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE*1e-6,2) || ' (' || T_CPU.VL_GRID_ROW_DIMENSION || ' x ' || T_CPU.VL_GRID_COLUMN_DIMENSION  || ')' AS VL_CONCAT_BLOCK_SIZE_MB_GRID_ROW_X_COLUMN_DIMENSION,
					--T_CPU.NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU_GPU,
					--CASE
					--	WHEN T_CPU.DS_ALGORITHM = 'KMEANS'
					--		THEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE*1e-6,0) || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*5 || ')'
					--	WHEN T_CPU.DS_ALGORITHM = 'MATMUL_DISLIB'
					--		THEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE*1e-6,0) || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION + T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*(T_CPU.VL_GRID_ROW_DIMENSION-1)  || ')'
					--	ELSE
					--		'999999999999'
					--END AS VL_CONCAT_BLOCK_SIZE_MB_NR_TASKS,
					CASE
						WHEN T_CPU.DS_ALGORITHM = 'KMEANS'
							THEN
								CASE
									WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 0.3 THEN 0.4 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*5  || ')'
									WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 0.7 THEN 0.8 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*5  || ')'
									WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 1.5 THEN 1.6 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*5  || ')'
									WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 3.0 THEN 3.1 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*5  || ')'
									WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 6.2 THEN 6.3 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*5  || ')'
									ELSE ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*5  || ')'
								END
						WHEN T_CPU.DS_ALGORITHM = 'MATMUL_DISLIB'
							THEN
								CASE
									WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 0.3 THEN 0.4 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION + T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*(T_CPU.VL_GRID_ROW_DIMENSION-1)  || ')'
									WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 0.7 THEN 0.8 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION + T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*(T_CPU.VL_GRID_ROW_DIMENSION-1)  || ')'
									WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 1.5 THEN 1.6 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION + T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*(T_CPU.VL_GRID_ROW_DIMENSION-1)  || ')'
									WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 3.0 THEN 3.1 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION + T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*(T_CPU.VL_GRID_ROW_DIMENSION-1)  || ')'
									WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 6.2 THEN 6.3 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION + T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*(T_CPU.VL_GRID_ROW_DIMENSION-1)  || ')'
									ELSE ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*5  || ')'
								END
						ELSE
							'999999999999'
					END AS CONCAT_BLOCK_PERCENT_DATASET_NR_TASKS,
                    CASE
                    WHEN (T_CPU.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC/T_GPU.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC) > 1.00 THEN (T_CPU.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC/T_GPU.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC)
                    ELSE -(T_GPU.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC/T_CPU.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC)
                    END AS SPEEDUP_GPU_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                    CASE
                    WHEN (T_CPU.VL_INTRA_TASK_EXECUTION_TIME_FREE_COMMUNICATION/T_GPU.VL_INTRA_TASK_EXECUTION_TIME_FREE_COMMUNICATION) > 1.00 THEN (T_CPU.VL_INTRA_TASK_EXECUTION_TIME_FREE_COMMUNICATION/T_GPU.VL_INTRA_TASK_EXECUTION_TIME_FREE_COMMUNICATION)
                    ELSE -(T_GPU.VL_INTRA_TASK_EXECUTION_TIME_FREE_COMMUNICATION/T_CPU.VL_INTRA_TASK_EXECUTION_TIME_FREE_COMMUNICATION)
                    END AS SPEEDUP_GPU_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                    --CASE
                    --WHEN (T_CPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC/T_GPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC) > 1.00 THEN (T_CPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC/T_GPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC)
                    --ELSE -(T_GPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC/T_CPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC)
                    --END AS SPEEDUP_GPU_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
					CASE
                    WHEN (T_CPU.VL_INTER_TASK_EXECUTION_TIME/T_GPU.VL_INTER_TASK_EXECUTION_TIME) > 1.00 THEN (T_CPU.VL_INTER_TASK_EXECUTION_TIME/T_GPU.VL_INTER_TASK_EXECUTION_TIME)
                    ELSE -(T_GPU.VL_INTER_TASK_EXECUTION_TIME/T_CPU.VL_INTER_TASK_EXECUTION_TIME)
                    END AS SPEEDUP_GPU_INTER_TASK_EXECUTION_TIME
                    FROM T_CPU INNER JOIN T_GPU ON (T_CPU.CD_PARAMETER = T_GPU.CD_PARAMETER)
                    WHERE
                    T_CPU.VL_GRID_ROW_DIMENSION = T_GPU.VL_GRID_ROW_DIMENSION
                    AND T_CPU.VL_GRID_COLUMN_DIMENSION = T_GPU.VL_GRID_COLUMN_DIMENSION
                    AND T_CPU.VL_BLOCK_ROW_DIMENSION = T_GPU.VL_BLOCK_ROW_DIMENSION
                    AND T_CPU.VL_BLOCK_COLUMN_DIMENSION = T_GPU.VL_BLOCK_COLUMN_DIMENSION
					AND T_CPU.ds_dataset = 'S_10GB_1'
					AND T_CPU.ds_parameter_type = 'VAR_GRID_ROW_5'
                    ORDER BY
                    T_CPU.DS_DATASET,
                    T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET





-- SPEEDUPS KMEANS
-- CONSIDERING ALL INTRA-TASK OVERHEADS
WITH T_CPU AS (
                                    SELECT
                                    A.VL_TOTAL_EXECUTION_TIME,
                                    A.VL_INTER_TASK_EXECUTION_TIME,
                                    A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                                    A.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                                    A.VL_COMMUNICATION_TIME,
                                    (A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC + A.VL_COMMUNICATION_TIME) AS VL_INTRA_TASK_EXECUTION_TIME_FREE_ADDITIONAL,
                                    B.ID_PARAMETER,
                                    B.CD_PARAMETER,
                                    B.CD_CONFIGURATION,
                                    B.ID_ALGORITHM,
                                    (SELECT DISTINCT X.DS_ALGORITHM FROM schema_dev.ALGORITHM X WHERE X.ID_ALGORITHM = B.ID_ALGORITHM) AS DS_ALGORITHM,
                                    B.ID_FUNCTION,
                                    (SELECT DISTINCT X.DS_FUNCTION FROM schema_dev.FUNCTION X WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS DS_FUNCTION,
                                    (SELECT DISTINCT Y.ID_DEVICE FROM schema_dev.FUNCTION X INNER JOIN schema_dev.DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS ID_DEVICE,
                                    (SELECT DISTINCT Y.DS_DEVICE FROM schema_dev.FUNCTION X INNER JOIN schema_dev.DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS DS_DEVICE,
                                    B.ID_DATASET,
                                    B.ID_RESOURCE,
                                    B.ID_PARAMETER_TYPE,
                                    (SELECT X.DS_PARAMETER_TYPE FROM schema_dev.PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) AS DS_PARAMETER_TYPE,
                                    (SELECT X.DS_PARAMETER_ATTRIBUTE FROM schema_dev.PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) AS DS_PARAMETER_ATTRIBUTE,
                                    B.NR_ITERATIONS,
                                    B.VL_GRID_ROW_DIMENSION,
                                    B.VL_GRID_COLUMN_DIMENSION,
                                    B.VL_BLOCK_ROW_DIMENSION,
                                    B.VL_BLOCK_COLUMN_DIMENSION,
                                    B.VL_BLOCK_MEMORY_SIZE,
                                    B.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                                    B.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                                    ROUND((CAST(B.VL_BLOCK_MEMORY_SIZE AS NUMERIC)/CAST(D.VL_DATASET_MEMORY_SIZE AS NUMERIC))*100,2) AS VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                    C.DS_RESOURCE,
                                    C.NR_NODES,
                                    C.NR_COMPUTING_UNITS_CPU,
                                    C.NR_COMPUTING_UNITS_GPU,
                                    C.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                                    C.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
									(C.NR_NODES-1) || ' (' || (C.NR_NODES-1)*C.NR_COMPUTING_UNITS_CPU || ';' || (C.NR_NODES-1)*4 || ')' AS NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU_GPU,
                                    D.DS_DATASET,
                                    D.VL_DATASET_MEMORY_SIZE,
                                    D.DS_DATA_TYPE,
                                    D.VL_DATA_TYPE_MEMORY_SIZE,
                                    D.VL_DATASET_DIMENSION,
                                    D.VL_DATASET_ROW_DIMENSION,
                                    D.VL_DATASET_COLUMN_DIMENSION,
                                    D.NR_RANDOM_STATE
                                FROM schema_dev.EXPERIMENT A
                                INNER JOIN schema_dev.PARAMETER B ON (A.ID_PARAMETER = B.ID_PARAMETER)
                                INNER JOIN schema_dev.RESOURCE C ON (B.ID_RESOURCE = C.ID_RESOURCE)
                                INNER JOIN schema_dev.DATASET D ON (B.ID_DATASET = D.ID_DATASET)
                                WHERE
                                (SELECT DISTINCT Y.DS_DEVICE FROM schema_dev.FUNCTION X INNER JOIN schema_dev.DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) = 'CPU'
                                
                                UNION ALL
                        
                                    SELECT
                                    Y.VL_TOTAL_EXECUTION_TIME,
                                    Y.VL_INTER_TASK_EXECUTION_TIME,
                                    Y.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                                    Y.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                                    Y.VL_COMMUNICATION_TIME,
                                    (Y.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC + Y.VL_COMMUNICATION_TIME) AS VL_INTRA_TASK_EXECUTION_TIME_FREE_ADDITIONAL,
                                    Y.ID_PARAMETER,
                                    Y.CD_PARAMETER,
                                    Y.CD_CONFIGURATION,
                                    Y.ID_ALGORITHM,
                                    Y.DS_ALGORITHM,
                                    Y.ID_FUNCTION,
                                    Y.DS_FUNCTION,
                                    Y.ID_DEVICE,
                                    Y.DS_DEVICE,
                                    Y.ID_DATASET,
                                    Y.ID_RESOURCE,
                                    Y.ID_PARAMETER_TYPE,
                                    Y.DS_PARAMETER_TYPE,
                                    Y.DS_PARAMETER_ATTRIBUTE,
                                    Y.NR_ITERATIONS,
                                    Y.VL_GRID_ROW_DIMENSION,
                                    Y.VL_GRID_COLUMN_DIMENSION,
                                    Y.VL_BLOCK_ROW_DIMENSION,
                                    Y.VL_BLOCK_COLUMN_DIMENSION,
                                    Y.VL_BLOCK_MEMORY_SIZE,
                                    Y.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                                    Y.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                                    Y.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                    Y.DS_RESOURCE,
                                    Y.NR_NODES,
                                    Y.NR_COMPUTING_UNITS_CPU,
                                    Y.NR_COMPUTING_UNITS_GPU,
                                    Y.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                                    Y.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
									Y.NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU_GPU,
                                    Y.DS_DATASET,
                                    Y.VL_DATASET_MEMORY_SIZE,
                                    Y.DS_DATA_TYPE,
                                    Y.VL_DATA_TYPE_MEMORY_SIZE,
                                    Y.VL_DATASET_DIMENSION,
                                    Y.VL_DATASET_ROW_DIMENSION,
                                    Y.VL_DATASET_COLUMN_DIMENSION,
                                    Y.NR_RANDOM_STATE
                                    FROM
                                    (
                                        SELECT
                                        AVG(X.VL_TOTAL_EXECUTION_TIME) AS VL_TOTAL_EXECUTION_TIME,
                                        AVG(X.VL_INTER_TASK_EXECUTION_TIME) AS VL_INTER_TASK_EXECUTION_TIME,
                                        AVG(X.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC) AS VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                                        AVG(X.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC) AS VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                                        AVG(X.VL_COMMUNICATION_TIME_1) AS VL_COMMUNICATION_TIME_1,
                                        AVG(X.VL_COMMUNICATION_TIME_2) AS VL_COMMUNICATION_TIME_2,
                                        AVG(X.VL_COMMUNICATION_TIME) AS VL_COMMUNICATION_TIME,
                                        AVG(X.VL_ADDITIONAL_TIME_1) AS VL_ADDITIONAL_TIME_1,
                                        AVG(X.VL_ADDITIONAL_TIME_2) AS VL_ADDITIONAL_TIME_2,
                                        AVG(X.VL_ADDITIONAL_TIME) AS VL_ADDITIONAL_TIME,
                                        X.ID_PARAMETER,
                                        X.CD_PARAMETER,
                                        X.CD_CONFIGURATION,
                                        X.ID_ALGORITHM,
                                        X.DS_ALGORITHM,
                                        X.ID_FUNCTION,
                                        X.DS_FUNCTION,
                                        X.ID_DEVICE,
                                        X.DS_DEVICE,
                                        X.ID_DATASET,
                                        X.ID_RESOURCE,
                                        X.ID_PARAMETER_TYPE,
                                        X.DS_PARAMETER_TYPE,
                                        X.DS_PARAMETER_ATTRIBUTE,
                                        X.NR_ITERATIONS,
                                        X.VL_GRID_ROW_DIMENSION,
                                        X.VL_GRID_COLUMN_DIMENSION,
                                        X.VL_GRID_ROW_X_COLUMN_DIMENSION,
                                        X.VL_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                        X.VL_CONCAT_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                        X.VL_BLOCK_ROW_DIMENSION,
                                        X.VL_BLOCK_COLUMN_DIMENSION,
                                        X.VL_BLOCK_ROW_X_COLUMN_DIMENSION,
                                        X.VL_BLOCK_MEMORY_SIZE,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                        X.VL_CONCAT_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                        X.DS_RESOURCE,
                                        X.NR_NODES,
                                        X.NR_COMPUTING_UNITS_CPU,
                                        X.NR_COMPUTING_UNITS_GPU,
                                        X.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                                        X.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
										X.NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU_GPU,
                                        X.DS_DATASET,
                                        X.VL_DATASET_MEMORY_SIZE,
                                        X.DS_DATA_TYPE,
                                        X.VL_DATA_TYPE_MEMORY_SIZE,
                                        X.VL_DATASET_DIMENSION,
                                        X.VL_DATASET_ROW_DIMENSION,
                                        X.VL_DATASET_COLUMN_DIMENSION,
                                        X.VL_DATASET_ROW_X_COLUMN_DIMENSION,
                                        X.NR_RANDOM_STATE
                                        FROM
                                        (
                                            SELECT
                                                A.ID_EXPERIMENT,
                                                A.VL_TOTAL_EXECUTION_TIME,
                                                A.VL_INTER_TASK_EXECUTION_TIME,
                                                A.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                                                A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                                                A.VL_COMMUNICATION_TIME_1,
                                                A.VL_COMMUNICATION_TIME_2,
                                                A.VL_COMMUNICATION_TIME_1 + A.VL_COMMUNICATION_TIME_2 AS VL_COMMUNICATION_TIME,
                                                A.VL_ADDITIONAL_TIME_1,
                                                A.VL_ADDITIONAL_TIME_2,
                                                A.VL_ADDITIONAL_TIME_1 + A.VL_ADDITIONAL_TIME_2 AS VL_ADDITIONAL_TIME,
                                                A.DT_PROCESSING,
                                                B.ID_PARAMETER,
                                                B.CD_PARAMETER,
                                                B.CD_CONFIGURATION,
                                                B.ID_ALGORITHM,
                                                (SELECT DISTINCT X.DS_ALGORITHM FROM schema_dev.ALGORITHM X WHERE X.ID_ALGORITHM = B.ID_ALGORITHM) AS DS_ALGORITHM,
                                                B.ID_FUNCTION,
                                                (SELECT DISTINCT X.DS_FUNCTION FROM schema_dev.FUNCTION X WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS DS_FUNCTION,
                                                (SELECT DISTINCT Y.ID_DEVICE FROM schema_dev.FUNCTION X INNER JOIN schema_dev.DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS ID_DEVICE,
                                                (SELECT DISTINCT Y.DS_DEVICE FROM schema_dev.FUNCTION X INNER JOIN schema_dev.DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS DS_DEVICE,
                                                B.ID_DATASET,
                                                B.ID_RESOURCE,
                                                B.ID_PARAMETER_TYPE,
                                                (SELECT X.DS_PARAMETER_TYPE FROM schema_dev.PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) AS DS_PARAMETER_TYPE,
                                                (SELECT X.DS_PARAMETER_ATTRIBUTE FROM schema_dev.PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) AS DS_PARAMETER_ATTRIBUTE,
                                                B.NR_ITERATIONS,
                                                B.VL_GRID_ROW_DIMENSION,
                                                B.VL_GRID_COLUMN_DIMENSION,
                                                B.VL_GRID_ROW_DIMENSION || ' x ' || B.VL_GRID_COLUMN_DIMENSION AS VL_GRID_ROW_X_COLUMN_DIMENSION,
                                                ROUND((CAST(B.VL_GRID_COLUMN_DIMENSION AS NUMERIC)/CAST(D.VL_DATASET_COLUMN_DIMENSION AS NUMERIC))*100,2) AS VL_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                                B.VL_GRID_ROW_DIMENSION || ' x ' || B.VL_GRID_COLUMN_DIMENSION || ' (' || ROUND((CAST(B.VL_GRID_COLUMN_DIMENSION AS NUMERIC)/CAST(D.VL_DATASET_COLUMN_DIMENSION AS NUMERIC))*100,2) || '%)' AS VL_CONCAT_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                                B.VL_BLOCK_ROW_DIMENSION,
                                                B.VL_BLOCK_COLUMN_DIMENSION,
                                                B.VL_BLOCK_ROW_DIMENSION || ' x ' || B.VL_BLOCK_COLUMN_DIMENSION AS VL_BLOCK_ROW_X_COLUMN_DIMENSION,
                                                B.VL_BLOCK_MEMORY_SIZE,
                                                B.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                                                B.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                                                ROUND((CAST(B.VL_BLOCK_MEMORY_SIZE AS NUMERIC)/CAST(D.VL_DATASET_MEMORY_SIZE AS NUMERIC))*100,2) AS VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                                ROUND(B.VL_BLOCK_MEMORY_SIZE*1e-6,2) || ' (' || ROUND((CAST(B.VL_BLOCK_MEMORY_SIZE AS NUMERIC)/CAST(D.VL_DATASET_MEMORY_SIZE AS NUMERIC))*100,2) || '%)' AS VL_CONCAT_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                                C.DS_RESOURCE,
                                                C.NR_NODES,
                                                C.NR_COMPUTING_UNITS_CPU,
                                                C.NR_COMPUTING_UNITS_GPU,
                                                C.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                                                C.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
												(C.NR_NODES-1) || ' (' || (C.NR_NODES-1)*C.NR_COMPUTING_UNITS_CPU || ';' || (C.NR_NODES-1)*4 || ')' AS NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU_GPU,
                                                D.DS_DATASET,
                                                D.VL_DATASET_MEMORY_SIZE,
                                                D.DS_DATA_TYPE,
                                                D.VL_DATA_TYPE_MEMORY_SIZE,
                                                D.VL_DATASET_DIMENSION,
                                                D.VL_DATASET_ROW_DIMENSION,
                                                D.VL_DATASET_COLUMN_DIMENSION,
                                                D.VL_DATASET_ROW_DIMENSION || ' x ' || D.VL_DATASET_COLUMN_DIMENSION AS VL_DATASET_ROW_X_COLUMN_DIMENSION,
                                                D.NR_RANDOM_STATE
                                            FROM schema_dev.EXPERIMENT_RAW A
                                            INNER JOIN schema_dev.PARAMETER B ON (A.ID_PARAMETER = B.ID_PARAMETER)
                                            INNER JOIN schema_dev.RESOURCE C ON (B.ID_RESOURCE = C.ID_RESOURCE)
                                            INNER JOIN schema_dev.DATASET D ON (B.ID_DATASET = D.ID_DATASET)
                                            WHERE
                                            (SELECT DISTINCT Z.DS_DEVICE FROM schema_dev.FUNCTION W INNER JOIN schema_dev.DEVICE Z ON (W.ID_DEVICE = Z.ID_DEVICE) WHERE W.ID_FUNCTION = B.ID_FUNCTION) = 'CPU'
                                            AND A.NR_ALGORITHM_ITERATION <> 0
                                        ) X
                                        GROUP BY
                                        X.ID_PARAMETER,
                                        X.CD_PARAMETER,
                                        X.CD_CONFIGURATION,
                                        X.ID_ALGORITHM,
                                        X.DS_ALGORITHM,
                                        X.ID_FUNCTION,
                                        X.DS_FUNCTION,
                                        X.ID_DEVICE,
                                        X.DS_DEVICE,
                                        X.ID_DATASET,
                                        X.ID_RESOURCE,
                                        X.ID_PARAMETER_TYPE,
                                        X.DS_PARAMETER_TYPE,
                                        X.DS_PARAMETER_ATTRIBUTE,
                                        X.NR_ITERATIONS,
                                        X.VL_GRID_ROW_DIMENSION,
                                        X.VL_GRID_COLUMN_DIMENSION,
                                        X.VL_GRID_ROW_X_COLUMN_DIMENSION,
                                        X.VL_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                        X.VL_CONCAT_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                        X.VL_BLOCK_ROW_DIMENSION,
                                        X.VL_BLOCK_COLUMN_DIMENSION,
                                        X.VL_BLOCK_ROW_X_COLUMN_DIMENSION,
                                        X.VL_BLOCK_MEMORY_SIZE,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                        X.VL_CONCAT_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                        X.DS_RESOURCE,
                                        X.NR_NODES,
                                        X.NR_COMPUTING_UNITS_CPU,
                                        X.NR_COMPUTING_UNITS_GPU,
                                        X.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                                        X.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
										X.NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU_GPU,
                                        X.DS_DATASET,
                                        X.VL_DATASET_MEMORY_SIZE,
                                        X.DS_DATA_TYPE,
                                        X.VL_DATA_TYPE_MEMORY_SIZE,
                                        X.VL_DATASET_DIMENSION,
                                        X.VL_DATASET_ROW_DIMENSION,
                                        X.VL_DATASET_COLUMN_DIMENSION,
                                        X.VL_DATASET_ROW_X_COLUMN_DIMENSION,
                                        X.NR_RANDOM_STATE
                                    ) Y
                        
                                ),
                    T_GPU AS (
                                    SELECT
                                    A.VL_TOTAL_EXECUTION_TIME,
                                    A.VL_INTER_TASK_EXECUTION_TIME,
                                    A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                                    A.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                                    A.VL_COMMUNICATION_TIME,
                                    (A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC + A.VL_COMMUNICATION_TIME) AS VL_INTRA_TASK_EXECUTION_TIME_FREE_ADDITIONAL,
                                    B.ID_PARAMETER,
                                    B.CD_PARAMETER,
                                    B.CD_CONFIGURATION,
                                    B.ID_ALGORITHM,
                                    (SELECT DISTINCT X.DS_ALGORITHM FROM schema_dev.ALGORITHM X WHERE X.ID_ALGORITHM = B.ID_ALGORITHM) AS DS_ALGORITHM,
                                    B.ID_FUNCTION,
                                    (SELECT DISTINCT X.DS_FUNCTION FROM FUNCTION X WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS DS_FUNCTION,
                                    (SELECT DISTINCT Y.ID_DEVICE FROM FUNCTION X INNER JOIN schema_dev.DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS ID_DEVICE,
                                    (SELECT DISTINCT Y.DS_DEVICE FROM FUNCTION X INNER JOIN schema_dev.DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS DS_DEVICE,
                                    B.ID_DATASET,
                                    B.ID_RESOURCE,
                                    B.ID_PARAMETER_TYPE,
                                    (SELECT X.DS_PARAMETER_TYPE FROM schema_dev.PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) AS DS_PARAMETER_TYPE,
                                    (SELECT X.DS_PARAMETER_ATTRIBUTE FROM schema_dev.PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) AS DS_PARAMETER_ATTRIBUTE,
                                    B.NR_ITERATIONS,
                                    B.VL_GRID_ROW_DIMENSION,
                                    B.VL_GRID_COLUMN_DIMENSION,
                                    B.VL_BLOCK_ROW_DIMENSION,
                                    B.VL_BLOCK_COLUMN_DIMENSION,
                                    B.VL_BLOCK_MEMORY_SIZE,
                                    B.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                                    B.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                                    ROUND((CAST(B.VL_BLOCK_MEMORY_SIZE AS NUMERIC)/CAST(D.VL_DATASET_MEMORY_SIZE AS NUMERIC))*100,2) AS VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                    C.DS_RESOURCE,
                                    C.NR_NODES,
                                    C.NR_COMPUTING_UNITS_CPU,
                                    C.NR_COMPUTING_UNITS_GPU,
                                    C.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                                    C.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
									(C.NR_NODES-1) || ' (' || (C.NR_NODES-1)*C.NR_COMPUTING_UNITS_CPU || ';' || (C.NR_NODES-1)*4 || ')' AS NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU_GPU,
                                    D.DS_DATASET,
                                    D.VL_DATASET_MEMORY_SIZE,
                                    D.DS_DATA_TYPE,
                                    D.VL_DATA_TYPE_MEMORY_SIZE,
                                    D.VL_DATASET_DIMENSION,
                                    D.VL_DATASET_ROW_DIMENSION,
                                    D.VL_DATASET_COLUMN_DIMENSION,
                                    D.NR_RANDOM_STATE
                                    FROM schema_dev.EXPERIMENT A
                                    INNER JOIN schema_dev.PARAMETER B ON (A.ID_PARAMETER = B.ID_PARAMETER)
                                    INNER JOIN schema_dev.RESOURCE C ON (B.ID_RESOURCE = C.ID_RESOURCE)
                                    INNER JOIN schema_dev.DATASET D ON (B.ID_DATASET = D.ID_DATASET)
                                    WHERE
                                    (SELECT DISTINCT Y.DS_DEVICE FROM FUNCTION X INNER JOIN schema_dev.DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) = 'GPU'
                            
                                UNION ALL
                        
                                    SELECT
                                    Y.VL_TOTAL_EXECUTION_TIME,
                                    Y.VL_INTER_TASK_EXECUTION_TIME,
                                    Y.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                                    Y.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                                    Y.VL_COMMUNICATION_TIME,
                                    (Y.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC + Y.VL_COMMUNICATION_TIME) AS VL_INTRA_TASK_EXECUTION_TIME_FREE_ADDITIONAL,
                                    Y.ID_PARAMETER,
                                    Y.CD_PARAMETER,
                                    Y.CD_CONFIGURATION,
                                    Y.ID_ALGORITHM,
                                    Y.DS_ALGORITHM,
                                    Y.ID_FUNCTION,
                                    Y.DS_FUNCTION,
                                    Y.ID_DEVICE,
                                    Y.DS_DEVICE,
                                    Y.ID_DATASET,
                                    Y.ID_RESOURCE,
                                    Y.ID_PARAMETER_TYPE,
                                    Y.DS_PARAMETER_TYPE,
                                    Y.DS_PARAMETER_ATTRIBUTE,
                                    Y.NR_ITERATIONS,
                                    Y.VL_GRID_ROW_DIMENSION,
                                    Y.VL_GRID_COLUMN_DIMENSION,
                                    Y.VL_BLOCK_ROW_DIMENSION,
                                    Y.VL_BLOCK_COLUMN_DIMENSION,
                                    Y.VL_BLOCK_MEMORY_SIZE,
                                    Y.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                                    Y.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                                    Y.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                    Y.DS_RESOURCE,
                                    Y.NR_NODES,
                                    Y.NR_COMPUTING_UNITS_CPU,
                                    Y.NR_COMPUTING_UNITS_GPU,
                                    Y.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                                    Y.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
									Y.NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU_GPU,
                                    Y.DS_DATASET,
                                    Y.VL_DATASET_MEMORY_SIZE,
                                    Y.DS_DATA_TYPE,
                                    Y.VL_DATA_TYPE_MEMORY_SIZE,
                                    Y.VL_DATASET_DIMENSION,
                                    Y.VL_DATASET_ROW_DIMENSION,
                                    Y.VL_DATASET_COLUMN_DIMENSION,
                                    Y.NR_RANDOM_STATE
                                    FROM
                                    (
                                        SELECT
                                        AVG(X.VL_TOTAL_EXECUTION_TIME) AS VL_TOTAL_EXECUTION_TIME,
                                        AVG(X.VL_INTER_TASK_EXECUTION_TIME) AS VL_INTER_TASK_EXECUTION_TIME,
                                        AVG(X.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC) AS VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                                        AVG(X.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC) AS VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                                        AVG(X.VL_COMMUNICATION_TIME_1) AS VL_COMMUNICATION_TIME_1,
                                        AVG(X.VL_COMMUNICATION_TIME_2) AS VL_COMMUNICATION_TIME_2,
                                        AVG(X.VL_COMMUNICATION_TIME) AS VL_COMMUNICATION_TIME,
                                        AVG(X.VL_ADDITIONAL_TIME_1) AS VL_ADDITIONAL_TIME_1,
                                        AVG(X.VL_ADDITIONAL_TIME_2) AS VL_ADDITIONAL_TIME_2,
                                        AVG(X.VL_ADDITIONAL_TIME) AS VL_ADDITIONAL_TIME,
                                        X.ID_PARAMETER,
                                        X.CD_PARAMETER,
                                        X.CD_CONFIGURATION,
                                        X.ID_ALGORITHM,
                                        X.DS_ALGORITHM,
                                        X.ID_FUNCTION,
                                        X.DS_FUNCTION,
                                        X.ID_DEVICE,
                                        X.DS_DEVICE,
                                        X.ID_DATASET,
                                        X.ID_RESOURCE,
                                        X.ID_PARAMETER_TYPE,
                                        X.DS_PARAMETER_TYPE,
                                        X.DS_PARAMETER_ATTRIBUTE,
                                        X.NR_ITERATIONS,
                                        X.VL_GRID_ROW_DIMENSION,
                                        X.VL_GRID_COLUMN_DIMENSION,
                                        X.VL_GRID_ROW_X_COLUMN_DIMENSION,
                                        X.VL_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                        X.VL_CONCAT_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                        X.VL_BLOCK_ROW_DIMENSION,
                                        X.VL_BLOCK_COLUMN_DIMENSION,
                                        X.VL_BLOCK_ROW_X_COLUMN_DIMENSION,
                                        X.VL_BLOCK_MEMORY_SIZE,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                        X.VL_CONCAT_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                        X.DS_RESOURCE,
                                        X.NR_NODES,
                                        X.NR_COMPUTING_UNITS_CPU,
                                        X.NR_COMPUTING_UNITS_GPU,
                                        X.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                                        X.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
										X.NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU_GPU,
                                        X.DS_DATASET,
                                        X.VL_DATASET_MEMORY_SIZE,
                                        X.DS_DATA_TYPE,
                                        X.VL_DATA_TYPE_MEMORY_SIZE,
                                        X.VL_DATASET_DIMENSION,
                                        X.VL_DATASET_ROW_DIMENSION,
                                        X.VL_DATASET_COLUMN_DIMENSION,
                                        X.VL_DATASET_ROW_X_COLUMN_DIMENSION,
                                        X.NR_RANDOM_STATE
                                        FROM
                                        (
                                            SELECT
                                                A.ID_EXPERIMENT,
                                                A.VL_TOTAL_EXECUTION_TIME,
                                                A.VL_INTER_TASK_EXECUTION_TIME,
                                                A.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                                                A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                                                A.VL_COMMUNICATION_TIME_1,
                                                A.VL_COMMUNICATION_TIME_2,
                                                A.VL_COMMUNICATION_TIME_1 + A.VL_COMMUNICATION_TIME_2 AS VL_COMMUNICATION_TIME,
                                                A.VL_ADDITIONAL_TIME_1,
                                                A.VL_ADDITIONAL_TIME_2,
                                                A.VL_ADDITIONAL_TIME_1 + A.VL_ADDITIONAL_TIME_2 AS VL_ADDITIONAL_TIME,
                                                A.DT_PROCESSING,
                                                B.ID_PARAMETER,
                                                B.CD_PARAMETER,
                                                B.CD_CONFIGURATION,
                                                B.ID_ALGORITHM,
                                                (SELECT DISTINCT X.DS_ALGORITHM FROM schema_dev.ALGORITHM X WHERE X.ID_ALGORITHM = B.ID_ALGORITHM) AS DS_ALGORITHM,
                                                B.ID_FUNCTION,
                                                (SELECT DISTINCT X.DS_FUNCTION FROM FUNCTION X WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS DS_FUNCTION,
                                                (SELECT DISTINCT Y.ID_DEVICE FROM FUNCTION X INNER JOIN schema_dev.DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS ID_DEVICE,
                                                (SELECT DISTINCT Y.DS_DEVICE FROM FUNCTION X INNER JOIN schema_dev.DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS DS_DEVICE,
                                                B.ID_DATASET,
                                                B.ID_RESOURCE,
                                                B.ID_PARAMETER_TYPE,
                                                (SELECT X.DS_PARAMETER_TYPE FROM schema_dev.PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) AS DS_PARAMETER_TYPE,
                                                (SELECT X.DS_PARAMETER_ATTRIBUTE FROM schema_dev.PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) AS DS_PARAMETER_ATTRIBUTE,
                                                B.NR_ITERATIONS,
                                                B.VL_GRID_ROW_DIMENSION,
                                                B.VL_GRID_COLUMN_DIMENSION,
                                                B.VL_GRID_ROW_DIMENSION || ' x ' || B.VL_GRID_COLUMN_DIMENSION AS VL_GRID_ROW_X_COLUMN_DIMENSION,
                                                ROUND((CAST(B.VL_GRID_COLUMN_DIMENSION AS NUMERIC)/CAST(D.VL_DATASET_COLUMN_DIMENSION AS NUMERIC))*100,2) AS VL_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                                B.VL_GRID_ROW_DIMENSION || ' x ' || B.VL_GRID_COLUMN_DIMENSION || ' (' || ROUND((CAST(B.VL_GRID_COLUMN_DIMENSION AS NUMERIC)/CAST(D.VL_DATASET_COLUMN_DIMENSION AS NUMERIC))*100,2) || '%)' AS VL_CONCAT_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                                B.VL_BLOCK_ROW_DIMENSION,
                                                B.VL_BLOCK_COLUMN_DIMENSION,
                                                B.VL_BLOCK_ROW_DIMENSION || ' x ' || B.VL_BLOCK_COLUMN_DIMENSION AS VL_BLOCK_ROW_X_COLUMN_DIMENSION,
                                                B.VL_BLOCK_MEMORY_SIZE,
                                                B.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                                                B.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                                                ROUND((CAST(B.VL_BLOCK_MEMORY_SIZE AS NUMERIC)/CAST(D.VL_DATASET_MEMORY_SIZE AS NUMERIC))*100,2) AS VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                                ROUND(B.VL_BLOCK_MEMORY_SIZE*1e-6,2) || ' (' || ROUND((CAST(B.VL_BLOCK_MEMORY_SIZE AS NUMERIC)/CAST(D.VL_DATASET_MEMORY_SIZE AS NUMERIC))*100,2) || '%)' AS VL_CONCAT_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                                C.DS_RESOURCE,
                                                C.NR_NODES,
                                                C.NR_COMPUTING_UNITS_CPU,
                                                C.NR_COMPUTING_UNITS_GPU,
                                                C.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                                                C.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
												(C.NR_NODES-1) || ' (' || (C.NR_NODES-1)*C.NR_COMPUTING_UNITS_CPU || ';' || (C.NR_NODES-1)*4 || ')' AS NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU_GPU,
                                                D.DS_DATASET,
                                                D.VL_DATASET_MEMORY_SIZE,
                                                D.DS_DATA_TYPE,
                                                D.VL_DATA_TYPE_MEMORY_SIZE,
                                                D.VL_DATASET_DIMENSION,
                                                D.VL_DATASET_ROW_DIMENSION,
                                                D.VL_DATASET_COLUMN_DIMENSION,
                                                D.VL_DATASET_ROW_DIMENSION || ' x ' || D.VL_DATASET_COLUMN_DIMENSION AS VL_DATASET_ROW_X_COLUMN_DIMENSION,
                                                D.NR_RANDOM_STATE
                                            FROM schema_dev.EXPERIMENT_RAW A
                                            INNER JOIN schema_dev.PARAMETER B ON (A.ID_PARAMETER = B.ID_PARAMETER)
                                            INNER JOIN schema_dev.RESOURCE C ON (B.ID_RESOURCE = C.ID_RESOURCE)
                                            INNER JOIN schema_dev.DATASET D ON (B.ID_DATASET = D.ID_DATASET)
                                            WHERE
                                            (SELECT DISTINCT Z.DS_DEVICE FROM FUNCTION W INNER JOIN schema_dev.DEVICE Z ON (W.ID_DEVICE = Z.ID_DEVICE) WHERE W.ID_FUNCTION = B.ID_FUNCTION) = 'GPU'
                                            --AND A.ID_EXPERIMENT NOT IN (776778, 776777, 776780, 776779, 776776, 776794, 776793, 776795, 776792, 776791, 776784) --FILTERING OUTLIERS KMEANS EXTRA EXPERIMENTS
                                            AND A.NR_ALGORITHM_ITERATION <> 0
                                        ) X
                                        GROUP BY
                                        X.ID_PARAMETER,
                                        X.CD_PARAMETER,
                                        X.CD_CONFIGURATION,
                                        X.ID_ALGORITHM,
                                        X.DS_ALGORITHM,
                                        X.ID_FUNCTION,
                                        X.DS_FUNCTION,
                                        X.ID_DEVICE,
                                        X.DS_DEVICE,
                                        X.ID_DATASET,
                                        X.ID_RESOURCE,
                                        X.ID_PARAMETER_TYPE,
                                        X.DS_PARAMETER_TYPE,
                                        X.DS_PARAMETER_ATTRIBUTE,
                                        X.NR_ITERATIONS,
                                        X.VL_GRID_ROW_DIMENSION,
                                        X.VL_GRID_COLUMN_DIMENSION,
                                        X.VL_GRID_ROW_X_COLUMN_DIMENSION,
                                        X.VL_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                        X.VL_CONCAT_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                        X.VL_BLOCK_ROW_DIMENSION,
                                        X.VL_BLOCK_COLUMN_DIMENSION,
                                        X.VL_BLOCK_ROW_X_COLUMN_DIMENSION,
                                        X.VL_BLOCK_MEMORY_SIZE,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                        X.VL_CONCAT_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                        X.DS_RESOURCE,
                                        X.NR_NODES,
                                        X.NR_COMPUTING_UNITS_CPU,
                                        X.NR_COMPUTING_UNITS_GPU,
                                        X.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                                        X.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
										X.NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU_GPU,
                                        X.DS_DATASET,
                                        X.VL_DATASET_MEMORY_SIZE,
                                        X.DS_DATA_TYPE,
                                        X.VL_DATA_TYPE_MEMORY_SIZE,
                                        X.VL_DATASET_DIMENSION,
                                        X.VL_DATASET_ROW_DIMENSION,
                                        X.VL_DATASET_COLUMN_DIMENSION,
                                        X.VL_DATASET_ROW_X_COLUMN_DIMENSION,
                                        X.NR_RANDOM_STATE
                                    ) Y
                    )
                    SELECT
                    --T_CPU.ID_PARAMETER_TYPE,
                    --T_CPU.CD_PARAMETER,
                    T_CPU.DS_ALGORITHM,
                    --T_CPU.NR_ITERATIONS,
                    --CASE
                    --WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 0.3 THEN 0.4
                    --WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 0.7 THEN 0.8
                    --WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 1.5 THEN 1.6
                    --WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 3.0 THEN 3.1
                    --WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 6.2 THEN 6.3
                    --ELSE ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1)
					--END AS VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                    --CASE
                    --WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 0.3 THEN 0.4 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION || ' x ' || T_CPU.VL_GRID_COLUMN_DIMENSION  || ')'
                    --WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 0.7 THEN 0.8 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION || ' x ' || T_CPU.VL_GRID_COLUMN_DIMENSION  || ')'
                    --WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 1.5 THEN 1.6 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION || ' x ' || T_CPU.VL_GRID_COLUMN_DIMENSION  || ')'
                    --WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 3.0 THEN 3.1 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION || ' x ' || T_CPU.VL_GRID_COLUMN_DIMENSION  || ')'
                    --WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 6.2 THEN 6.3 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION || ' x ' || T_CPU.VL_GRID_COLUMN_DIMENSION  || ')'
                    --ELSE ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) || ' (' || T_CPU.VL_GRID_ROW_DIMENSION || ' x ' || T_CPU.VL_GRID_COLUMN_DIMENSION  || ')'
					--END AS CONCAT_BLOCK_PERCENT_DATASET_GRID_DIMENSION,
                    --ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) AS VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                    --T_CPU.DS_RESOURCE,
                    --T_CPU.DS_PARAMETER_TYPE,
                    --T_CPU.DS_PARAMETER_ATTRIBUTE,
                    T_CPU.DS_DATASET,
                    --CAST(T_CPU.VL_DATASET_MEMORY_SIZE*1e-6 AS BIGINT) as VL_DATASET_MEMORY_SIZE,
                    --T_CPU.VL_DATASET_DIMENSION,
                    --T_CPU.VL_DATASET_ROW_DIMENSION,
                    --T_CPU.VL_DATASET_COLUMN_DIMENSION,
                    --T_CPU.VL_GRID_ROW_DIMENSION,
                    --T_CPU.VL_GRID_COLUMN_DIMENSION,
                    --T_CPU.VL_BLOCK_ROW_DIMENSION,
                    --T_CPU.VL_BLOCK_COLUMN_DIMENSION,
                    --T_CPU.VL_BLOCK_MEMORY_SIZE,
                    --ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE*1e-6,2) || ' (' || T_CPU.VL_GRID_ROW_DIMENSION || ' x ' || T_CPU.VL_GRID_COLUMN_DIMENSION  || ')' AS VL_CONCAT_BLOCK_SIZE_MB_GRID_ROW_X_COLUMN_DIMENSION,
					--T_CPU.NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU_GPU,
					--CASE
					--	WHEN T_CPU.DS_ALGORITHM = 'KMEANS'
					--		THEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE*1e-6,0) || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*5 || ')'
					--	WHEN T_CPU.DS_ALGORITHM = 'MATMUL_DISLIB'
					--		THEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE*1e-6,0) || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION + T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*(T_CPU.VL_GRID_ROW_DIMENSION-1)  || ')'
					--	ELSE
					--		'999999999999'
					--END AS VL_CONCAT_BLOCK_SIZE_MB_NR_TASKS,
					CASE
						WHEN T_CPU.DS_ALGORITHM = 'KMEANS'
							THEN
								CASE
									WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 0.3 THEN 0.4 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*5  || ')'
									WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 0.7 THEN 0.8 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*5  || ')'
									WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 1.5 THEN 1.6 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*5  || ')'
									WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 3.0 THEN 3.1 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*5  || ')'
									WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 6.2 THEN 6.3 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*5  || ')'
									ELSE ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*5  || ')'
								END
						WHEN T_CPU.DS_ALGORITHM = 'MATMUL_DISLIB'
							THEN
								CASE
									WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 0.3 THEN 0.4 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION + T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*(T_CPU.VL_GRID_ROW_DIMENSION-1)  || ')'
									WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 0.7 THEN 0.8 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION + T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*(T_CPU.VL_GRID_ROW_DIMENSION-1)  || ')'
									WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 1.5 THEN 1.6 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION + T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*(T_CPU.VL_GRID_ROW_DIMENSION-1)  || ')'
									WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 3.0 THEN 3.1 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION + T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*(T_CPU.VL_GRID_ROW_DIMENSION-1)  || ')'
									WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 6.2 THEN 6.3 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION + T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*(T_CPU.VL_GRID_ROW_DIMENSION-1)  || ')'
									ELSE ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*5  || ')'
								END
						ELSE
							'999999999999'
					END AS CONCAT_BLOCK_PERCENT_DATASET_NR_TASKS,
                    CASE
                    WHEN (T_CPU.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC/T_GPU.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC) > 1.00 THEN (T_CPU.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC/T_GPU.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC)
                    ELSE -(T_GPU.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC/T_CPU.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC)
                    END AS SPEEDUP_GPU_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                    CASE
                    WHEN (T_CPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC/T_GPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC) > 1.00 THEN (T_CPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC/T_GPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC)
                    ELSE -(T_GPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC/T_CPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC)
                    END AS SPEEDUP_GPU_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
					CASE
                    WHEN (T_CPU.VL_INTER_TASK_EXECUTION_TIME/T_GPU.VL_INTER_TASK_EXECUTION_TIME) > 1.00 THEN (T_CPU.VL_INTER_TASK_EXECUTION_TIME/T_GPU.VL_INTER_TASK_EXECUTION_TIME)
                    ELSE -(T_GPU.VL_INTER_TASK_EXECUTION_TIME/T_CPU.VL_INTER_TASK_EXECUTION_TIME)
                    END AS SPEEDUP_GPU_INTER_TASK_EXECUTION_TIME
                    FROM T_CPU INNER JOIN T_GPU ON (T_CPU.CD_PARAMETER = T_GPU.CD_PARAMETER)
                    WHERE
                    T_CPU.VL_GRID_ROW_DIMENSION = T_GPU.VL_GRID_ROW_DIMENSION
                    AND T_CPU.VL_GRID_COLUMN_DIMENSION = T_GPU.VL_GRID_COLUMN_DIMENSION
                    AND T_CPU.VL_BLOCK_ROW_DIMENSION = T_GPU.VL_BLOCK_ROW_DIMENSION
                    AND T_CPU.VL_BLOCK_COLUMN_DIMENSION = T_GPU.VL_BLOCK_COLUMN_DIMENSION
					AND T_CPU.ds_dataset = 'S_10GB_1'
					AND T_CPU.ds_parameter_type = 'VAR_GRID_ROW_5'
                    ORDER BY
                    T_CPU.DS_DATASET,
                    T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET




             
                    
-- SPEEDUPS MATMUL
WITH T_CPU AS (
                                    SELECT
                                    A.VL_TOTAL_EXECUTION_TIME,
                                    A.VL_INTER_TASK_EXECUTION_TIME,
                                    A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                                    A.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                                    A.VL_COMMUNICATION_TIME,
                                    (A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC + A.VL_COMMUNICATION_TIME) AS VL_INTRA_TASK_EXECUTION_TIME_FREE_ADDITIONAL,
                                    B.ID_PARAMETER,
                                    B.CD_PARAMETER,
                                    B.CD_CONFIGURATION,
                                    B.ID_ALGORITHM,
                                    (SELECT DISTINCT X.DS_ALGORITHM FROM ALGORITHM X WHERE X.ID_ALGORITHM = B.ID_ALGORITHM) AS DS_ALGORITHM,
                                    B.ID_FUNCTION,
                                    (SELECT DISTINCT X.DS_FUNCTION FROM FUNCTION X WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS DS_FUNCTION,
                                    (SELECT DISTINCT Y.ID_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS ID_DEVICE,
                                    (SELECT DISTINCT Y.DS_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS DS_DEVICE,
                                    B.ID_DATASET,
                                    B.ID_RESOURCE,
                                    B.ID_PARAMETER_TYPE,
                                    (SELECT X.DS_PARAMETER_TYPE FROM PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) AS DS_PARAMETER_TYPE,
                                    (SELECT X.DS_PARAMETER_ATTRIBUTE FROM PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) AS DS_PARAMETER_ATTRIBUTE,
                                    B.NR_ITERATIONS,
                                    B.VL_GRID_ROW_DIMENSION,
                                    B.VL_GRID_COLUMN_DIMENSION,
                                    B.VL_BLOCK_ROW_DIMENSION,
                                    B.VL_BLOCK_COLUMN_DIMENSION,
                                    B.VL_BLOCK_MEMORY_SIZE,
                                    B.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                                    B.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                                    ROUND((CAST(B.VL_BLOCK_MEMORY_SIZE AS NUMERIC)/CAST(D.VL_DATASET_MEMORY_SIZE AS NUMERIC))*100,2) AS VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                    C.DS_RESOURCE,
                                    C.NR_NODES,
                                    C.NR_COMPUTING_UNITS_CPU,
                                    C.NR_COMPUTING_UNITS_GPU,
                                    C.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                                    C.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
									(C.NR_NODES-1) || ' (' || (C.NR_NODES-1)*C.NR_COMPUTING_UNITS_CPU || ';' || (C.NR_NODES-1)*4 || ')' AS NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU_GPU,
                                    D.DS_DATASET,
                                    D.VL_DATASET_MEMORY_SIZE,
                                    D.DS_DATA_TYPE,
                                    D.VL_DATA_TYPE_MEMORY_SIZE,
                                    D.VL_DATASET_DIMENSION,
                                    D.VL_DATASET_ROW_DIMENSION,
                                    D.VL_DATASET_COLUMN_DIMENSION,
                                    D.NR_RANDOM_STATE
                                FROM EXPERIMENT A
                                INNER JOIN PARAMETER B ON (A.ID_PARAMETER = B.ID_PARAMETER)
                                INNER JOIN RESOURCE C ON (B.ID_RESOURCE = C.ID_RESOURCE)
                                INNER JOIN DATASET D ON (B.ID_DATASET = D.ID_DATASET)
                                WHERE
                                (SELECT DISTINCT Y.DS_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) = 'CPU'
                                
                                UNION ALL
                        
                                    SELECT
                                    Y.VL_TOTAL_EXECUTION_TIME,
                                    Y.VL_INTER_TASK_EXECUTION_TIME,
                                    Y.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                                    Y.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                                    Y.VL_COMMUNICATION_TIME,
                                    (Y.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC + Y.VL_COMMUNICATION_TIME) AS VL_INTRA_TASK_EXECUTION_TIME_FREE_ADDITIONAL,
                                    Y.ID_PARAMETER,
                                    Y.CD_PARAMETER,
                                    Y.CD_CONFIGURATION,
                                    Y.ID_ALGORITHM,
                                    Y.DS_ALGORITHM,
                                    Y.ID_FUNCTION,
                                    Y.DS_FUNCTION,
                                    Y.ID_DEVICE,
                                    Y.DS_DEVICE,
                                    Y.ID_DATASET,
                                    Y.ID_RESOURCE,
                                    Y.ID_PARAMETER_TYPE,
                                    Y.DS_PARAMETER_TYPE,
                                    Y.DS_PARAMETER_ATTRIBUTE,
                                    Y.NR_ITERATIONS,
                                    Y.VL_GRID_ROW_DIMENSION,
                                    Y.VL_GRID_COLUMN_DIMENSION,
                                    Y.VL_BLOCK_ROW_DIMENSION,
                                    Y.VL_BLOCK_COLUMN_DIMENSION,
                                    Y.VL_BLOCK_MEMORY_SIZE,
                                    Y.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                                    Y.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                                    Y.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                    Y.DS_RESOURCE,
                                    Y.NR_NODES,
                                    Y.NR_COMPUTING_UNITS_CPU,
                                    Y.NR_COMPUTING_UNITS_GPU,
                                    Y.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                                    Y.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
									Y.NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU_GPU,
                                    Y.DS_DATASET,
                                    Y.VL_DATASET_MEMORY_SIZE,
                                    Y.DS_DATA_TYPE,
                                    Y.VL_DATA_TYPE_MEMORY_SIZE,
                                    Y.VL_DATASET_DIMENSION,
                                    Y.VL_DATASET_ROW_DIMENSION,
                                    Y.VL_DATASET_COLUMN_DIMENSION,
                                    Y.NR_RANDOM_STATE
                                    FROM
                                    (
                                        SELECT
                                        AVG(X.VL_TOTAL_EXECUTION_TIME) AS VL_TOTAL_EXECUTION_TIME,
                                        AVG(X.VL_INTER_TASK_EXECUTION_TIME) AS VL_INTER_TASK_EXECUTION_TIME,
                                        AVG(X.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC) AS VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                                        AVG(X.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC) AS VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                                        AVG(X.VL_COMMUNICATION_TIME_1) AS VL_COMMUNICATION_TIME_1,
                                        AVG(X.VL_COMMUNICATION_TIME_2) AS VL_COMMUNICATION_TIME_2,
                                        AVG(X.VL_COMMUNICATION_TIME) AS VL_COMMUNICATION_TIME,
                                        AVG(X.VL_ADDITIONAL_TIME_1) AS VL_ADDITIONAL_TIME_1,
                                        AVG(X.VL_ADDITIONAL_TIME_2) AS VL_ADDITIONAL_TIME_2,
                                        AVG(X.VL_ADDITIONAL_TIME) AS VL_ADDITIONAL_TIME,
                                        X.ID_PARAMETER,
                                        X.CD_PARAMETER,
                                        X.CD_CONFIGURATION,
                                        X.ID_ALGORITHM,
                                        X.DS_ALGORITHM,
                                        X.ID_FUNCTION,
                                        X.DS_FUNCTION,
                                        X.ID_DEVICE,
                                        X.DS_DEVICE,
                                        X.ID_DATASET,
                                        X.ID_RESOURCE,
                                        X.ID_PARAMETER_TYPE,
                                        X.DS_PARAMETER_TYPE,
                                        X.DS_PARAMETER_ATTRIBUTE,
                                        X.NR_ITERATIONS,
                                        X.VL_GRID_ROW_DIMENSION,
                                        X.VL_GRID_COLUMN_DIMENSION,
                                        X.VL_GRID_ROW_X_COLUMN_DIMENSION,
                                        X.VL_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                        X.VL_CONCAT_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                        X.VL_BLOCK_ROW_DIMENSION,
                                        X.VL_BLOCK_COLUMN_DIMENSION,
                                        X.VL_BLOCK_ROW_X_COLUMN_DIMENSION,
                                        X.VL_BLOCK_MEMORY_SIZE,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                        X.VL_CONCAT_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                        X.DS_RESOURCE,
                                        X.NR_NODES,
                                        X.NR_COMPUTING_UNITS_CPU,
                                        X.NR_COMPUTING_UNITS_GPU,
                                        X.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                                        X.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
										X.NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU_GPU,
                                        X.DS_DATASET,
                                        X.VL_DATASET_MEMORY_SIZE,
                                        X.DS_DATA_TYPE,
                                        X.VL_DATA_TYPE_MEMORY_SIZE,
                                        X.VL_DATASET_DIMENSION,
                                        X.VL_DATASET_ROW_DIMENSION,
                                        X.VL_DATASET_COLUMN_DIMENSION,
                                        X.VL_DATASET_ROW_X_COLUMN_DIMENSION,
                                        X.NR_RANDOM_STATE
                                        FROM
                                        (
                                            SELECT
                                                A.ID_EXPERIMENT,
                                                A.VL_TOTAL_EXECUTION_TIME,
                                                A.VL_INTER_TASK_EXECUTION_TIME,
                                                A.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                                                A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                                                A.VL_COMMUNICATION_TIME_1,
                                                A.VL_COMMUNICATION_TIME_2,
                                                A.VL_COMMUNICATION_TIME_1 + A.VL_COMMUNICATION_TIME_2 AS VL_COMMUNICATION_TIME,
                                                A.VL_ADDITIONAL_TIME_1,
                                                A.VL_ADDITIONAL_TIME_2,
                                                A.VL_ADDITIONAL_TIME_1 + A.VL_ADDITIONAL_TIME_2 AS VL_ADDITIONAL_TIME,
                                                A.DT_PROCESSING,
                                                B.ID_PARAMETER,
                                                B.CD_PARAMETER,
                                                B.CD_CONFIGURATION,
                                                B.ID_ALGORITHM,
                                                (SELECT DISTINCT X.DS_ALGORITHM FROM ALGORITHM X WHERE X.ID_ALGORITHM = B.ID_ALGORITHM) AS DS_ALGORITHM,
                                                B.ID_FUNCTION,
                                                (SELECT DISTINCT X.DS_FUNCTION FROM FUNCTION X WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS DS_FUNCTION,
                                                (SELECT DISTINCT Y.ID_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS ID_DEVICE,
                                                (SELECT DISTINCT Y.DS_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS DS_DEVICE,
                                                B.ID_DATASET,
                                                B.ID_RESOURCE,
                                                B.ID_PARAMETER_TYPE,
                                                (SELECT X.DS_PARAMETER_TYPE FROM PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) AS DS_PARAMETER_TYPE,
                                                (SELECT X.DS_PARAMETER_ATTRIBUTE FROM PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) AS DS_PARAMETER_ATTRIBUTE,
                                                B.NR_ITERATIONS,
                                                B.VL_GRID_ROW_DIMENSION,
                                                B.VL_GRID_COLUMN_DIMENSION,
                                                B.VL_GRID_ROW_DIMENSION || ' x ' || B.VL_GRID_COLUMN_DIMENSION AS VL_GRID_ROW_X_COLUMN_DIMENSION,
                                                ROUND((CAST(B.VL_GRID_COLUMN_DIMENSION AS NUMERIC)/CAST(D.VL_DATASET_COLUMN_DIMENSION AS NUMERIC))*100,2) AS VL_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                                B.VL_GRID_ROW_DIMENSION || ' x ' || B.VL_GRID_COLUMN_DIMENSION || ' (' || ROUND((CAST(B.VL_GRID_COLUMN_DIMENSION AS NUMERIC)/CAST(D.VL_DATASET_COLUMN_DIMENSION AS NUMERIC))*100,2) || '%)' AS VL_CONCAT_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                                B.VL_BLOCK_ROW_DIMENSION,
                                                B.VL_BLOCK_COLUMN_DIMENSION,
                                                B.VL_BLOCK_ROW_DIMENSION || ' x ' || B.VL_BLOCK_COLUMN_DIMENSION AS VL_BLOCK_ROW_X_COLUMN_DIMENSION,
                                                B.VL_BLOCK_MEMORY_SIZE,
                                                B.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                                                B.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                                                ROUND((CAST(B.VL_BLOCK_MEMORY_SIZE AS NUMERIC)/CAST(D.VL_DATASET_MEMORY_SIZE AS NUMERIC))*100,2) AS VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                                ROUND(B.VL_BLOCK_MEMORY_SIZE*1e-6,2) || ' (' || ROUND((CAST(B.VL_BLOCK_MEMORY_SIZE AS NUMERIC)/CAST(D.VL_DATASET_MEMORY_SIZE AS NUMERIC))*100,2) || '%)' AS VL_CONCAT_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                                C.DS_RESOURCE,
                                                C.NR_NODES,
                                                C.NR_COMPUTING_UNITS_CPU,
                                                C.NR_COMPUTING_UNITS_GPU,
                                                C.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                                                C.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
												(C.NR_NODES-1) || ' (' || (C.NR_NODES-1)*C.NR_COMPUTING_UNITS_CPU || ';' || (C.NR_NODES-1)*4 || ')' AS NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU_GPU,
                                                D.DS_DATASET,
                                                D.VL_DATASET_MEMORY_SIZE,
                                                D.DS_DATA_TYPE,
                                                D.VL_DATA_TYPE_MEMORY_SIZE,
                                                D.VL_DATASET_DIMENSION,
                                                D.VL_DATASET_ROW_DIMENSION,
                                                D.VL_DATASET_COLUMN_DIMENSION,
                                                D.VL_DATASET_ROW_DIMENSION || ' x ' || D.VL_DATASET_COLUMN_DIMENSION AS VL_DATASET_ROW_X_COLUMN_DIMENSION,
                                                D.NR_RANDOM_STATE
                                            FROM EXPERIMENT_RAW A
                                            INNER JOIN PARAMETER B ON (A.ID_PARAMETER = B.ID_PARAMETER)
                                            INNER JOIN RESOURCE C ON (B.ID_RESOURCE = C.ID_RESOURCE)
                                            INNER JOIN DATASET D ON (B.ID_DATASET = D.ID_DATASET)
                                            WHERE
                                            (SELECT DISTINCT Z.DS_DEVICE FROM FUNCTION W INNER JOIN DEVICE Z ON (W.ID_DEVICE = Z.ID_DEVICE) WHERE W.ID_FUNCTION = B.ID_FUNCTION) = 'CPU'
                                            AND A.NR_ALGORITHM_ITERATION <> 0
                                        ) X
										WHERE
										X.DS_FUNCTION = 'MATMUL_FUNC'
                                        GROUP BY
                                        X.ID_PARAMETER,
                                        X.CD_PARAMETER,
                                        X.CD_CONFIGURATION,
                                        X.ID_ALGORITHM,
                                        X.DS_ALGORITHM,
                                        X.ID_FUNCTION,
                                        X.DS_FUNCTION,
                                        X.ID_DEVICE,
                                        X.DS_DEVICE,
                                        X.ID_DATASET,
                                        X.ID_RESOURCE,
                                        X.ID_PARAMETER_TYPE,
                                        X.DS_PARAMETER_TYPE,
                                        X.DS_PARAMETER_ATTRIBUTE,
                                        X.NR_ITERATIONS,
                                        X.VL_GRID_ROW_DIMENSION,
                                        X.VL_GRID_COLUMN_DIMENSION,
                                        X.VL_GRID_ROW_X_COLUMN_DIMENSION,
                                        X.VL_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                        X.VL_CONCAT_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                        X.VL_BLOCK_ROW_DIMENSION,
                                        X.VL_BLOCK_COLUMN_DIMENSION,
                                        X.VL_BLOCK_ROW_X_COLUMN_DIMENSION,
                                        X.VL_BLOCK_MEMORY_SIZE,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                        X.VL_CONCAT_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                        X.DS_RESOURCE,
                                        X.NR_NODES,
                                        X.NR_COMPUTING_UNITS_CPU,
                                        X.NR_COMPUTING_UNITS_GPU,
                                        X.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                                        X.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
										X.NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU_GPU,
                                        X.DS_DATASET,
                                        X.VL_DATASET_MEMORY_SIZE,
                                        X.DS_DATA_TYPE,
                                        X.VL_DATA_TYPE_MEMORY_SIZE,
                                        X.VL_DATASET_DIMENSION,
                                        X.VL_DATASET_ROW_DIMENSION,
                                        X.VL_DATASET_COLUMN_DIMENSION,
                                        X.VL_DATASET_ROW_X_COLUMN_DIMENSION,
                                        X.NR_RANDOM_STATE
                                    ) Y
                        
                                ),
                    T_GPU AS (
                                    SELECT
                                    A.VL_TOTAL_EXECUTION_TIME,
                                    A.VL_INTER_TASK_EXECUTION_TIME,
                                    A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                                    A.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                                    A.VL_COMMUNICATION_TIME,
                                    (A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC + A.VL_COMMUNICATION_TIME) AS VL_INTRA_TASK_EXECUTION_TIME_FREE_ADDITIONAL,
                                    B.ID_PARAMETER,
                                    B.CD_PARAMETER,
                                    B.CD_CONFIGURATION,
                                    B.ID_ALGORITHM,
                                    (SELECT DISTINCT X.DS_ALGORITHM FROM ALGORITHM X WHERE X.ID_ALGORITHM = B.ID_ALGORITHM) AS DS_ALGORITHM,
                                    B.ID_FUNCTION,
                                    (SELECT DISTINCT X.DS_FUNCTION FROM FUNCTION X WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS DS_FUNCTION,
                                    (SELECT DISTINCT Y.ID_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS ID_DEVICE,
                                    (SELECT DISTINCT Y.DS_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS DS_DEVICE,
                                    B.ID_DATASET,
                                    B.ID_RESOURCE,
                                    B.ID_PARAMETER_TYPE,
                                    (SELECT X.DS_PARAMETER_TYPE FROM PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) AS DS_PARAMETER_TYPE,
                                    (SELECT X.DS_PARAMETER_ATTRIBUTE FROM PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) AS DS_PARAMETER_ATTRIBUTE,
                                    B.NR_ITERATIONS,
                                    B.VL_GRID_ROW_DIMENSION,
                                    B.VL_GRID_COLUMN_DIMENSION,
                                    B.VL_BLOCK_ROW_DIMENSION,
                                    B.VL_BLOCK_COLUMN_DIMENSION,
                                    B.VL_BLOCK_MEMORY_SIZE,
                                    B.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                                    B.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                                    ROUND((CAST(B.VL_BLOCK_MEMORY_SIZE AS NUMERIC)/CAST(D.VL_DATASET_MEMORY_SIZE AS NUMERIC))*100,2) AS VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                    C.DS_RESOURCE,
                                    C.NR_NODES,
                                    C.NR_COMPUTING_UNITS_CPU,
                                    C.NR_COMPUTING_UNITS_GPU,
                                    C.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                                    C.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
									(C.NR_NODES-1) || ' (' || (C.NR_NODES-1)*C.NR_COMPUTING_UNITS_CPU || ';' || (C.NR_NODES-1)*4 || ')' AS NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU_GPU,
                                    D.DS_DATASET,
                                    D.VL_DATASET_MEMORY_SIZE,
                                    D.DS_DATA_TYPE,
                                    D.VL_DATA_TYPE_MEMORY_SIZE,
                                    D.VL_DATASET_DIMENSION,
                                    D.VL_DATASET_ROW_DIMENSION,
                                    D.VL_DATASET_COLUMN_DIMENSION,
                                    D.NR_RANDOM_STATE
                                    FROM EXPERIMENT A
                                    INNER JOIN PARAMETER B ON (A.ID_PARAMETER = B.ID_PARAMETER)
                                    INNER JOIN RESOURCE C ON (B.ID_RESOURCE = C.ID_RESOURCE)
                                    INNER JOIN DATASET D ON (B.ID_DATASET = D.ID_DATASET)
                                    WHERE
                                    (SELECT DISTINCT Y.DS_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) = 'GPU'
                            
                                UNION ALL
                        
                                    SELECT
                                    Y.VL_TOTAL_EXECUTION_TIME,
                                    Y.VL_INTER_TASK_EXECUTION_TIME,
                                    Y.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                                    Y.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                                    Y.VL_COMMUNICATION_TIME,
                                    (Y.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC + Y.VL_COMMUNICATION_TIME) AS VL_INTRA_TASK_EXECUTION_TIME_FREE_ADDITIONAL,
                                    Y.ID_PARAMETER,
                                    Y.CD_PARAMETER,
                                    Y.CD_CONFIGURATION,
                                    Y.ID_ALGORITHM,
                                    Y.DS_ALGORITHM,
                                    Y.ID_FUNCTION,
                                    Y.DS_FUNCTION,
                                    Y.ID_DEVICE,
                                    Y.DS_DEVICE,
                                    Y.ID_DATASET,
                                    Y.ID_RESOURCE,
                                    Y.ID_PARAMETER_TYPE,
                                    Y.DS_PARAMETER_TYPE,
                                    Y.DS_PARAMETER_ATTRIBUTE,
                                    Y.NR_ITERATIONS,
                                    Y.VL_GRID_ROW_DIMENSION,
                                    Y.VL_GRID_COLUMN_DIMENSION,
                                    Y.VL_BLOCK_ROW_DIMENSION,
                                    Y.VL_BLOCK_COLUMN_DIMENSION,
                                    Y.VL_BLOCK_MEMORY_SIZE,
                                    Y.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                                    Y.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                                    Y.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                    Y.DS_RESOURCE,
                                    Y.NR_NODES,
                                    Y.NR_COMPUTING_UNITS_CPU,
                                    Y.NR_COMPUTING_UNITS_GPU,
                                    Y.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                                    Y.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
									Y.NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU_GPU,
                                    Y.DS_DATASET,
                                    Y.VL_DATASET_MEMORY_SIZE,
                                    Y.DS_DATA_TYPE,
                                    Y.VL_DATA_TYPE_MEMORY_SIZE,
                                    Y.VL_DATASET_DIMENSION,
                                    Y.VL_DATASET_ROW_DIMENSION,
                                    Y.VL_DATASET_COLUMN_DIMENSION,
                                    Y.NR_RANDOM_STATE
                                    FROM
                                    (
                                        SELECT
                                        AVG(X.VL_TOTAL_EXECUTION_TIME) AS VL_TOTAL_EXECUTION_TIME,
                                        AVG(X.VL_INTER_TASK_EXECUTION_TIME) AS VL_INTER_TASK_EXECUTION_TIME,
                                        AVG(X.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC) AS VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                                        AVG(X.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC) AS VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                                        AVG(X.VL_COMMUNICATION_TIME_1) AS VL_COMMUNICATION_TIME_1,
                                        AVG(X.VL_COMMUNICATION_TIME_2) AS VL_COMMUNICATION_TIME_2,
                                        AVG(X.VL_COMMUNICATION_TIME) AS VL_COMMUNICATION_TIME,
                                        AVG(X.VL_ADDITIONAL_TIME_1) AS VL_ADDITIONAL_TIME_1,
                                        AVG(X.VL_ADDITIONAL_TIME_2) AS VL_ADDITIONAL_TIME_2,
                                        AVG(X.VL_ADDITIONAL_TIME) AS VL_ADDITIONAL_TIME,
                                        X.ID_PARAMETER,
                                        X.CD_PARAMETER,
                                        X.CD_CONFIGURATION,
                                        X.ID_ALGORITHM,
                                        X.DS_ALGORITHM,
                                        X.ID_FUNCTION,
                                        X.DS_FUNCTION,
                                        X.ID_DEVICE,
                                        X.DS_DEVICE,
                                        X.ID_DATASET,
                                        X.ID_RESOURCE,
                                        X.ID_PARAMETER_TYPE,
                                        X.DS_PARAMETER_TYPE,
                                        X.DS_PARAMETER_ATTRIBUTE,
                                        X.NR_ITERATIONS,
                                        X.VL_GRID_ROW_DIMENSION,
                                        X.VL_GRID_COLUMN_DIMENSION,
                                        X.VL_GRID_ROW_X_COLUMN_DIMENSION,
                                        X.VL_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                        X.VL_CONCAT_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                        X.VL_BLOCK_ROW_DIMENSION,
                                        X.VL_BLOCK_COLUMN_DIMENSION,
                                        X.VL_BLOCK_ROW_X_COLUMN_DIMENSION,
                                        X.VL_BLOCK_MEMORY_SIZE,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                        X.VL_CONCAT_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                        X.DS_RESOURCE,
                                        X.NR_NODES,
                                        X.NR_COMPUTING_UNITS_CPU,
                                        X.NR_COMPUTING_UNITS_GPU,
                                        X.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                                        X.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
										X.NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU_GPU,
                                        X.DS_DATASET,
                                        X.VL_DATASET_MEMORY_SIZE,
                                        X.DS_DATA_TYPE,
                                        X.VL_DATA_TYPE_MEMORY_SIZE,
                                        X.VL_DATASET_DIMENSION,
                                        X.VL_DATASET_ROW_DIMENSION,
                                        X.VL_DATASET_COLUMN_DIMENSION,
                                        X.VL_DATASET_ROW_X_COLUMN_DIMENSION,
                                        X.NR_RANDOM_STATE
                                        FROM
                                        (
                                            SELECT
                                                A.ID_EXPERIMENT,
                                                A.VL_TOTAL_EXECUTION_TIME,
                                                A.VL_INTER_TASK_EXECUTION_TIME,
                                                A.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                                                A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                                                A.VL_COMMUNICATION_TIME_1,
                                                A.VL_COMMUNICATION_TIME_2,
                                                A.VL_COMMUNICATION_TIME_1 + A.VL_COMMUNICATION_TIME_2 AS VL_COMMUNICATION_TIME,
                                                A.VL_ADDITIONAL_TIME_1,
                                                A.VL_ADDITIONAL_TIME_2,
                                                A.VL_ADDITIONAL_TIME_1 + A.VL_ADDITIONAL_TIME_2 AS VL_ADDITIONAL_TIME,
                                                A.DT_PROCESSING,
                                                B.ID_PARAMETER,
                                                B.CD_PARAMETER,
                                                B.CD_CONFIGURATION,
                                                B.ID_ALGORITHM,
                                                (SELECT DISTINCT X.DS_ALGORITHM FROM ALGORITHM X WHERE X.ID_ALGORITHM = B.ID_ALGORITHM) AS DS_ALGORITHM,
                                                B.ID_FUNCTION,
                                                (SELECT DISTINCT X.DS_FUNCTION FROM FUNCTION X WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS DS_FUNCTION,
                                                (SELECT DISTINCT Y.ID_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS ID_DEVICE,
                                                (SELECT DISTINCT Y.DS_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS DS_DEVICE,
                                                B.ID_DATASET,
                                                B.ID_RESOURCE,
                                                B.ID_PARAMETER_TYPE,
                                                (SELECT X.DS_PARAMETER_TYPE FROM PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) AS DS_PARAMETER_TYPE,
                                                (SELECT X.DS_PARAMETER_ATTRIBUTE FROM PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) AS DS_PARAMETER_ATTRIBUTE,
                                                B.NR_ITERATIONS,
                                                B.VL_GRID_ROW_DIMENSION,
                                                B.VL_GRID_COLUMN_DIMENSION,
                                                B.VL_GRID_ROW_DIMENSION || ' x ' || B.VL_GRID_COLUMN_DIMENSION AS VL_GRID_ROW_X_COLUMN_DIMENSION,
                                                ROUND((CAST(B.VL_GRID_COLUMN_DIMENSION AS NUMERIC)/CAST(D.VL_DATASET_COLUMN_DIMENSION AS NUMERIC))*100,2) AS VL_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                                B.VL_GRID_ROW_DIMENSION || ' x ' || B.VL_GRID_COLUMN_DIMENSION || ' (' || ROUND((CAST(B.VL_GRID_COLUMN_DIMENSION AS NUMERIC)/CAST(D.VL_DATASET_COLUMN_DIMENSION AS NUMERIC))*100,2) || '%)' AS VL_CONCAT_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                                B.VL_BLOCK_ROW_DIMENSION,
                                                B.VL_BLOCK_COLUMN_DIMENSION,
                                                B.VL_BLOCK_ROW_DIMENSION || ' x ' || B.VL_BLOCK_COLUMN_DIMENSION AS VL_BLOCK_ROW_X_COLUMN_DIMENSION,
                                                B.VL_BLOCK_MEMORY_SIZE,
                                                B.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                                                B.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                                                ROUND((CAST(B.VL_BLOCK_MEMORY_SIZE AS NUMERIC)/CAST(D.VL_DATASET_MEMORY_SIZE AS NUMERIC))*100,2) AS VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                                ROUND(B.VL_BLOCK_MEMORY_SIZE*1e-6,2) || ' (' || ROUND((CAST(B.VL_BLOCK_MEMORY_SIZE AS NUMERIC)/CAST(D.VL_DATASET_MEMORY_SIZE AS NUMERIC))*100,2) || '%)' AS VL_CONCAT_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                                C.DS_RESOURCE,
                                                C.NR_NODES,
                                                C.NR_COMPUTING_UNITS_CPU,
                                                C.NR_COMPUTING_UNITS_GPU,
                                                C.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                                                C.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
												(C.NR_NODES-1) || ' (' || (C.NR_NODES-1)*C.NR_COMPUTING_UNITS_CPU || ';' || (C.NR_NODES-1)*4 || ')' AS NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU_GPU,
                                                D.DS_DATASET,
                                                D.VL_DATASET_MEMORY_SIZE,
                                                D.DS_DATA_TYPE,
                                                D.VL_DATA_TYPE_MEMORY_SIZE,
                                                D.VL_DATASET_DIMENSION,
                                                D.VL_DATASET_ROW_DIMENSION,
                                                D.VL_DATASET_COLUMN_DIMENSION,
                                                D.VL_DATASET_ROW_DIMENSION || ' x ' || D.VL_DATASET_COLUMN_DIMENSION AS VL_DATASET_ROW_X_COLUMN_DIMENSION,
                                                D.NR_RANDOM_STATE
                                            FROM EXPERIMENT_RAW A
                                            INNER JOIN PARAMETER B ON (A.ID_PARAMETER = B.ID_PARAMETER)
                                            INNER JOIN RESOURCE C ON (B.ID_RESOURCE = C.ID_RESOURCE)
                                            INNER JOIN DATASET D ON (B.ID_DATASET = D.ID_DATASET)
                                            WHERE
                                            (SELECT DISTINCT Z.DS_DEVICE FROM FUNCTION W INNER JOIN DEVICE Z ON (W.ID_DEVICE = Z.ID_DEVICE) WHERE W.ID_FUNCTION = B.ID_FUNCTION) = 'GPU'
                                            --AND A.ID_EXPERIMENT NOT IN (370685,362026,362018,362024,362037,362036,362028,362032,362029,362023,362052) --FILTERING OUTLIERS MATMUL EXTRA EXPERIMENTS
                                            AND A.NR_ALGORITHM_ITERATION <> 0
                                        ) X
										WHERE
										X.DS_FUNCTION = 'MATMUL_FUNC'
                                        GROUP BY
                                        X.ID_PARAMETER,
                                        X.CD_PARAMETER,
                                        X.CD_CONFIGURATION,
                                        X.ID_ALGORITHM,
                                        X.DS_ALGORITHM,
                                        X.ID_FUNCTION,
                                        X.DS_FUNCTION,
                                        X.ID_DEVICE,
                                        X.DS_DEVICE,
                                        X.ID_DATASET,
                                        X.ID_RESOURCE,
                                        X.ID_PARAMETER_TYPE,
                                        X.DS_PARAMETER_TYPE,
                                        X.DS_PARAMETER_ATTRIBUTE,
                                        X.NR_ITERATIONS,
                                        X.VL_GRID_ROW_DIMENSION,
                                        X.VL_GRID_COLUMN_DIMENSION,
                                        X.VL_GRID_ROW_X_COLUMN_DIMENSION,
                                        X.VL_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                        X.VL_CONCAT_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                        X.VL_BLOCK_ROW_DIMENSION,
                                        X.VL_BLOCK_COLUMN_DIMENSION,
                                        X.VL_BLOCK_ROW_X_COLUMN_DIMENSION,
                                        X.VL_BLOCK_MEMORY_SIZE,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                        X.VL_CONCAT_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                        X.DS_RESOURCE,
                                        X.NR_NODES,
                                        X.NR_COMPUTING_UNITS_CPU,
                                        X.NR_COMPUTING_UNITS_GPU,
                                        X.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                                        X.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
										X.NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU_GPU,
                                        X.DS_DATASET,
                                        X.VL_DATASET_MEMORY_SIZE,
                                        X.DS_DATA_TYPE,
                                        X.VL_DATA_TYPE_MEMORY_SIZE,
                                        X.VL_DATASET_DIMENSION,
                                        X.VL_DATASET_ROW_DIMENSION,
                                        X.VL_DATASET_COLUMN_DIMENSION,
                                        X.VL_DATASET_ROW_X_COLUMN_DIMENSION,
                                        X.NR_RANDOM_STATE
                                    ) Y
                    )
                    SELECT
                    --T_CPU.ID_PARAMETER_TYPE,
                    --T_CPU.CD_PARAMETER,
                    T_CPU.DS_ALGORITHM,
                    --T_CPU.NR_ITERATIONS,
                    --CASE
                    --WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 0.3 THEN 0.4
                    --WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 0.7 THEN 0.8
                    --WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 1.5 THEN 1.6
                    --WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 3.0 THEN 3.1
                    --WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 6.2 THEN 6.3
                    --ELSE ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1)
					--END AS VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                    --CASE
                    --WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 0.3 THEN 0.4 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION || ' x ' || T_CPU.VL_GRID_COLUMN_DIMENSION  || ')'
                    --WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 0.7 THEN 0.8 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION || ' x ' || T_CPU.VL_GRID_COLUMN_DIMENSION  || ')'
                    --WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 1.5 THEN 1.6 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION || ' x ' || T_CPU.VL_GRID_COLUMN_DIMENSION  || ')'
                    --WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 3.0 THEN 3.1 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION || ' x ' || T_CPU.VL_GRID_COLUMN_DIMENSION  || ')'
                    --WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 6.2 THEN 6.3 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION || ' x ' || T_CPU.VL_GRID_COLUMN_DIMENSION  || ')'
                    --ELSE ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) || ' (' || T_CPU.VL_GRID_ROW_DIMENSION || ' x ' || T_CPU.VL_GRID_COLUMN_DIMENSION  || ')'
					--END AS CONCAT_BLOCK_PERCENT_DATASET_GRID_DIMENSION,
                    --ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) AS VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                    --T_CPU.DS_RESOURCE,
                    --T_CPU.DS_PARAMETER_TYPE,
                    --T_CPU.DS_PARAMETER_ATTRIBUTE,
                    T_CPU.DS_DATASET,
                    --CAST(T_CPU.VL_DATASET_MEMORY_SIZE*1e-6 AS BIGINT) as VL_DATASET_MEMORY_SIZE,
                    --T_CPU.VL_DATASET_DIMENSION,
                    --T_CPU.VL_DATASET_ROW_DIMENSION,
                    --T_CPU.VL_DATASET_COLUMN_DIMENSION,
                    --T_CPU.VL_GRID_ROW_DIMENSION,
                    --T_CPU.VL_GRID_COLUMN_DIMENSION,
                    --T_CPU.VL_BLOCK_ROW_DIMENSION,
                    --T_CPU.VL_BLOCK_COLUMN_DIMENSION,
                    --T_CPU.VL_BLOCK_MEMORY_SIZE,
                    --ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE*1e-6,2) || ' (' || T_CPU.VL_GRID_ROW_DIMENSION || ' x ' || T_CPU.VL_GRID_COLUMN_DIMENSION  || ')' AS VL_CONCAT_BLOCK_SIZE_MB_GRID_ROW_X_COLUMN_DIMENSION,
					--T_CPU.NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU_GPU,
					--CASE
					--	WHEN T_CPU.DS_ALGORITHM = 'KMEANS'
					--		THEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE*1e-6,0) || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*5 || ')'
					--	WHEN T_CPU.DS_ALGORITHM = 'MATMUL_DISLIB'
					--		THEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE*1e-6,0) || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION + T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*(T_CPU.VL_GRID_ROW_DIMENSION-1)  || ')'
					--	ELSE
					--		'999999999999'
					--END AS VL_CONCAT_BLOCK_SIZE_MB_NR_TASKS,
					CASE
						WHEN T_CPU.DS_ALGORITHM = 'KMEANS'
							THEN
								CASE
									WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 0.3 THEN 0.4 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*5  || ')'
									WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 0.7 THEN 0.8 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*5  || ')'
									WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 1.5 THEN 1.6 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*5  || ')'
									WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 3.0 THEN 3.1 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*5  || ')'
									WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 6.2 THEN 6.3 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*5  || ')'
									ELSE ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*5  || ')'
								END
						WHEN T_CPU.DS_ALGORITHM = 'MATMUL_DISLIB'
							THEN
								CASE
									WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 0.3 THEN 0.4 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION + T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*(T_CPU.VL_GRID_ROW_DIMENSION-1)  || ')'
									WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 0.7 THEN 0.8 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION + T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*(T_CPU.VL_GRID_ROW_DIMENSION-1)  || ')'
									WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 1.5 THEN 1.6 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION + T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*(T_CPU.VL_GRID_ROW_DIMENSION-1)  || ')'
									WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 3.0 THEN 3.1 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION + T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*(T_CPU.VL_GRID_ROW_DIMENSION-1)  || ')'
									WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 6.2 THEN 6.3 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION + T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*(T_CPU.VL_GRID_ROW_DIMENSION-1)  || ')'
									ELSE ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION + T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*(T_CPU.VL_GRID_ROW_DIMENSION-1)   || ')'
								END
						ELSE
							'999999999999'
					END AS CONCAT_BLOCK_PERCENT_DATASET_NR_TASKS,
                    CASE
                    WHEN (T_CPU.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC/T_GPU.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC) > 1.00 THEN (T_CPU.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC/T_GPU.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC)
                    ELSE -(T_GPU.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC/T_CPU.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC)
                    END AS SPEEDUP_GPU_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                    CASE
                    WHEN (T_CPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC/T_GPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC) > 1.00 THEN (T_CPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC/T_GPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC)
                    ELSE -(T_GPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC/T_CPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC)
                    END AS SPEEDUP_GPU_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
					CASE
                    WHEN (T_CPU.VL_TOTAL_EXECUTION_TIME/T_GPU.VL_TOTAL_EXECUTION_TIME) > 1.00 THEN (T_CPU.VL_TOTAL_EXECUTION_TIME/T_GPU.VL_TOTAL_EXECUTION_TIME)
                    ELSE -(T_GPU.VL_TOTAL_EXECUTION_TIME/T_CPU.VL_TOTAL_EXECUTION_TIME)
                    END AS SPEEDUP_GPU_TOTAL_EXECUTION_TIME
                    FROM T_CPU INNER JOIN T_GPU ON (T_CPU.CD_PARAMETER = T_GPU.CD_PARAMETER)
                    WHERE
                    T_CPU.VL_GRID_ROW_DIMENSION = T_GPU.VL_GRID_ROW_DIMENSION
                    AND T_CPU.VL_GRID_COLUMN_DIMENSION = T_GPU.VL_GRID_COLUMN_DIMENSION
                    AND T_CPU.VL_BLOCK_ROW_DIMENSION = T_GPU.VL_BLOCK_ROW_DIMENSION
                    AND T_CPU.VL_BLOCK_COLUMN_DIMENSION = T_GPU.VL_BLOCK_COLUMN_DIMENSION
					AND T_CPU.ds_dataset = 'S_8GB_1'
					AND T_CPU.ds_parameter_type = 'VAR_GRID_SHAPE_MATMUL_2'
                    ORDER BY
                    T_CPU.DS_DATASET,
                    T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET





-- BREAKING TASK OVERHEADS
SELECT
DS_ALGORITHM,
DS_DEVICE,
CASE
	WHEN DS_ALGORITHM = 'KMEANS'
		THEN
			CASE
				WHEN ROUND(VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 0.3 THEN 0.4 || ' (' || VL_GRID_ROW_DIMENSION*5  || ')'
				WHEN ROUND(VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 0.7 THEN 0.8 || ' (' || VL_GRID_ROW_DIMENSION*5  || ')'
				WHEN ROUND(VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 1.5 THEN 1.6 || ' (' || VL_GRID_ROW_DIMENSION*5  || ')'
				WHEN ROUND(VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 3.0 THEN 3.1 || ' (' || VL_GRID_ROW_DIMENSION*5  || ')'
				WHEN ROUND(VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 6.2 THEN 6.3 || ' (' || VL_GRID_ROW_DIMENSION*5  || ')'
				ELSE ROUND(VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) || ' (' || VL_GRID_ROW_DIMENSION*5  || ')'
			END
	WHEN DS_ALGORITHM = 'MATMUL_DISLIB'
		THEN
			CASE
				WHEN ROUND(VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 0.3 THEN 0.4 || ' (' || VL_GRID_ROW_DIMENSION*VL_GRID_ROW_DIMENSION*VL_GRID_ROW_DIMENSION + VL_GRID_ROW_DIMENSION*VL_GRID_ROW_DIMENSION*(VL_GRID_ROW_DIMENSION-1)  || ')'
				WHEN ROUND(VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 0.7 THEN 0.8 || ' (' || VL_GRID_ROW_DIMENSION*VL_GRID_ROW_DIMENSION*VL_GRID_ROW_DIMENSION + VL_GRID_ROW_DIMENSION*VL_GRID_ROW_DIMENSION*(VL_GRID_ROW_DIMENSION-1)  || ')'
				WHEN ROUND(VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 1.5 THEN 1.6 || ' (' || VL_GRID_ROW_DIMENSION*VL_GRID_ROW_DIMENSION*VL_GRID_ROW_DIMENSION + VL_GRID_ROW_DIMENSION*VL_GRID_ROW_DIMENSION*(VL_GRID_ROW_DIMENSION-1)  || ')'
				WHEN ROUND(VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 3.0 THEN 3.1 || ' (' || VL_GRID_ROW_DIMENSION*VL_GRID_ROW_DIMENSION*VL_GRID_ROW_DIMENSION + VL_GRID_ROW_DIMENSION*VL_GRID_ROW_DIMENSION*(VL_GRID_ROW_DIMENSION-1)  || ')'
				WHEN ROUND(VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 6.2 THEN 6.3 || ' (' || VL_GRID_ROW_DIMENSION*VL_GRID_ROW_DIMENSION*VL_GRID_ROW_DIMENSION + VL_GRID_ROW_DIMENSION*VL_GRID_ROW_DIMENSION*(VL_GRID_ROW_DIMENSION-1)  || ')'
				ELSE ROUND(VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) || ' (' || VL_GRID_ROW_DIMENSION*VL_GRID_ROW_DIMENSION*VL_GRID_ROW_DIMENSION + VL_GRID_ROW_DIMENSION*VL_GRID_ROW_DIMENSION*(VL_GRID_ROW_DIMENSION-1)  || ')'
			END
	ELSE
		'999999999999'
END AS CONCAT_BLOCK_PERCENT_DATASET_NR_TASKS,
VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
VL_BLOCK_ROW_X_COLUMN_DIMENSION,
VL_GRID_ROW_X_COLUMN_DIMENSION,
VL_CONCAT_GRID_ROW_X_COLUMN_DIMENSION_BLOCK_SIZE_MB,
VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC AS USER_CODE,
VL_ADDITIONAL_TIME AS SERIAL_CODE,
VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC AS PARALLEL_CODE,
VL_COMMUNICATION_TIME AS CPU_GPU_COMMUNICATION,
VL_ADDITIONAL_TIME/VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC AS P_SERIAL_CODE,
VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC/VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC AS P_PARALLEL_CODE,
VL_COMMUNICATION_TIME/VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC AS P_CPU_GPU_COMMUNICATION
FROM
(
SELECT
                            A.VL_TOTAL_EXECUTION_TIME,
                            A.VL_INTER_TASK_EXECUTION_TIME,
                            (A.VL_INTER_TASK_EXECUTION_TIME - A.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC) AS VL_INTER_TASK_OVERHEAD_TIME,
                            A.VL_INTER_TASK_EXECUTION_TIME - (A.VL_INTER_TASK_EXECUTION_TIME - A.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC) AS VL_INTER_TASK_EXECUTION_TIME_FREE_OVERHEAD,
                            A.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                            A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                            A.VL_COMMUNICATION_TIME,
                            A.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC - (A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC+A.VL_COMMUNICATION_TIME) AS VL_ADDITIONAL_TIME,
                            (A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC + A.VL_COMMUNICATION_TIME) AS VL_INTRA_TASK_EXECUTION_TIME_FREE_ADDITIONAL,
                            --B.ID_PARAMETER,
                            B.CD_PARAMETER,
                            B.CD_CONFIGURATION,
                            B.ID_ALGORITHM,
                            (SELECT DISTINCT X.DS_ALGORITHM FROM ALGORITHM X WHERE X.ID_ALGORITHM = B.ID_ALGORITHM) AS DS_ALGORITHM,
                            --B.ID_FUNCTION,
                            --(SELECT DISTINCT X.DS_FUNCTION FROM FUNCTION X WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS DS_FUNCTION,
                            (SELECT DISTINCT Y.ID_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS ID_DEVICE,
                            (SELECT DISTINCT Y.DS_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS DS_DEVICE,
                            B.ID_DATASET,
                            B.ID_RESOURCE,
                            B.ID_PARAMETER_TYPE,
                            (SELECT X.DS_PARAMETER_TYPE FROM PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) AS DS_PARAMETER_TYPE,
                            (SELECT X.DS_PARAMETER_ATTRIBUTE FROM PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) AS DS_PARAMETER_ATTRIBUTE,
                            B.NR_ITERATIONS,
                            B.VL_GRID_ROW_DIMENSION,
                            B.VL_GRID_COLUMN_DIMENSION,
                            B.VL_GRID_ROW_DIMENSION || ' x ' || B.VL_GRID_COLUMN_DIMENSION AS VL_GRID_ROW_X_COLUMN_DIMENSION,
							B.VL_GRID_ROW_DIMENSION || ' x ' || B.VL_GRID_COLUMN_DIMENSION || ' (' || ROUND(B.VL_BLOCK_MEMORY_SIZE*1e-6,0) || ')' AS VL_CONCAT_GRID_ROW_X_COLUMN_DIMENSION_BLOCK_SIZE_MB,
                            ROUND((CAST(B.VL_GRID_COLUMN_DIMENSION AS NUMERIC)/CAST(D.VL_DATASET_COLUMN_DIMENSION AS NUMERIC))*100,2) AS VL_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                            B.VL_GRID_ROW_DIMENSION || ' x ' || B.VL_GRID_COLUMN_DIMENSION || ' (' || ROUND((CAST(B.VL_GRID_COLUMN_DIMENSION AS NUMERIC)/CAST(D.VL_DATASET_COLUMN_DIMENSION AS NUMERIC))*100,2) || '%)' AS VL_CONCAT_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                            B.VL_BLOCK_ROW_DIMENSION,
                            B.VL_BLOCK_COLUMN_DIMENSION,
                            B.VL_BLOCK_ROW_DIMENSION || ' x ' || B.VL_BLOCK_COLUMN_DIMENSION AS VL_BLOCK_ROW_X_COLUMN_DIMENSION,
                            B.VL_BLOCK_MEMORY_SIZE,
                            B.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                            B.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                            ROUND((CAST(B.VL_BLOCK_MEMORY_SIZE AS NUMERIC)/CAST(D.VL_DATASET_MEMORY_SIZE AS NUMERIC))*100,2) AS VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                            ROUND(B.VL_BLOCK_MEMORY_SIZE*1e-6,2) || ' (' || ROUND((CAST(B.VL_BLOCK_MEMORY_SIZE AS NUMERIC)/CAST(D.VL_DATASET_MEMORY_SIZE AS NUMERIC))*100,2) || '%)' AS VL_CONCAT_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                            C.DS_RESOURCE,
                            C.NR_NODES,
                            C.NR_COMPUTING_UNITS_CPU,
                            (C.NR_NODES-1)*C.NR_COMPUTING_UNITS_CPU AS NR_TOTAL_COMPUTING_UNITS_CPU,
                            (C.NR_NODES-1) || ' (' || (C.NR_NODES-1)*C.NR_COMPUTING_UNITS_CPU || ')' AS NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU,
                            C.NR_COMPUTING_UNITS_GPU,
                            C.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                            C.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
                            D.DS_DATASET,
                            D.VL_DATASET_MEMORY_SIZE,
                            D.DS_DATA_TYPE,
                            D.VL_DATA_TYPE_MEMORY_SIZE,
                            D.VL_DATASET_DIMENSION,
                            D.VL_DATASET_ROW_DIMENSION,
                            D.VL_DATASET_COLUMN_DIMENSION,
                            D.VL_DATASET_ROW_DIMENSION || ' x ' || D.VL_DATASET_COLUMN_DIMENSION AS VL_DATASET_ROW_X_COLUMN_DIMENSION,
                            D.NR_RANDOM_STATE
                        FROM EXPERIMENT A
                        INNER JOIN PARAMETER B ON (A.ID_PARAMETER = B.ID_PARAMETER)
                        INNER JOIN RESOURCE C ON (B.ID_RESOURCE = C.ID_RESOURCE)
                        INNER JOIN DATASET D ON (B.ID_DATASET = D.ID_DATASET)
                        WHERE
                        A.VL_TOTAL_EXECUTION_TIME is not null
                        --(SELECT X.DS_PARAMETER_ATTRIBUTE FROM PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) <> 'MAX_INTER_MIN_INTRA'

                        UNION ALL


                        -- EXPERIMENT RAW QUERY
                        SELECT
                        Y.VL_TOTAL_EXECUTION_TIME,
                        Y.VL_INTER_TASK_EXECUTION_TIME,
                        (Y.VL_INTER_TASK_EXECUTION_TIME - Y.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC) AS VL_INTER_TASK_OVERHEAD_TIME,
                        Y.VL_INTER_TASK_EXECUTION_TIME - (Y.VL_INTER_TASK_EXECUTION_TIME - Y.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC) AS VL_INTER_TASK_EXECUTION_TIME_FREE_OVERHEAD,
                        Y.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                        Y.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                        Y.VL_COMMUNICATION_TIME,
                        Y.VL_ADDITIONAL_TIME,
                        (Y.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC + Y.VL_COMMUNICATION_TIME) AS VL_INTRA_TASK_EXECUTION_TIME_FREE_ADDITIONAL,
                        --Y.ID_PARAMETER,
                        Y.CD_PARAMETER,
                        Y.CD_CONFIGURATION,
                        Y.ID_ALGORITHM,
                        Y.DS_ALGORITHM,
                        --Y.ID_FUNCTION,
                        --Y.DS_FUNCTION,
                        Y.ID_DEVICE,
                        Y.DS_DEVICE,
                        Y.ID_DATASET,
                        Y.ID_RESOURCE,
                        Y.ID_PARAMETER_TYPE,
                        Y.DS_PARAMETER_TYPE,
                        Y.DS_PARAMETER_ATTRIBUTE,
                        Y.NR_ITERATIONS,
                        Y.VL_GRID_ROW_DIMENSION,
                        Y.VL_GRID_COLUMN_DIMENSION,
                        Y.VL_GRID_ROW_X_COLUMN_DIMENSION,
						Y.VL_CONCAT_GRID_ROW_X_COLUMN_DIMENSION_BLOCK_SIZE_MB,
                        Y.VL_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                        Y.VL_CONCAT_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                        Y.VL_BLOCK_ROW_DIMENSION,
                        Y.VL_BLOCK_COLUMN_DIMENSION,
                        Y.VL_BLOCK_ROW_X_COLUMN_DIMENSION,
                        Y.VL_BLOCK_MEMORY_SIZE,
                        Y.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                        Y.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                        Y.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                        Y.VL_CONCAT_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                        Y.DS_RESOURCE,
                        Y.NR_NODES,
                        Y.NR_COMPUTING_UNITS_CPU,
                        (Y.NR_NODES-1)*Y.NR_COMPUTING_UNITS_CPU AS NR_TOTAL_COMPUTING_UNITS_CPU,
                        (Y.NR_NODES-1) || ' (' || (Y.NR_NODES-1)*Y.NR_COMPUTING_UNITS_CPU || ')' AS NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU,
                        Y.NR_COMPUTING_UNITS_GPU,
                        Y.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                        Y.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
                        Y.DS_DATASET,
                        Y.VL_DATASET_MEMORY_SIZE,
                        Y.DS_DATA_TYPE,
                        Y.VL_DATA_TYPE_MEMORY_SIZE,
                        Y.VL_DATASET_DIMENSION,
                        Y.VL_DATASET_ROW_DIMENSION,
                        Y.VL_DATASET_COLUMN_DIMENSION,
                        Y.VL_DATASET_ROW_X_COLUMN_DIMENSION,
                        Y.NR_RANDOM_STATE
                        FROM
                        (
                            SELECT
                            AVG(X.VL_TOTAL_EXECUTION_TIME) AS VL_TOTAL_EXECUTION_TIME,
                            AVG(X.VL_INTER_TASK_EXECUTION_TIME) AS VL_INTER_TASK_EXECUTION_TIME,
                            AVG(X.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC) AS VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                            AVG(X.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC) AS VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                            AVG(X.VL_COMMUNICATION_TIME_1) AS VL_COMMUNICATION_TIME_1,
                            AVG(X.VL_COMMUNICATION_TIME_2) AS VL_COMMUNICATION_TIME_2,
                            AVG(X.VL_COMMUNICATION_TIME) AS VL_COMMUNICATION_TIME,
                            AVG(X.VL_ADDITIONAL_TIME_1) AS VL_ADDITIONAL_TIME_1,
                            AVG(X.VL_ADDITIONAL_TIME_2) AS VL_ADDITIONAL_TIME_2,
                            AVG(X.VL_ADDITIONAL_TIME) AS VL_ADDITIONAL_TIME,
                            --X.ID_PARAMETER,
                            X.CD_PARAMETER,
                            X.CD_CONFIGURATION,
                            X.ID_ALGORITHM,
                            X.DS_ALGORITHM,
                            --X.ID_FUNCTION,
                            --X.DS_FUNCTION,
                            X.ID_DEVICE,
                            X.DS_DEVICE,
                            X.ID_DATASET,
                            X.ID_RESOURCE,
                            X.ID_PARAMETER_TYPE,
                            X.DS_PARAMETER_TYPE,
                            X.DS_PARAMETER_ATTRIBUTE,
                            X.NR_ITERATIONS,
                            X.VL_GRID_ROW_DIMENSION,
                            X.VL_GRID_COLUMN_DIMENSION,
                            X.VL_GRID_ROW_X_COLUMN_DIMENSION,
							X.VL_CONCAT_GRID_ROW_X_COLUMN_DIMENSION_BLOCK_SIZE_MB,
                            X.VL_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                            X.VL_CONCAT_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                            X.VL_BLOCK_ROW_DIMENSION,
                            X.VL_BLOCK_COLUMN_DIMENSION,
                            X.VL_BLOCK_ROW_X_COLUMN_DIMENSION,
                            X.VL_BLOCK_MEMORY_SIZE,
                            X.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                            X.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                            X.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                            X.VL_CONCAT_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                            X.DS_RESOURCE,
                            X.NR_NODES,
                            X.NR_COMPUTING_UNITS_CPU,
                            X.NR_COMPUTING_UNITS_GPU,
                            X.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                            X.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
                            X.DS_DATASET,
                            X.VL_DATASET_MEMORY_SIZE,
                            X.DS_DATA_TYPE,
                            X.VL_DATA_TYPE_MEMORY_SIZE,
                            X.VL_DATASET_DIMENSION,
                            X.VL_DATASET_ROW_DIMENSION,
                            X.VL_DATASET_COLUMN_DIMENSION,
                            X.VL_DATASET_ROW_X_COLUMN_DIMENSION,
                            X.NR_RANDOM_STATE
                            FROM
                            (
                                SELECT
                                    A.ID_EXPERIMENT,
                                    A.VL_TOTAL_EXECUTION_TIME,
                                    A.VL_INTER_TASK_EXECUTION_TIME,
                                    A.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                                    A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                                    A.VL_COMMUNICATION_TIME_1,
                                    A.VL_COMMUNICATION_TIME_2,
                                    A.VL_COMMUNICATION_TIME_1 + A.VL_COMMUNICATION_TIME_2 AS VL_COMMUNICATION_TIME,
                                    A.VL_ADDITIONAL_TIME_1,
                                    A.VL_ADDITIONAL_TIME_2,
                                    A.VL_ADDITIONAL_TIME_1 + A.VL_ADDITIONAL_TIME_2 AS VL_ADDITIONAL_TIME,
                                    (A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC + A.VL_ADDITIONAL_TIME_1 + A.VL_ADDITIONAL_TIME_2) AS VL_INTRA_TASK_EXECUTION_TIME_FREE_ADDITIONAL,
                                    A.DT_PROCESSING,
                                    --B.ID_PARAMETER,
                                    B.CD_PARAMETER,
                                    B.CD_CONFIGURATION,
                                    B.ID_ALGORITHM,
                                    (SELECT DISTINCT X.DS_ALGORITHM FROM ALGORITHM X WHERE X.ID_ALGORITHM = B.ID_ALGORITHM) AS DS_ALGORITHM,
                                    B.ID_FUNCTION,
                                    (SELECT DISTINCT X.DS_FUNCTION FROM FUNCTION X WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS DS_FUNCTION,
                                    (SELECT DISTINCT Y.ID_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS ID_DEVICE,
                                    (SELECT DISTINCT Y.DS_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS DS_DEVICE,
                                    B.ID_DATASET,
                                    B.ID_RESOURCE,
                                    B.ID_PARAMETER_TYPE,
                                    (SELECT X.DS_PARAMETER_TYPE FROM PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) AS DS_PARAMETER_TYPE,
                                    (SELECT X.DS_PARAMETER_ATTRIBUTE FROM PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) AS DS_PARAMETER_ATTRIBUTE,
                                    B.NR_ITERATIONS,
                                    B.VL_GRID_ROW_DIMENSION,
                                    B.VL_GRID_COLUMN_DIMENSION,
                                    B.VL_GRID_ROW_DIMENSION || ' x ' || B.VL_GRID_COLUMN_DIMENSION AS VL_GRID_ROW_X_COLUMN_DIMENSION,
                                    B.VL_GRID_ROW_DIMENSION || ' x ' || B.VL_GRID_COLUMN_DIMENSION || ' (' || ROUND(B.VL_BLOCK_MEMORY_SIZE*1e-6,0) || ')' AS VL_CONCAT_GRID_ROW_X_COLUMN_DIMENSION_BLOCK_SIZE_MB,
									ROUND((CAST(B.VL_GRID_COLUMN_DIMENSION AS NUMERIC)/CAST(D.VL_DATASET_COLUMN_DIMENSION AS NUMERIC))*100,2) AS VL_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                    B.VL_GRID_ROW_DIMENSION || ' x ' || B.VL_GRID_COLUMN_DIMENSION || ' (' || ROUND((CAST(B.VL_GRID_COLUMN_DIMENSION AS NUMERIC)/CAST(D.VL_DATASET_COLUMN_DIMENSION AS NUMERIC))*100,2) || '%)' AS VL_CONCAT_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                    B.VL_BLOCK_ROW_DIMENSION,
                                    B.VL_BLOCK_COLUMN_DIMENSION,
                                    B.VL_BLOCK_ROW_DIMENSION || ' x ' || B.VL_BLOCK_COLUMN_DIMENSION AS VL_BLOCK_ROW_X_COLUMN_DIMENSION,
                                    B.VL_BLOCK_MEMORY_SIZE,
                                    B.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                                    B.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                                    ROUND((CAST(B.VL_BLOCK_MEMORY_SIZE AS NUMERIC)/CAST(D.VL_DATASET_MEMORY_SIZE AS NUMERIC))*100,2) AS VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                    ROUND(B.VL_BLOCK_MEMORY_SIZE*1e-6,2) || ' (' || ROUND((CAST(B.VL_BLOCK_MEMORY_SIZE AS NUMERIC)/CAST(D.VL_DATASET_MEMORY_SIZE AS NUMERIC))*100,2) || '%)' AS VL_CONCAT_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                    C.DS_RESOURCE,
                                    C.NR_NODES,
                                    C.NR_COMPUTING_UNITS_CPU,
                                    C.NR_COMPUTING_UNITS_GPU,
                                    C.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                                    C.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
                                    D.DS_DATASET,
                                    D.VL_DATASET_MEMORY_SIZE,
                                    D.DS_DATA_TYPE,
                                    D.VL_DATA_TYPE_MEMORY_SIZE,
                                    D.VL_DATASET_DIMENSION,
                                    D.VL_DATASET_ROW_DIMENSION,
                                    D.VL_DATASET_COLUMN_DIMENSION,
                                    D.VL_DATASET_ROW_DIMENSION || ' x ' || D.VL_DATASET_COLUMN_DIMENSION AS VL_DATASET_ROW_X_COLUMN_DIMENSION,
                                    D.NR_RANDOM_STATE
                                FROM EXPERIMENT_RAW A
                                INNER JOIN PARAMETER B ON (A.ID_PARAMETER = B.ID_PARAMETER)
                                INNER JOIN RESOURCE C ON (B.ID_RESOURCE = C.ID_RESOURCE)
                                INNER JOIN DATASET D ON (B.ID_DATASET = D.ID_DATASET)
                                WHERE
                                --AND A.ID_EXPERIMENT NOT IN (776778, 776777, 776780, 776779, 776776, 776794, 776793, 776795, 776792, 776791, 776784) --FILTERING OUTLIERS KMEANS EXTRA EXPERIMENTS
                                --AND A.ID_EXPERIMENT NOT IN (370685,362026,362018,362024,362037,362036,362028,362032,362029,362023,362052) --FILTERING OUTLIERS MATMUL EXTRA EXPERIMENTS
                                A.NR_ALGORITHM_ITERATION <> 0
                            ) X
                            GROUP BY
                            --X.ID_PARAMETER,
                            X.CD_PARAMETER,
                            X.CD_CONFIGURATION,
                            X.ID_ALGORITHM,
                            X.DS_ALGORITHM,
                            --X.ID_FUNCTION,
                            --X.DS_FUNCTION,
                            X.ID_DEVICE,
                            X.DS_DEVICE,
                            X.ID_DATASET,
                            X.ID_RESOURCE,
                            X.ID_PARAMETER_TYPE,
                            X.DS_PARAMETER_TYPE,
                            X.DS_PARAMETER_ATTRIBUTE,
                            X.NR_ITERATIONS,
                            X.VL_GRID_ROW_DIMENSION,
                            X.VL_GRID_COLUMN_DIMENSION,
                            X.VL_GRID_ROW_X_COLUMN_DIMENSION,
							X.VL_CONCAT_GRID_ROW_X_COLUMN_DIMENSION_BLOCK_SIZE_MB,
                            X.VL_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                            X.VL_CONCAT_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                            X.VL_BLOCK_ROW_DIMENSION,
                            X.VL_BLOCK_COLUMN_DIMENSION,
                            X.VL_BLOCK_ROW_X_COLUMN_DIMENSION,
                            X.VL_BLOCK_MEMORY_SIZE,
                            X.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                            X.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                            X.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                            X.VL_CONCAT_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                            X.DS_RESOURCE,
                            X.NR_NODES,
                            X.NR_COMPUTING_UNITS_CPU,
                            X.NR_COMPUTING_UNITS_GPU,
                            X.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                            X.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
                            X.DS_DATASET,
                            X.VL_DATASET_MEMORY_SIZE,
                            X.DS_DATA_TYPE,
                            X.VL_DATA_TYPE_MEMORY_SIZE,
                            X.VL_DATASET_DIMENSION,
                            X.VL_DATASET_ROW_DIMENSION,
                            X.VL_DATASET_COLUMN_DIMENSION,
                            X.VL_DATASET_ROW_X_COLUMN_DIMENSION,
                            X.NR_RANDOM_STATE
                        ) Y
		) ZZ
WHERE
ZZ.nr_iterations = 5
AND ZZ.ds_algorithm='KMEANS'
AND ZZ.ds_dataset = 'S_10GB_1'
AND ZZ.ds_parameter_type = 'VAR_GRID_ROW_5'
--AND ZZ.ds_algorithm='MATMUL_DISLIB'
----AND ZZ.ds_function = 'ADD_FUNC'
--AND ZZ.ds_dataset = 'S_8GB_1'
--AND ZZ.ds_parameter_type = 'VAR_GRID_SHAPE_MATMUL_1'
ORDER BY
DS_DEVICE,
VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
DS_ALGORITHM DESC


-- QUERY USED TO FILTER OUTLIERS (top 10 VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC for each ID parameter in GPU (warm up GPU for CUDA code, given that only one execution was made)) KMEANS AND MATMUL (ADDITIONAL EXPERIMENTS PAPER 1) - LARGER DATASETS
SELECT
                                    A.ID_EXPERIMENT,
                                    A.VL_TOTAL_EXECUTION_TIME,
                                    A.VL_INTER_TASK_EXECUTION_TIME,
                                    A.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                                    A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                                    A.VL_COMMUNICATION_TIME_1,
                                    A.VL_COMMUNICATION_TIME_2,
                                    A.VL_COMMUNICATION_TIME_1 + A.VL_COMMUNICATION_TIME_2 AS VL_COMMUNICATION_TIME,
                                    A.VL_ADDITIONAL_TIME_1,
                                    A.VL_ADDITIONAL_TIME_2,
                                    A.VL_ADDITIONAL_TIME_1 + A.VL_ADDITIONAL_TIME_2 AS VL_ADDITIONAL_TIME,
                                    (A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC + A.VL_ADDITIONAL_TIME_1 + A.VL_ADDITIONAL_TIME_2) AS VL_INTRA_TASK_EXECUTION_TIME_FREE_ADDITIONAL,
                                    A.DT_PROCESSING,
                                    --B.ID_PARAMETER,
                                    B.CD_PARAMETER,
                                    B.CD_CONFIGURATION,
                                    B.ID_ALGORITHM,
                                    (SELECT DISTINCT X.DS_ALGORITHM FROM ALGORITHM X WHERE X.ID_ALGORITHM = B.ID_ALGORITHM) AS DS_ALGORITHM,
                                    B.ID_FUNCTION,
                                    (SELECT DISTINCT X.DS_FUNCTION FROM FUNCTION X WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS DS_FUNCTION,
                                    (SELECT DISTINCT Y.ID_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS ID_DEVICE,
                                    (SELECT DISTINCT Y.DS_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS DS_DEVICE,
                                    B.ID_DATASET,
                                    B.ID_RESOURCE,
                                    B.ID_PARAMETER_TYPE,
                                    (SELECT X.DS_PARAMETER_TYPE FROM PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) AS DS_PARAMETER_TYPE,
                                    (SELECT X.DS_PARAMETER_ATTRIBUTE FROM PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) AS DS_PARAMETER_ATTRIBUTE,
                                    B.NR_ITERATIONS,
                                    B.VL_GRID_ROW_DIMENSION,
                                    B.VL_GRID_COLUMN_DIMENSION,
                                    B.VL_GRID_ROW_DIMENSION || ' x ' || B.VL_GRID_COLUMN_DIMENSION AS VL_GRID_ROW_X_COLUMN_DIMENSION,
                                    B.VL_GRID_ROW_DIMENSION || ' x ' || B.VL_GRID_COLUMN_DIMENSION || ' (' || ROUND(B.VL_BLOCK_MEMORY_SIZE*1e-6,0) || ')' AS VL_CONCAT_GRID_ROW_X_COLUMN_DIMENSION_BLOCK_SIZE_MB,
									ROUND((CAST(B.VL_GRID_COLUMN_DIMENSION AS NUMERIC)/CAST(D.VL_DATASET_COLUMN_DIMENSION AS NUMERIC))*100,2) AS VL_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                    B.VL_GRID_ROW_DIMENSION || ' x ' || B.VL_GRID_COLUMN_DIMENSION || ' (' || ROUND((CAST(B.VL_GRID_COLUMN_DIMENSION AS NUMERIC)/CAST(D.VL_DATASET_COLUMN_DIMENSION AS NUMERIC))*100,2) || '%)' AS VL_CONCAT_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                    B.VL_BLOCK_ROW_DIMENSION,
                                    B.VL_BLOCK_COLUMN_DIMENSION,
                                    B.VL_BLOCK_ROW_DIMENSION || ' x ' || B.VL_BLOCK_COLUMN_DIMENSION AS VL_BLOCK_ROW_X_COLUMN_DIMENSION,
                                    B.VL_BLOCK_MEMORY_SIZE,
                                    B.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                                    B.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                                    ROUND((CAST(B.VL_BLOCK_MEMORY_SIZE AS NUMERIC)/CAST(D.VL_DATASET_MEMORY_SIZE AS NUMERIC))*100,2) AS VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                    ROUND(B.VL_BLOCK_MEMORY_SIZE*1e-6,2) || ' (' || ROUND((CAST(B.VL_BLOCK_MEMORY_SIZE AS NUMERIC)/CAST(D.VL_DATASET_MEMORY_SIZE AS NUMERIC))*100,2) || '%)' AS VL_CONCAT_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                    C.DS_RESOURCE,
                                    C.NR_NODES,
                                    C.NR_COMPUTING_UNITS_CPU,
                                    C.NR_COMPUTING_UNITS_GPU,
                                    C.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                                    C.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
                                    D.DS_DATASET,
                                    D.VL_DATASET_MEMORY_SIZE,
                                    D.DS_DATA_TYPE,
                                    D.VL_DATA_TYPE_MEMORY_SIZE,
                                    D.VL_DATASET_DIMENSION,
                                    D.VL_DATASET_ROW_DIMENSION,
                                    D.VL_DATASET_COLUMN_DIMENSION,
                                    D.VL_DATASET_ROW_DIMENSION || ' x ' || D.VL_DATASET_COLUMN_DIMENSION AS VL_DATASET_ROW_X_COLUMN_DIMENSION,
                                    D.NR_RANDOM_STATE
                                FROM EXPERIMENT_RAW A
                                INNER JOIN PARAMETER B ON (A.ID_PARAMETER = B.ID_PARAMETER)
                                INNER JOIN RESOURCE C ON (B.ID_RESOURCE = C.ID_RESOURCE)
                                INNER JOIN DATASET D ON (B.ID_DATASET = D.ID_DATASET)
								WHERE
								--D.DS_DATASET = 'S_100GB_1'
								--AND (SELECT X.DS_PARAMETER_TYPE FROM PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) = 'VAR_GRID_ROW_5'
								--AND (SELECT DISTINCT Y.DS_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) = 'GPU'
								--AND A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC IS NOT NULL
                                ----AND B.VL_GRID_ROW_DIMENSION = 64--256,128,64,32,16
                                --AND A.ID_EXPERIMENT NOT IN (778235,778499,778234,778250,778251,778249,778248,778241,778240,778239) -- GRID ROW DIM 256
								--AND A.ID_EXPERIMENT NOT IN (791476,791478,791474,791498,791473,791614,791472,791471,791501,791613) -- GRID ROW DIM 128
								--AND A.ID_EXPERIMENT NOT IN (790508,790515,790496,790510,790517,790516,790518,790498,790497,790525) -- GRID ROW DIM 64
								--AND A.ID_EXPERIMENT NOT IN (776778,776777,776780,776779,776776,776794,776793,776795,776792,776791) -- GRID ROW DIM 32
								--AND A.ID_EXPERIMENT NOT IN (790087,790094,790086,790098,790100,790099,790096,790097,790149,790104) -- GRID ROW DIM 16
								--AND A.ID_EXPERIMENT NOT IN (776778, 776777, 776780, 776779, 776776, 776794, 776793, 776795, 776792, 776791, 776784) -- OLD IDS (NOT FILTERED ANYMORE)
								D.DS_DATASET = 'S_32GB_1'
								AND (SELECT X.DS_PARAMETER_TYPE FROM PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) = 'VAR_GRID_SHAPE_MATMUL_1'
								AND (SELECT DISTINCT Y.DS_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) = 'GPU'
								AND A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC IS NOT NULL
								AND B.VL_GRID_ROW_DIMENSION = 8--16,8,4
								--AND A.ID_EXPERIMENT NOT IN (370685,370675,370662,370681,370667,370670,370676,370652,370679,370669) -- GRID ROW DIM 16
								--AND A.ID_EXPERIMENT NOT IN (380224,380190,380234,380233,380206,380248,380156,380152,380151,380158) -- GRID ROW DIM 8
								--AND A.ID_EXPERIMENT NOT IN (362026,362018,362024,362037,362036,362028,362032,362029,362023,362052) -- GRID ROW DIM 4
								--AND A.ID_EXPERIMENT NOT IN (370685,362026,362018,362024,362037,362036,362028,362032,362029,362023,362052) -- OLD IDS (NOT FILTERED ANYMORE)
								ORDER BY A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC DESC




-- QUERY USED TO FILTER OUTLIERS (top 10 VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC for each ID parameter in GPU (warm up GPU for CUDA code, given that only one execution was made)) KMEANS (ADDITIONAL EXPERIMENTS PAPER 1) - SKEWED DATASETS
SELECT
		A.ID_EXPERIMENT,
		A.VL_TOTAL_EXECUTION_TIME,
		A.VL_INTER_TASK_EXECUTION_TIME,
		A.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
		A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
		A.VL_COMMUNICATION_TIME_1,
		A.VL_COMMUNICATION_TIME_2,
		A.VL_COMMUNICATION_TIME_1 + A.VL_COMMUNICATION_TIME_2 AS VL_COMMUNICATION_TIME,
		A.VL_ADDITIONAL_TIME_1,
		A.VL_ADDITIONAL_TIME_2,
		A.VL_ADDITIONAL_TIME_1 + A.VL_ADDITIONAL_TIME_2 AS VL_ADDITIONAL_TIME,
		(A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC + A.VL_ADDITIONAL_TIME_1 + A.VL_ADDITIONAL_TIME_2) AS VL_INTRA_TASK_EXECUTION_TIME_FREE_ADDITIONAL,
		A.DT_PROCESSING,
		--B.ID_PARAMETER,
		B.CD_PARAMETER,
		B.CD_CONFIGURATION,
		B.ID_ALGORITHM,
		(SELECT DISTINCT X.DS_ALGORITHM FROM ALGORITHM X WHERE X.ID_ALGORITHM = B.ID_ALGORITHM) AS DS_ALGORITHM,
		B.ID_FUNCTION,
		(SELECT DISTINCT X.DS_FUNCTION FROM FUNCTION X WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS DS_FUNCTION,
		(SELECT DISTINCT Y.ID_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS ID_DEVICE,
		(SELECT DISTINCT Y.DS_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS DS_DEVICE,
		B.ID_DATASET,
		B.ID_RESOURCE,
		B.ID_PARAMETER_TYPE,
		(SELECT X.DS_PARAMETER_TYPE FROM PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) AS DS_PARAMETER_TYPE,
		(SELECT X.DS_PARAMETER_ATTRIBUTE FROM PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) AS DS_PARAMETER_ATTRIBUTE,
		B.NR_ITERATIONS,
		B.VL_GRID_ROW_DIMENSION,
		B.VL_GRID_COLUMN_DIMENSION,
		B.VL_GRID_ROW_DIMENSION || ' x ' || B.VL_GRID_COLUMN_DIMENSION AS VL_GRID_ROW_X_COLUMN_DIMENSION,
		B.VL_GRID_ROW_DIMENSION || ' x ' || B.VL_GRID_COLUMN_DIMENSION || ' (' || ROUND(B.VL_BLOCK_MEMORY_SIZE*1e-6,0) || ')' AS VL_CONCAT_GRID_ROW_X_COLUMN_DIMENSION_BLOCK_SIZE_MB,
		ROUND((CAST(B.VL_GRID_COLUMN_DIMENSION AS NUMERIC)/CAST(D.VL_DATASET_COLUMN_DIMENSION AS NUMERIC))*100,2) AS VL_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
		B.VL_GRID_ROW_DIMENSION || ' x ' || B.VL_GRID_COLUMN_DIMENSION || ' (' || ROUND((CAST(B.VL_GRID_COLUMN_DIMENSION AS NUMERIC)/CAST(D.VL_DATASET_COLUMN_DIMENSION AS NUMERIC))*100,2) || '%)' AS VL_CONCAT_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
		B.VL_BLOCK_ROW_DIMENSION,
		B.VL_BLOCK_COLUMN_DIMENSION,
		B.VL_BLOCK_ROW_DIMENSION || ' x ' || B.VL_BLOCK_COLUMN_DIMENSION AS VL_BLOCK_ROW_X_COLUMN_DIMENSION,
		B.VL_BLOCK_MEMORY_SIZE,
		B.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
		B.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
		ROUND((CAST(B.VL_BLOCK_MEMORY_SIZE AS NUMERIC)/CAST(D.VL_DATASET_MEMORY_SIZE AS NUMERIC))*100,2) AS VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
		ROUND(B.VL_BLOCK_MEMORY_SIZE*1e-6,2) || ' (' || ROUND((CAST(B.VL_BLOCK_MEMORY_SIZE AS NUMERIC)/CAST(D.VL_DATASET_MEMORY_SIZE AS NUMERIC))*100,2) || '%)' AS VL_CONCAT_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
		C.DS_RESOURCE,
		C.NR_NODES,
		C.NR_COMPUTING_UNITS_CPU,
		C.NR_COMPUTING_UNITS_GPU,
		C.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
		C.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
		D.DS_DATASET,
		D.VL_DATASET_MEMORY_SIZE,
		D.DS_DATA_TYPE,
		D.VL_DATA_TYPE_MEMORY_SIZE,
		D.VL_DATASET_DIMENSION,
		D.VL_DATASET_ROW_DIMENSION,
		D.VL_DATASET_COLUMN_DIMENSION,
		D.VL_DATASET_ROW_DIMENSION || ' x ' || D.VL_DATASET_COLUMN_DIMENSION AS VL_DATASET_ROW_X_COLUMN_DIMENSION,
		D.NR_RANDOM_STATE
	FROM EXPERIMENT_RAW A
	INNER JOIN PARAMETER B ON (A.ID_PARAMETER = B.ID_PARAMETER)
	INNER JOIN RESOURCE C ON (B.ID_RESOURCE = C.ID_RESOURCE)
	INNER JOIN DATASET D ON (B.ID_DATASET = D.ID_DATASET)
	WHERE
	D.DS_DATASET = 'S_2GB_3'
	AND (SELECT X.DS_PARAMETER_TYPE FROM PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) = 'VAR_GRID_SHAPE_MATMUL_1'
	AND (SELECT DISTINCT Y.DS_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) = 'GPU'
	AND A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC IS NOT NULL
	AND B.VL_GRID_ROW_DIMENSION = 16
	--MATMUL
	--AND A.ID_EXPERIMENT NOT IN () -- GRID ROW DIM 1 SKEWED ('S_2GB_1') -- NO NEED TO FILTER (ONLY ONE TASK)
	--AND A.ID_EXPERIMENT NOT IN () -- GRID ROW DIM 1 NOT SKEWED ('S_2GB_3') -- NO NEED TO FILTER (ONLY ONE TASK)
	--AND A.ID_EXPERIMENT NOT IN () -- GRID ROW DIM 2 SKEWED ('S_2GB_1')
	--AND A.ID_EXPERIMENT NOT IN (381272) -- GRID ROW DIM 2 NOT SKEWED ('S_2GB_3')
	--AND A.ID_EXPERIMENT NOT IN () -- GRID ROW DIM 4 SKEWED ('S_2GB_1')
	--AND A.ID_EXPERIMENT NOT IN (381470,381469,381512,381472,381511,381513,381441,381444,381442,381501) -- GRID ROW DIM 4 NOT SKEWED ('S_2GB_3')
	--AND A.ID_EXPERIMENT NOT IN () -- GRID ROW DIM 8 SKEWED ('S_2GB_1')
	--AND A.ID_EXPERIMENT NOT IN (382730,382750,382694,382666,382699,382679,382674,382718,382685,382697) -- GRID ROW DIM 8 NOT SKEWED ('S_2GB_3')
	--AND A.ID_EXPERIMENT NOT IN () -- GRID ROW DIM 16 SKEWED ('S_2GB_1')
	--AND A.ID_EXPERIMENT NOT IN (392241,392315,392316,392331,392285,392358,392250,392249,392244,392246) -- GRID ROW DIM 16 NOT SKEWED ('S_2GB_3')
	--KMEANS
	--AND A.ID_EXPERIMENT NOT IN () -- GRID ROW DIM 1 SKEWED ('S_1GB_1') -- NO NEED TO FILTER (ONLY ONE TASK)
	--AND A.ID_EXPERIMENT NOT IN () -- GRID ROW DIM 1 NOT SKEWED ('S_1GB_3') -- NO NEED TO FILTER (ONLY ONE TASK)
	--AND A.ID_EXPERIMENT NOT IN (784797,784799,784798) -- GRID ROW DIM 2 SKEWED ('S_1GB_1')
	--AND A.ID_EXPERIMENT NOT IN (779557,779558,779559) -- GRID ROW DIM 2 NOT SKEWED ('S_1GB_3')
	--AND A.ID_EXPERIMENT NOT IN (784838,784839,784836,784845,784837,784847,784844) -- GRID ROW DIM 4 SKEWED ('S_1GB_1')
	--AND A.ID_EXPERIMENT NOT IN (779598,779599,779609,779614,779610,779597,779604) -- GRID ROW DIM 4 NOT SKEWED ('S_1GB_3')
	--AND A.ID_EXPERIMENT NOT IN (784911,784913,784912,784910,784909,784908,784944,784929,784928,784938) -- GRID ROW DIM 8 SKEWED ('S_1GB_1')
	--AND A.ID_EXPERIMENT NOT IN (779672,779671,779673,779670,779668,779669,779667,779676,779683,779677) -- GRID ROW DIM 8 NOT SKEWED ('S_1GB_3')
	--AND A.ID_EXPERIMENT NOT IN (785049,785048,785046,785047,785038,785039,785057,785095,785067,785060) -- GRID ROW DIM 16 SKEWED ('S_1GB_1')
	--AND A.ID_EXPERIMENT NOT IN (779805,779807,779806,779810,779811,779808,779809,779800,779799,779798) -- GRID ROW DIM 16 NOT SKEWED ('S_1GB_3')
	--AND A.ID_EXPERIMENT NOT IN (785321,785320,785323,785322,785310,785309,785311,785308,785317,785318) -- GRID ROW DIM 32 SKEWED ('S_1GB_1')
	--AND A.ID_EXPERIMENT NOT IN (780079,780078,780074,780075,780076,780077,780083,780082,780081,780080) -- GRID ROW DIM 32 NOT SKEWED ('S_1GB_3')
	--AND A.ID_EXPERIMENT NOT IN (785827,785832,785825,785826,785828,785834,785824,785823,786016,786080) -- GRID ROW DIM 64 SKEWED ('S_1GB_1')
	--AND A.ID_EXPERIMENT NOT IN (780603,780602,780607,780606,780601,780605,780568,780565,780589,780567) -- GRID ROW DIM 64 NOT SKEWED ('S_1GB_3')
	--AND A.ID_EXPERIMENT NOT IN (786781,786784,786780,786783,786793,786827,786812,786807,786808,786803) -- GRID ROW DIM 128 SKEWED ('S_1GB_1')
	--AND A.ID_EXPERIMENT NOT IN (781551,781549,781548,781544,781545,781541,781546,781540,781562,781542) -- GRID ROW DIM 128 NOT SKEWED ('S_1GB_3')
	--AND A.ID_EXPERIMENT NOT IN (788843,788847,788728,788729,788735,788734,788739,788738,788727,788733) -- GRID ROW DIM 256 SKEWED ('S_1GB_1')
	--AND A.ID_EXPERIMENT NOT IN () -- GRID ROW DIM 256 NOT SKEWED ('S_1GB_3')
	ORDER BY A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC DESC
	
	










--###################### QUERY EXPERIMENT 2
WITH T_CPU AS (
                                    SELECT
                                    A.VL_TOTAL_EXECUTION_TIME,
                                    A.VL_INTER_TASK_EXECUTION_TIME,
                                    A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                                    A.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
									0 AS VL_COMMUNICATION_TIME_1,
									0 AS VL_COMMUNICATION_TIME_2,
                                    A.VL_COMMUNICATION_TIME,
									A.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC-(A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC + A.VL_COMMUNICATION_TIME) AS VL_ADDITIONAL_TIME,
                                    B.ID_PARAMETER,
                                    B.CD_PARAMETER,
                                    B.CD_CONFIGURATION,
                                    B.ID_ALGORITHM,
                                    (SELECT DISTINCT X.DS_ALGORITHM FROM ALGORITHM X WHERE X.ID_ALGORITHM = B.ID_ALGORITHM) AS DS_ALGORITHM,
                                    B.ID_FUNCTION,
                                    (SELECT DISTINCT X.DS_FUNCTION FROM FUNCTION X WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS DS_FUNCTION,
                                    (SELECT DISTINCT Y.ID_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS ID_DEVICE,
                                    (SELECT DISTINCT Y.DS_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS DS_DEVICE,
                                    B.ID_DATASET,
                                    B.ID_RESOURCE,
                                    B.ID_PARAMETER_TYPE,
                                    (SELECT X.DS_PARAMETER_TYPE FROM PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) AS DS_PARAMETER_TYPE,
                                    (SELECT X.DS_PARAMETER_ATTRIBUTE FROM PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) AS DS_PARAMETER_ATTRIBUTE,
                                    B.NR_ITERATIONS,
                                    B.VL_GRID_ROW_DIMENSION,
                                    B.VL_GRID_COLUMN_DIMENSION,
                                    B.VL_BLOCK_ROW_DIMENSION,
                                    B.VL_BLOCK_COLUMN_DIMENSION,
                                    B.VL_BLOCK_MEMORY_SIZE,
                                    B.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                                    B.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                                    ROUND((CAST(B.VL_BLOCK_MEMORY_SIZE AS NUMERIC)/CAST(D.VL_DATASET_MEMORY_SIZE AS NUMERIC))*100,2) AS VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                    C.DS_RESOURCE,
                                    C.NR_NODES,
                                    C.NR_COMPUTING_UNITS_CPU,
                                    C.NR_COMPUTING_UNITS_GPU,
                                    C.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                                    C.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
									(C.NR_NODES-1) || ' (' || (C.NR_NODES-1)*C.NR_COMPUTING_UNITS_CPU || ';' || (C.NR_NODES-1)*4 || ')' AS NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU_GPU,
                                    D.DS_DATASET,
                                    D.VL_DATASET_MEMORY_SIZE,
                                    D.DS_DATA_TYPE,
                                    D.VL_DATA_TYPE_MEMORY_SIZE,
                                    D.VL_DATASET_DIMENSION,
                                    D.VL_DATASET_ROW_DIMENSION,
                                    D.VL_DATASET_COLUMN_DIMENSION,
                                    D.NR_RANDOM_STATE
                                FROM EXPERIMENT A
                                INNER JOIN PARAMETER B ON (A.ID_PARAMETER = B.ID_PARAMETER)
                                INNER JOIN RESOURCE C ON (B.ID_RESOURCE = C.ID_RESOURCE)
                                INNER JOIN DATASET D ON (B.ID_DATASET = D.ID_DATASET)
                                WHERE
                                (SELECT DISTINCT Y.DS_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) = 'CPU'
                                
                                UNION ALL
                        
                                    SELECT
                                    Y.VL_TOTAL_EXECUTION_TIME,
                                    Y.VL_INTER_TASK_EXECUTION_TIME,
                                    Y.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                                    Y.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
									Y.VL_COMMUNICATION_TIME_1 AS VL_COMMUNICATION_TIME_1,
									Y.VL_COMMUNICATION_TIME_2 AS VL_COMMUNICATION_TIME_2,
                                    Y.VL_COMMUNICATION_TIME,
                                    Y.VL_ADDITIONAL_TIME,
                                    Y.ID_PARAMETER,
                                    Y.CD_PARAMETER,
                                    Y.CD_CONFIGURATION,
                                    Y.ID_ALGORITHM,
                                    Y.DS_ALGORITHM,
                                    Y.ID_FUNCTION,
                                    Y.DS_FUNCTION,
                                    Y.ID_DEVICE,
                                    Y.DS_DEVICE,
                                    Y.ID_DATASET,
                                    Y.ID_RESOURCE,
                                    Y.ID_PARAMETER_TYPE,
                                    Y.DS_PARAMETER_TYPE,
                                    Y.DS_PARAMETER_ATTRIBUTE,
                                    Y.NR_ITERATIONS,
                                    Y.VL_GRID_ROW_DIMENSION,
                                    Y.VL_GRID_COLUMN_DIMENSION,
                                    Y.VL_BLOCK_ROW_DIMENSION,
                                    Y.VL_BLOCK_COLUMN_DIMENSION,
                                    Y.VL_BLOCK_MEMORY_SIZE,
                                    Y.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                                    Y.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                                    Y.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                    Y.DS_RESOURCE,
                                    Y.NR_NODES,
                                    Y.NR_COMPUTING_UNITS_CPU,
                                    Y.NR_COMPUTING_UNITS_GPU,
                                    Y.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                                    Y.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
									Y.NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU_GPU,
                                    Y.DS_DATASET,
                                    Y.VL_DATASET_MEMORY_SIZE,
                                    Y.DS_DATA_TYPE,
                                    Y.VL_DATA_TYPE_MEMORY_SIZE,
                                    Y.VL_DATASET_DIMENSION,
                                    Y.VL_DATASET_ROW_DIMENSION,
                                    Y.VL_DATASET_COLUMN_DIMENSION,
                                    Y.NR_RANDOM_STATE
                                    FROM
                                    (
                                        SELECT
                                        AVG(X.VL_TOTAL_EXECUTION_TIME) AS VL_TOTAL_EXECUTION_TIME,
                                        AVG(X.VL_INTER_TASK_EXECUTION_TIME) AS VL_INTER_TASK_EXECUTION_TIME,
                                        AVG(X.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC) AS VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                                        AVG(X.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC) AS VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                                        AVG(X.VL_COMMUNICATION_TIME_1) AS VL_COMMUNICATION_TIME_1,
                                        AVG(X.VL_COMMUNICATION_TIME_2) AS VL_COMMUNICATION_TIME_2,
                                        AVG(X.VL_COMMUNICATION_TIME) AS VL_COMMUNICATION_TIME,
                                        AVG(X.VL_ADDITIONAL_TIME_1) AS VL_ADDITIONAL_TIME_1,
                                        AVG(X.VL_ADDITIONAL_TIME_2) AS VL_ADDITIONAL_TIME_2,
                                        AVG(X.VL_ADDITIONAL_TIME) AS VL_ADDITIONAL_TIME,
                                        X.ID_PARAMETER,
                                        X.CD_PARAMETER,
                                        X.CD_CONFIGURATION,
                                        X.ID_ALGORITHM,
                                        X.DS_ALGORITHM,
                                        X.ID_FUNCTION,
                                        X.DS_FUNCTION,
                                        X.ID_DEVICE,
                                        X.DS_DEVICE,
                                        X.ID_DATASET,
                                        X.ID_RESOURCE,
                                        X.ID_PARAMETER_TYPE,
                                        X.DS_PARAMETER_TYPE,
                                        X.DS_PARAMETER_ATTRIBUTE,
                                        X.NR_ITERATIONS,
                                        X.VL_GRID_ROW_DIMENSION,
                                        X.VL_GRID_COLUMN_DIMENSION,
                                        X.VL_GRID_ROW_X_COLUMN_DIMENSION,
                                        X.VL_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                        X.VL_CONCAT_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                        X.VL_BLOCK_ROW_DIMENSION,
                                        X.VL_BLOCK_COLUMN_DIMENSION,
                                        X.VL_BLOCK_ROW_X_COLUMN_DIMENSION,
                                        X.VL_BLOCK_MEMORY_SIZE,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                        X.VL_CONCAT_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                        X.DS_RESOURCE,
                                        X.NR_NODES,
                                        X.NR_COMPUTING_UNITS_CPU,
                                        X.NR_COMPUTING_UNITS_GPU,
                                        X.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                                        X.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
										X.NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU_GPU,
                                        X.DS_DATASET,
                                        X.VL_DATASET_MEMORY_SIZE,
                                        X.DS_DATA_TYPE,
                                        X.VL_DATA_TYPE_MEMORY_SIZE,
                                        X.VL_DATASET_DIMENSION,
                                        X.VL_DATASET_ROW_DIMENSION,
                                        X.VL_DATASET_COLUMN_DIMENSION,
                                        X.VL_DATASET_ROW_X_COLUMN_DIMENSION,
                                        X.NR_RANDOM_STATE
                                        FROM
                                        (
                                            SELECT
                                                A.ID_EXPERIMENT,
                                                A.VL_TOTAL_EXECUTION_TIME,
                                                A.VL_INTER_TASK_EXECUTION_TIME,
                                                A.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                                                A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                                                A.VL_COMMUNICATION_TIME_1,
                                                A.VL_COMMUNICATION_TIME_2,
                                                A.VL_COMMUNICATION_TIME_1 + A.VL_COMMUNICATION_TIME_2 AS VL_COMMUNICATION_TIME,
                                                A.VL_ADDITIONAL_TIME_1,
                                                A.VL_ADDITIONAL_TIME_2,
                                                A.VL_ADDITIONAL_TIME_1 + A.VL_ADDITIONAL_TIME_2 AS VL_ADDITIONAL_TIME,
                                                A.DT_PROCESSING,
                                                B.ID_PARAMETER,
                                                B.CD_PARAMETER,
                                                B.CD_CONFIGURATION,
                                                B.ID_ALGORITHM,
                                                (SELECT DISTINCT X.DS_ALGORITHM FROM ALGORITHM X WHERE X.ID_ALGORITHM = B.ID_ALGORITHM) AS DS_ALGORITHM,
                                                B.ID_FUNCTION,
                                                (SELECT DISTINCT X.DS_FUNCTION FROM FUNCTION X WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS DS_FUNCTION,
                                                (SELECT DISTINCT Y.ID_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS ID_DEVICE,
                                                (SELECT DISTINCT Y.DS_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS DS_DEVICE,
                                                B.ID_DATASET,
                                                B.ID_RESOURCE,
                                                B.ID_PARAMETER_TYPE,
                                                (SELECT X.DS_PARAMETER_TYPE FROM PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) AS DS_PARAMETER_TYPE,
                                                (SELECT X.DS_PARAMETER_ATTRIBUTE FROM PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) AS DS_PARAMETER_ATTRIBUTE,
                                                B.NR_ITERATIONS,
                                                B.VL_GRID_ROW_DIMENSION,
                                                B.VL_GRID_COLUMN_DIMENSION,
                                                B.VL_GRID_ROW_DIMENSION || ' x ' || B.VL_GRID_COLUMN_DIMENSION AS VL_GRID_ROW_X_COLUMN_DIMENSION,
                                                ROUND((CAST(B.VL_GRID_COLUMN_DIMENSION AS NUMERIC)/CAST(D.VL_DATASET_COLUMN_DIMENSION AS NUMERIC))*100,2) AS VL_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                                B.VL_GRID_ROW_DIMENSION || ' x ' || B.VL_GRID_COLUMN_DIMENSION || ' (' || ROUND((CAST(B.VL_GRID_COLUMN_DIMENSION AS NUMERIC)/CAST(D.VL_DATASET_COLUMN_DIMENSION AS NUMERIC))*100,2) || '%)' AS VL_CONCAT_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                                B.VL_BLOCK_ROW_DIMENSION,
                                                B.VL_BLOCK_COLUMN_DIMENSION,
                                                B.VL_BLOCK_ROW_DIMENSION || ' x ' || B.VL_BLOCK_COLUMN_DIMENSION AS VL_BLOCK_ROW_X_COLUMN_DIMENSION,
                                                B.VL_BLOCK_MEMORY_SIZE,
                                                B.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                                                B.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                                                ROUND((CAST(B.VL_BLOCK_MEMORY_SIZE AS NUMERIC)/CAST(D.VL_DATASET_MEMORY_SIZE AS NUMERIC))*100,2) AS VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                                ROUND(B.VL_BLOCK_MEMORY_SIZE*1e-6,2) || ' (' || ROUND((CAST(B.VL_BLOCK_MEMORY_SIZE AS NUMERIC)/CAST(D.VL_DATASET_MEMORY_SIZE AS NUMERIC))*100,2) || '%)' AS VL_CONCAT_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                                C.DS_RESOURCE,
                                                C.NR_NODES,
                                                C.NR_COMPUTING_UNITS_CPU,
                                                C.NR_COMPUTING_UNITS_GPU,
                                                C.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                                                C.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
												(C.NR_NODES-1) || ' (' || (C.NR_NODES-1)*C.NR_COMPUTING_UNITS_CPU || ';' || (C.NR_NODES-1)*4 || ')' AS NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU_GPU,
                                                D.DS_DATASET,
                                                D.VL_DATASET_MEMORY_SIZE,
                                                D.DS_DATA_TYPE,
                                                D.VL_DATA_TYPE_MEMORY_SIZE,
                                                D.VL_DATASET_DIMENSION,
                                                D.VL_DATASET_ROW_DIMENSION,
                                                D.VL_DATASET_COLUMN_DIMENSION,
                                                D.VL_DATASET_ROW_DIMENSION || ' x ' || D.VL_DATASET_COLUMN_DIMENSION AS VL_DATASET_ROW_X_COLUMN_DIMENSION,
                                                D.NR_RANDOM_STATE
                                            FROM EXPERIMENT_RAW A
                                            INNER JOIN PARAMETER B ON (A.ID_PARAMETER = B.ID_PARAMETER)
                                            INNER JOIN RESOURCE C ON (B.ID_RESOURCE = C.ID_RESOURCE)
                                            INNER JOIN DATASET D ON (B.ID_DATASET = D.ID_DATASET)
                                            WHERE
                                            (SELECT DISTINCT Z.DS_DEVICE FROM FUNCTION W INNER JOIN DEVICE Z ON (W.ID_DEVICE = Z.ID_DEVICE) WHERE W.ID_FUNCTION = B.ID_FUNCTION) = 'CPU'
                                            AND A.NR_ALGORITHM_ITERATION <> 0
                                        ) X
										WHERE
										X.DS_FUNCTION = 'ADD_FUNC'--'MATMUL_FUNC'
                                        GROUP BY
                                        X.ID_PARAMETER,
                                        X.CD_PARAMETER,
                                        X.CD_CONFIGURATION,
                                        X.ID_ALGORITHM,
                                        X.DS_ALGORITHM,
                                        X.ID_FUNCTION,
                                        X.DS_FUNCTION,
                                        X.ID_DEVICE,
                                        X.DS_DEVICE,
                                        X.ID_DATASET,
                                        X.ID_RESOURCE,
                                        X.ID_PARAMETER_TYPE,
                                        X.DS_PARAMETER_TYPE,
                                        X.DS_PARAMETER_ATTRIBUTE,
                                        X.NR_ITERATIONS,
                                        X.VL_GRID_ROW_DIMENSION,
                                        X.VL_GRID_COLUMN_DIMENSION,
                                        X.VL_GRID_ROW_X_COLUMN_DIMENSION,
                                        X.VL_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                        X.VL_CONCAT_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                        X.VL_BLOCK_ROW_DIMENSION,
                                        X.VL_BLOCK_COLUMN_DIMENSION,
                                        X.VL_BLOCK_ROW_X_COLUMN_DIMENSION,
                                        X.VL_BLOCK_MEMORY_SIZE,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                        X.VL_CONCAT_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                        X.DS_RESOURCE,
                                        X.NR_NODES,
                                        X.NR_COMPUTING_UNITS_CPU,
                                        X.NR_COMPUTING_UNITS_GPU,
                                        X.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                                        X.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
										X.NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU_GPU,
                                        X.DS_DATASET,
                                        X.VL_DATASET_MEMORY_SIZE,
                                        X.DS_DATA_TYPE,
                                        X.VL_DATA_TYPE_MEMORY_SIZE,
                                        X.VL_DATASET_DIMENSION,
                                        X.VL_DATASET_ROW_DIMENSION,
                                        X.VL_DATASET_COLUMN_DIMENSION,
                                        X.VL_DATASET_ROW_X_COLUMN_DIMENSION,
                                        X.NR_RANDOM_STATE
                                    ) Y
                        
                                ),
                    T_GPU AS (
                                    SELECT
                                    A.VL_TOTAL_EXECUTION_TIME,
                                    A.VL_INTER_TASK_EXECUTION_TIME,
                                    A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                                    A.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
									0 AS VL_COMMUNICATION_TIME_1,
									0 AS VL_COMMUNICATION_TIME_2,
                                    A.VL_COMMUNICATION_TIME,
									A.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC-(A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC + A.VL_COMMUNICATION_TIME) AS VL_ADDITIONAL_TIME,
                                    B.ID_PARAMETER,
                                    B.CD_PARAMETER,
                                    B.CD_CONFIGURATION,
                                    B.ID_ALGORITHM,
                                    (SELECT DISTINCT X.DS_ALGORITHM FROM ALGORITHM X WHERE X.ID_ALGORITHM = B.ID_ALGORITHM) AS DS_ALGORITHM,
                                    B.ID_FUNCTION,
                                    (SELECT DISTINCT X.DS_FUNCTION FROM FUNCTION X WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS DS_FUNCTION,
                                    (SELECT DISTINCT Y.ID_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS ID_DEVICE,
                                    (SELECT DISTINCT Y.DS_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS DS_DEVICE,
                                    B.ID_DATASET,
                                    B.ID_RESOURCE,
                                    B.ID_PARAMETER_TYPE,
                                    (SELECT X.DS_PARAMETER_TYPE FROM PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) AS DS_PARAMETER_TYPE,
                                    (SELECT X.DS_PARAMETER_ATTRIBUTE FROM PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) AS DS_PARAMETER_ATTRIBUTE,
                                    B.NR_ITERATIONS,
                                    B.VL_GRID_ROW_DIMENSION,
                                    B.VL_GRID_COLUMN_DIMENSION,
                                    B.VL_BLOCK_ROW_DIMENSION,
                                    B.VL_BLOCK_COLUMN_DIMENSION,
                                    B.VL_BLOCK_MEMORY_SIZE,
                                    B.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                                    B.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                                    ROUND((CAST(B.VL_BLOCK_MEMORY_SIZE AS NUMERIC)/CAST(D.VL_DATASET_MEMORY_SIZE AS NUMERIC))*100,2) AS VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                    C.DS_RESOURCE,
                                    C.NR_NODES,
                                    C.NR_COMPUTING_UNITS_CPU,
                                    C.NR_COMPUTING_UNITS_GPU,
                                    C.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                                    C.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
									(C.NR_NODES-1) || ' (' || (C.NR_NODES-1)*C.NR_COMPUTING_UNITS_CPU || ';' || (C.NR_NODES-1)*4 || ')' AS NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU_GPU,
                                    D.DS_DATASET,
                                    D.VL_DATASET_MEMORY_SIZE,
                                    D.DS_DATA_TYPE,
                                    D.VL_DATA_TYPE_MEMORY_SIZE,
                                    D.VL_DATASET_DIMENSION,
                                    D.VL_DATASET_ROW_DIMENSION,
                                    D.VL_DATASET_COLUMN_DIMENSION,
                                    D.NR_RANDOM_STATE
                                    FROM EXPERIMENT A
                                    INNER JOIN PARAMETER B ON (A.ID_PARAMETER = B.ID_PARAMETER)
                                    INNER JOIN RESOURCE C ON (B.ID_RESOURCE = C.ID_RESOURCE)
                                    INNER JOIN DATASET D ON (B.ID_DATASET = D.ID_DATASET)
                                    WHERE
                                    (SELECT DISTINCT Y.DS_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) = 'GPU'
                            
                                UNION ALL
                        
                                    SELECT
                                    Y.VL_TOTAL_EXECUTION_TIME,
                                    Y.VL_INTER_TASK_EXECUTION_TIME,
                                    Y.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                                    Y.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
									Y.VL_COMMUNICATION_TIME_1 AS VL_COMMUNICATION_TIME_1,
									Y.VL_COMMUNICATION_TIME_2 AS VL_COMMUNICATION_TIME_2,
                                    Y.VL_COMMUNICATION_TIME,
                                    Y.VL_ADDITIONAL_TIME,
                                    Y.ID_PARAMETER,
                                    Y.CD_PARAMETER,
                                    Y.CD_CONFIGURATION,
                                    Y.ID_ALGORITHM,
                                    Y.DS_ALGORITHM,
                                    Y.ID_FUNCTION,
                                    Y.DS_FUNCTION,
                                    Y.ID_DEVICE,
                                    Y.DS_DEVICE,
                                    Y.ID_DATASET,
                                    Y.ID_RESOURCE,
                                    Y.ID_PARAMETER_TYPE,
                                    Y.DS_PARAMETER_TYPE,
                                    Y.DS_PARAMETER_ATTRIBUTE,
                                    Y.NR_ITERATIONS,
                                    Y.VL_GRID_ROW_DIMENSION,
                                    Y.VL_GRID_COLUMN_DIMENSION,
                                    Y.VL_BLOCK_ROW_DIMENSION,
                                    Y.VL_BLOCK_COLUMN_DIMENSION,
                                    Y.VL_BLOCK_MEMORY_SIZE,
                                    Y.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                                    Y.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                                    Y.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                    Y.DS_RESOURCE,
                                    Y.NR_NODES,
                                    Y.NR_COMPUTING_UNITS_CPU,
                                    Y.NR_COMPUTING_UNITS_GPU,
                                    Y.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                                    Y.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
									Y.NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU_GPU,
                                    Y.DS_DATASET,
                                    Y.VL_DATASET_MEMORY_SIZE,
                                    Y.DS_DATA_TYPE,
                                    Y.VL_DATA_TYPE_MEMORY_SIZE,
                                    Y.VL_DATASET_DIMENSION,
                                    Y.VL_DATASET_ROW_DIMENSION,
                                    Y.VL_DATASET_COLUMN_DIMENSION,
                                    Y.NR_RANDOM_STATE
                                    FROM
                                    (
                                        SELECT
                                        AVG(X.VL_TOTAL_EXECUTION_TIME) AS VL_TOTAL_EXECUTION_TIME,
                                        AVG(X.VL_INTER_TASK_EXECUTION_TIME) AS VL_INTER_TASK_EXECUTION_TIME,
                                        AVG(X.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC) AS VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                                        AVG(X.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC) AS VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                                        AVG(X.VL_COMMUNICATION_TIME_1) AS VL_COMMUNICATION_TIME_1,
                                        AVG(X.VL_COMMUNICATION_TIME_2) AS VL_COMMUNICATION_TIME_2,
                                        AVG(X.VL_COMMUNICATION_TIME) AS VL_COMMUNICATION_TIME,
                                        AVG(X.VL_ADDITIONAL_TIME_1) AS VL_ADDITIONAL_TIME_1,
                                        AVG(X.VL_ADDITIONAL_TIME_2) AS VL_ADDITIONAL_TIME_2,
                                        AVG(X.VL_ADDITIONAL_TIME) AS VL_ADDITIONAL_TIME,
                                        X.ID_PARAMETER,
                                        X.CD_PARAMETER,
                                        X.CD_CONFIGURATION,
                                        X.ID_ALGORITHM,
                                        X.DS_ALGORITHM,
                                        X.ID_FUNCTION,
                                        X.DS_FUNCTION,
                                        X.ID_DEVICE,
                                        X.DS_DEVICE,
                                        X.ID_DATASET,
                                        X.ID_RESOURCE,
                                        X.ID_PARAMETER_TYPE,
                                        X.DS_PARAMETER_TYPE,
                                        X.DS_PARAMETER_ATTRIBUTE,
                                        X.NR_ITERATIONS,
                                        X.VL_GRID_ROW_DIMENSION,
                                        X.VL_GRID_COLUMN_DIMENSION,
                                        X.VL_GRID_ROW_X_COLUMN_DIMENSION,
                                        X.VL_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                        X.VL_CONCAT_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                        X.VL_BLOCK_ROW_DIMENSION,
                                        X.VL_BLOCK_COLUMN_DIMENSION,
                                        X.VL_BLOCK_ROW_X_COLUMN_DIMENSION,
                                        X.VL_BLOCK_MEMORY_SIZE,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                        X.VL_CONCAT_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                        X.DS_RESOURCE,
                                        X.NR_NODES,
                                        X.NR_COMPUTING_UNITS_CPU,
                                        X.NR_COMPUTING_UNITS_GPU,
                                        X.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                                        X.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
										X.NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU_GPU,
                                        X.DS_DATASET,
                                        X.VL_DATASET_MEMORY_SIZE,
                                        X.DS_DATA_TYPE,
                                        X.VL_DATA_TYPE_MEMORY_SIZE,
                                        X.VL_DATASET_DIMENSION,
                                        X.VL_DATASET_ROW_DIMENSION,
                                        X.VL_DATASET_COLUMN_DIMENSION,
                                        X.VL_DATASET_ROW_X_COLUMN_DIMENSION,
                                        X.NR_RANDOM_STATE
                                        FROM
                                        (
                                            SELECT
                                                A.ID_EXPERIMENT,
                                                A.VL_TOTAL_EXECUTION_TIME,
                                                A.VL_INTER_TASK_EXECUTION_TIME,
                                                A.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                                                A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                                                A.VL_COMMUNICATION_TIME_1,
                                                A.VL_COMMUNICATION_TIME_2,
                                                A.VL_COMMUNICATION_TIME_1 + A.VL_COMMUNICATION_TIME_2 AS VL_COMMUNICATION_TIME,
                                                A.VL_ADDITIONAL_TIME_1,
                                                A.VL_ADDITIONAL_TIME_2,
                                                A.VL_ADDITIONAL_TIME_1 + A.VL_ADDITIONAL_TIME_2 AS VL_ADDITIONAL_TIME,
                                                A.DT_PROCESSING,
                                                B.ID_PARAMETER,
                                                B.CD_PARAMETER,
                                                B.CD_CONFIGURATION,
                                                B.ID_ALGORITHM,
                                                (SELECT DISTINCT X.DS_ALGORITHM FROM ALGORITHM X WHERE X.ID_ALGORITHM = B.ID_ALGORITHM) AS DS_ALGORITHM,
                                                B.ID_FUNCTION,
                                                (SELECT DISTINCT X.DS_FUNCTION FROM FUNCTION X WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS DS_FUNCTION,
                                                (SELECT DISTINCT Y.ID_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS ID_DEVICE,
                                                (SELECT DISTINCT Y.DS_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) AS DS_DEVICE,
                                                B.ID_DATASET,
                                                B.ID_RESOURCE,
                                                B.ID_PARAMETER_TYPE,
                                                (SELECT X.DS_PARAMETER_TYPE FROM PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) AS DS_PARAMETER_TYPE,
                                                (SELECT X.DS_PARAMETER_ATTRIBUTE FROM PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) AS DS_PARAMETER_ATTRIBUTE,
                                                B.NR_ITERATIONS,
                                                B.VL_GRID_ROW_DIMENSION,
                                                B.VL_GRID_COLUMN_DIMENSION,
                                                B.VL_GRID_ROW_DIMENSION || ' x ' || B.VL_GRID_COLUMN_DIMENSION AS VL_GRID_ROW_X_COLUMN_DIMENSION,
                                                ROUND((CAST(B.VL_GRID_COLUMN_DIMENSION AS NUMERIC)/CAST(D.VL_DATASET_COLUMN_DIMENSION AS NUMERIC))*100,2) AS VL_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                                B.VL_GRID_ROW_DIMENSION || ' x ' || B.VL_GRID_COLUMN_DIMENSION || ' (' || ROUND((CAST(B.VL_GRID_COLUMN_DIMENSION AS NUMERIC)/CAST(D.VL_DATASET_COLUMN_DIMENSION AS NUMERIC))*100,2) || '%)' AS VL_CONCAT_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                                B.VL_BLOCK_ROW_DIMENSION,
                                                B.VL_BLOCK_COLUMN_DIMENSION,
                                                B.VL_BLOCK_ROW_DIMENSION || ' x ' || B.VL_BLOCK_COLUMN_DIMENSION AS VL_BLOCK_ROW_X_COLUMN_DIMENSION,
                                                B.VL_BLOCK_MEMORY_SIZE,
                                                B.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                                                B.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                                                ROUND((CAST(B.VL_BLOCK_MEMORY_SIZE AS NUMERIC)/CAST(D.VL_DATASET_MEMORY_SIZE AS NUMERIC))*100,2) AS VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                                ROUND(B.VL_BLOCK_MEMORY_SIZE*1e-6,2) || ' (' || ROUND((CAST(B.VL_BLOCK_MEMORY_SIZE AS NUMERIC)/CAST(D.VL_DATASET_MEMORY_SIZE AS NUMERIC))*100,2) || '%)' AS VL_CONCAT_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                                C.DS_RESOURCE,
                                                C.NR_NODES,
                                                C.NR_COMPUTING_UNITS_CPU,
                                                C.NR_COMPUTING_UNITS_GPU,
                                                C.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                                                C.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
												(C.NR_NODES-1) || ' (' || (C.NR_NODES-1)*C.NR_COMPUTING_UNITS_CPU || ';' || (C.NR_NODES-1)*4 || ')' AS NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU_GPU,
                                                D.DS_DATASET,
                                                D.VL_DATASET_MEMORY_SIZE,
                                                D.DS_DATA_TYPE,
                                                D.VL_DATA_TYPE_MEMORY_SIZE,
                                                D.VL_DATASET_DIMENSION,
                                                D.VL_DATASET_ROW_DIMENSION,
                                                D.VL_DATASET_COLUMN_DIMENSION,
                                                D.VL_DATASET_ROW_DIMENSION || ' x ' || D.VL_DATASET_COLUMN_DIMENSION AS VL_DATASET_ROW_X_COLUMN_DIMENSION,
                                                D.NR_RANDOM_STATE
                                            FROM EXPERIMENT_RAW A
                                            INNER JOIN PARAMETER B ON (A.ID_PARAMETER = B.ID_PARAMETER)
                                            INNER JOIN RESOURCE C ON (B.ID_RESOURCE = C.ID_RESOURCE)
                                            INNER JOIN DATASET D ON (B.ID_DATASET = D.ID_DATASET)
                                            WHERE
                                            (SELECT DISTINCT Z.DS_DEVICE FROM FUNCTION W INNER JOIN DEVICE Z ON (W.ID_DEVICE = Z.ID_DEVICE) WHERE W.ID_FUNCTION = B.ID_FUNCTION) = 'GPU'
                                            AND A.NR_ALGORITHM_ITERATION <> 0
                                        ) X
										WHERE
										X.DS_FUNCTION = 'ADD_FUNC'--'MATMUL_FUNC'
                                        GROUP BY
                                        X.ID_PARAMETER,
                                        X.CD_PARAMETER,
                                        X.CD_CONFIGURATION,
                                        X.ID_ALGORITHM,
                                        X.DS_ALGORITHM,
                                        X.ID_FUNCTION,
                                        X.DS_FUNCTION,
                                        X.ID_DEVICE,
                                        X.DS_DEVICE,
                                        X.ID_DATASET,
                                        X.ID_RESOURCE,
                                        X.ID_PARAMETER_TYPE,
                                        X.DS_PARAMETER_TYPE,
                                        X.DS_PARAMETER_ATTRIBUTE,
                                        X.NR_ITERATIONS,
                                        X.VL_GRID_ROW_DIMENSION,
                                        X.VL_GRID_COLUMN_DIMENSION,
                                        X.VL_GRID_ROW_X_COLUMN_DIMENSION,
                                        X.VL_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                        X.VL_CONCAT_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                        X.VL_BLOCK_ROW_DIMENSION,
                                        X.VL_BLOCK_COLUMN_DIMENSION,
                                        X.VL_BLOCK_ROW_X_COLUMN_DIMENSION,
                                        X.VL_BLOCK_MEMORY_SIZE,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                                        X.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                        X.VL_CONCAT_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                        X.DS_RESOURCE,
                                        X.NR_NODES,
                                        X.NR_COMPUTING_UNITS_CPU,
                                        X.NR_COMPUTING_UNITS_GPU,
                                        X.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                                        X.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
										X.NR_CONCAT_NODES_TOTAL_COMPUTING_UNITS_CPU_GPU,
                                        X.DS_DATASET,
                                        X.VL_DATASET_MEMORY_SIZE,
                                        X.DS_DATA_TYPE,
                                        X.VL_DATA_TYPE_MEMORY_SIZE,
                                        X.VL_DATASET_DIMENSION,
                                        X.VL_DATASET_ROW_DIMENSION,
                                        X.VL_DATASET_COLUMN_DIMENSION,
                                        X.VL_DATASET_ROW_X_COLUMN_DIMENSION,
                                        X.NR_RANDOM_STATE
                                    ) Y
                    )
                    SELECT
                    T_CPU.DS_ALGORITHM,
					T_CPU.DS_FUNCTION,
					T_CPU.DS_PARAMETER_TYPE,
                    ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE*1e-6,0) as VL_BLOCK_MEMORY_SIZE_MB,
                    T_CPU.DS_DATASET,
					T_CPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC AS USER_CODE_CPU,
					T_CPU.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC AS PARALLEL_CODE_CPU,
					T_CPU.VL_COMMUNICATION_TIME_1 AS CPU_GPU_COMMUNICATION_CPU,
					T_CPU.VL_COMMUNICATION_TIME_2 AS GPU_CPU_COMMUNICATION_CPU,
					T_CPU.VL_COMMUNICATION_TIME AS TOTAL_COMMUNICATION_CPU,
					T_CPU.VL_ADDITIONAL_TIME AS SERIAL_CODE_CPU,

					T_GPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC AS USER_CODE_GPU,
					T_GPU.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC AS PARALLEL_CODE_GPU,
					T_GPU.VL_COMMUNICATION_TIME_1 AS CPU_GPU_COMMUNICATION_GPU,
					T_GPU.VL_COMMUNICATION_TIME_2 AS GPU_CPU_COMMUNICATION_GPU,
					T_GPU.VL_COMMUNICATION_TIME AS TOTAL_COMMUNICATION_GPU,
					T_GPU.VL_ADDITIONAL_TIME AS SERIAL_CODE_GPU,
                    CASE
                    WHEN (T_CPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC/T_GPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC) > 1.00 THEN (T_CPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC/T_GPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC)
                    ELSE -(T_GPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC/T_CPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC)
                    END AS SPEEDUP_GPU_USER_CODE
                    FROM T_CPU INNER JOIN T_GPU ON (T_CPU.CD_PARAMETER = T_GPU.CD_PARAMETER)
                    WHERE
                    T_CPU.VL_GRID_ROW_DIMENSION = T_GPU.VL_GRID_ROW_DIMENSION
                    AND T_CPU.VL_GRID_COLUMN_DIMENSION = T_GPU.VL_GRID_COLUMN_DIMENSION
                    AND T_CPU.VL_BLOCK_ROW_DIMENSION = T_GPU.VL_BLOCK_ROW_DIMENSION
                    AND T_CPU.VL_BLOCK_COLUMN_DIMENSION = T_GPU.VL_BLOCK_COLUMN_DIMENSION
					--AND T_CPU.DS_ALGORITHM = 'KMEANS'
					--AND T_CPU.DS_DATASET = 'S_10GB_1'
					--AND T_CPU.DS_PARAMETER_TYPE IN ('VAR_GRID_ROW_5','VAR_GRID_ROW_7')
					AND T_CPU.DS_ALGORITHM = 'MATMUL_DISLIB'
					AND T_CPU.DS_DATASET = 'S_8GB_1'
					AND T_CPU.DS_PARAMETER_TYPE = 'VAR_GRID_SHAPE_MATMUL_1'
                    ORDER BY
                    T_CPU.DS_DATASET,
                    T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET