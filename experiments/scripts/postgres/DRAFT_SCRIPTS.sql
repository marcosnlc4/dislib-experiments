CALL INSERT_DATA()
CALL DELETE_TABLES()

CALL CREATE_TABLES()
CALL DROP_TABLES()



SELECT * FROM DEVICE
SELECT * FROM FUNCTION
SELECT * FROM ALGORITHM
SELECT * FROM CONFIGURATION
SELECT * FROM RESOURCE
SELECT * FROM DATASET
SELECT * FROM PARAMETER_TYPE
SELECT * FROM PARAMETER
SELECT * FROM EXPERIMENT



-- PARAMETER QUERY
SELECT
	A.ID_PARAMETER,
	A.CD_PARAMETER,
	A.CD_CONFIGURATION,
	A.ID_ALGORITHM,
	(SELECT DISTINCT X.DS_ALGORITHM FROM ALGORITHM X WHERE X.ID_ALGORITHM = A.ID_ALGORITHM) AS DS_ALGORITHM,
	A.ID_FUNCTION,
	(SELECT DISTINCT X.DS_FUNCTION FROM FUNCTION X WHERE X.ID_FUNCTION = A.ID_FUNCTION) AS DS_FUNCTION,
	(SELECT DISTINCT Y.ID_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = A.ID_FUNCTION) AS ID_DEVICE,
	(SELECT DISTINCT Y.DS_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = A.ID_FUNCTION) AS DS_DEVICE,
	A.ID_DATASET,
	A.ID_RESOURCE,
	A.ID_PARAMETER_TYPE,
	(SELECT X.DS_PARAMETER_TYPE FROM PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = A.ID_PARAMETER_TYPE) AS DS_PARAMETER_TYPE,
	(SELECT X.DS_PARAMETER_ATTRIBUTE FROM PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = A.ID_PARAMETER_TYPE) AS DS_PARAMETER_ATTRIBUTE,
	A.NR_ITERATIONS,
	A.VL_GRID_ROW_DIMENSION,
	A.VL_GRID_COLUMN_DIMENSION,
	A.VL_BLOCK_ROW_DIMENSION,
	A.VL_BLOCK_COLUMN_DIMENSION,
	A.VL_BLOCK_MEMORY_SIZE,
	A.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
	A.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
	B.DS_RESOURCE,
	B.NR_NODES,
	B.NR_COMPUTING_UNITS_CPU,
	B.NR_COMPUTING_UNITS_GPU,
	B.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
	B.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
	C.DS_DATASET,
	C.VL_DATASET_MEMORY_SIZE,
	C.DS_DATA_TYPE,
	C.VL_DATA_TYPE_MEMORY_SIZE,
	C.VL_DATASET_DIMENSION,
	C.VL_DATASET_ROW_DIMENSION,
	C.VL_DATASET_COLUMN_DIMENSION,
	C.NR_RANDOM_STATE
FROM PARAMETER A
INNER JOIN RESOURCE B ON (A.ID_RESOURCE = B.ID_RESOURCE)
INNER JOIN DATASET C ON (A.ID_DATASET = C.ID_DATASET)
WHERE
(SELECT DISTINCT X.DS_ALGORITHM FROM ALGORITHM X WHERE X.ID_ALGORITHM = A.ID_ALGORITHM) = 'KMEANS' -- FIXED VALUE
AND A.NR_ITERATIONS = 5 -- FIXED VALUE
AND B.DS_RESOURCE = 'MINOTAURO_1' -- FIXED VALUE
AND (SELECT X.DS_PARAMETER_TYPE FROM PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = A.ID_PARAMETER_TYPE) = 'VAR_BLOCK_CAPACITY_SIZE' -- 1.1, 1.2, 1.3, 1.4
--AND (SELECT X.DS_PARAMETER_TYPE FROM PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = A.ID_PARAMETER_TYPE) = 'VAR_PARALLELISM_LEVEL' -- 2.1, 2.2
AND (SELECT X.DS_PARAMETER_ATTRIBUTE FROM PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = A.ID_PARAMETER_TYPE) = '0.25' -- 1.1
--AND (SELECT X.DS_PARAMETER_ATTRIBUTE FROM PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = A.ID_PARAMETER_TYPE) = '0.5' -- 1.2
--AND (SELECT X.DS_PARAMETER_ATTRIBUTE FROM PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = A.ID_PARAMETER_TYPE) = '0.75' -- 1.3
--AND (SELECT X.DS_PARAMETER_ATTRIBUTE FROM PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = A.ID_PARAMETER_TYPE) = '1' -- 1.4
--AND (SELECT X.DS_PARAMETER_ATTRIBUTE FROM PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = A.ID_PARAMETER_TYPE) = 'MIN_INTER_MAX_INTRA'--2.1
--AND (SELECT X.DS_PARAMETER_ATTRIBUTE FROM PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = A.ID_PARAMETER_TYPE) = 'MAX_INTER_MIN_INTRA'--2.2
ORDER BY A.ID_PARAMETER




-- EXPERIMENT QUERY
SELECT
	A.ID_EXPERIMENT,
	A.VL_TOTAL_EXECUTION_TIME,
	A.VL_INTER_TASK_EXECUTION_TIME,
	A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
	A.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
	A.VL_COMMUNICATION_TIME,
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
	B.VL_BLOCK_ROW_DIMENSION,
	B.VL_BLOCK_COLUMN_DIMENSION,
	B.VL_BLOCK_MEMORY_SIZE,
	B.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
	B.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
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
	D.NR_RANDOM_STATE
FROM EXPERIMENT A
INNER JOIN PARAMETER B ON (A.ID_PARAMETER = B.ID_PARAMETER)
INNER JOIN RESOURCE C ON (B.ID_RESOURCE = C.ID_RESOURCE)
INNER JOIN DATASET D ON (B.ID_DATASET = D.ID_DATASET)
ORDER BY A.ID_PARAMETER;



-- EXPERIMENT QUERIES
-- MODE 1: BEHAVIOR OF DEVICES ACCORDING TO DATA SET MEMORY SIZE
SELECT
--SBQ.DS_DATASET,
SBQ.DS_DEVICE,
SBQ.VL_DATASET_MEMORY_SIZE,
AVG(SBQ.VL_TOTAL_EXECUTION_TIME) AS AVG_VL_TOTAL_EXECUTION_TIME,
AVG(SBQ.VL_INTER_TASK_EXECUTION_TIME) AS AVG_VL_INTER_TASK_EXECUTION_TIME,
AVG(SBQ.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC) AS AVG_VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
AVG(SBQ.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC) AS AVG_VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
AVG(SBQ.VL_COMMUNICATION_TIME) AS AVG_VL_COMMUNICATION_TIME
FROM
(
			SELECT
			A.ID_EXPERIMENT,
			A.VL_TOTAL_EXECUTION_TIME,
			A.VL_INTER_TASK_EXECUTION_TIME,
			A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
			A.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
			A.VL_COMMUNICATION_TIME,
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
			B.VL_BLOCK_ROW_DIMENSION,
			B.VL_BLOCK_COLUMN_DIMENSION,
			B.VL_BLOCK_MEMORY_SIZE,
			B.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
			B.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
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
			D.NR_RANDOM_STATE
		FROM EXPERIMENT A
		INNER JOIN PARAMETER B ON (A.ID_PARAMETER = B.ID_PARAMETER)
		INNER JOIN RESOURCE C ON (B.ID_RESOURCE = C.ID_RESOURCE)
		INNER JOIN DATASET D ON (B.ID_DATASET = D.ID_DATASET)
) SBQ
GROUP BY
--SBQ.DS_DATASET,
SBQ.DS_DEVICE,
SBQ.VL_DATASET_MEMORY_SIZE
ORDER BY
AVG(SBQ.VL_TOTAL_EXECUTION_TIME) DESC
