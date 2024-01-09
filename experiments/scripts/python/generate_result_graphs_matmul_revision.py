import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from config import open_connection, close_connection
import numpy as np
import csv
import os
import math
import matplotlib
from sklearn.feature_selection import mutual_info_regression, mutual_info_classif
import statsmodels.api as sm

def main(ds_algorithm, ds_resource, nr_iterations, mode):

    dst_path_figs = '../../results/figures/'

    # Open connection to the database
    cur, conn = open_connection()

    # Set sql query according to mode
    # CPU AND GPU SPEEDUPS
    if (mode == 18 or mode == 188 or mode == 1888):
        sql_query = """
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
                    T_CPU.ID_PARAMETER_TYPE,
                    T_CPU.CD_PARAMETER,
                    T_CPU.DS_ALGORITHM,
                    T_CPU.DS_FUNCTION,
                    T_CPU.NR_ITERATIONS,
                    CASE
                    WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 0.3 THEN 0.4
                    WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 0.7 THEN 0.8
                    WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 1.5 THEN 1.6
                    WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 3.0 THEN 3.1
                    WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 6.2 THEN 6.3
                    ELSE ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) END AS VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                    CASE
                    WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 0.3 THEN 0.4 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION || ' x ' || T_CPU.VL_GRID_COLUMN_DIMENSION  || ')'
                    WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 0.7 THEN 0.8 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION || ' x ' || T_CPU.VL_GRID_COLUMN_DIMENSION  || ')'
                    WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 1.5 THEN 1.6 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION || ' x ' || T_CPU.VL_GRID_COLUMN_DIMENSION  || ')'
                    WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 3.0 THEN 3.1 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION || ' x ' || T_CPU.VL_GRID_COLUMN_DIMENSION  || ')'
                    WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 6.2 THEN 6.3 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION || ' x ' || T_CPU.VL_GRID_COLUMN_DIMENSION  || ')'
                    ELSE ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) || ' (' || T_CPU.VL_GRID_ROW_DIMENSION || ' x ' || T_CPU.VL_GRID_COLUMN_DIMENSION  || ')' END AS CONCAT_BLOCK_PERCENT_DATASET_GRID_DIMENSION,
                    --ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) AS VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                    T_CPU.DS_RESOURCE,
                    T_CPU.DS_PARAMETER_TYPE,
                    T_CPU.DS_PARAMETER_ATTRIBUTE,
                    T_CPU.DS_DATASET,
                    CAST(T_CPU.VL_DATASET_MEMORY_SIZE*1e-6 AS BIGINT) as VL_DATASET_MEMORY_SIZE,
                    T_CPU.VL_DATASET_DIMENSION,
                    T_CPU.VL_DATASET_ROW_DIMENSION,
                    T_CPU.VL_DATASET_COLUMN_DIMENSION,
                    T_CPU.VL_GRID_ROW_DIMENSION,
                    T_CPU.VL_GRID_COLUMN_DIMENSION,
                    T_CPU.VL_BLOCK_ROW_DIMENSION,
                    T_CPU.VL_BLOCK_COLUMN_DIMENSION,
                    T_CPU.VL_BLOCK_MEMORY_SIZE,
                    ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE*1e-6,0) || ' (' || T_CPU.VL_GRID_ROW_DIMENSION || ' x ' || T_CPU.VL_GRID_COLUMN_DIMENSION  || ')' AS VL_CONCAT_BLOCK_SIZE_MB_GRID_ROW_X_COLUMN_DIMENSION,
					CASE
						WHEN T_CPU.DS_ALGORITHM = 'KMEANS'
							THEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE*1e-6,0) || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*5 || ')'
						WHEN T_CPU.DS_ALGORITHM = 'MATMUL_DISLIB'
							THEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE*1e-6,0) || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION + T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*(T_CPU.VL_GRID_ROW_DIMENSION-1)  || ')'
						ELSE
							'999999999999'
					END AS VL_CONCAT_BLOCK_SIZE_MB_NR_TASKS,
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
									ELSE ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION + T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*(T_CPU.VL_GRID_ROW_DIMENSION-1)  || ')'
								END
						ELSE
							'999999999999'
					END AS CONCAT_BLOCK_PERCENT_DATASET_NR_TASKS,
                    CASE
                    WHEN (T_GPU.VL_TOTAL_EXECUTION_TIME/T_CPU.VL_TOTAL_EXECUTION_TIME) > 1.00 THEN (T_GPU.VL_TOTAL_EXECUTION_TIME/T_CPU.VL_TOTAL_EXECUTION_TIME)
                    ELSE -(T_CPU.VL_TOTAL_EXECUTION_TIME/T_GPU.VL_TOTAL_EXECUTION_TIME)
                    END AS SPEEDUP_CPU_TOTAL_EXECUTION_TIME,
                    CASE
                    WHEN (T_GPU.VL_INTER_TASK_EXECUTION_TIME/T_CPU.VL_INTER_TASK_EXECUTION_TIME) > 1.00 THEN (T_GPU.VL_INTER_TASK_EXECUTION_TIME/T_CPU.VL_INTER_TASK_EXECUTION_TIME)
                    ELSE -(T_CPU.VL_INTER_TASK_EXECUTION_TIME/T_GPU.VL_INTER_TASK_EXECUTION_TIME)
                    END AS SPEEDUP_CPU_INTER_TASK_EXECUTION_TIME,
                    CASE
                    WHEN (T_GPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC/T_CPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC) > 1.00 THEN (T_GPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC/T_CPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC)
                    ELSE -(T_CPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC/T_GPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC)
                    END AS SPEEDUP_CPU_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                    CASE
                    WHEN (T_GPU.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC/T_CPU.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC) > 1.00 THEN (T_GPU.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC/T_CPU.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC)
                    ELSE -(T_CPU.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC/T_GPU.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC)
                    END AS SPEEDUP_CPU_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                    CASE
                    WHEN (T_GPU.VL_INTRA_TASK_EXECUTION_TIME_FREE_ADDITIONAL/T_CPU.VL_INTRA_TASK_EXECUTION_TIME_FREE_ADDITIONAL) > 1.00 THEN (T_GPU.VL_INTRA_TASK_EXECUTION_TIME_FREE_ADDITIONAL/T_CPU.VL_INTRA_TASK_EXECUTION_TIME_FREE_ADDITIONAL)
                    ELSE -(T_CPU.VL_INTRA_TASK_EXECUTION_TIME_FREE_ADDITIONAL/T_GPU.VL_INTRA_TASK_EXECUTION_TIME_FREE_ADDITIONAL)
                    END AS SPEEDUP_CPU_INTRA_TASK_EXECUTION_TIME_FREE_ADDITIONAL,
                    CASE
                    WHEN (T_CPU.VL_TOTAL_EXECUTION_TIME/T_GPU.VL_TOTAL_EXECUTION_TIME) > 1.00 THEN (T_CPU.VL_TOTAL_EXECUTION_TIME/T_GPU.VL_TOTAL_EXECUTION_TIME)
                    ELSE -(T_GPU.VL_TOTAL_EXECUTION_TIME/T_CPU.VL_TOTAL_EXECUTION_TIME)
                    END AS SPEEDUP_GPU_TOTAL_EXECUTION_TIME,
                    CASE
                    WHEN (T_CPU.VL_INTER_TASK_EXECUTION_TIME/T_GPU.VL_INTER_TASK_EXECUTION_TIME) > 1.00 THEN (T_CPU.VL_INTER_TASK_EXECUTION_TIME/T_GPU.VL_INTER_TASK_EXECUTION_TIME)
                    ELSE -(T_GPU.VL_INTER_TASK_EXECUTION_TIME/T_CPU.VL_INTER_TASK_EXECUTION_TIME)
                    END AS SPEEDUP_GPU_INTER_TASK_EXECUTION_TIME,
                    CASE
                    WHEN (T_CPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC/T_GPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC) > 1.00 THEN (T_CPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC/T_GPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC)
                    ELSE -(T_GPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC/T_CPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC)
                    END AS SPEEDUP_GPU_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                    CASE
                    WHEN (T_CPU.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC/T_GPU.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC) > 1.00 THEN (T_CPU.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC/T_GPU.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC)
                    ELSE -(T_GPU.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC/T_CPU.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC)
                    END AS SPEEDUP_GPU_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                    CASE
                    WHEN (T_CPU.VL_INTRA_TASK_EXECUTION_TIME_FREE_ADDITIONAL/T_GPU.VL_INTRA_TASK_EXECUTION_TIME_FREE_ADDITIONAL) > 1.00 THEN (T_CPU.VL_INTRA_TASK_EXECUTION_TIME_FREE_ADDITIONAL/T_GPU.VL_INTRA_TASK_EXECUTION_TIME_FREE_ADDITIONAL)
                    ELSE -(T_GPU.VL_INTRA_TASK_EXECUTION_TIME_FREE_ADDITIONAL/T_CPU.VL_INTRA_TASK_EXECUTION_TIME_FREE_ADDITIONAL)
                    END AS SPEEDUP_GPU_INTRA_TASK_EXECUTION_TIME_FREE_ADDITIONAL
                    FROM T_CPU INNER JOIN T_GPU ON (T_CPU.CD_PARAMETER = T_GPU.CD_PARAMETER)
                    WHERE
                    T_CPU.VL_GRID_ROW_DIMENSION = T_GPU.VL_GRID_ROW_DIMENSION
                    AND T_CPU.VL_GRID_COLUMN_DIMENSION = T_GPU.VL_GRID_COLUMN_DIMENSION
                    AND T_CPU.VL_BLOCK_ROW_DIMENSION = T_GPU.VL_BLOCK_ROW_DIMENSION
                    AND T_CPU.VL_BLOCK_COLUMN_DIMENSION = T_GPU.VL_BLOCK_COLUMN_DIMENSION
                    ORDER BY
                    T_CPU.DS_DATASET,
                    T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET;"""
        
    elif (mode == 100):
        sql_query = """SELECT 1"""

        sql_queryA = """WITH T_CPU AS (
                                    SELECT
                                    A.VL_TOTAL_EXECUTION_TIME,
                                    A.VL_INTER_TASK_EXECUTION_TIME,
									A.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                                    A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
									A.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC - (A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC+A.VL_COMMUNICATION_TIME) AS VL_ADDITIONAL_TIME,
                                    A.VL_COMMUNICATION_TIME,
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
									Y.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
									Y.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
									Y.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC - (Y.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC+Y.VL_COMMUNICATION_TIME) AS VL_ADDITIONAL_TIME,
									Y.VL_COMMUNICATION_TIME,
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
									A.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
									A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
									A.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC - (A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC+A.VL_COMMUNICATION_TIME) AS VL_ADDITIONAL_TIME,
									A.VL_COMMUNICATION_TIME,
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
                                    Y.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
									Y.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
									Y.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC - (Y.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC+Y.VL_COMMUNICATION_TIME) AS VL_ADDITIONAL_TIME,
									Y.VL_COMMUNICATION_TIME,
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
                    T_CPU.ID_PARAMETER_TYPE,
                    T_CPU.CD_PARAMETER,
                    T_CPU.DS_ALGORITHM,
                    T_CPU.DS_FUNCTION,
                    T_CPU.NR_ITERATIONS,
                    CASE
                    WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 0.3 THEN 0.4
                    WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 0.7 THEN 0.8
                    WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 1.5 THEN 1.6
                    WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 3.0 THEN 3.1
                    WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 6.2 THEN 6.3
                    ELSE ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) END AS VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                    CASE
                    WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 0.3 THEN 0.4 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION || ' x ' || T_CPU.VL_GRID_COLUMN_DIMENSION  || ')'
                    WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 0.7 THEN 0.8 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION || ' x ' || T_CPU.VL_GRID_COLUMN_DIMENSION  || ')'
                    WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 1.5 THEN 1.6 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION || ' x ' || T_CPU.VL_GRID_COLUMN_DIMENSION  || ')'
                    WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 3.0 THEN 3.1 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION || ' x ' || T_CPU.VL_GRID_COLUMN_DIMENSION  || ')'
                    WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 6.2 THEN 6.3 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION || ' x ' || T_CPU.VL_GRID_COLUMN_DIMENSION  || ')'
                    ELSE ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) || ' (' || T_CPU.VL_GRID_ROW_DIMENSION || ' x ' || T_CPU.VL_GRID_COLUMN_DIMENSION  || ')' END AS CONCAT_BLOCK_PERCENT_DATASET_GRID_DIMENSION,
                    --ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) AS VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                    T_CPU.DS_RESOURCE,
                    T_CPU.DS_PARAMETER_TYPE,
                    T_CPU.DS_PARAMETER_ATTRIBUTE,
                    T_CPU.DS_DATASET,
                    CAST(T_CPU.VL_DATASET_MEMORY_SIZE*1e-6 AS BIGINT) as VL_DATASET_MEMORY_SIZE,
                    T_CPU.VL_DATASET_DIMENSION,
                    T_CPU.VL_DATASET_ROW_DIMENSION,
                    T_CPU.VL_DATASET_COLUMN_DIMENSION,
                    T_CPU.VL_GRID_ROW_DIMENSION,
                    T_CPU.VL_GRID_COLUMN_DIMENSION,
                    T_CPU.VL_BLOCK_ROW_DIMENSION,
                    T_CPU.VL_BLOCK_COLUMN_DIMENSION,
                    T_CPU.VL_BLOCK_MEMORY_SIZE,
                    ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE*1e-6,0)::varchar(255) as VL_BLOCK_MEMORY_SIZE_MB,
                    ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE*1e-6,0) || ' (' || T_CPU.VL_GRID_ROW_DIMENSION || ' x ' || T_CPU.VL_GRID_COLUMN_DIMENSION  || ')' AS VL_CONCAT_BLOCK_SIZE_MB_GRID_ROW_X_COLUMN_DIMENSION,
					CASE
						WHEN T_CPU.DS_ALGORITHM = 'KMEANS'
							THEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE*1e-6,0) || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*5 || ')'
						WHEN T_CPU.DS_ALGORITHM = 'MATMUL_DISLIB'
							THEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE*1e-6,0) || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION + T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*(T_CPU.VL_GRID_ROW_DIMENSION-1)  || ')'
						ELSE
							'999999999999'
					END AS VL_CONCAT_BLOCK_SIZE_MB_NR_TASKS,
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
									ELSE ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION + T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*(T_CPU.VL_GRID_ROW_DIMENSION-1)  || ')'
								END
						ELSE
							'999999999999'
					END AS CONCAT_BLOCK_PERCENT_DATASET_NR_TASKS,
					T_CPU.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC AS VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC_CPU,
					T_GPU.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC AS VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC_GPU,
					T_CPU.VL_ADDITIONAL_TIME AS VL_ADDITIONAL_TIME_CPU,
					T_GPU.VL_ADDITIONAL_TIME AS VL_ADDITIONAL_TIME_GPU,
					T_CPU.VL_COMMUNICATION_TIME AS VL_COMMUNICATION_TIME_CPU,
					T_GPU.VL_COMMUNICATION_TIME AS VL_COMMUNICATION_TIME_GPU,
                    CASE
                    WHEN ROUND((T_CPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC/T_GPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC)::numeric,2) > 1.00 THEN ROUND((T_CPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC/T_GPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC)::numeric,2)
                    ELSE -ROUND((T_GPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC/T_CPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC)::numeric,2)
                    END AS SPEEDUP_GPU_INTRA_TASK_EXECUTION_TIME_FULL_FUNC
                    FROM T_CPU LEFT JOIN T_GPU ON (T_CPU.CD_PARAMETER = T_GPU.CD_PARAMETER
													AND T_CPU.VL_GRID_ROW_DIMENSION = T_GPU.VL_GRID_ROW_DIMENSION
													AND T_CPU.VL_GRID_COLUMN_DIMENSION = T_GPU.VL_GRID_COLUMN_DIMENSION
													AND T_CPU.VL_BLOCK_ROW_DIMENSION = T_GPU.VL_BLOCK_ROW_DIMENSION
													AND T_CPU.VL_BLOCK_COLUMN_DIMENSION = T_GPU.VL_BLOCK_COLUMN_DIMENSION)
                    ORDER BY
                    T_CPU.DS_DATASET,
                    T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET;"""
        
        sql_queryB = """WITH T_CPU AS (
                                    SELECT
                                    A.VL_TOTAL_EXECUTION_TIME,
                                    A.VL_INTER_TASK_EXECUTION_TIME,
									A.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                                    A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
									A.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC - (A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC+A.VL_COMMUNICATION_TIME) AS VL_ADDITIONAL_TIME,
                                    A.VL_COMMUNICATION_TIME,
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
									Y.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
									Y.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
									Y.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC - (Y.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC+Y.VL_COMMUNICATION_TIME) AS VL_ADDITIONAL_TIME,
									Y.VL_COMMUNICATION_TIME,
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
										X.DS_FUNCTION = 'ADD_FUNC'
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
									A.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
									A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
									A.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC - (A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC+A.VL_COMMUNICATION_TIME) AS VL_ADDITIONAL_TIME,
									A.VL_COMMUNICATION_TIME,
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
                                    Y.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
									Y.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
									Y.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC - (Y.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC+Y.VL_COMMUNICATION_TIME) AS VL_ADDITIONAL_TIME,
									Y.VL_COMMUNICATION_TIME,
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
										X.DS_FUNCTION = 'ADD_FUNC'
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
                    T_CPU.ID_PARAMETER_TYPE,
                    T_CPU.CD_PARAMETER,
                    T_CPU.DS_ALGORITHM,
                    T_CPU.DS_FUNCTION,
                    T_CPU.NR_ITERATIONS,
                    CASE
                    WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 0.3 THEN 0.4
                    WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 0.7 THEN 0.8
                    WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 1.5 THEN 1.6
                    WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 3.0 THEN 3.1
                    WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 6.2 THEN 6.3
                    ELSE ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) END AS VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                    CASE
                    WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 0.3 THEN 0.4 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION || ' x ' || T_CPU.VL_GRID_COLUMN_DIMENSION  || ')'
                    WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 0.7 THEN 0.8 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION || ' x ' || T_CPU.VL_GRID_COLUMN_DIMENSION  || ')'
                    WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 1.5 THEN 1.6 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION || ' x ' || T_CPU.VL_GRID_COLUMN_DIMENSION  || ')'
                    WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 3.0 THEN 3.1 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION || ' x ' || T_CPU.VL_GRID_COLUMN_DIMENSION  || ')'
                    WHEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) = 6.2 THEN 6.3 || ' (' || T_CPU.VL_GRID_ROW_DIMENSION || ' x ' || T_CPU.VL_GRID_COLUMN_DIMENSION  || ')'
                    ELSE ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) || ' (' || T_CPU.VL_GRID_ROW_DIMENSION || ' x ' || T_CPU.VL_GRID_COLUMN_DIMENSION  || ')' END AS CONCAT_BLOCK_PERCENT_DATASET_GRID_DIMENSION,
                    --ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) AS VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                    T_CPU.DS_RESOURCE,
                    T_CPU.DS_PARAMETER_TYPE,
                    T_CPU.DS_PARAMETER_ATTRIBUTE,
                    T_CPU.DS_DATASET,
                    CAST(T_CPU.VL_DATASET_MEMORY_SIZE*1e-6 AS BIGINT) as VL_DATASET_MEMORY_SIZE,
                    T_CPU.VL_DATASET_DIMENSION,
                    T_CPU.VL_DATASET_ROW_DIMENSION,
                    T_CPU.VL_DATASET_COLUMN_DIMENSION,
                    T_CPU.VL_GRID_ROW_DIMENSION,
                    T_CPU.VL_GRID_COLUMN_DIMENSION,
                    T_CPU.VL_BLOCK_ROW_DIMENSION,
                    T_CPU.VL_BLOCK_COLUMN_DIMENSION,
                    T_CPU.VL_BLOCK_MEMORY_SIZE,
                    ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE*1e-6,0)::varchar(255) as VL_BLOCK_MEMORY_SIZE_MB,
                    ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE*1e-6,0) || ' (' || T_CPU.VL_GRID_ROW_DIMENSION || ' x ' || T_CPU.VL_GRID_COLUMN_DIMENSION  || ')' AS VL_CONCAT_BLOCK_SIZE_MB_GRID_ROW_X_COLUMN_DIMENSION,
					CASE
						WHEN T_CPU.DS_ALGORITHM = 'KMEANS'
							THEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE*1e-6,0) || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*5 || ')'
						WHEN T_CPU.DS_ALGORITHM = 'MATMUL_DISLIB'
							THEN ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE*1e-6,0) || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION + T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*(T_CPU.VL_GRID_ROW_DIMENSION-1)  || ')'
						ELSE
							'999999999999'
					END AS VL_CONCAT_BLOCK_SIZE_MB_NR_TASKS,
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
									ELSE ROUND(T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,1) || ' (' || T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION + T_CPU.VL_GRID_ROW_DIMENSION*T_CPU.VL_GRID_ROW_DIMENSION*(T_CPU.VL_GRID_ROW_DIMENSION-1)  || ')'
								END
						ELSE
							'999999999999'
					END AS CONCAT_BLOCK_PERCENT_DATASET_NR_TASKS,
					T_CPU.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC AS VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC_CPU,
					T_GPU.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC AS VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC_GPU,
					T_CPU.VL_ADDITIONAL_TIME AS VL_ADDITIONAL_TIME_CPU,
					T_GPU.VL_ADDITIONAL_TIME AS VL_ADDITIONAL_TIME_GPU,
					T_CPU.VL_COMMUNICATION_TIME AS VL_COMMUNICATION_TIME_CPU,
					T_GPU.VL_COMMUNICATION_TIME AS VL_COMMUNICATION_TIME_GPU,
                    CASE
                    WHEN ROUND((T_CPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC/T_GPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC)::numeric,2) > 1.00 THEN ROUND((T_CPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC/T_GPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC)::numeric,2)
                    ELSE -ROUND((T_GPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC/T_CPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC)::numeric,2)
                    END AS SPEEDUP_GPU_INTRA_TASK_EXECUTION_TIME_FULL_FUNC
                    FROM T_CPU LEFT JOIN T_GPU ON (T_CPU.CD_PARAMETER = T_GPU.CD_PARAMETER
													AND T_CPU.VL_GRID_ROW_DIMENSION = T_GPU.VL_GRID_ROW_DIMENSION
													AND T_CPU.VL_GRID_COLUMN_DIMENSION = T_GPU.VL_GRID_COLUMN_DIMENSION
													AND T_CPU.VL_BLOCK_ROW_DIMENSION = T_GPU.VL_BLOCK_ROW_DIMENSION
													AND T_CPU.VL_BLOCK_COLUMN_DIMENSION = T_GPU.VL_BLOCK_COLUMN_DIMENSION)
                    ORDER BY
                    T_CPU.DS_DATASET,
                    T_CPU.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET;"""
        
    else:
        sql_query = """SELECT
                            A.VL_TOTAL_EXECUTION_TIME,
                            A.VL_INTER_TASK_EXECUTION_TIME,
                            (A.VL_INTER_TASK_EXECUTION_TIME - A.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC) AS VL_INTER_TASK_OVERHEAD_TIME,
                            A.VL_INTER_TASK_EXECUTION_TIME - (A.VL_INTER_TASK_EXECUTION_TIME - A.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC) AS VL_INTER_TASK_EXECUTION_TIME_FREE_OVERHEAD,
                            A.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                            A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                            A.VL_COMMUNICATION_TIME,
                            A.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC - (A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC+A.VL_COMMUNICATION_TIME) AS VL_ADDITIONAL_TIME,
                            (A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC + A.VL_COMMUNICATION_TIME) AS VL_INTRA_TASK_EXECUTION_TIME_FREE_ADDITIONAL,
							NULL AS VL_STD_TOTAL_EXECUTION_TIME,
                            NULL AS VL_STD_INTER_TASK_EXECUTION_TIME,
                            NULL AS VL_STD_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                            NULL AS VL_STD_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                            NULL AS VL_STD_COMMUNICATION_TIME,
                            ROUND(((A.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC)/(A.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC-A.VL_COMMUNICATION_TIME))::numeric,2) AS P_FRACTION,
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
							B.VL_GRID_ROW_DIMENSION || ' x ' || B.VL_GRID_COLUMN_DIMENSION || '(' || ROUND(B.VL_BLOCK_MEMORY_SIZE*1e-6,2) || ')' AS VL_CONCAT_GRID_ROW_X_COLUMN_DIMENSION_BLOCK_SIZE_MB,
                            ROUND(D.VL_DATASET_MEMORY_SIZE*1e-6,0) || ' (' || ROUND((CAST(B.VL_BLOCK_MEMORY_SIZE AS NUMERIC)/CAST(D.VL_DATASET_MEMORY_SIZE AS NUMERIC))*100,2) || '%)' AS VL_CONCAT_DATASET_MB_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                            CASE
								WHEN (SELECT DISTINCT X.DS_ALGORITHM FROM ALGORITHM X WHERE X.ID_ALGORITHM = B.ID_ALGORITHM) = 'KMEANS'
									THEN ROUND(B.VL_BLOCK_MEMORY_SIZE*1e-6,2) || ' (' || B.VL_GRID_ROW_DIMENSION*5  || ')'
								WHEN (SELECT DISTINCT X.DS_ALGORITHM FROM ALGORITHM X WHERE X.ID_ALGORITHM = B.ID_ALGORITHM) = 'MATMUL_DISLIB'
									THEN ROUND(B.VL_BLOCK_MEMORY_SIZE*1e-6,2) || ' (' || B.VL_GRID_ROW_DIMENSION*B.VL_GRID_ROW_DIMENSION*B.VL_GRID_ROW_DIMENSION + B.VL_GRID_ROW_DIMENSION*B.VL_GRID_ROW_DIMENSION*(B.VL_GRID_ROW_DIMENSION-1)  || ')'
								ELSE
									'999999999999'
							END AS VL_CONCAT_BLOCK_SIZE_MB_NR_TASKS,
							ROUND(B.VL_BLOCK_MEMORY_SIZE*1e-6,0) || ' (' || B.VL_GRID_ROW_DIMENSION || ' x ' || B.VL_GRID_COLUMN_DIMENSION  || ')' AS VL_CONCAT_BLOCK_SIZE_MB_GRID_ROW_X_COLUMN_DIMENSION,
                            ROUND((CAST(B.VL_GRID_COLUMN_DIMENSION AS NUMERIC)/CAST(D.VL_DATASET_COLUMN_DIMENSION AS NUMERIC))*100,2) AS VL_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                            B.VL_GRID_ROW_DIMENSION || ' x ' || B.VL_GRID_COLUMN_DIMENSION || ' (' || ROUND((CAST(B.VL_GRID_COLUMN_DIMENSION AS NUMERIC)/CAST(D.VL_DATASET_COLUMN_DIMENSION AS NUMERIC))*100,2) || '%)' AS VL_CONCAT_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                            B.VL_BLOCK_ROW_DIMENSION,
                            B.VL_BLOCK_COLUMN_DIMENSION,
                            B.VL_BLOCK_ROW_DIMENSION || ' x ' || B.VL_BLOCK_COLUMN_DIMENSION AS VL_BLOCK_ROW_X_COLUMN_DIMENSION,
                            ROUND(B.VL_BLOCK_MEMORY_SIZE*1e-6,2) AS VL_BLOCK_MEMORY_SIZE,
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
                            D.NR_RANDOM_STATE,
                            CASE
                                WHEN (SELECT DISTINCT Y.DS_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) = 'CPU' AND D.VL_DATA_SPARSITY = 0 THEN 'CPU dense'
                                WHEN (SELECT DISTINCT Y.DS_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) = 'CPU' AND D.VL_DATA_SPARSITY = 1 THEN 'CPU sparse'
                                WHEN (SELECT DISTINCT Y.DS_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) = 'GPU' AND D.VL_DATA_SPARSITY = 0 THEN 'GPU dense'
                                WHEN (SELECT DISTINCT Y.DS_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) = 'GPU' AND D.VL_DATA_SPARSITY = 1 THEN 'GPU sparse'
                            ELSE ''
                            END AS DEVICE_SPARSITY,
                            CASE
                                WHEN (SELECT DISTINCT Y.DS_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) = 'CPU' AND D.VL_DATA_SKEWNESS = 0 THEN 'CPU NOT SKEWED'
                                WHEN (SELECT DISTINCT Y.DS_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) = 'CPU' AND D.VL_DATA_SKEWNESS = 0.5 THEN 'CPU SKEWED'
                                WHEN (SELECT DISTINCT Y.DS_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) = 'GPU' AND D.VL_DATA_SKEWNESS = 0 THEN 'GPU NOT SKEWED'
                                WHEN (SELECT DISTINCT Y.DS_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) = 'GPU' AND D.VL_DATA_SKEWNESS = 0.5 THEN 'GPU SKEWED'
                            ELSE ''
                            END AS DEVICE_SKEWNESS
                        FROM EXPERIMENT A
                        INNER JOIN PARAMETER B ON (A.ID_PARAMETER = B.ID_PARAMETER)
                        INNER JOIN RESOURCE C ON (B.ID_RESOURCE = C.ID_RESOURCE)
                        INNER JOIN DATASET D ON (B.ID_DATASET = D.ID_DATASET)
                        WHERE
                        A.VL_TOTAL_EXECUTION_TIME is not null
                        --(SELECT X.DS_PARAMETER_ATTRIBUTE FROM PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) <> 'MAX_INTER_MIN_INTRA'
                        --AND DATE_TRUNC('day', A.DT_PROCESSING) < TO_DATE('15/11/2022', 'dd/mm/yyyy')
                        
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
						Y.VL_STD_TOTAL_EXECUTION_TIME,
						Y.VL_STD_INTER_TASK_EXECUTION_TIME,
						Y.VL_STD_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
						Y.VL_STD_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
						Y.VL_STD_COMMUNICATION_TIME,
                        ROUND(((Y.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC)/(Y.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC-Y.VL_COMMUNICATION_TIME))::numeric,2) AS P_FRACTION,
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
                        Y.VL_GRID_ROW_X_COLUMN_DIMENSION,
						Y.VL_CONCAT_GRID_ROW_X_COLUMN_DIMENSION_BLOCK_SIZE_MB,
                        Y.VL_CONCAT_DATASET_MB_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
						Y.VL_CONCAT_BLOCK_SIZE_MB_NR_TASKS,
                        Y.VL_CONCAT_BLOCK_SIZE_MB_GRID_ROW_X_COLUMN_DIMENSION,
                        Y.VL_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                        Y.VL_CONCAT_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                        Y.VL_BLOCK_ROW_DIMENSION,
                        Y.VL_BLOCK_COLUMN_DIMENSION,
                        Y.VL_BLOCK_ROW_X_COLUMN_DIMENSION,
						ROUND(Y.VL_BLOCK_MEMORY_SIZE*1e-6,2) AS VL_BLOCK_MEMORY_SIZE,
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
                        Y.NR_RANDOM_STATE,
                        CASE
                            WHEN Y.DS_DEVICE = 'CPU' AND Y.VL_DATA_SPARSITY = 0 THEN 'CPU dense'
                            WHEN Y.DS_DEVICE = 'CPU' AND Y.VL_DATA_SPARSITY = 1 THEN 'CPU sparse'
                            WHEN Y.DS_DEVICE = 'GPU' AND Y.VL_DATA_SPARSITY = 0 THEN 'GPU dense'
                            WHEN Y.DS_DEVICE = 'GPU' AND Y.VL_DATA_SPARSITY = 1 THEN 'GPU sparse'
                            ELSE ''
                        END AS DEVICE_SPARSITY,
                        CASE
                            WHEN Y.DS_DEVICE = 'CPU' AND Y.VL_DATA_SKEWNESS = 0 THEN 'CPU NOT SKEWED'
                            WHEN Y.DS_DEVICE = 'CPU' AND Y.VL_DATA_SKEWNESS = 0.5 THEN 'CPU SKEWED'
                            WHEN Y.DS_DEVICE = 'GPU' AND Y.VL_DATA_SKEWNESS = 0 THEN 'GPU NOT SKEWED'
                            WHEN Y.DS_DEVICE = 'GPU' AND Y.VL_DATA_SKEWNESS = 0.5 THEN 'GPU SKEWED'
                            ELSE ''
                        END AS DEVICE_SKEWNESS
                        FROM
                        (
                            SELECT
                            AVG(X.VL_TOTAL_EXECUTION_TIME) AS VL_TOTAL_EXECUTION_TIME,
                            CASE
								WHEN X.DS_FUNCTION = 'MATMUL_FUNC' THEN AVG(X.VL_INTER_TASK_EXECUTION_TIME)
								WHEN X.DS_FUNCTION = 'ADD_FUNC' THEN AVG(X.VL_INTER_TASK_EXECUTION_TIME)*ceil(ln(X.VL_GRID_ROW_DIMENSION)/ln(2))
								ELSE AVG(X.VL_INTER_TASK_EXECUTION_TIME)
							END AS VL_INTER_TASK_EXECUTION_TIME,
                            AVG(X.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC) AS VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                            AVG(X.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC) AS VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                            AVG(X.VL_COMMUNICATION_TIME_1) AS VL_COMMUNICATION_TIME_1,
                            AVG(X.VL_COMMUNICATION_TIME_2) AS VL_COMMUNICATION_TIME_2,
                            AVG(X.VL_COMMUNICATION_TIME) AS VL_COMMUNICATION_TIME,
                            AVG(X.VL_ADDITIONAL_TIME_1) AS VL_ADDITIONAL_TIME_1,
                            AVG(X.VL_ADDITIONAL_TIME_2) AS VL_ADDITIONAL_TIME_2,
                            AVG(X.VL_ADDITIONAL_TIME) AS VL_ADDITIONAL_TIME,
                            STDDEV(X.VL_TOTAL_EXECUTION_TIME) AS VL_STD_TOTAL_EXECUTION_TIME,
                            STDDEV(X.VL_INTER_TASK_EXECUTION_TIME) AS VL_STD_INTER_TASK_EXECUTION_TIME,
                            STDDEV(X.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC) AS VL_STD_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                            STDDEV(X.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC) AS VL_STD_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                            STDDEV(X.VL_COMMUNICATION_TIME) AS VL_STD_COMMUNICATION_TIME,
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
							X.VL_CONCAT_GRID_ROW_X_COLUMN_DIMENSION_BLOCK_SIZE_MB,
                            X.VL_CONCAT_DATASET_MB_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
							X.VL_CONCAT_BLOCK_SIZE_MB_NR_TASKS,
                            X.VL_CONCAT_BLOCK_SIZE_MB_GRID_ROW_X_COLUMN_DIMENSION,
                            X.VL_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                            X.VL_CONCAT_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                            X.VL_BLOCK_ROW_DIMENSION,
                            X.VL_BLOCK_COLUMN_DIMENSION,
                            X.VL_BLOCK_ROW_X_COLUMN_DIMENSION,
							ROUND(X.VL_BLOCK_MEMORY_SIZE*1e-6,2) AS VL_BLOCK_MEMORY_SIZE,
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
                            X.NR_RANDOM_STATE,
							X.VL_DATA_SPARSITY,
                            X.VL_DATA_SKEWNESS
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
									B.VL_GRID_ROW_DIMENSION || ' x ' || B.VL_GRID_COLUMN_DIMENSION || '(' || ROUND(B.VL_BLOCK_MEMORY_SIZE*1e-6,2) || ')' AS VL_CONCAT_GRID_ROW_X_COLUMN_DIMENSION_BLOCK_SIZE_MB,
                                    ROUND(D.VL_DATASET_MEMORY_SIZE*1e-6,0) || ' (' || ROUND((CAST(B.VL_BLOCK_MEMORY_SIZE AS NUMERIC)/CAST(D.VL_DATASET_MEMORY_SIZE AS NUMERIC))*100,2) || '%)' AS VL_CONCAT_DATASET_MB_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
									CASE
										WHEN (SELECT DISTINCT X.DS_ALGORITHM FROM ALGORITHM X WHERE X.ID_ALGORITHM = B.ID_ALGORITHM) = 'KMEANS'
											THEN ROUND(B.VL_BLOCK_MEMORY_SIZE*1e-6,2) || ' (' || B.VL_GRID_ROW_DIMENSION*5  || ')'
										WHEN (SELECT DISTINCT X.DS_ALGORITHM FROM ALGORITHM X WHERE X.ID_ALGORITHM = B.ID_ALGORITHM) = 'MATMUL_DISLIB'
											THEN ROUND(B.VL_BLOCK_MEMORY_SIZE*1e-6,2) || ' (' || B.VL_GRID_ROW_DIMENSION*B.VL_GRID_ROW_DIMENSION*B.VL_GRID_ROW_DIMENSION + B.VL_GRID_ROW_DIMENSION*B.VL_GRID_ROW_DIMENSION*(B.VL_GRID_ROW_DIMENSION-1)  || ')'
										ELSE
											'999999999999'
									END AS VL_CONCAT_BLOCK_SIZE_MB_NR_TASKS,
									ROUND(B.VL_BLOCK_MEMORY_SIZE*1e-6,0) || ' (' || B.VL_GRID_ROW_DIMENSION || ' x ' || B.VL_GRID_COLUMN_DIMENSION  || ')' AS VL_CONCAT_BLOCK_SIZE_MB_GRID_ROW_X_COLUMN_DIMENSION,
                                    ROUND((CAST(B.VL_GRID_COLUMN_DIMENSION AS NUMERIC)/CAST(D.VL_DATASET_COLUMN_DIMENSION AS NUMERIC))*100,2) AS VL_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                    B.VL_GRID_ROW_DIMENSION || ' x ' || B.VL_GRID_COLUMN_DIMENSION || ' (' || ROUND((CAST(B.VL_GRID_COLUMN_DIMENSION AS NUMERIC)/CAST(D.VL_DATASET_COLUMN_DIMENSION AS NUMERIC))*100,2) || '%)' AS VL_CONCAT_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                    B.VL_BLOCK_ROW_DIMENSION,
                                    B.VL_BLOCK_COLUMN_DIMENSION,
                                    B.VL_BLOCK_ROW_DIMENSION || ' x ' || B.VL_BLOCK_COLUMN_DIMENSION AS VL_BLOCK_ROW_X_COLUMN_DIMENSION,
                                    ROUND(B.VL_BLOCK_MEMORY_SIZE*1e-6,2) AS VL_BLOCK_MEMORY_SIZE,
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
                                    D.NR_RANDOM_STATE,
									D.VL_DATA_SPARSITY,
									D.VL_DATA_SKEWNESS
                                FROM EXPERIMENT_RAW A
                                INNER JOIN PARAMETER B ON (A.ID_PARAMETER = B.ID_PARAMETER)
                                INNER JOIN RESOURCE C ON (B.ID_RESOURCE = C.ID_RESOURCE)
                                INNER JOIN DATASET D ON (B.ID_DATASET = D.ID_DATASET)
                                WHERE
                                A.NR_ALGORITHM_ITERATION = 0
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
							X.VL_CONCAT_GRID_ROW_X_COLUMN_DIMENSION_BLOCK_SIZE_MB,
                            X.VL_CONCAT_DATASET_MB_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
							X.VL_CONCAT_BLOCK_SIZE_MB_NR_TASKS,
                            X.VL_CONCAT_BLOCK_SIZE_MB_GRID_ROW_X_COLUMN_DIMENSION,
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
                            X.NR_RANDOM_STATE,
							X.VL_DATA_SPARSITY,
                            X.VL_DATA_SKEWNESS
                        ) Y
                        ORDER BY ID_PARAMETER;"""

    if (mode == 100):

        # Get dataframe from query
        dfA = get_df_from_query(sql_queryA,conn)
        dfB = get_df_from_query(sql_queryB,conn)

        df = pd.concat([dfA, dfB])

        print(df)

        # Close connection to the database
        close_connection(cur, conn)

    else:
        # Get dataframe from query
        df = get_df_from_query(sql_query,conn)

        # Close connection to the database
        close_connection(cur, conn)

    # Generate graph (mode 2)
    generate_graph(df, dst_path_figs, ds_algorithm, ds_resource, nr_iterations, mode)

# Function that takes in a PostgreSQL query and outputs a pandas dataframe
def get_df_from_query(sql_query, conn):
    df = pd.read_sql_query(sql_query, conn)
    return df

# Function that generates a graph according to the mode
def generate_graph(df, dst_path_figs, ds_algorithm, ds_resource, nr_iterations, mode):

    # if (mode == 100):

    #     # Get dataframe from query
    #     dfA = get_df_from_query(sql_queryA,conn)
    #     # Close connection to the database
    #     close_connection(cur, conn)

    #     # Path of the "tb_experiments_motivation" table - CSV file
    #     dst_path_experiments = "/home/marcos/Dev/project/dev_env/dislib-experiments/experiments/results/tb_experiments_fig8.csv"

    #     # Reading "tb_experiments_motivation" csv table
    #     param_file = os.path.join(dst_path_experiments)
    #     df_filtered = pd.read_csv(param_file)

    # else:


    # General filtering and sorting parameters - V2 (VAR_GRID_ROW)
    df_filtered = df[
                    (df["ds_algorithm"] == ds_algorithm.upper()) # FIXED VALUE
                    & (df["nr_iterations"] == int(nr_iterations)) # FIXED VALUE
                    & (df["ds_resource"] == ds_resource.upper()) # FIXED VALUE
                    # & (df["ds_dataset"].isin(["S_128MB_1","S_512MB_1","S_2GB_1","S_8GB_1","S_32GB_1"])) # FIXED VALUE
                    # & (df["vl_grid_row_dimension"] == 2)
                    # & (df["ds_dataset"].isin(["S_2GB_1"]))
                    # & (df["ds_dataset"].isin(["S_2GB_1","S_2GB_2"])) #mode 155 and 1555 only
                    # & (df["ds_dataset"] != "S_128MB_1")
                    # & (df["ds_device"] == "GPU")
                    # VAR_GRID_SHAPE_MATMUL_1, VAR_GRID_SHAPE_MATMUL_2
                    #mode == 100
                    # & (df["ds_dataset"] == "S_8GB_1")
                    # & (df["ds_parameter_type"] == "VAR_GRID_SHAPE_MATMUL_1")
                    # MATMUL_FUNC, ADD_FUNC
                    # & (df["vl_concat_block_size_mb_grid_row_x_column_dimension"] != "8 (16 x 16)")
                    # & (df["vl_block_memory_size_percent_dataset"] != 0.4)
                    # for mode == 15 AND 16
                    # & (df["ds_parameter_type"].isin(["VAR_GRID_SHAPE_MATMUL_6","VAR_GRID_SHAPE_MATMUL_2","VAR_GRID_SHAPE_MATMUL_1","VAR_GRID_SHAPE_MATMUL_5"])) # FIXED VALUE
                    # & (df["ds_dataset"] == "S_8GB_1")
                    # & (df["ds_function"] == "MATMUL_FUNC")
                    #mode == 1555
                    & (df["ds_dataset"].isin(["S_2GB_1","S_2GB_3"])) #mode 1555 only
                    & (df["ds_parameter_type"] == "VAR_GRID_SHAPE_MATMUL_1")
                    # & (df["ds_function"] == "MATMUL_FUNC")
                    ]


    if mode == 15:

        matplotlib.rcParams.update({'font.size': 16})

        print("\nMode ",mode,": Plotting all execution times x grid and block shapes, without parameter filters")

        ds_dataset = df_filtered["ds_dataset"].unique()
        ds_dataset = '(' + ', '.join(ds_dataset) + ')'

        # x_value_list = ['vl_grid_row_x_column_dimension','vl_block_row_x_column_dimension','vl_grid_row_dimension','vl_block_row_dimension','vl_concat_grid_row_x_column_dimension_block_size_mb']

        # x_value_list = ['vl_grid_row_dimension','vl_block_row_dimension']

        # x_value_list = ['vl_concat_block_size_mb_grid_row_x_column_dimension']

        # x_value_list = ['vl_concat_dataset_mb_block_memory_size_percent_dataset']

        x_value_list = ['vl_concat_block_size_mb_grid_row_x_column_dimension']

        # x_value_list = ['vl_block_memory_size','vl_concat_block_size_mb_grid_row_x_column_dimension','vl_concat_block_size_mb_nr_tasks']


        for x_value in x_value_list:

            if x_value == 'vl_grid_row_x_column_dimension':
                x_value_title = 'Grid Shape'

            elif x_value == 'vl_concat_grid_row_x_column_dimension_block_size_mb':
                x_value_title = 'Grid Shape Dimension (Block Size MB)'

            elif x_value == 'vl_concat_block_size_mb_grid_row_x_column_dimension':
                x_value_title = 'Block Size MB (Grid Dimension)'

            elif x_value == 'vl_concat_dataset_mb_block_memory_size_percent_dataset':
                x_value_title = 'Dataset MB (Block Size % Dataset)'

            elif x_value == 'vl_block_row_x_column_dimension':
                x_value_title = 'Block Shape'

            elif x_value == 'vl_grid_row_dimension':
                x_value_title = 'Grid Row'

            elif x_value == 'vl_block_row_dimension':
                x_value_title = 'Block Row'

            elif x_value == 'vl_block_memory_size':
                x_value_title = 'Block Size B'

            df_filtered_mean = df_filtered.groupby(['ds_device', x_value], as_index=False).mean()

            df_filtered_mean_cpu = df_filtered_mean[(df_filtered_mean.ds_device=="CPU")]
            df_filtered_mean_gpu = df_filtered_mean[(df_filtered_mean.ds_device=="GPU")]

            df_filtered_mean_cpu.name = 'df_filtered_mean_cpu'
            df_filtered_mean_gpu.name = 'df_filtered_mean_gpu'

            if (x_value == 'vl_grid_row_x_column_dimension') | (x_value == 'vl_concat_grid_row_x_column_dimension_block_size_mb'):
                df_filtered_mean_cpu.sort_values('vl_grid_row_dimension', inplace=True)
                df_filtered_mean_gpu.sort_values('vl_grid_row_dimension', inplace=True)
                # df_filtered_mean_cpu.sort_values(by=['vl_grid_row_dimension'])
                # df_filtered_mean_gpu.sort_values(by=['vl_grid_row_dimension'])

            if (x_value == 'vl_block_row_x_column_dimension') | (x_value == 'vl_concat_block_size_mb_grid_row_x_column_dimension') | (x_value == 'vl_block_memory_size'):
                df_filtered_mean_cpu.sort_values('vl_block_row_dimension', inplace=True)
                df_filtered_mean_gpu.sort_values('vl_block_row_dimension', inplace=True)
                # df_filtered_mean_cpu.sort_values(by=['vl_block_row_dimension'])
                # df_filtered_mean_gpu.sort_values(by=['vl_block_row_dimension'])

            if (x_value == 'vl_concat_dataset_mb_block_memory_size_percent_dataset'):
                df_filtered_mean_cpu.sort_values(['vl_dataset_memory_size','vl_block_row_dimension'], inplace=True)
                df_filtered_mean_gpu.sort_values(['vl_dataset_memory_size','vl_block_row_dimension'], inplace=True)

            # VL_TOTAL_EXECUTION_TIME
            fig, ax = plt.subplots()
            ax.plot(df_filtered_mean_cpu['vl_concat_block_size_mb_grid_row_x_column_dimension'], df_filtered_mean_cpu['vl_total_execution_time'], color='C1', linestyle = 'dotted', label='CPU', zorder=3, linewidth=2.5)
            ax.plot(df_filtered_mean_gpu['vl_concat_block_size_mb_grid_row_x_column_dimension'], df_filtered_mean_gpu['vl_total_execution_time'], color='C1', linestyle = 'solid', label='GPU', zorder=3, linewidth=2.5)
            ax.set_xlabel(x_value_title)
            ax.set_ylabel('Parallel Tasks Average Time (s)')
            ax.legend()
            plt.grid(zorder=0)
            ax.tick_params(axis='x', labelrotation = 45)
            fig.autofmt_xdate(rotation=45, ha='right')  # Rotate the entire x-axis labels
            # # NORMAL SCALE
            plt.ylim([0, 2500])
            # LOG SCALE
            # plt.ylim([0, 265])
            # plt.ylim([1e-1, 1e3])
            # plt.yscale("log")
            # plt.savefig(dst_path_figs+'mode_'+str(mode)+'_avg_total_execution_time_per_'+x_value+'_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_avg_total_execution_time_per_'+x_value+'_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.pdf',bbox_inches='tight',dpi=100)


        # #     # plt.legend(loc='best')
        # #     # df_filtered_mean_cpu.plot(x = x_value, y = 'vl_total_execution_time', kind = 'line', color='C0', linestyle = 'dotted', ax=ax, label='CPU', zorder=3)
        # #     # df_filtered_mean_gpu.plot(x = x_value, y = 'vl_total_execution_time', kind = 'line', color='C0', linestyle = 'solid', ax=ax, label='GPU', zorder=3)
        # #     # plt.xlabel(x_value_title)
        # #     # plt.ylabel('Average Total Execution Time (s)')
        # #     # plt.title('Average Total Execution Time x '+x_value_title+' ' + ds_dataset,fontstyle='italic',fontweight="bold")
        # #     # plt.grid(zorder=0)
        # #     # ax.tick_params(axis='x', labelrotation = 90)
        # #     # # # NORMAL SCALE
        # #     # # plt.ylim([0, 1000])
        # #     # # LOG SCALE
        # #     # plt.ylim([1e0, 1e4])
        # #     # plt.yscale("log")
        # #     # plt.savefig(dst_path_figs+'mode_'+str(mode)+'_avg_total_execution_time_per_'+x_value+'_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)


        #     # # BREAKING VL_INTER_TASK_EXECUTION_TIME = VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC + VL_INTER_TASK_OVERHEAD_TIME
        #     # fig = plt.figure()
        #     # ax = plt.gca()
        #     # for frame in [df_filtered_mean_cpu, df_filtered_mean_gpu]:
        #     #     if frame.name == 'df_filtered_mean_cpu':
        #     #         # plt.xticks(frame[x_value], frame['vl_grid_row_x_column_dimension'])
        #     #         plt.plot(frame[x_value], frame['vl_inter_task_execution_time'], color='C1', linestyle = 'dotted', label='$T_{w\_inter}$ CPU', zorder=3)
        #     #         # plt.plot(frame[x_value], frame['vl_inter_task_overhead_time'], color='C9', linestyle = 'dotted', label='$T_{o\_inter}$ CPU', zorder=3)
        #     #         # plt.plot(frame[x_value], frame['vl_intra_task_execution_time_full_func'], color='C2', linestyle = 'dotted', label='$T_{w\_intra}$ CPU', zorder=3)
        #     #     if frame.name == 'df_filtered_mean_gpu':
        #     #         # plt.xticks(frame[x_value], frame['vl_grid_row_x_column_dimension'])
        #     #         plt.plot(frame[x_value], frame['vl_inter_task_execution_time'], color='C1', linestyle = 'solid', label='$T_{w\_inter}$ GPU', zorder=3)
        #     #         # plt.plot(frame[x_value], frame['vl_inter_task_overhead_time'], color='C9', linestyle = 'solid', label='$T_{o\_inter}$ GPU', zorder=3)
        #     #         # plt.plot(frame[x_value], frame['vl_intra_task_execution_time_full_func'], color='C2', linestyle = 'solid', label='$T_{w\_intra}$ GPU', zorder=3)

        #     # plt.legend(loc='best')
        #     # plt.xlabel(x_value_title)
        #     # plt.ylabel('Time (s)')
        #     # plt.title('$T_{w\_inter}$ Time Composition x '+x_value_title+' ' + ds_dataset,fontstyle='italic',fontweight="bold")
        #     # plt.grid(zorder=0)
        #     # ax.tick_params(axis='x', labelrotation = 90)
        #     # # # # NORMAL SCALE
        #     # # # plt.ylim([0.0000, 265.0000])
        #     # # if x_value == 'vl_grid_row_dimension' or x_value == 'vl_block_row_dimension':
        #     # #     ax.ticklabel_format(scilimits=(-5, 1))
        #     # # # LOG SCALE
        #     # plt.ylim([1e-1, 1e4])
        #     # plt.yscale("log")
        #     # plt.savefig(dst_path_figs+'mode_'+str(mode)+'_avg_inter_task_composition_time_per_'+x_value+'_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

            # # # BREAKING VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC = VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC + VL_COMMUNICATION_TIME + VL_ADDITIONAL_TIME
            # fig = plt.figure()
            # ax = plt.gca()
            # for frame in [df_filtered_mean_cpu, df_filtered_mean_gpu]:
            #     if frame.name == 'df_filtered_mean_cpu':
            #         # plt.xticks(frame[x_value], frame['vl_grid_row_x_column_dimension'])
            #         # plt.plot(frame[x_value], frame['vl_intra_task_execution_time_full_func'], color='C2', linestyle = 'dotted', label='$T_{w\_intra}$ CPU', zorder=3)
            #         plt.plot(frame[x_value], frame['vl_intra_task_execution_time_device_func'], color='C3', linestyle = 'dotted', label='$T_{p\_intra}$ CPU', zorder=3)
            #         # plt.plot(frame[x_value], frame['vl_communication_time'], color='C4', linestyle = 'dotted', label='$T_{c\_intra}$ CPU', zorder=3)
            #         # plt.plot(frame[x_value], frame['vl_additional_time'], color='C8', linestyle = 'dotted', label='$T_{s\_intra}$ CPU', zorder=3)
            #     if frame.name == 'df_filtered_mean_gpu':
            #         # plt.xticks(frame[x_value], frame['vl_grid_row_x_column_dimension'])
            #         # plt.plot(frame[x_value], frame['vl_intra_task_execution_time_full_func'], color='C2', linestyle = 'solid', label='$T_{w\_intra}$ GPU', zorder=3)
            #         plt.plot(frame[x_value], frame['vl_intra_task_execution_time_device_func'], color='C3', linestyle = 'solid', label='$T_{p\_intra}$ GPU', zorder=3)
            #         plt.plot(frame[x_value], frame['vl_communication_time'], color='C4', linestyle = 'solid', label='$T_{c\_intra}$ GPU', zorder=3)
            #         # plt.plot(frame[x_value], frame['vl_additional_time'], color='C8', linestyle = 'solid', label='$T_{s\_intra}$ GPU', zorder=3)

            # plt.legend(loc='best')
            # plt.xlabel(x_value_title)
            # plt.ylabel('Time (s)')
            # plt.title('$T_{w\_intra}$ Time Composition x '+x_value_title+' ' + ds_dataset,fontstyle='italic',fontweight="bold")
            # plt.grid(zorder=0)
            # ax.tick_params(axis='x', labelrotation = 90)
            # # # # NORMAL SCALE
            # # # plt.ylim([0.0000, 18.0])
            # # if x_value == 'vl_grid_row_dimension' or x_value == 'vl_block_row_dimension':
            # #     ax.ticklabel_format(scilimits=(-5, 1))
            # # # LOG SCALE
            # plt.ylim([1e-3, 1e3])
            # plt.yscale("log")
            # plt.savefig(dst_path_figs+'mode_'+str(mode)+'_avg_intra_task_composition_time_per_'+x_value+'_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)


            # # STANDARD DEVIATION BREAKING VL_TOTAL_TASK_EXECUTION_TIME
            # fig = plt.figure()
            # ax = plt.gca()
            # for frame in [df_filtered_mean_cpu, df_filtered_mean_gpu]:
            #     if frame.name == 'df_filtered_mean_cpu':
            #         plt.plot(frame[x_value], frame['vl_std_total_execution_time'], color='C0', linestyle = 'dotted', label='Std. dev. CPU', zorder=3)
            #     if frame.name == 'df_filtered_mean_gpu':
            #         plt.plot(frame[x_value], frame['vl_std_total_execution_time'], color='C0', linestyle = 'solid', label='Std. dev. GPU', zorder=3)
            # plt.legend(loc='best')
            # plt.xlabel(x_value_title)
            # plt.ylabel('Time (s)')
            # plt.title('$T_{w\_total}$ Std. dev. x '+x_value_title+' ' + ds_dataset,fontstyle='italic',fontweight="bold")
            # plt.grid(zorder=0)
            # ax.tick_params(axis='x', labelrotation = 90)
            # # NORMAL SCALE
            # # plt.ylim([0.0, 40.0])
            # plt.ylim([0.0, 165.0])
            # plt.savefig(dst_path_figs+'mode_'+str(mode)+'_stddev_inter_task_composition_time_per_'+x_value+'_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

    elif mode == 16:
        matplotlib.rcParams.update({'font.size': 18})

        print("\nMode ",mode,": Plotting all execution times x grid and block shapes, without parameter filters")
        
        x = 'vl_concat_block_size_mb_grid_row_x_column_dimension'
        x_value = "vl_concat_block_size_mb_grid_row_x_column_dimension"
        x_value_title = 'Block size MB'

        df_filtered_mean = df_filtered.groupby(['ds_device', 'ds_parameter_type', x_value], as_index=False).mean()

        # Matmul Time 
        # local order
        df_filtered_mean_left_top_cpu = df_filtered_mean[(df_filtered_mean.ds_device=='CPU') & (df_filtered_mean.ds_parameter_type=='VAR_GRID_SHAPE_MATMUL_6')]
        df_filtered_mean_left_top_gpu = df_filtered_mean[(df_filtered_mean.ds_device=='GPU') & (df_filtered_mean.ds_parameter_type=='VAR_GRID_SHAPE_MATMUL_6')]
        # local data
        df_filtered_mean_right_top_cpu = df_filtered_mean[(df_filtered_mean.ds_device=='CPU') & (df_filtered_mean.ds_parameter_type=='VAR_GRID_SHAPE_MATMUL_2')]
        df_filtered_mean_right_top_gpu = df_filtered_mean[(df_filtered_mean.ds_device=='GPU') & (df_filtered_mean.ds_parameter_type=='VAR_GRID_SHAPE_MATMUL_2')]
        
        # Matmul Time
        # shared order
        df_filtered_mean_left_bottom_cpu = df_filtered_mean[(df_filtered_mean.ds_device=='CPU') & (df_filtered_mean.ds_parameter_type=='VAR_GRID_SHAPE_MATMUL_1')]
        df_filtered_mean_left_bottom_gpu = df_filtered_mean[(df_filtered_mean.ds_device=='GPU') & (df_filtered_mean.ds_parameter_type=='VAR_GRID_SHAPE_MATMUL_1')]
        # local order
        df_filtered_mean_right_bottom_cpu = df_filtered_mean[(df_filtered_mean.ds_device=='CPU') & (df_filtered_mean.ds_parameter_type=='VAR_GRID_SHAPE_MATMUL_5')]
        df_filtered_mean_right_bottom_gpu = df_filtered_mean[(df_filtered_mean.ds_device=='GPU') & (df_filtered_mean.ds_parameter_type=='VAR_GRID_SHAPE_MATMUL_5')]
        
        df_filtered_mean_left_top_cpu.name = 'df_filtered_mean_left_top_cpu'
        df_filtered_mean_left_top_gpu.name = 'df_filtered_mean_left_top_gpu'
        df_filtered_mean_right_top_cpu.name = 'df_filtered_mean_right_top_cpu'
        df_filtered_mean_right_top_gpu.name = 'df_filtered_mean_right_top_gpu'
        df_filtered_mean_left_bottom_cpu.name = 'df_filtered_mean_left_bottom_cpu'
        df_filtered_mean_left_bottom_gpu.name = 'df_filtered_mean_left_bottom_gpu'
        df_filtered_mean_right_bottom_cpu.name = 'df_filtered_mean_right_bottom_cpu'
        df_filtered_mean_right_bottom_gpu.name = 'df_filtered_mean_right_bottom_gpu'

        # Times
        df1_cpu = df_filtered_mean_left_top_cpu.sort_values(by=["vl_block_row_dimension"], ascending=[True])
        df1_gpu = df_filtered_mean_left_top_gpu.sort_values(by=["vl_block_row_dimension"], ascending=[True])
        df2_cpu = df_filtered_mean_right_top_cpu.sort_values(by=["vl_block_row_dimension"], ascending=[True])
        df2_gpu = df_filtered_mean_right_top_gpu.sort_values(by=["vl_block_row_dimension"], ascending=[True])
        df3_cpu = df_filtered_mean_left_bottom_cpu.sort_values(by=["vl_block_row_dimension"], ascending=[True])
        df3_gpu = df_filtered_mean_left_bottom_gpu.sort_values(by=["vl_block_row_dimension"], ascending=[True])
        df4_cpu = df_filtered_mean_right_bottom_cpu.sort_values(by=["vl_block_row_dimension"], ascending=[True])
        df4_gpu = df_filtered_mean_right_bottom_gpu.sort_values(by=["vl_block_row_dimension"], ascending=[True])

        fig, axs = plt.subplots(1, 4, figsize=(24, 4), sharey='row', sharex='col')

      
        # Plot the first chart (top-left - Bar chart)
        axs[0].plot(df1_cpu[x_value],df1_cpu['vl_total_execution_time'], color='C1', linestyle = 'dotted', label='CPU', zorder=3, linewidth=2.5)
        axs[0].plot(df1_gpu[x_value],df1_gpu['vl_total_execution_time'], color='C1', linestyle = 'solid', label='GPU', zorder=3, linewidth=2.5)
        axs[0].set_xlabel('Block size MB (Grid Dimension)')
        axs[0].legend(loc='upper left', frameon=False, labelspacing=0.01, ncol=2, borderpad=0.1)
        axs[0].set_ylabel('P. Tasks Average Time (s)')  # Add y-axis label
        axs[0].set_ylim([0, 2500])
        axs[0].grid(zorder=0,axis='y')
        axs[0].set_title('Local disk, task generation order', pad=10)

        # Plot the second chart (top-right - Bar chart)
        axs[1].plot(df2_cpu[x_value],df2_cpu['vl_total_execution_time'], color='C1', linestyle = 'dotted', zorder=3, linewidth=2.5)
        axs[1].plot(df2_gpu[x_value],df2_gpu['vl_total_execution_time'], color='C1', linestyle = 'solid', zorder=3, linewidth=2.5)
        axs[1].legend(loc='upper left', frameon=False, labelspacing=0.01, ncol=2, borderpad=0.1)
        axs[1].set_ylim([0, 2500])
        axs[1].grid(zorder=0,axis='y')
        axs[1].set_title('Local disk, data locality', pad=10)

        # Plot the third chart (bottom-left - Line chart)
        axs[2].plot(df3_cpu[x_value],df3_cpu['vl_total_execution_time'], color='C1', linestyle = 'dotted', zorder=3, linewidth=2.5)
        axs[2].plot(df3_gpu[x_value],df3_gpu['vl_total_execution_time'], color='C1', linestyle = 'solid', zorder=3, linewidth=2.5)
        axs[2].set_ylim([0, 2500])
        axs[2].tick_params(axis='x', labelrotation = 35)
        axs[2].grid(zorder=0,axis='y')
        axs[2].set_title('Shared disk, task generation order', pad=10)
        
        
        # Plot the fourth chart (bottom-center - Line chart)
        axs[3].plot(df4_cpu[x_value],df4_cpu['vl_total_execution_time'], color='C1', linestyle = 'dotted', zorder=3, linewidth=2.5)
        axs[3].plot(df4_gpu[x_value],df4_gpu['vl_total_execution_time'], color='C1', linestyle = 'solid', zorder=3, linewidth=2.5)
        axs[3].set_ylim([0, 2500])
        axs[3].tick_params(axis='x', labelrotation = 35)
        axs[3].grid(zorder=0,axis='y')
        axs[3].set_title('Shared disk, data locality', pad=10)
        
        # Adjust layout to prevent clipping of titles and labels
        plt.tight_layout()

        fig.autofmt_xdate(rotation=35, ha='right')

        # Adjust spacing
        plt.subplots_adjust(wspace=0.01, hspace=0.28)
        
        # Show the plots
        # plt.show()
        plt.savefig(dst_path_figs+'FIG10.png',bbox_inches='tight',dpi=100)
        plt.savefig(dst_path_figs+'FIG10.pdf',bbox_inches='tight',dpi=100)

    elif mode == 155:

        print("\nMode ",mode,": Plotting intra-task execution times x grid and block shapes, without parameter filters")

        ds_dataset = df_filtered["ds_dataset"].unique()
        ds_dataset = '(' + ', '.join(ds_dataset) + ')'

        x_value_list = ['vl_concat_block_size_mb_grid_row_x_column_dimension']

        for x_value in x_value_list:

            if x_value == 'vl_concat_grid_row_x_column_dimension_block_size_mb':
                x_value_title = 'Grid Shape (Block Size MB)'
            elif x_value == 'vl_concat_block_size_mb_grid_row_x_column_dimension':
                x_value_title = 'Block Size MB (Grid Shape)'

            df_filtered_mean = df_filtered.groupby(['ds_device', 'ds_dataset', x_value], as_index=False).mean()

            df_filtered_mean_cpu_dense = df_filtered_mean[(df_filtered_mean.ds_dataset=="S_2GB_1") & (df_filtered_mean.ds_device=="CPU")]
            df_filtered_mean_gpu_dense = df_filtered_mean[(df_filtered_mean.ds_dataset=="S_2GB_1") & (df_filtered_mean.ds_device=="GPU")]

            df_filtered_mean_cpu_sparse = df_filtered_mean[(df_filtered_mean.ds_dataset=="S_2GB_2") & (df_filtered_mean.ds_device=="CPU")]
            df_filtered_mean_gpu_sparse = df_filtered_mean[(df_filtered_mean.ds_dataset=="S_2GB_2") & (df_filtered_mean.ds_device=="GPU")]

            df_filtered_mean_cpu_dense.name = 'df_filtered_mean_cpu_dense'
            df_filtered_mean_gpu_dense.name = 'df_filtered_mean_gpu_dense'
            df_filtered_mean_cpu_sparse.name = 'df_filtered_mean_cpu_sparse'
            df_filtered_mean_gpu_sparse.name = 'df_filtered_mean_gpu_sparse'

            if (x_value == 'vl_grid_row_x_column_dimension') | (x_value == 'vl_concat_grid_row_x_column_dimension_block_size_mb'):
                df_filtered_mean_cpu_dense.sort_values('vl_grid_row_dimension', inplace=True)
                df_filtered_mean_gpu_dense.sort_values('vl_grid_row_dimension', inplace=True)
                df_filtered_mean_cpu_sparse.sort_values('vl_grid_row_dimension', inplace=True)
                df_filtered_mean_gpu_sparse.sort_values('vl_grid_row_dimension', inplace=True)

            if (x_value == 'vl_block_row_x_column_dimension') | (x_value == 'vl_concat_block_size_mb_grid_row_x_column_dimension'):
                df_filtered_mean_cpu_dense.sort_values('vl_block_row_dimension', inplace=True)
                df_filtered_mean_gpu_dense.sort_values('vl_block_row_dimension', inplace=True)
                df_filtered_mean_cpu_sparse.sort_values('vl_block_row_dimension', inplace=True)
                df_filtered_mean_gpu_sparse.sort_values('vl_block_row_dimension', inplace=True)

            # # BREAKING (FULL) VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC = VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC + VL_COMMUNICATION_TIME + VL_ADDITIONAL_TIME
            fig = plt.figure()
            ax = plt.gca()
            for frame in [df_filtered_mean_cpu_dense, df_filtered_mean_gpu_dense, df_filtered_mean_cpu_sparse, df_filtered_mean_gpu_sparse]:
                # if frame.name == 'df_filtered_mean_cpu_dense':
                #     plt.plot(frame[x_value], frame['vl_intra_task_execution_time_full_func'], color='C2', linestyle = 'dotted', label='$T_{w\_intra}$ CPU dense', zorder=3)
                if frame.name == 'df_filtered_mean_gpu_dense':
                    plt.plot(frame[x_value], frame['vl_intra_task_execution_time_full_func'], color='C2', linestyle = 'solid', label='$T_{w\_intra}$ GPU dense', zorder=3)
                    # plt.plot(frame[x_value], frame['vl_intra_task_execution_time_device_func'], color='C3', linestyle = 'solid', label='$T_{p\_intra}$ GPU dense', zorder=3)
                    # plt.plot(frame[x_value], frame['vl_communication_time'], color='C4', linestyle = 'solid', label='$T_{c\_intra}$ GPU dense', zorder=3)
                # if frame.name == 'df_filtered_mean_cpu_sparse':
                #     plt.plot(frame[x_value], frame['vl_intra_task_execution_time_full_func'], color='C2', linestyle = 'dashed', label='$T_{w\_intra}$ CPU sparse', zorder=3)
                if frame.name == 'df_filtered_mean_gpu_sparse':
                    plt.plot(frame[x_value], frame['vl_intra_task_execution_time_full_func'], color='C2', linestyle = 'dashdot', label='$T_{w\_intra}$ GPU sparse', zorder=3)
                    # plt.plot(frame[x_value], frame['vl_intra_task_execution_time_device_func'], color='C3', linestyle = 'dashdot', label='$T_{p\_intra}$ GPU sparse', zorder=3)
                    # plt.plot(frame[x_value], frame['vl_communication_time'], color='C4', linestyle = 'dashdot', label='$T_{c\_intra}$ GPU sparse', zorder=3)

            plt.legend(loc='best')
            plt.xlabel(x_value_title)
            plt.ylabel('Time (s)')
            plt.title('$T_{w\_intra}$ Time Composition x '+x_value_title+' ' + ds_dataset,fontstyle='italic',fontweight="bold")
            plt.grid(zorder=0)
            ax.tick_params(axis='x', labelrotation = 90)
            # # # NORMAL SCALE
            # # plt.ylim([0.0000, 18.0])
            # if x_value == 'vl_grid_row_dimension' or x_value == 'vl_block_row_dimension':
            #     ax.ticklabel_format(scilimits=(-5, 1))
            # # LOG SCALE
            plt.ylim([1e-3, 1e4])
            plt.yscale("log")
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_avg_intra_task_composition_time_per_'+x_value+'_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)


            # # BREAKING (CPU) VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC = VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC + VL_COMMUNICATION_TIME + VL_ADDITIONAL_TIME
            fig = plt.figure()
            ax = plt.gca()
            for frame in [df_filtered_mean_cpu_dense, df_filtered_mean_gpu_dense, df_filtered_mean_cpu_sparse, df_filtered_mean_gpu_sparse]:
                if frame.name == 'df_filtered_mean_cpu_dense':
                    plt.plot(frame[x_value], frame['vl_intra_task_execution_time_full_func'], color='C2', linestyle = 'dotted', label='$T_{w\_intra}$ CPU dense', zorder=3)
                if frame.name == 'df_filtered_mean_cpu_sparse':
                    plt.plot(frame[x_value], frame['vl_intra_task_execution_time_full_func'], color='C2', linestyle = 'dashed', label='$T_{w\_intra}$ CPU sparse', zorder=3)

            plt.legend(loc='best')
            plt.xlabel(x_value_title)
            plt.ylabel('Time (s)')
            plt.title('$T_{w\_intra}$ Time Composition x '+x_value_title+' ' + ds_dataset,fontstyle='italic',fontweight="bold")
            plt.grid(zorder=0)
            ax.tick_params(axis='x', labelrotation = 90)
            # # # NORMAL SCALE
            # # plt.ylim([0.0000, 18.0])
            # if x_value == 'vl_grid_row_dimension' or x_value == 'vl_block_row_dimension':
            #     ax.ticklabel_format(scilimits=(-5, 1))
            # # LOG SCALE
            # plt.ylim([1e-3, 1e4])
            # plt.yscale("log")
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_CPU_avg_intra_task_composition_time_per_'+x_value+'_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)


            # # BREAKING (GPU) VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC = VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC + VL_COMMUNICATION_TIME + VL_ADDITIONAL_TIME
            fig = plt.figure()
            ax = plt.gca()
            for frame in [df_filtered_mean_cpu_dense, df_filtered_mean_gpu_dense, df_filtered_mean_cpu_sparse, df_filtered_mean_gpu_sparse]:
                if frame.name == 'df_filtered_mean_gpu_dense':
                    plt.plot(frame[x_value], frame['vl_intra_task_execution_time_full_func'], color='C2', linestyle = 'solid', label='$T_{w\_intra}$ GPU dense', zorder=3)
                if frame.name == 'df_filtered_mean_gpu_sparse':
                    plt.plot(frame[x_value], frame['vl_intra_task_execution_time_full_func'], color='C2', linestyle = 'dashdot', label='$T_{w\_intra}$ GPU sparse', zorder=3)

            plt.legend(loc='best')
            plt.xlabel(x_value_title)
            plt.ylabel('Time (s)')
            plt.title('$T_{w\_intra}$ Time Composition x '+x_value_title+' ' + ds_dataset,fontstyle='italic',fontweight="bold")
            plt.grid(zorder=0)
            ax.tick_params(axis='x', labelrotation = 90)
            # # # NORMAL SCALE
            # # plt.ylim([0.0000, 18.0])
            # if x_value == 'vl_grid_row_dimension' or x_value == 'vl_block_row_dimension':
            #     ax.ticklabel_format(scilimits=(-5, 1))
            # # LOG SCALE
            # plt.ylim([1e-3, 1e4])
            # plt.yscale("log")
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_GPU_avg_intra_task_composition_time_per_'+x_value+'_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)


    # FOR DATA SKEWNESS
    elif mode == 1555:

        matplotlib.rcParams.update({'font.size': 18})

        print("\nMode ",mode,": Plotting intra-task execution times x grid and block shapes, without parameter filters")

        ds_dataset = df_filtered["ds_dataset"].unique()
        ds_dataset = '(' + ', '.join(ds_dataset) + ')'
        
        # Define the size of the overall chart area in inches
        chart_width = 6.4
        chart_height = 4.8

        # Create a figure with a fixed size
        fig = plt.figure(figsize=(chart_width, chart_height))

        # Define the size and position of the plot area within the chart
        #BEST
        # left_margin = 0.25
        # bottom_margin = 0.08
        # plot_width = 1
        # plot_height = 1

        left_margin = 0.15
        bottom_margin = -0.15
        plot_width = 1
        plot_height = 1


        # Calculate the position of the plot area
        plot_left = left_margin
        plot_bottom = bottom_margin
        plot_right = left_margin + plot_width
        plot_top = bottom_margin + plot_height

        # Create the plot within the defined plot area
        ax = fig.add_axes([plot_left, plot_bottom, plot_width, plot_height])


        x_value_list = ['vl_concat_block_size_mb_grid_row_x_column_dimension']

        for x_value in x_value_list:

            if x_value == 'vl_concat_grid_row_x_column_dimension_block_size_mb':
                x_value_title = 'Grid Shape (Block Size MB)'
            elif x_value == 'vl_concat_block_size_mb_grid_row_x_column_dimension':
                x_value_title = 'Block Size MB (Grid Shape)'
            
            df_filtered_mean = df_filtered.groupby([x_value,'device_skewness'], as_index=False).mean()

            df_filtered_mean.sort_values(by=['vl_grid_row_dimension'], ascending=[False], inplace=True)
            
            df_filtered_mean = df_filtered_mean[[x_value,'device_skewness','vl_total_execution_time','vl_intra_task_execution_time_full_func','vl_intra_task_execution_time_device_func']]
            

            plt.figure(2)
            X_axis = np.arange(len(df_filtered_mean[x_value].drop_duplicates()))
            plt.bar(X_axis - 0.2, df_filtered_mean[(df_filtered_mean.device_skewness=="CPU NOT SKEWED")]["vl_intra_task_execution_time_full_func"], 0.3, label = "Dataset 0% Skewed", color='C0', alpha = 0.5, zorder=3)
            plt.bar(X_axis + 0.2, df_filtered_mean[(df_filtered_mean.device_skewness=="CPU SKEWED")]["vl_intra_task_execution_time_full_func"], 0.3, label = "Dataset 50% Skewed", color='C0', alpha = 0.5, hatch='oo', zorder=3)
            # plt.bar(X_axis - 0.2, df_filtered_mean[(df_filtered_mean.device_skewness=="CPU NOT SKEWED")]["vl_total_execution_time"], 0.3, label = "P. Task 0% Skew.", color='C1', alpha = 0.5, zorder=1)
            # plt.bar(X_axis - 0.2, df_filtered_mean[(df_filtered_mean.device_skewness=="CPU NOT SKEWED")]["vl_intra_task_execution_time_full_func"], 0.3, label = "Usr. code 0% Skew.", color='C1', alpha = 0.5, zorder=2)
            # plt.bar(X_axis - 0.2, df_filtered_mean[(df_filtered_mean.device_skewness=="CPU NOT SKEWED")]["vl_intra_task_execution_time_device_func"], 0.3, label = "P. Frac 0% Skew.", color='C0', alpha = 0.5, zorder=3)
            # plt.bar(X_axis + 0.2, df_filtered_mean[(df_filtered_mean.device_skewness=="CPU SKEWED")]["vl_total_execution_time"], 0.3, label = "P. Task 50% Skew.", color='C1', alpha = 0.5, hatch='oo', zorder=1)
            # plt.bar(X_axis + 0.2, df_filtered_mean[(df_filtered_mean.device_skewness=="CPU SKEWED")]["vl_intra_task_execution_time_full_func"], 0.3, label = "Usr. code 50% Skew.", color='C1', alpha = 0.5, hatch='oo', zorder=2)
            # plt.bar(X_axis + 0.2, df_filtered_mean[(df_filtered_mean.device_skewness=="CPU SKEWED")]["vl_intra_task_execution_time_device_func"], 0.3, label = "P. Frac 50% Skew.", color='C0', alpha = 0.5, hatch='oo', zorder=3)
            plt.xticks(X_axis, df_filtered_mean[x_value].drop_duplicates(), rotation=30)
            # plt.xlabel(x_value_title)
            plt.ylabel('User Code Exec. Time CPU (s)')
            # plt.title('$T_{w\_intra}$ Time x '+x_value_title+' ' + ds_dataset,fontstyle='italic',fontweight="bold")
            plt.grid(zorder=0,axis='y')
            plt.figlegend(loc=(0.18,0.78), ncol=1, frameon=False)
            # plt.ylim([0, 2.5])
            # plt.yscale("log")
            # fig.autofmt_xdate(rotation=30, ha='right')  # Rotate the entire x-axis labels
            plt.xticks(rotation=30, ha='right')
            # plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=len(df_filtered_mean[x_value].drop_duplicates()))
            # plt.savefig(dst_path_figs+'mode_'+str(mode)+'_CPU_avg_intra_task_composition_time_per_'+x_value+'_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_CPU_avg_intra_task_composition_time_per_'+x_value+'_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.pdf',bbox_inches='tight',dpi=100)


            plt.figure(3)
            X_axis = np.arange(len(df_filtered_mean[x_value].drop_duplicates()))
            plt.bar(X_axis - 0.2, df_filtered_mean[(df_filtered_mean.device_skewness=="GPU NOT SKEWED")]["vl_intra_task_execution_time_full_func"], 0.3, label = "Dataset 0% Skewed", color='C0', alpha = 0.5, zorder=3)
            plt.bar(X_axis + 0.2, df_filtered_mean[(df_filtered_mean.device_skewness=="GPU SKEWED")]["vl_intra_task_execution_time_full_func"], 0.3, label = "Dataset 50% Skewed", color='C0', alpha = 0.5, hatch='oo', zorder=3)
            plt.xticks(X_axis, df_filtered_mean[x_value].drop_duplicates(), rotation=30)
            # plt.xlabel(x_value_title)
            plt.ylabel('User Code Exec. Time GPU (s)')
            # plt.title('$T_{w\_intra}$ Time x '+x_value_title+' ' + ds_dataset,fontstyle='italic',fontweight="bold")
            plt.grid(zorder=0,axis='y')
            # plt.figlegend(loc=(0.18,0.78), ncol=1, frameon=False)
            # plt.ylim([0, 2.5])
            # plt.yscale("log")
            # fig.autofmt_xdate(rotation=30, ha='right')  # Rotate the entire x-axis labels
            plt.xticks(rotation=30, ha='right')
            # plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=len(df_filtered_mean[x_value].drop_duplicates()))
            # plt.savefig(dst_path_figs+'mode_'+str(mode)+'_GPU_avg_intra_task_composition_time_per_'+x_value+'_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_GPU_avg_intra_task_composition_time_per_'+x_value+'_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.pdf',bbox_inches='tight',dpi=100)



    # FOR DATA SKEWNESS
    elif mode == 1556:

        matplotlib.rcParams.update({'font.size': 18})

        print("\nMode ",mode,": Plotting intra-task execution times x grid and block shapes, without parameter filters")

        ds_dataset = df_filtered["ds_dataset"].unique()
        ds_dataset = '(' + ', '.join(ds_dataset) + ')'

        x_value = 'vl_concat_block_size_mb_grid_row_x_column_dimension'

        x_value_title = 'Block Size MB (Grid Shape)'

        df_filtered_mean = df_filtered.groupby([x_value,'device_skewness'], as_index=False).mean()

        df_filtered_mean.sort_values(by=['vl_grid_row_dimension'], ascending=[False], inplace=True)
        
        df_filtered_mean = df_filtered_mean[[x_value,'device_skewness','vl_total_execution_time','vl_intra_task_execution_time_full_func','vl_intra_task_execution_time_device_func']]
        
        X_axis = np.arange(len(df_filtered_mean[x_value].drop_duplicates()))
        
        fig, axs = plt.subplots(2, 1, figsize=(7, 8), sharey='row', sharex='col')

        # Plot the first chart (top - Bar chart)
        axs[0].bar(X_axis - 0.2,df_filtered_mean[(df_filtered_mean.device_skewness=="CPU NOT SKEWED")]["vl_intra_task_execution_time_full_func"], 0.3, label = "0% Skewness", color='C0', alpha = 0.5, zorder=3)
        axs[0].bar(X_axis + 0.2,df_filtered_mean[(df_filtered_mean.device_skewness=="CPU SKEWED")]["vl_intra_task_execution_time_full_func"], 0.3, label = "50% Skewness", color='red', alpha = 0.5, hatch='oo', zorder=3)
        axs[0].legend(loc=(-0.000,0.99), frameon=False, labelspacing=0.01, ncol=2, borderpad=0.1)
        axs[0].set_ylabel('Usr. Code Time CPU (s)')  # Add y-axis label
        axs[0].grid(zorder=0,axis='y')
        axs[0].set_title('Matmul', pad=20)
        axs[0].set_xticks(X_axis, df_filtered_mean[x_value].drop_duplicates(), rotation=30)

        # Plot the second chart (bottom - Bar chart)
        axs[1].bar(X_axis - 0.2, df_filtered_mean[(df_filtered_mean.device_skewness=="GPU NOT SKEWED")]["vl_intra_task_execution_time_full_func"], 0.3, color='C0', alpha = 0.5, zorder=3)
        axs[1].bar(X_axis + 0.2, df_filtered_mean[(df_filtered_mean.device_skewness=="GPU SKEWED")]["vl_intra_task_execution_time_full_func"], 0.3, color='red', alpha = 0.5, hatch='oo', zorder=3)
        axs[1].set_ylabel('Usr. Code Time GPU (s)')  # Add y-axis label
        axs[1].set_xlabel('Block size MB (Grid Dimension)')
        axs[1].grid(zorder=0,axis='y')
        axs[1].set_xticks(X_axis, df_filtered_mean[x_value].drop_duplicates(), rotation=30)


        # Adjust layout to prevent clipping of titles and labels
        # plt.tight_layout()

        fig.autofmt_xdate(rotation=30, ha='right')

        # Adjust spacing
        plt.subplots_adjust(wspace=0.01, hspace=0.25)
        
        # Show the plots
        # plt.show()
        plt.savefig(dst_path_figs+'FIG11.png',bbox_inches='tight',dpi=100)
        plt.savefig(dst_path_figs+'FIG11.pdf',bbox_inches='tight',dpi=100)


   

    # FOR DATA SPARSITY
    # elif mode == 1555:

    #     matplotlib.rcParams.update({'font.size': 16})

    #     print("\nMode ",mode,": Plotting intra-task execution times x grid and block shapes, without parameter filters")

    #     ds_dataset = df_filtered["ds_dataset"].unique()
    #     ds_dataset = '(' + ', '.join(ds_dataset) + ')'
        
    #     # Define the size of the overall chart area in inches
    #     chart_width = 6.4
    #     chart_height = 4.8

    #     # Create a figure with a fixed size
    #     fig = plt.figure(figsize=(chart_width, chart_height))

    #     # Define the size and position of the plot area within the chart
    #     #BEST
    #     # left_margin = 0.25
    #     # bottom_margin = 0.08
    #     # plot_width = 1
    #     # plot_height = 1

    #     left_margin = 0.15
    #     bottom_margin = -0.15
    #     plot_width = 1
    #     plot_height = 1


    #     # Calculate the position of the plot area
    #     plot_left = left_margin
    #     plot_bottom = bottom_margin
    #     plot_right = left_margin + plot_width
    #     plot_top = bottom_margin + plot_height

    #     # Create the plot within the defined plot area
    #     ax = fig.add_axes([plot_left, plot_bottom, plot_width, plot_height])


    #     x_value_list = ['vl_concat_block_size_mb_grid_row_x_column_dimension']

    #     for x_value in x_value_list:

    #         if x_value == 'vl_concat_grid_row_x_column_dimension_block_size_mb':
    #             x_value_title = 'Grid Shape (Block Size MB)'
    #         elif x_value == 'vl_concat_block_size_mb_grid_row_x_column_dimension':
    #             x_value_title = 'Block Size MB (Grid Shape)'
            
    #         df_filtered_mean = df_filtered.groupby([x_value,'device_sparsity'], as_index=False).mean()

    #         df_filtered_mean.sort_values(by=['vl_grid_row_dimension'], ascending=[False], inplace=True)
            
    #         df_filtered_mean = df_filtered_mean[[x_value,'device_sparsity','vl_intra_task_execution_time_full_func']]

    #         plt.figure(2)
    #         X_axis = np.arange(len(df_filtered_mean[x_value].drop_duplicates()))
    #         plt.bar(X_axis - 0.2, df_filtered_mean[(df_filtered_mean.device_sparsity=="CPU dense")]["vl_intra_task_execution_time_full_func"], 0.3, label = "Dense dataset", color='C0', alpha = 0.25, zorder=3)
    #         plt.bar(X_axis + 0.2, df_filtered_mean[(df_filtered_mean.device_sparsity=="CPU sparse")]["vl_intra_task_execution_time_full_func"], 0.3, label = "Sparse dataset", color='C0', alpha = 0.25, hatch='oo', zorder=3)
    #         plt.xticks(X_axis, df_filtered_mean[x_value].drop_duplicates(), rotation=90)
    #         plt.xlabel(x_value_title)
    #         plt.ylabel('User Code Exec. Time CPU (s)')
    #         # plt.title('$T_{w\_intra}$ Time x '+x_value_title+' ' + ds_dataset,fontstyle='italic',fontweight="bold")
    #         plt.grid(zorder=0,axis='y')
    #         plt.figlegend(loc='upper center', ncol=2, frameon=False)
    #         plt.ylim([0, 250])
    #         # plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=len(df_filtered_mean[x_value].drop_duplicates()))
    #         plt.savefig(dst_path_figs+'mode_'+str(mode)+'_CPU_avg_intra_task_composition_time_per_'+x_value+'_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)
    #         plt.savefig(dst_path_figs+'mode_'+str(mode)+'_CPU_avg_intra_task_composition_time_per_'+x_value+'_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.pdf',bbox_inches='tight',dpi=100)


    #         plt.figure(3)
    #         X_axis = np.arange(len(df_filtered_mean[x_value].drop_duplicates()))
    #         plt.bar(X_axis - 0.2, df_filtered_mean[(df_filtered_mean.device_sparsity=="GPU dense")]["vl_intra_task_execution_time_full_func"], 0.3, label = "Dense dataset", color='C0', alpha = 0.25, zorder=3)
    #         plt.bar(X_axis + 0.2, df_filtered_mean[(df_filtered_mean.device_sparsity=="GPU sparse")]["vl_intra_task_execution_time_full_func"], 0.3, label = "Sparse dataset", color='C0', alpha = 0.25, hatch='oo', zorder=3)
    #         plt.xticks(X_axis, df_filtered_mean[x_value].drop_duplicates(), rotation=90)
    #         plt.xlabel(x_value_title)
    #         plt.ylabel('User Code Exec. Time GPU (s)')
    #         # plt.title('$T_{w\_intra}$ Time x '+x_value_title+' ' + ds_dataset,fontstyle='italic',fontweight="bold")
    #         plt.grid(zorder=0,axis='y')
    #         plt.figlegend(loc='upper center', ncol=2, frameon=False)
    #         plt.ylim([0, 11])
    #         # plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=len(df_filtered_mean[x_value].drop_duplicates()))
    #         plt.savefig(dst_path_figs+'mode_'+str(mode)+'_GPU_avg_intra_task_composition_time_per_'+x_value+'_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)
    #         plt.savefig(dst_path_figs+'mode_'+str(mode)+'_GPU_avg_intra_task_composition_time_per_'+x_value+'_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.pdf',bbox_inches='tight',dpi=100)


    elif mode == 18:

        print("\nMode ",mode,": Plotting an CPU and GPU speedups per block memory size '%' data set memory size (vl_block_memory_size_percent_dataset) and data set memory size (vl_dataset_memory_size)")

        speedup_list = ["speedup_cpu_total_execution_time","speedup_gpu_total_execution_time","speedup_cpu_intra_task_execution_time_full_func","speedup_gpu_intra_task_execution_time_full_func"]

        # speedup_list = ["speedup_cpu_total_execution_time","speedup_cpu_inter_task_execution_time","speedup_cpu_intra_task_execution_time_full_func","speedup_cpu_intra_task_execution_time_device_func","speedup_gpu_total_execution_time","speedup_gpu_inter_task_execution_time","speedup_gpu_intra_task_execution_time_full_func","speedup_gpu_intra_task_execution_time_device_func","speedup_cpu_intra_task_execution_time_free_additional","speedup_gpu_intra_task_execution_time_free_additional"]

        # speedup_list = ["speedup_cpu_intra_task_execution_time_free_additional","speedup_gpu_intra_task_execution_time_free_additional"]

        # speedup_list = ["speedup_cpu_intra_task_execution_time_full_func","speedup_gpu_intra_task_execution_time_full_func","speedup_cpu_inter_task_execution_time","speedup_gpu_inter_task_execution_time"]

        for speedup in speedup_list:

            if speedup == "speedup_cpu_total_execution_time":
                speedup_title = "$T_{w\_total}$ Speedup CPU over GPU"
                vmax=4.00
            elif speedup == "speedup_cpu_inter_task_execution_time":
                speedup_title = "$T_{w\_inter}$ Speedup CPU over GPU"
                vmax=16.00
            elif speedup == "speedup_cpu_intra_task_execution_time_full_func":
                speedup_title = "$T_{w\_intra}$ Speedup CPU over GPU"
                vmax=26.00
            elif speedup == "speedup_cpu_intra_task_execution_time_device_func":
                speedup_title = "$T_{p\_intra}$ Speedup CPU over GPU"
                vmax=9.50
            elif speedup == "speedup_cpu_intra_task_execution_time_free_additional":
                speedup_title = "$T_{p\_intra}$ + $T_{c\_intra}$ Times Speedup CPU over GPU"
                vmax=4.90
            elif speedup == "speedup_gpu_total_execution_time":
                speedup_title = "$T_{w\_total}$ Speedup GPU over CPU"
                vmax=4.00
            elif speedup == "speedup_gpu_inter_task_execution_time":
                speedup_title = "$T_{w\_inter}$ Speedup GPU over CPU"
                vmax=16.00
            elif speedup == "speedup_gpu_intra_task_execution_time_full_func":
                speedup_title = "$T_{w\_intra}$ Speedup GPU over CPU"
                vmax=26.00
            elif speedup == "speedup_gpu_intra_task_execution_time_device_func":
                speedup_title = "$T_{p\_intra}$ Speedup GPU over CPU"
                vmax=9.50
            elif speedup == "speedup_gpu_intra_task_execution_time_free_additional":
                speedup_title = "$T_{p\_intra}$ + $T_{c\_intra}$ Times Speedup GPU over CPU"
                vmax=4.90

            # Heatmap Speedups
            df_filtered_heatmap = df_filtered[["vl_block_memory_size_percent_dataset","vl_dataset_memory_size",speedup]].sort_values(by=["vl_dataset_memory_size","vl_block_memory_size_percent_dataset"], ascending=[True,False])

            heatmap_pt = pd.pivot_table(df_filtered_heatmap,values = speedup, index=['vl_dataset_memory_size'], columns='vl_block_memory_size_percent_dataset')

            heatmap_pt.sort_index(level=0, ascending=False, inplace=True)

            values = heatmap_pt.to_numpy(dtype=float)

            plt.figure()
            fig, ax = plt.subplots(figsize=(16,8))
            sns.set()
            ax = sns.heatmap(values, cmap='YlGnBu', vmin=1, vmax=vmax, square=True, annot=True, fmt='.1f')
            sns.heatmap(values, xticklabels=heatmap_pt.columns, yticklabels=heatmap_pt.index,
            cmap=plt.get_cmap('binary'), vmin=1, vmax=2, mask=values > 1, cbar=False, ax=ax, fmt='.1f')
            plt.xticks(rotation=15)
            plt.xlabel('Block (% Data Set Size)')
            plt.ylabel('Data Set Size (MB)')
            plt.title(speedup_title,fontstyle='italic',fontweight="bold")
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_heatmap_'+speedup+'_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

    #BLOCK SIZE PERCENT DATA SET
    # elif mode == 188:

    #     print("\nMode ",mode,": Plotting CPU and GPU speedups per block size")

    #     ds_dataset = df_filtered["ds_dataset"].unique()
    #     ds_dataset = '(' + ', '.join(ds_dataset) + ')'

    #     df_filtered_mean = df_filtered[["vl_block_memory_size_percent_dataset","speedup_gpu_intra_task_execution_time_device_func","speedup_gpu_intra_task_execution_time_full_func","speedup_gpu_inter_task_execution_time"]]

    #     print(df_filtered_mean)

    #     x_value = 'vl_block_memory_size_percent_dataset'
    #     x_value_title = 'Block Size (% Data Set Size)'
    #     speedup_title = 'Speedups GPU over CPU x Worker Nodes ' + ds_dataset

    #     df_filtered_mean.sort_values('vl_block_memory_size_percent_dataset', inplace=True)

    #     # OVERVIEW OF ALL EXECUTION TIMES
    #     plt.figure(1)
    #     ax = plt.gca()
    #     df_filtered_mean.set_index(x_value).plot(kind = 'line',color=['C3','C2','C1'],zorder=3,linewidth=4)
    #     # plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True)
    #     # plt.legend(['$T_{w\_inter}$', '$T_{w\_intra}$', '$T_{p\_intra}$'])
    #     plt.legend(['$T_{p\_intra}$ (No overhead)', '$T_{w\_intra}$ (Intra overhead)', '$T_{w\_inter}$ (Inter+Intra overhead)'])
    #     # plt.legend(['Inter+Intra overheads', 'Intra overhead', 'No overhead'])
    #     plt.xlabel(x_value_title)
    #     plt.ylabel('Speedup')
    #     plt.title('Speedups GPU over CPU x Device',fontstyle='italic',fontweight="bold")
    #     plt.title(speedup_title,fontstyle='italic',fontweight="bold")
    #     plt.grid(zorder=0)
    #     plt.ylim([0, 35])
    #     # plt.xscale("log")
    #     plt.savefig(dst_path_figs+'mode_'+str(mode)+'_overview_gpu_speedup_times_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)


    elif mode == 188:

        print("\nMode ",mode,": Plotting CPU and GPU speedups per block size")

        ds_dataset = df_filtered["ds_dataset"].unique()
        ds_dataset = '(' + ', '.join(ds_dataset) + ')'

        # df_filtered.sort_values('vl_block_memory_size_percent_dataset', inplace=True)

        # df_filtered_mean = df_filtered[["vl_concat_block_size_mb_grid_row_x_column_dimension","speedup_gpu_intra_task_execution_time_device_func","speedup_gpu_intra_task_execution_time_full_func","speedup_gpu_total_execution_time"]]

        # x_value = 'vl_concat_block_size_mb_grid_row_x_column_dimension'
        # x_value_title = 'Block Size MB (Grid Dimension)'
        # speedup_title = 'Speedups GPU over CPU x Worker Nodes ' + ds_dataset

        # df_filtered.sort_values('vl_block_memory_size_percent_dataset', inplace=True)

        # df_filtered_mean = df_filtered[["concat_block_percent_dataset_grid_dimension","speedup_gpu_intra_task_execution_time_device_func","speedup_gpu_intra_task_execution_time_full_func","speedup_gpu_total_execution_time"]]

        # x_value = 'concat_block_percent_dataset_grid_dimension'
        # x_value_title = 'Block Size % Data Set (Grid Shape)'
        # speedup_title = 'Speedups GPU over CPU x Block Size '


        # df_filtered.sort_values('vl_block_memory_size', inplace=True)

        # df_filtered_mean = df_filtered[["vl_concat_block_size_mb_nr_tasks","speedup_gpu_intra_task_execution_time_device_func","speedup_gpu_intra_task_execution_time_full_func","speedup_gpu_total_execution_time"]]

        # x_value = 'vl_concat_block_size_mb_nr_tasks'
        # x_value_title = 'Block Size MB (#tasks)'
        # speedup_title = 'Speedups GPU over CPU x Block Size '


        df_filtered.sort_values('vl_block_memory_size', inplace=True)

        df_filtered_mean = df_filtered[["concat_block_percent_dataset_nr_tasks","speedup_gpu_intra_task_execution_time_device_func","speedup_gpu_intra_task_execution_time_full_func","speedup_gpu_total_execution_time"]]

        x_value = 'concat_block_percent_dataset_nr_tasks'
        x_value_title = 'Block Size % Data Set Size (#tasks)'
        speedup_title = 'Speedups GPU over CPU x Block Size '


        # OVERVIEW OF ALL EXECUTION TIMES
        plt.figure(1)
        ax = plt.gca()
        df_filtered_mean.set_index(x_value).plot(kind = 'line',color=['C3','C2','C1'],zorder=3,linewidth=4)
        # plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True)
        # plt.legend(['$T_{w\_inter}$', '$T_{w\_intra}$', '$T_{p\_intra}$'])
        plt.legend(['No overhead', 'Intra overhead', 'Inter+Intra overhead'])
        # plt.legend(['Inter+Intra overheads', 'Intra overhead', 'No overhead'])
        plt.xlabel(x_value_title)
        plt.ylabel('Speedup')
        plt.title(speedup_title,fontstyle='italic',fontweight="bold")
        plt.grid(zorder=0)
        plt.ylim([1, 28])
        plt.xticks(rotation = 90)
        plt.yticks(np.arange(1, 28, 1))
        # plt.yscale("log")
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_overview_gpu_speedup_times_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)


    elif mode == 1888:

        print("\nMode ",mode,": Plotting CPU and GPU speedups per block size")

        ds_dataset = df_filtered["ds_dataset"].unique()
        ds_dataset = '(' + ', '.join(ds_dataset) + ')'

        df_filtered_mean = df_filtered[["vl_block_memory_size","speedup_gpu_intra_task_execution_time_device_func","speedup_gpu_intra_task_execution_time_full_func","speedup_gpu_total_execution_time"]]

        print(df_filtered_mean)

        x_value = 'vl_block_memory_size'
        x_value_title = 'Block Size (B)'
        speedup_title = 'Speedups GPU over CPU x Worker Nodes ' + ds_dataset

        df_filtered_mean.sort_values('vl_block_memory_size', inplace=True)

        # OVERVIEW OF ALL EXECUTION TIMES
        plt.figure(1)
        ax = plt.gca()
        df_filtered_mean.set_index(x_value).plot(kind = 'line',color=['C3','C2','C1'],zorder=3,linewidth=4)
        # plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True)
        # plt.legend(['$T_{w\_inter}$', '$T_{w\_intra}$', '$T_{p\_intra}$'])
        plt.legend(['$T_{p\_intra}$ (No overhead)', '$T_{w\_intra}$ (Intra overhead)', '$T_{w\_inter}$ (Inter+Intra overhead)'])
        # plt.legend(['Inter+Intra overheads', 'Intra overhead', 'No overhead'])
        plt.xlabel(x_value_title)
        plt.ylabel('Speedup')
        plt.title('Speedups GPU over CPU x Device',fontstyle='italic',fontweight="bold")
        plt.title(speedup_title,fontstyle='italic',fontweight="bold")
        plt.grid(zorder=0)
        # plt.ylim([0, 6.5])
        plt.xscale("log")
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_overview_gpu_speedup_times_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)


    elif mode == 100:

        matplotlib.rcParams.update({'font.size': 18})

        print("\nMode ",mode,": Plotting GPU speedups and user code execution times per block size")

        ds_function = df_filtered['ds_function'].unique()

        ds_function = str(df_filtered['ds_function'].values[0])

        speedup = "speedup_gpu_intra_task_execution_time_full_func"

        speedup_title = "Speedup GPU over CPU"

        # Matmul Speedup
        # matmul_func
        df_filtered_left_top = df_filtered[(df_filtered.ds_function=='MATMUL_FUNC')]
        # add_func
        df_filtered_right_top = df_filtered[(df_filtered.ds_function=='ADD_FUNC')]
        
        # Matmul Time
        # matmul_func
        df_filtered_left_bottom = df_filtered[(df_filtered.ds_function=='MATMUL_FUNC')]
        # add_func
        df_filtered_right_bottom = df_filtered[(df_filtered.ds_function=='ADD_FUNC')]
        left_title = 'matmul_func'
        right_title = 'add_func'

        # Speedups
        df1 = df_filtered_left_top[["vl_block_memory_size","vl_block_memory_size_mb","speedup_gpu_intra_task_execution_time_full_func"]].sort_values(by=["vl_block_memory_size"], ascending=[True])
        df2 = df_filtered_right_top[["vl_block_memory_size","vl_block_memory_size_mb","speedup_gpu_intra_task_execution_time_full_func"]].sort_values(by=["vl_block_memory_size"], ascending=[True])
        print(df_filtered_right_top)
        # Times
        df3 = df_filtered_left_bottom[["vl_block_memory_size","vl_block_memory_size_mb","vl_intra_task_execution_time_device_func_cpu","vl_additional_time_cpu","vl_communication_time_cpu","vl_intra_task_execution_time_device_func_gpu","vl_additional_time_gpu","vl_communication_time_gpu"]].sort_values(by=["vl_block_memory_size"], ascending=[True])
        df4 = df_filtered_right_bottom[["vl_block_memory_size","vl_block_memory_size_mb","vl_intra_task_execution_time_device_func_cpu","vl_additional_time_cpu","vl_communication_time_cpu","vl_intra_task_execution_time_device_func_gpu","vl_additional_time_gpu","vl_communication_time_gpu"]].sort_values(by=["vl_block_memory_size"], ascending=[True])

        x = 'vl_block_memory_size_mb'
        x_value = "vl_block_memory_size_mb"
        x_value_title = 'Block size MB'

        fig, axs = plt.subplots(2, 2, figsize=(10, 8), sharey='row', sharex='col')

        # Plot the first chart (top-left - Bar chart)
        axs[0, 0].bar(df1[x_value],df1['speedup_gpu_intra_task_execution_time_full_func'], color='C0', alpha = 0.5, label='Usr. Code')
        axs[0, 0].legend(loc=(-0.000,0.99), frameon=False, labelspacing=0.01, ncol=3, borderpad=0.1)
        axs[0, 0].set_ylabel('GPU Speedup over CPU')  # Add y-axis label
        axs[0, 0].set_ylim([-5, 25])
        axs[0, 0].grid(zorder=0,axis='y')
        axs[0, 0].set_title(left_title, pad=25, style='italic')

        # Plot the second chart (top-right - Bar chart)
        axs[0, 1].bar(df2[x],df2['speedup_gpu_intra_task_execution_time_full_func'],color='C0', alpha = 0.5)
        axs[0, 1].set_ylim([-5, 25])
        axs[0, 1].grid(zorder=0,axis='y')
        axs[0, 1].set_title(right_title, pad=25, style='italic')

        # Plot the third chart (bottom-left - Line chart)
        axs[1, 0].plot(df3[x], df3['vl_intra_task_execution_time_device_func_cpu'], color='C2', linestyle = 'dotted', label='P. Frac. CPU', linewidth=2.5)
        axs[1, 0].plot(df3[x], df3['vl_intra_task_execution_time_device_func_gpu'], color='C2', linestyle = 'solid', label='P. Frac. GPU', linewidth=2.5)
        axs[1, 0].plot(df3[x], df3['vl_communication_time_gpu'], color='C4', linestyle = 'solid', label='CPU-GPU Comm.', linewidth=2.5)
        axs[1, 0].legend(loc=(-0.000,0.99), frameon=False, labelspacing=0.01, ncol=3, borderpad=0.1)
        axs[1, 0].set_xlabel('Block size MB')  # Add x-axis label
        axs[1, 0].set_ylabel('Average Time per Task (s)')  # Add y-axis label
        axs[1, 0].set_yscale('log')
        axs[1, 0].set_ylim([1e-3, 1e4])
        axs[1, 0].tick_params(axis='x', labelrotation = 0)
        axs[1, 0].grid(zorder=0,axis='y')
        
        # Plot the fourth chart (bottom-right - Line chart)
        axs[1, 1].plot(df4[x], df4['vl_intra_task_execution_time_device_func_cpu'], color='C2', linestyle = 'dotted', linewidth=2.5)
        axs[1, 1].plot(df4[x], df4['vl_intra_task_execution_time_device_func_gpu'], color='C2', linestyle = 'solid', linewidth=2.5)
        axs[1, 1].plot(df4[x], df4['vl_communication_time_gpu'], color='C4', linestyle = 'solid', linewidth=2.5)
        axs[1, 1].legend(loc=(-0.000,0.99), frameon=False, labelspacing=0.01, ncol=3, borderpad=0.1)
        axs[1, 1].set_xlabel('Block size MB')  # Add x-axis label
        axs[1, 1].set_yscale('log')
        axs[1, 1].set_ylim([1e-3, 1e4])
        axs[1, 1].tick_params(axis='x', labelrotation = 0)
        axs[1, 1].grid(zorder=0,axis='y')
        
        # Adjust layout to prevent clipping of titles and labels
        plt.tight_layout()

        # Adjust spacing
        plt.subplots_adjust(wspace=0.01, hspace=0.25)
        
        # Show the plots
        # plt.show()
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_overview_avg_execution_times_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_overview_avg_execution_times_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.pdf',bbox_inches='tight',dpi=100)

       
    else:

        print("\nInvalid mode.")


def parse_args():
    import argparse
    description = 'Generating graphs for the experiments'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-a', '--ds_algorithm', type=str, default="MATMUL_DISLIB",
                        help='Algorithm description'
                        )
    parser.add_argument('-r', '--ds_resource', type=str, default="MINOTAURO_9_NODES_1_CORE",
                        help='Resource description'
                        )
    parser.add_argument('-i', '--nr_iterations', type=int, default=5,
                        help='Number of iterations'
                        )
    parser.add_argument('-m', '--mode', type=int, default=1,
                        help='Graph mode'
                        )
    return parser.parse_args()


if __name__ == "__main__":
    opts = parse_args()
    main(**vars(opts))
