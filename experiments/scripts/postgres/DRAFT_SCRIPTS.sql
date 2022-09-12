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
SELECT * FROM PARAMETER
SELECT * FROM EXPERIMENT




SELECT
	A.ID_PARAMETER,
	A.CD_PARAMETER,
	A.CD_CONFIGURATION,
	A.CD_ALGORITHM,
	(SELECT DISTINCT X.DS_ALGORITHM FROM ALGORITHM X WHERE X.CD_ALGORITHM = A.CD_ALGORITHM) AS DS_ALGORITHM,
	A.CD_FUNCTION,
	(SELECT DISTINCT X.DS_FUNCTION FROM FUNCTION X WHERE X.CD_FUNCTION = A.CD_FUNCTION) AS DS_FUNCTION,
	A.ID_DEVICE,
	(SELECT DISTINCT X.DS_DEVICE FROM DEVICE X WHERE X.ID_DEVICE = A.ID_DEVICE) AS DS_DEVICE,
	A.CD_DATASET,
	A.CD_RESOURCE,
	A.NR_ITERATIONS,
	A.DS_TP_PARAMETER,
	A.VL_DATASET_ROW_SIZE,
	A.VL_DATASET_COLUMN_SIZE,
	A.VL_GRID_ROW_SIZE,
	A.VL_GRID_COLUMN_SIZE,
	A.VL_BLOCK_ROW_SIZE,
	A.VL_BLOCK_COLUMN_SIZE,
	A.VL_BLOCK_MEMORY_SIZE,
	A.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
	A.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
	A.DS_STATUS_PARALLELISM,
	A.VL_BLOCK_SIZE_PERCENT_DATASET,
	B.DS_RESOURCE,
	B.NR_NODES,
	B.NR_COMPUTING_UNITS_CPU,
	B.NR_COMPUTING_UNITS_GPU,
	B.VL_MEMORY_PER_CPU_COMPUTING_UNIT,
	B.VL_MEMORY_PER_GPU_COMPUTING_UNIT,
	C.DS_DATASET,
	C.VL_DATASET_MEMORY_SIZE,
	C.DS_DATA_TYPE,
	C.VL_DATA_TYPE_MEMORY_SIZE,
	C.VL_DATASET_SIZE,
	C.VL_DATASET_ROW_SIZE,
	C.VL_DATASET_COLUMN_SIZE,
	C.NR_RANDOM_STATE
FROM PARAMETER A
INNER JOIN RESOURCE B ON (A.CD_RESOURCE = B.CD_RESOURCE)
INNER JOIN DATASET C ON (A.CD_DATASET = C.CD_DATASET)
WHERE
(SELECT DISTINCT X.DS_ALGORITHM FROM ALGORITHM X WHERE X.CD_ALGORITHM = A.CD_ALGORITHM) = 'KMEANS' -- FIXED VALUE
AND A.NR_ITERATIONS = 5 -- FIXED VALUE
AND B.DS_RESOURCE = 'MINOTAURO_1' -- FIXED VALUE
AND A.DS_TP_PARAMETER = 'VAR_BLOCK_CAPACITY_SIZE' -- 1.1, 1.2, 1.3, 1.4
--AND DS_TP_PARAMETER = 'VAR_PARALLELISM_LEVEL' -- 2.1, 2.2
AND VL_BLOCK_SIZE_PERCENT_DATASET = 0.25 -- 1.1
--AND A.VL_BLOCK_SIZE_PERCENT_DATASET = 0.5 -- 1.2
--AND VL_BLOCK_SIZE_PERCENT_DATASET = 0.75 -- 1.3
--AND VL_BLOCK_SIZE_PERCENT_DATASET = 1 -- 1.4
--AND DS_STATUS_PARALLELISM = 'MIN_INTER_MAX_INTRA'--2.1
--AND DS_STATUS_PARALLELISM = 'MAX_INTER_MIN_INTRA'--2.2
ORDER BY A.ID_PARAMETER




-- PARAMETER QUERY
SELECT
	A.ID_PARAMETER,
	A.CD_PARAMETER,
	A.CD_CONFIGURATION,
	A.CD_ALGORITHM,
	(SELECT DISTINCT X.DS_ALGORITHM FROM ALGORITHM X WHERE X.CD_ALGORITHM = A.CD_ALGORITHM) AS DS_ALGORITHM,
	A.CD_FUNCTION,
	(SELECT DISTINCT X.DS_FUNCTION FROM FUNCTION X WHERE X.CD_FUNCTION = A.CD_FUNCTION) AS DS_FUNCTION,
	A.ID_DEVICE,
	(SELECT DISTINCT X.DS_DEVICE FROM DEVICE X WHERE X.ID_DEVICE = A.ID_DEVICE) AS DS_DEVICE,
	A.CD_DATASET,
	A.CD_RESOURCE,
	A.NR_ITERATIONS,
	A.DS_TP_PARAMETER,
	A.VL_DATASET_ROW_SIZE,
	A.VL_DATASET_COLUMN_SIZE,
	A.VL_GRID_ROW_SIZE,
	A.VL_GRID_COLUMN_SIZE,
	A.VL_BLOCK_ROW_SIZE,
	A.VL_BLOCK_COLUMN_SIZE,
	A.VL_BLOCK_MEMORY_SIZE,
	A.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
	A.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
	A.DS_STATUS_PARALLELISM,
	A.VL_BLOCK_SIZE_PERCENT_DATASET,
	B.DS_RESOURCE,
	B.NR_NODES,
	B.NR_COMPUTING_UNITS_CPU,
	B.NR_COMPUTING_UNITS_GPU,
	B.VL_MEMORY_PER_CPU_COMPUTING_UNIT,
	B.VL_MEMORY_PER_GPU_COMPUTING_UNIT,
	C.DS_DATASET,
	C.VL_DATASET_MEMORY_SIZE,
	C.DS_DATA_TYPE,
	C.VL_DATA_TYPE_MEMORY_SIZE,
	C.VL_DATASET_SIZE,
	C.VL_DATASET_ROW_SIZE,
	C.VL_DATASET_COLUMN_SIZE,
	C.NR_RANDOM_STATE
FROM PARAMETER A
INNER JOIN RESOURCE B ON (A.CD_RESOURCE = B.CD_RESOURCE)
INNER JOIN DATASET C ON (A.CD_DATASET = C.CD_DATASET)
WHERE
(SELECT DISTINCT X.DS_ALGORITHM FROM ALGORITHM X WHERE X.CD_ALGORITHM = A.CD_ALGORITHM) = 'KMEANS' -- FIXED VALUE
AND A.NR_ITERATIONS = 5 -- FIXED VALUE
AND B.DS_RESOURCE = 'MINOTAURO_1' -- FIXED VALUE
AND A.DS_TP_PARAMETER = 'VAR_BLOCK_CAPACITY_SIZE' -- 1.1, 1.2, 1.3, 1.4
--AND DS_TP_PARAMETER = 'VAR_PARALLELISM_LEVEL' -- 2.1, 2.2
AND VL_BLOCK_SIZE_PERCENT_DATASET = 0.25 -- 1.1
--AND A.VL_BLOCK_SIZE_PERCENT_DATASET = 0.5 -- 1.2
--AND VL_BLOCK_SIZE_PERCENT_DATASET = 0.75 -- 1.3
--AND VL_BLOCK_SIZE_PERCENT_DATASET = 1 -- 1.4
--AND DS_STATUS_PARALLELISM = 'MIN_INTER_MAX_INTRA'--2.1
--AND DS_STATUS_PARALLELISM = 'MAX_INTER_MIN_INTRA'--2.2
ORDER BY A.ID_PARAMETER




-- EXPERIMENT QUERIES
-- MODE 1: BEHAVIOUR OF DEVICES ACCORDING TO DATA SET MEMORY SIZE
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
		A.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
		A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
		A.VL_COMMUNICATION_TIME,
		A.DT_PROCESSING,
		B.ID_PARAMETER,
		B.CD_PARAMETER,
		B.CD_CONFIGURATION,
		B.CD_ALGORITHM,
		(SELECT DISTINCT X.DS_ALGORITHM FROM ALGORITHM X WHERE X.CD_ALGORITHM = B.CD_ALGORITHM) AS DS_ALGORITHM,
		B.CD_FUNCTION,
		(SELECT DISTINCT X.DS_FUNCTION FROM FUNCTION X WHERE X.CD_FUNCTION = B.CD_FUNCTION) AS DS_FUNCTION,
		B.ID_DEVICE,
		(SELECT DISTINCT X.DS_DEVICE FROM DEVICE X WHERE X.ID_DEVICE = B.ID_DEVICE) AS DS_DEVICE,
		B.CD_DATASET,
		B.CD_RESOURCE,
		B.NR_ITERATIONS,
		B.DS_TP_PARAMETER,
		B.VL_DATASET_ROW_SIZE,
		B.VL_DATASET_COLUMN_SIZE,
		B.VL_GRID_ROW_SIZE,
		B.VL_GRID_COLUMN_SIZE,
		B.VL_BLOCK_ROW_SIZE,
		B.VL_BLOCK_COLUMN_SIZE,
		B.VL_BLOCK_MEMORY_SIZE,
		B.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
		B.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
		B.DS_STATUS_PARALLELISM,
		B.VL_BLOCK_SIZE_PERCENT_DATASET,
		C.DS_RESOURCE,
		C.NR_NODES,
		C.NR_COMPUTING_UNITS_CPU,
		C.NR_COMPUTING_UNITS_GPU,
		C.VL_MEMORY_PER_CPU_COMPUTING_UNIT,
		C.VL_MEMORY_PER_GPU_COMPUTING_UNIT,
		D.DS_DATASET,
		D.VL_DATASET_MEMORY_SIZE,
		D.DS_DATA_TYPE,
		D.VL_DATA_TYPE_MEMORY_SIZE,
		D.VL_DATASET_SIZE,
		D.VL_DATASET_ROW_SIZE,
		D.VL_DATASET_COLUMN_SIZE,
		D.NR_RANDOM_STATE
	FROM EXPERIMENT A
	INNER JOIN PARAMETER B ON (A.ID_PARAMETER = B.ID_PARAMETER)
	INNER JOIN RESOURCE C ON (B.CD_RESOURCE = C.CD_RESOURCE)
	INNER JOIN DATASET D ON (B.CD_DATASET = D.CD_DATASET)
	WHERE
	(SELECT DISTINCT X.DS_ALGORITHM FROM ALGORITHM X WHERE X.CD_ALGORITHM = B.CD_ALGORITHM) = 'KMEANS' -- FIXED VALUE
	AND B.NR_ITERATIONS = 5 -- FIXED VALUE
	AND C.DS_RESOURCE = 'MINOTAURO_1' -- FIXED VALUE
	AND B.DS_TP_PARAMETER = 'VAR_BLOCK_CAPACITY_SIZE' -- 1.1, 1.2, 1.3, 1.4
	--ORDER BY A.ID_EXPERIMENT;
) SBQ
GROUP BY
--SBQ.DS_DATASET,
SBQ.DS_DEVICE,
SBQ.VL_DATASET_MEMORY_SIZE
ORDER BY
AVG(SBQ.VL_TOTAL_EXECUTION_TIME) DESC
