import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from config import open_connection, close_connection
import numpy as np

def main(ds_algorithm, ds_resource, nr_iterations, mode):

    dst_path_figs = '../../results/figures/'

    # Open connection to the database
    cur, conn = open_connection()

    # Set sql query according to mode

    # CPU SPEEDUP
    if mode == 8:
        sql_query = """
                        WITH T_CPU AS (
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
                                    WHERE
                                    (SELECT DISTINCT Y.DS_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) = 'CPU'
                                ),
                        T_GPU AS (
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
                                    WHERE
                                    (SELECT DISTINCT Y.DS_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) = 'GPU'
                                )
                        SELECT 
                        T_CPU.CD_PARAMETER,
                        T_CPU.DS_ALGORITHM,
                        T_CPU.NR_ITERATIONS,
                        T_CPU.DS_RESOURCE,
                        T_CPU.DS_PARAMETER_TYPE,
                        T_CPU.DS_PARAMETER_ATTRIBUTE,
                        T_CPU.DS_DATASET,
                        T_CPU.VL_DATASET_MEMORY_SIZE,
                        T_CPU.VL_DATASET_DIMENSION,
                        T_CPU.VL_DATASET_ROW_DIMENSION,
                        T_CPU.VL_DATASET_COLUMN_DIMENSION,
                        T_CPU.VL_GRID_ROW_DIMENSION,
                        T_CPU.VL_GRID_COLUMN_DIMENSION,
                        T_CPU.VL_BLOCK_ROW_DIMENSION,
                        T_CPU.VL_BLOCK_COLUMN_DIMENSION,
                        T_GPU.VL_TOTAL_EXECUTION_TIME/T_CPU.VL_TOTAL_EXECUTION_TIME AS SPEEDUP_CPU_TOTAL_EXECUTION_TIME,
                        T_GPU.VL_INTER_TASK_EXECUTION_TIME/T_CPU.VL_INTER_TASK_EXECUTION_TIME AS SPEEDUP_CPU_INTER_TASK_EXECUTION_TIME,
                        T_GPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC/T_CPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC AS SPEEDUP_CPU_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                        T_GPU.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC/T_CPU.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC AS SPEEDUP_CPU_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC
                        FROM T_CPU INNER JOIN T_GPU ON (T_CPU.CD_PARAMETER = T_GPU.CD_PARAMETER)
                        WHERE
                        T_CPU.VL_TOTAL_EXECUTION_TIME < T_GPU.VL_TOTAL_EXECUTION_TIME;"""

    # GPU SPEEDUP
    elif mode == 9:
        sql_query = """
                        WITH T_CPU AS (
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
                                    WHERE
                                    (SELECT DISTINCT Y.DS_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) = 'CPU'
                                ),
                        T_GPU AS (
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
                                    WHERE
                                    (SELECT DISTINCT Y.DS_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) = 'GPU'
                                )
                        SELECT 
                        T_GPU.CD_PARAMETER,
                        T_GPU.DS_ALGORITHM,
                        T_GPU.NR_ITERATIONS,
                        T_GPU.DS_RESOURCE,
                        T_GPU.DS_PARAMETER_TYPE,
                        T_GPU.DS_PARAMETER_ATTRIBUTE,
                        T_GPU.DS_DATASET,
                        T_GPU.VL_DATASET_MEMORY_SIZE,
                        T_GPU.VL_DATASET_DIMENSION,
                        T_GPU.VL_DATASET_ROW_DIMENSION,
                        T_GPU.VL_DATASET_COLUMN_DIMENSION,
                        T_GPU.VL_GRID_ROW_DIMENSION,
                        T_GPU.VL_GRID_COLUMN_DIMENSION,
                        T_GPU.VL_BLOCK_ROW_DIMENSION,
                        T_GPU.VL_BLOCK_COLUMN_DIMENSION,
                        T_CPU.VL_TOTAL_EXECUTION_TIME/T_GPU.VL_TOTAL_EXECUTION_TIME AS SPEEDUP_GPU_TOTAL_EXECUTION_TIME,
                        T_CPU.VL_INTER_TASK_EXECUTION_TIME/T_GPU.VL_INTER_TASK_EXECUTION_TIME AS SPEEDUP_GPU_INTER_TASK_EXECUTION_TIME,
                        T_CPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC/T_GPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC AS SPEEDUP_GPU_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                        T_CPU.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC/T_GPU.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC AS SPEEDUP_GPU_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC
                        FROM T_CPU INNER JOIN T_GPU ON (T_CPU.CD_PARAMETER = T_GPU.CD_PARAMETER)
                        WHERE
                        T_GPU.VL_TOTAL_EXECUTION_TIME < T_CPU.VL_TOTAL_EXECUTION_TIME
                        --AND T_GPU.VL_INTER_TASK_EXECUTION_TIME < T_CPU.VL_INTER_TASK_EXECUTION_TIME
                        --AND T_GPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC < T_CPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC
                        --AND T_GPU.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC < T_CPU.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC
                        --AND T_GPU.DS_PARAMETER_TYPE = 'VAR_BLOCK_CAPACITY_SIZE'
                        --AND T_GPU.DS_PARAMETER_TYPE = 'VAR_PARALLELISM_LEVEL'
                        ORDER BY T_CPU.VL_TOTAL_EXECUTION_TIME/T_GPU.VL_TOTAL_EXECUTION_TIME DESC;"""
    # FIND WHERE CPUs HAVE A LOWER LATENCY THAN GPUs
    elif mode == 10:
        sql_query = """
                        SELECT
                        SBQ.ID_EXPERIMENT,
                        SBQ.ID_PARAMETER,
                        SBQ.CD_PARAMETER,
                        SBQ.DS_ALGORITHM,
                        SBQ.NR_ITERATIONS,
                        SBQ.DS_RESOURCE,
                        SBQ.DS_DEVICE,
                        SBQ.DS_PARAMETER_TYPE,
                        SBQ.DS_PARAMETER_ATTRIBUTE,
                        SBQ.DS_DATASET,
                        SBQ.VL_DATASET_MEMORY_SIZE,
                        SBQ.VL_DATASET_DIMENSION,
                        SBQ.VL_DATASET_ROW_DIMENSION,
                        SBQ.VL_DATASET_COLUMN_DIMENSION,
                        SBQ.VL_GRID_ROW_DIMENSION,
                        SBQ.VL_GRID_COLUMN_DIMENSION,
                        SBQ.VL_BLOCK_ROW_DIMENSION,
                        SBQ.VL_BLOCK_COLUMN_DIMENSION,
                        SBQ.VL_TOTAL_EXECUTION_TIME,
                        SBQ.VL_INTER_TASK_EXECUTION_TIME,
                        SBQ.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                        SBQ.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                        SBQ.VL_COMMUNICATION_TIME
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
                            WHERE
                            B.CD_PARAMETER IN
                            (
                                WITH T_CPU AS (
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
                                            WHERE
                                            (SELECT DISTINCT Y.DS_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) = 'CPU'
                                        ),
                                T_GPU AS (
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
                                            WHERE
                                            (SELECT DISTINCT Y.DS_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = B.ID_FUNCTION) = 'GPU'
                                        )
                                SELECT DISTINCT T_CPU.CD_PARAMETER
                                FROM T_CPU INNER JOIN T_GPU ON (T_CPU.CD_PARAMETER = T_GPU.CD_PARAMETER)
                                --WHERE
                                --T_CPU.VL_TOTAL_EXECUTION_TIME is not null --EXPERIMENTS OK
                                --T_CPU.VL_TOTAL_EXECUTION_TIME is null --FAILED EXPERIMENTS
                                --AND T_CPU.VL_TOTAL_EXECUTION_TIME < T_GPU.VL_TOTAL_EXECUTION_TIME
                                --AND T_CPU.VL_INTER_TASK_EXECUTION_TIME < T_GPU.VL_INTER_TASK_EXECUTION_TIME
                                --AND T_CPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC < T_GPU.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC
                                --AND T_CPU.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC < T_GPU.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC
                            )
                        ) SBQ;"""
    # OTHER MODES
    else:
        sql_query = """SELECT
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
                        WHERE
                        A.VL_TOTAL_EXECUTION_TIME is not null
                        --(SELECT X.DS_PARAMETER_ATTRIBUTE FROM PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = B.ID_PARAMETER_TYPE) <> 'MAX_INTER_MIN_INTRA'
                        ORDER BY A.ID_PARAMETER;"""
    
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
    
    # General filtering and sorting parameters
    df_filtered = df[
                    (df["ds_algorithm"] == ds_algorithm.upper()) # FIXED VALUE
                    & (df["nr_iterations"] == int(nr_iterations)) # FIXED VALUE
                    & (df["ds_resource"] == ds_resource.upper()) # FIXED VALUE
                    # & (df["ds_dataset"].isin(["S_A_1","S_A_2","S_A_3","S_A_4","S_B_1","S_B_2","S_B_3","S_B_4","S_C_1","S_C_2","S_C_3","S_C_4"])) # FIXED VALUE
                    & (df["ds_dataset"].isin(["S_AA_1","S_AA_2","S_AA_3","S_AA_4","S_BB_1","S_BB_2","S_BB_3","S_BB_4","S_CC_1","S_CC_2","S_CC_3","S_CC_4"])) # FIXED VALUE
                    # & (df["ds_parameter_type"] == "VAR_BLOCK_CAPACITY_SIZE") # 1.1, 1.2, 1.3, 1.4
                    # & (df["ds_parameter_type"] == "VAR_PARALLELISM_LEVEL") # 2.1, 2.2
                    # & (df["ds_parameter_attribute"] == "0.25") # 1.1
                    # & (df["ds_parameter_attribute"] == "0.50") # 1.2
                    # & (df["ds_parameter_attribute"] == "0.75") # 1.3
                    # & (df["ds_parameter_attribute"] == "1.00") # 1.4
                    # & (df["ds_parameter_attribute"] == "MIN_INTER_MAX_INTRA") # 2.1
                    # & (df["ds_parameter_attribute"] == "MAX_INTER_MIN_INTRA") # 2.2
                    # & (df["vl_dataset_memory_size"] == 400) # 2.2.1
                    # & (df["vl_dataset_memory_size"] == 400000) # 2.2.2
                    # & (df["vl_dataset_memory_size"] == 400000000) # 2.2.3
                    # & (df["ds_dataset"] == "S_A_1")
                    # & (df["ds_dataset"] == "S_A_2")
                    # & (df["ds_dataset"] == "S_A_3")
                    # & (df["ds_dataset"] == "S_A_4")
                    # & (df["ds_dataset"] == "S_B_1")
                    # & (df["ds_dataset"] == "S_B_2")
                    # & (df["ds_dataset"] == "S_B_3")
                    # & (df["ds_dataset"] == "S_B_4")
                    # & (df["ds_dataset"] == "S_C_1")
                    # & (df["ds_dataset"] == "S_C_2")
                    # & (df["ds_dataset"] == "S_C_3")
                    # & (df["ds_dataset"] == "S_C_4")
                    ]

    

    if mode == 1:

        print("\nMode ",mode,": Ploting an overview of all execution times, without parameter filters")

        df_filtered_mean = df_filtered.groupby(["ds_device"], as_index=False).mean()

        df_filtered_mean = df_filtered_mean[["ds_device","vl_total_execution_time","vl_inter_task_execution_time","vl_intra_task_execution_time_full_func","vl_intra_task_execution_time_device_func"]]

        df_filtered_mean_cpu = df_filtered_mean[(df_filtered_mean.ds_device=="CPU")].sort_values("vl_total_execution_time")
        df_filtered_mean_gpu = df_filtered_mean[(df_filtered_mean.ds_device=="GPU")].sort_values("vl_total_execution_time")

        # OVERVIEW OF ALL EXECUTION TIMES
        plt.figure(1)
        ax = plt.gca()
        df_filtered_mean.set_index('ds_device').plot(kind = 'bar',zorder=3)
        plt.legend(['Total', 'Inter', 'Intra (Full Function)', 'Intra (Device Function)'])
        plt.xlabel('Device')
        plt.ylabel('Average Execution Times (s)')
        plt.title('Average Execution Times x Device',fontstyle='italic',fontweight="bold")
        plt.grid(zorder=0)
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_overview_avg_execution_times_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

        # VL_TOTAL_EXECUTION_TIME
        plt.figure(2)
        fig, ax = plt.subplots()
        ax.bar(df_filtered_mean_cpu['ds_device'], df_filtered_mean_cpu['vl_total_execution_time'], color='C0', hatch='.',zorder=3)
        ax.bar(df_filtered_mean_gpu['ds_device'], df_filtered_mean_gpu['vl_total_execution_time'], color='C0', hatch='|',zorder=3)
        plt.legend(['CPU','GPU'])
        plt.xlabel('Device')
        plt.ylabel('Average Total Execution Time (s)')
        plt.title('Average Total Execution Time x Device',fontstyle='italic',fontweight="bold")
        plt.grid(zorder=0)
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_overview_avg_total_execution_time_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

        # VL_INTER_TASK_EXECUTION_TIME
        df_filtered_mean_cpu = df_filtered_mean[(df_filtered_mean.ds_device=="CPU")].sort_values("vl_inter_task_execution_time")
        df_filtered_mean_gpu = df_filtered_mean[(df_filtered_mean.ds_device=="GPU")].sort_values("vl_inter_task_execution_time")
        plt.figure(3)
        fig, ax = plt.subplots()
        ax.bar(df_filtered_mean_cpu['ds_device'], df_filtered_mean_cpu['vl_inter_task_execution_time'], color='C1', hatch='.', zorder=3)
        ax.bar(df_filtered_mean_gpu['ds_device'], df_filtered_mean_gpu['vl_inter_task_execution_time'], color='C1', hatch='x', zorder=3)
        plt.legend(['CPU','GPU'])
        plt.xlabel('Device')
        plt.ylabel('Average Inter-Task Time (s)')
        plt.title('Average Inter-Task Time x Device',fontstyle='italic',fontweight="bold")
        plt.grid(zorder=0)
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_overview_avg_inter_task_execution_time_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

        # VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC
        df_filtered_mean_cpu = df_filtered_mean[(df_filtered_mean.ds_device=="CPU")].sort_values("vl_intra_task_execution_time_full_func")
        df_filtered_mean_gpu = df_filtered_mean[(df_filtered_mean.ds_device=="GPU")].sort_values("vl_intra_task_execution_time_full_func")
        plt.figure(4)
        fig, ax = plt.subplots()
        ax.bar(df_filtered_mean_cpu['ds_device'], df_filtered_mean_cpu['vl_intra_task_execution_time_full_func'], color='C2', hatch='.', zorder=3)
        ax.bar(df_filtered_mean_gpu['ds_device'], df_filtered_mean_gpu['vl_intra_task_execution_time_full_func'], color='C2', hatch='x', zorder=3)
        plt.legend(['CPU','GPU'])
        plt.xlabel('Device')
        plt.ylabel('Average Intra-Task (full func) Time (s)')
        plt.title('Average Intra-Task (full func) Time x Device',fontstyle='italic',fontweight="bold")
        plt.grid(zorder=0)
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_overview_avg_intra_task_execution_time_full_func_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

        # VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC
        df_filtered_mean_cpu = df_filtered_mean[(df_filtered_mean.ds_device=="CPU")].sort_values("vl_intra_task_execution_time_device_func")
        df_filtered_mean_gpu = df_filtered_mean[(df_filtered_mean.ds_device=="GPU")].sort_values("vl_intra_task_execution_time_device_func")
        plt.figure(5)
        fig, ax = plt.subplots()
        ax.bar(df_filtered_mean_cpu['ds_device'], df_filtered_mean_cpu['vl_intra_task_execution_time_device_func'], color='C3', hatch='.', zorder=3)
        ax.bar(df_filtered_mean_gpu['ds_device'], df_filtered_mean_gpu['vl_intra_task_execution_time_device_func'], color='C3', hatch='x', zorder=3)
        plt.legend(['CPU','GPU'])
        plt.xlabel('Device')
        plt.ylabel('Average Intra-Task (device func) Time (s)')
        plt.title('Average Intra-Task (device func) Time x Device',fontstyle='italic',fontweight="bold")
        plt.grid(zorder=0)
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_overview_avg_intra_task_execution_time_device_func_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)


    elif mode == 2:

        print("\nMode ",mode,": Ploting all execution times x data set memory size, without parameter filters")

        df_filtered_mean = df_filtered.groupby(['ds_device', 'vl_dataset_memory_size'], as_index=False).mean()

        df_filtered_mean_cpu = df_filtered_mean[(df_filtered_mean.ds_device=="CPU")]
        df_filtered_mean_gpu = df_filtered_mean[(df_filtered_mean.ds_device=="GPU")]

        # VL_TOTAL_EXECUTION_TIME
        plt.figure(1)
        ax = plt.gca()
        df_filtered_mean_cpu.plot(x = 'vl_dataset_memory_size', y = 'vl_total_execution_time', kind = 'line', color='C0', linestyle = 'dotted', ax=ax, label='CPU', zorder=3)
        df_filtered_mean_gpu.plot(x = 'vl_dataset_memory_size', y = 'vl_total_execution_time', kind = 'line', color='C0', linestyle = 'solid', ax=ax, label='GPU', zorder=3)
        plt.xlabel('Data Set Size (B)')
        plt.ylabel('Average Total Execution Time (s)')
        plt.title('Average Total Execution Time x Data Set Size',fontstyle='italic',fontweight="bold")
        plt.grid(zorder=0)
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_avg_total_execution_time_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)
        # plt.savefig(dst_path_figs+'avg_total_execution_time_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+int(nr_iterations)+'_'+ds_parameter_type+'_'+ds_parameter_attribute+'_mode_'+str(mode)+'.png',bbox_inches='tight',dpi=100)
        
        # VL_INTER_TASK_EXECUTION_TIME
        plt.figure(2)
        ax = plt.gca()
        df_filtered_mean_cpu.plot(x = 'vl_dataset_memory_size', y = 'vl_inter_task_execution_time', kind = 'line', color='C1', linestyle = 'dotted', ax=ax, label='CPU', zorder=3)
        df_filtered_mean_gpu.plot(x = 'vl_dataset_memory_size', y = 'vl_inter_task_execution_time', kind = 'line', color='C1', linestyle = 'solid', ax=ax, label='GPU', zorder=3)
        plt.xlabel('Data Set Size (B)')
        plt.ylabel('Average Inter-Task Time (s)')
        plt.title('Average Inter-Task Time x Data Set Size',fontstyle='italic',fontweight="bold")
        plt.grid(zorder=0)
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_avg_inter_task_execution_time_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

        # VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC
        plt.figure(3)
        ax = plt.gca()
        df_filtered_mean_cpu.plot(x = 'vl_dataset_memory_size', y = 'vl_intra_task_execution_time_full_func', kind = 'line', color='C2', linestyle = 'dotted', ax=ax, label='CPU', zorder=3)
        df_filtered_mean_gpu.plot(x = 'vl_dataset_memory_size', y = 'vl_intra_task_execution_time_full_func', kind = 'line', color='C2', linestyle = 'solid', ax=ax, label='GPU', zorder=3)
        plt.xlabel('Data Set Size (B)')
        plt.ylabel('Average Intra-Task (full func) Time (s)')
        plt.title('Average Intra-Task (full func) Time x Data Set Size',fontstyle='italic',fontweight="bold")
        plt.grid(zorder=0)
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_avg_intra_task_execution_time_full_func_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

        # VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC
        plt.figure(4)
        ax = plt.gca()
        df_filtered_mean_cpu.plot(x = 'vl_dataset_memory_size', y = 'vl_intra_task_execution_time_device_func', kind = 'line', color='C3', linestyle = 'dotted', ax=ax, label='CPU', zorder=3)
        df_filtered_mean_gpu.plot(x = 'vl_dataset_memory_size', y = 'vl_intra_task_execution_time_device_func', kind = 'line', color='C3', linestyle = 'solid', ax=ax, label='GPU', zorder=3)
        plt.xlabel('Data Set Size (B)')
        plt.ylabel('Average Intra-Task (device func) Time (s)')
        plt.title('Average Intra-Task (device func) Time x Data Set Size',fontstyle='italic',fontweight="bold")
        plt.grid(zorder=0)
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_avg_intra_task_execution_time_device_func_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

        # VL_COMMUNICATION_TIME
        plt.figure(5)
        ax = plt.gca()
        df_filtered_mean_cpu.plot(x = 'vl_dataset_memory_size', y = 'vl_communication_time', kind = 'line', color='C4', linestyle = 'dotted', ax=ax, label='CPU', zorder=3)
        df_filtered_mean_gpu.plot(x = 'vl_dataset_memory_size', y = 'vl_communication_time', kind = 'line', color='C4', linestyle = 'solid', ax=ax, label='GPU', zorder=3)
        plt.xlabel('Data Set Size (B)')
        plt.ylabel('Average Communication Time (s)')
        plt.title('Average Communication Time x Data Set Size',fontstyle='italic',fontweight="bold")
        plt.grid(zorder=0)
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_avg_communication_time_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)


    elif mode == 3:

        print("\nMode ",mode,": Ploting an overview of all execution times, filtering data set memory size")

        df_filtered_mean = df_filtered.groupby(["ds_device","vl_dataset_memory_size"], as_index=False).mean()

        df_filtered_mean = df_filtered_mean[["ds_device","vl_dataset_memory_size","vl_total_execution_time","vl_inter_task_execution_time","vl_intra_task_execution_time_full_func","vl_intra_task_execution_time_device_func"]]
        
        vl_dataset_memory_size_list = [400, 400000, 400000000]

        for vl_dataset_memory_size in vl_dataset_memory_size_list:

            if vl_dataset_memory_size == 400:
                vl_dataset_memory_size_title = "Data set " + str(vl_dataset_memory_size) + " B"
            elif vl_dataset_memory_size == 400000:
                vl_dataset_memory_size_title = "Data set " + str(vl_dataset_memory_size*1e-3) + " KB"
            elif vl_dataset_memory_size == 400000000:
                vl_dataset_memory_size_title = "Data set " + str(vl_dataset_memory_size*1e-6) + " MB"
            elif vl_dataset_memory_size == 400000000000:
                vl_dataset_memory_size_title = "Data set " + str(vl_dataset_memory_size*1e-9) + " GB"
            else:
                print("Invalid vl_dataset_memory_size")
                return

            df_filtered_mean_cpu = df_filtered_mean[(df_filtered_mean.ds_device=="CPU") & (df_filtered_mean.vl_dataset_memory_size==vl_dataset_memory_size)].sort_values("vl_total_execution_time")
            df_filtered_mean_gpu = df_filtered_mean[(df_filtered_mean.ds_device=="GPU") & (df_filtered_mean.vl_dataset_memory_size==vl_dataset_memory_size)].sort_values("vl_total_execution_time")

            
            # OVERVIEW OF ALL EXECUTION TIMES
            plt.figure()
            ax = plt.gca()
            df_filtered_mean.set_index('ds_device').plot(kind = 'bar', zorder=3)
            plt.legend(['Total', 'Inter', 'Intra (Full Function)', 'Intra (Device Function)'])
            plt.xlabel('Device')
            plt.ylabel('Average Execution Times (s)')
            plt.title('Average Execution Times per Device - '+vl_dataset_memory_size_title, fontstyle='italic',fontweight="bold")
            plt.grid(zorder=0)
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+str(vl_dataset_memory_size)+'_dataset_overview_avg_execution_times_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

            # VL_TOTAL_EXECUTION_TIME
            plt.figure()
            fig, ax = plt.subplots()
            ax.bar(df_filtered_mean_cpu['ds_device'], df_filtered_mean_cpu['vl_total_execution_time'], color='C0', hatch='.', zorder=3)
            ax.bar(df_filtered_mean_gpu['ds_device'], df_filtered_mean_gpu['vl_total_execution_time'], color='C0', hatch='|', zorder=3)
            plt.legend(['CPU','GPU'])
            plt.xlabel('Device')
            plt.ylabel('Average Total Execution Time (s)')
            plt.title('Average Total Execution Time per Device - '+vl_dataset_memory_size_title, fontstyle='italic',fontweight="bold")
            plt.grid(zorder=0)
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+str(vl_dataset_memory_size)+'_dataset_overview_avg_total_execution_time_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

            # VL_INTER_TASK_EXECUTION_TIME
            df_filtered_mean_cpu = df_filtered_mean[(df_filtered_mean.ds_device=="CPU") & (df_filtered_mean.vl_dataset_memory_size==vl_dataset_memory_size)].sort_values("vl_inter_task_execution_time")
            df_filtered_mean_gpu = df_filtered_mean[(df_filtered_mean.ds_device=="GPU") & (df_filtered_mean.vl_dataset_memory_size==vl_dataset_memory_size)].sort_values("vl_inter_task_execution_time")
            plt.figure()
            fig, ax = plt.subplots()
            ax.bar(df_filtered_mean_cpu['ds_device'], df_filtered_mean_cpu['vl_inter_task_execution_time'], color='C1', hatch='.', zorder=3)
            ax.bar(df_filtered_mean_gpu['ds_device'], df_filtered_mean_gpu['vl_inter_task_execution_time'], color='C1', hatch='x', zorder=3)
            plt.legend(['CPU','GPU'])
            plt.xlabel('Device')
            plt.ylabel('Average Inter-Task Time (s)')
            plt.title('Average Inter-Task Time per Device - '+vl_dataset_memory_size_title, fontstyle='italic',fontweight="bold")
            plt.grid(zorder=0)
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+str(vl_dataset_memory_size)+'_dataset_overview_avg_inter_task_execution_time_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

            # VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC
            df_filtered_mean_cpu = df_filtered_mean[(df_filtered_mean.ds_device=="CPU") & (df_filtered_mean.vl_dataset_memory_size==vl_dataset_memory_size)].sort_values("vl_intra_task_execution_time_full_func")
            df_filtered_mean_gpu = df_filtered_mean[(df_filtered_mean.ds_device=="GPU") & (df_filtered_mean.vl_dataset_memory_size==vl_dataset_memory_size)].sort_values("vl_intra_task_execution_time_full_func")
            plt.figure()
            fig, ax = plt.subplots()
            ax.bar(df_filtered_mean_cpu['ds_device'], df_filtered_mean_cpu['vl_intra_task_execution_time_full_func'], color='C2', hatch='.', zorder=3)
            ax.bar(df_filtered_mean_gpu['ds_device'], df_filtered_mean_gpu['vl_intra_task_execution_time_full_func'], color='C2', hatch='x', zorder=3)
            plt.legend(['CPU','GPU'])
            plt.xlabel('Device')
            plt.ylabel('Average Intra-Task (full func) Time (s)')
            plt.title('Average Intra-Task (full func)Time per Device - '+vl_dataset_memory_size_title, fontstyle='italic',fontweight="bold")
            plt.grid(zorder=0)
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+str(vl_dataset_memory_size)+'_dataset_overview_avg_intra_task_execution_time_full_func_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

            # VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC
            df_filtered_mean_cpu = df_filtered_mean[(df_filtered_mean.ds_device=="CPU") & (df_filtered_mean.vl_dataset_memory_size==vl_dataset_memory_size)].sort_values("vl_intra_task_execution_time_device_func")
            df_filtered_mean_gpu = df_filtered_mean[(df_filtered_mean.ds_device=="GPU") & (df_filtered_mean.vl_dataset_memory_size==vl_dataset_memory_size)].sort_values("vl_intra_task_execution_time_device_func")
            plt.figure()
            fig, ax = plt.subplots()
            ax.bar(df_filtered_mean_cpu['ds_device'], df_filtered_mean_cpu['vl_intra_task_execution_time_device_func'], color='C3', hatch='.', zorder=3)
            ax.bar(df_filtered_mean_gpu['ds_device'], df_filtered_mean_gpu['vl_intra_task_execution_time_device_func'], color='C3', hatch='x', zorder=3)
            plt.legend(['CPU','GPU'])
            plt.xlabel('Device')
            plt.ylabel('Average Intra-Task (device func) Time (s)')
            plt.title('Average Intra-Task (device func) Time per Device - '+vl_dataset_memory_size_title, fontstyle='italic',fontweight="bold")
            plt.grid(zorder=0)
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+str(vl_dataset_memory_size)+'_dataset_overview_avg_intra_task_execution_time_device_func_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)


    elif mode == 4:

        print("\nMode ",mode,": Ploting an overview of all execution times, filtering block dimension")

        df_filtered_mean = df_filtered.groupby(["ds_device","ds_parameter_attribute"], as_index=False).mean()

        df_filtered_mean = df_filtered_mean[["ds_device","ds_parameter_attribute","vl_total_execution_time","vl_inter_task_execution_time","vl_intra_task_execution_time_full_func","vl_intra_task_execution_time_device_func"]]
        
        ds_parameter_attribute_list = ["0.25","0.50","0.75","1.00"]

        for ds_parameter_attribute in ds_parameter_attribute_list:

            ds_parameter_attribute_title = str(float(ds_parameter_attribute)*100) + "% of dataset"

            df_filtered_mean_cpu = df_filtered_mean[(df_filtered_mean.ds_device=="CPU") & (df_filtered_mean.ds_parameter_attribute==ds_parameter_attribute)].sort_values("vl_total_execution_time")
            df_filtered_mean_gpu = df_filtered_mean[(df_filtered_mean.ds_device=="GPU") & (df_filtered_mean.ds_parameter_attribute==ds_parameter_attribute)].sort_values("vl_total_execution_time")

            
            # OVERVIEW OF ALL EXECUTION TIMES
            plt.figure()
            ax = plt.gca()
            df_filtered_mean.set_index('ds_device').plot(kind = 'bar', zorder=3)
            plt.legend(['Total Execution Time', 'Inter Task Execution Time', 'Intra Task Execution Time (Full Function)', 'Intra Task Execution Time (Device Function)'])
            plt.xlabel('Device')
            plt.ylabel('Average Execution Times (s)')
            plt.title('Average Execution Times per Device - Block '+ds_parameter_attribute_title, fontstyle='italic',fontweight="bold")
            plt.grid(zorder=0)
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+ds_parameter_attribute+'_dataset_overview_avg_execution_times_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

            # VL_TOTAL_EXECUTION_TIME
            plt.figure()
            fig, ax = plt.subplots()
            ax.bar(df_filtered_mean_cpu['ds_device'], df_filtered_mean_cpu['vl_total_execution_time'], color='C0', hatch='.', zorder=3)
            ax.bar(df_filtered_mean_gpu['ds_device'], df_filtered_mean_gpu['vl_total_execution_time'], color='C0', hatch='|', zorder=3)
            plt.legend(['CPU','GPU'])
            plt.xlabel('Device')
            plt.ylabel('Average Total Execution Time (s)')
            plt.title('Average Total Execution Time per Device - Block '+ds_parameter_attribute_title, fontstyle='italic',fontweight="bold")
            plt.grid(zorder=0)
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+ds_parameter_attribute+'_dataset_overview_avg_total_execution_time_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

            # VL_INTER_TASK_EXECUTION_TIME
            df_filtered_mean_cpu = df_filtered_mean[(df_filtered_mean.ds_device=="CPU") & (df_filtered_mean.ds_parameter_attribute==ds_parameter_attribute)].sort_values("vl_inter_task_execution_time")
            df_filtered_mean_gpu = df_filtered_mean[(df_filtered_mean.ds_device=="GPU") & (df_filtered_mean.ds_parameter_attribute==ds_parameter_attribute)].sort_values("vl_inter_task_execution_time")
            plt.figure()
            fig, ax = plt.subplots()
            ax.bar(df_filtered_mean_cpu['ds_device'], df_filtered_mean_cpu['vl_inter_task_execution_time'], color='C1', hatch='.', zorder=3)
            ax.bar(df_filtered_mean_gpu['ds_device'], df_filtered_mean_gpu['vl_inter_task_execution_time'], color='C1', hatch='x', zorder=3)
            plt.legend(['CPU','GPU'])
            plt.xlabel('Device')
            plt.ylabel('Average Inter-Task Time (s)')
            plt.title('Average Inter-Task Time per Device - Block '+ds_parameter_attribute_title, fontstyle='italic',fontweight="bold")
            plt.grid(zorder=0)
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+ds_parameter_attribute+'_dataset_overview_avg_inter_task_execution_time_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

            # VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC
            df_filtered_mean_cpu = df_filtered_mean[(df_filtered_mean.ds_device=="CPU") & (df_filtered_mean.ds_parameter_attribute==ds_parameter_attribute)].sort_values("vl_intra_task_execution_time_full_func")
            df_filtered_mean_gpu = df_filtered_mean[(df_filtered_mean.ds_device=="GPU") & (df_filtered_mean.ds_parameter_attribute==ds_parameter_attribute)].sort_values("vl_intra_task_execution_time_full_func")
            plt.figure()
            fig, ax = plt.subplots()
            ax.bar(df_filtered_mean_cpu['ds_device'], df_filtered_mean_cpu['vl_intra_task_execution_time_full_func'], color='C2', hatch='.', zorder=3)
            ax.bar(df_filtered_mean_gpu['ds_device'], df_filtered_mean_gpu['vl_intra_task_execution_time_full_func'], color='C2', hatch='x', zorder=3)
            plt.legend(['CPU','GPU'])
            plt.xlabel('Device')
            plt.ylabel('Average Intra-Task (full func) Time (s)')
            plt.title('Average Intra-Task (full func)Time per Device - Block '+ds_parameter_attribute_title, fontstyle='italic',fontweight="bold")
            plt.grid(zorder=0)
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+ds_parameter_attribute+'_dataset_overview_avg_intra_task_execution_time_full_func_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

            # VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC
            df_filtered_mean_cpu = df_filtered_mean[(df_filtered_mean.ds_device=="CPU") & (df_filtered_mean.ds_parameter_attribute==ds_parameter_attribute)].sort_values("vl_intra_task_execution_time_device_func")
            df_filtered_mean_gpu = df_filtered_mean[(df_filtered_mean.ds_device=="GPU") & (df_filtered_mean.ds_parameter_attribute==ds_parameter_attribute)].sort_values("vl_intra_task_execution_time_device_func")
            plt.figure()
            fig, ax = plt.subplots()
            ax.bar(df_filtered_mean_cpu['ds_device'], df_filtered_mean_cpu['vl_intra_task_execution_time_device_func'], color='C3', hatch='.', zorder=3)
            ax.bar(df_filtered_mean_gpu['ds_device'], df_filtered_mean_gpu['vl_intra_task_execution_time_device_func'], color='C3', hatch='x', zorder=3)
            plt.legend(['CPU','GPU'])
            plt.xlabel('Device')
            plt.ylabel('Average Intra-Task (device func) Time (s)')
            plt.title('Average Intra-Task (device func) Time per Device - Block '+ds_parameter_attribute_title, fontstyle='italic',fontweight="bold")
            plt.grid(zorder=0)
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+ds_parameter_attribute+'_dataset_overview_avg_intra_task_execution_time_device_func_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)


    elif mode == 5:

        print("\nMode ",mode,": Ploting an overview of all execution times, filtering parallelism level (extreme cases)")

        df_filtered_mean = df_filtered.groupby(["ds_device","ds_parameter_attribute"], as_index=False).mean()

        df_filtered_mean = df_filtered_mean[["ds_device","ds_parameter_attribute","vl_total_execution_time","vl_inter_task_execution_time","vl_intra_task_execution_time_full_func","vl_intra_task_execution_time_device_func"]]
        
        ds_parameter_attribute_list = ["MIN_INTER_MAX_INTRA", "MAX_INTER_MIN_INTRA"]

        for ds_parameter_attribute in ds_parameter_attribute_list:

            if ds_parameter_attribute == "MIN_INTER_MAX_INTRA":
                ds_parameter_attribute_title = "Min. Inter-parallelism"
            elif ds_parameter_attribute == "MAX_INTER_MIN_INTRA":
                ds_parameter_attribute_title = "Max. Inter-parallelism"
            else:
                print("Invalid ds_parameter_attribute")
                return

            df_filtered_mean_cpu = df_filtered_mean[(df_filtered_mean.ds_device=="CPU") & (df_filtered_mean.ds_parameter_attribute==ds_parameter_attribute)].sort_values("vl_total_execution_time")
            df_filtered_mean_gpu = df_filtered_mean[(df_filtered_mean.ds_device=="GPU") & (df_filtered_mean.ds_parameter_attribute==ds_parameter_attribute)].sort_values("vl_total_execution_time")

            
            # OVERVIEW OF ALL EXECUTION TIMES
            plt.figure()
            ax = plt.gca()
            df_filtered_mean.set_index('ds_device').plot(kind = 'bar', zorder=3)
            plt.legend(['Total Execution Time', 'Inter Task Execution Time', 'Intra Task Execution Time (Full Function)', 'Intra Task Execution Time (Device Function)'])
            plt.xlabel('Device')
            plt.ylabel('Average Execution Times (s)')
            plt.title('Average Execution Times per Device - '+ds_parameter_attribute_title, fontstyle='italic',fontweight="bold")
            plt.grid(zorder=0)
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+ds_parameter_attribute+'_dataset_overview_avg_execution_times_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

            # VL_TOTAL_EXECUTION_TIME
            plt.figure()
            fig, ax = plt.subplots()
            ax.bar(df_filtered_mean_cpu['ds_device'], df_filtered_mean_cpu['vl_total_execution_time'], color='C0', hatch='.', zorder=3)
            ax.bar(df_filtered_mean_gpu['ds_device'], df_filtered_mean_gpu['vl_total_execution_time'], color='C0', hatch='|', zorder=3)
            plt.legend(['CPU','GPU'])
            plt.xlabel('Device')
            plt.ylabel('Average Total Execution Time (s)')
            plt.title('Average Total Execution Time per Device - '+ds_parameter_attribute_title, fontstyle='italic',fontweight="bold")
            plt.grid(zorder=0)
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+ds_parameter_attribute+'_dataset_overview_avg_total_execution_time_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

            # VL_INTER_TASK_EXECUTION_TIME
            df_filtered_mean_cpu = df_filtered_mean[(df_filtered_mean.ds_device=="CPU") & (df_filtered_mean.ds_parameter_attribute==ds_parameter_attribute)].sort_values("vl_inter_task_execution_time")
            df_filtered_mean_gpu = df_filtered_mean[(df_filtered_mean.ds_device=="GPU") & (df_filtered_mean.ds_parameter_attribute==ds_parameter_attribute)].sort_values("vl_inter_task_execution_time")
            plt.figure()
            fig, ax = plt.subplots()
            ax.bar(df_filtered_mean_cpu['ds_device'], df_filtered_mean_cpu['vl_inter_task_execution_time'], color='C1', hatch='.', zorder=3)
            ax.bar(df_filtered_mean_gpu['ds_device'], df_filtered_mean_gpu['vl_inter_task_execution_time'], color='C1', hatch='x', zorder=3)
            plt.legend(['CPU','GPU'])
            plt.xlabel('Device')
            plt.ylabel('Average Inter-Task Time (s)')
            plt.title('Average Inter-Task Time per Device - '+ds_parameter_attribute_title, fontstyle='italic',fontweight="bold")
            plt.grid(zorder=0)
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+ds_parameter_attribute+'_dataset_overview_avg_inter_task_execution_time_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

            # VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC
            df_filtered_mean_cpu = df_filtered_mean[(df_filtered_mean.ds_device=="CPU") & (df_filtered_mean.ds_parameter_attribute==ds_parameter_attribute)].sort_values("vl_intra_task_execution_time_full_func")
            df_filtered_mean_gpu = df_filtered_mean[(df_filtered_mean.ds_device=="GPU") & (df_filtered_mean.ds_parameter_attribute==ds_parameter_attribute)].sort_values("vl_intra_task_execution_time_full_func")
            plt.figure()
            fig, ax = plt.subplots()
            ax.bar(df_filtered_mean_cpu['ds_device'], df_filtered_mean_cpu['vl_intra_task_execution_time_full_func'], color='C2', hatch='.', zorder=3)
            ax.bar(df_filtered_mean_gpu['ds_device'], df_filtered_mean_gpu['vl_intra_task_execution_time_full_func'], color='C2', hatch='x', zorder=3)
            plt.legend(['CPU','GPU'])
            plt.xlabel('Device')
            plt.ylabel('Average Intra-Task (full func) Time (s)')
            plt.title('Average Intra-Task (full func)Time per Device - '+ds_parameter_attribute_title, fontstyle='italic',fontweight="bold")
            plt.grid(zorder=0)
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+ds_parameter_attribute+'_dataset_overview_avg_intra_task_execution_time_full_func_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

            # VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC
            df_filtered_mean_cpu = df_filtered_mean[(df_filtered_mean.ds_device=="CPU") & (df_filtered_mean.ds_parameter_attribute==ds_parameter_attribute)].sort_values("vl_intra_task_execution_time_device_func")
            df_filtered_mean_gpu = df_filtered_mean[(df_filtered_mean.ds_device=="GPU") & (df_filtered_mean.ds_parameter_attribute==ds_parameter_attribute)].sort_values("vl_intra_task_execution_time_device_func")
            plt.figure()
            fig, ax = plt.subplots()
            ax.bar(df_filtered_mean_cpu['ds_device'], df_filtered_mean_cpu['vl_intra_task_execution_time_device_func'], color='C3', hatch='.', zorder=3)
            ax.bar(df_filtered_mean_gpu['ds_device'], df_filtered_mean_gpu['vl_intra_task_execution_time_device_func'], color='C3', hatch='x', zorder=3)
            plt.legend(['CPU','GPU'])
            plt.xlabel('Device')
            plt.ylabel('Average Intra-Task (device func) Time (s)')
            plt.title('Average Intra-Task (device func) Time per Device - '+ds_parameter_attribute_title, fontstyle='italic',fontweight="bold")
            plt.grid(zorder=0)
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+ds_parameter_attribute+'_dataset_overview_avg_intra_task_execution_time_device_func_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

    
    elif mode == 6:
        
        print("\nMode ",mode,": Ploting an overview of all execution times grouped by data set description")
        
        vl_dataset_memory_size_list = [400, 400000, 400000000]

        for vl_dataset_memory_size in vl_dataset_memory_size_list:

            if vl_dataset_memory_size == 400:
                vl_dataset_memory_size_title = str(int(vl_dataset_memory_size)) + " B"
            elif vl_dataset_memory_size == 400000:
                vl_dataset_memory_size_title = str(int(vl_dataset_memory_size*1e-3)) + " KB"
            elif vl_dataset_memory_size == 400000000:
                vl_dataset_memory_size_title = str(int(vl_dataset_memory_size*1e-6)) + " MB"

            df_filtered_loop = df_filtered[df_filtered.vl_dataset_memory_size==vl_dataset_memory_size]
            df_filtered_mean = df_filtered_loop.groupby(["ds_device","ds_dataset"], as_index=False).mean()
            df_filtered_mean = df_filtered_mean[["ds_device","ds_dataset","vl_total_execution_time","vl_inter_task_execution_time","vl_intra_task_execution_time_full_func","vl_intra_task_execution_time_device_func"]].sort_values(by=["ds_dataset"], ascending=True)
            
            # VL_TOTAL_EXECUTION_TIME
            plt.figure()
            X_axis = np.arange(len(df_filtered_mean["ds_dataset"].drop_duplicates()))
            plt.bar(X_axis - 0.2, df_filtered_mean[(df_filtered_mean.ds_device=="CPU")]["vl_total_execution_time"], 0.3, label = "CPU", color='C0', hatch='.', zorder=3)
            plt.bar(X_axis + 0.2, df_filtered_mean[(df_filtered_mean.ds_device=="GPU")]["vl_total_execution_time"], 0.3, label = "GPU", color='C0', hatch='x', zorder=3)
            plt.xticks(X_axis, df_filtered_mean["ds_dataset"].drop_duplicates(), rotation=0)
            plt.xlabel('Data Set Description')
            plt.ylabel('Average Total Execution Time (s)')
            plt.title('Average Total Execution Time per Data Set Description ' + vl_dataset_memory_size_title,fontstyle='italic',fontweight="bold")
            plt.grid(zorder=0)
            plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=len(df_filtered_mean["ds_dataset"].drop_duplicates()))
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+str(vl_dataset_memory_size)+'_avg_total_execution_time_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

            # VL_INTER_TASK_EXECUTION_TIME
            plt.figure()
            X_axis = np.arange(len(df_filtered_mean["ds_dataset"].drop_duplicates()))
            plt.bar(X_axis - 0.2, df_filtered_mean[(df_filtered_mean.ds_device=="CPU")]["vl_inter_task_execution_time"], 0.3, label = "CPU", color='C1', hatch='.', zorder=3)
            plt.bar(X_axis + 0.2, df_filtered_mean[(df_filtered_mean.ds_device=="GPU")]["vl_inter_task_execution_time"], 0.3, label = "GPU", color='C1', hatch='x', zorder=3)
            plt.xticks(X_axis, df_filtered_mean["ds_dataset"].drop_duplicates(), rotation=0)
            plt.xlabel('Data Set Description')
            plt.ylabel('Average Inter Task Execution Time (s)')
            plt.title('Average Inter Task Execution Time per Data Set Description ' + vl_dataset_memory_size_title,fontstyle='italic',fontweight="bold")
            plt.grid(zorder=0)
            plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=len(df_filtered_mean["ds_dataset"].drop_duplicates()))
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+str(vl_dataset_memory_size)+'_avg_inter_task_execution_time_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

            # VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC
            plt.figure()
            X_axis = np.arange(len(df_filtered_mean["ds_dataset"].drop_duplicates()))
            plt.bar(X_axis - 0.2, df_filtered_mean[(df_filtered_mean.ds_device=="CPU")]["vl_intra_task_execution_time_full_func"], 0.3, label = "CPU", color='C2', hatch='.', zorder=3)
            plt.bar(X_axis + 0.2, df_filtered_mean[(df_filtered_mean.ds_device=="GPU")]["vl_intra_task_execution_time_full_func"], 0.3, label = "GPU", color='C2', hatch='x', zorder=3)
            plt.xticks(X_axis, df_filtered_mean["ds_dataset"].drop_duplicates(), rotation=0)
            plt.xlabel('Data Set Description')
            plt.ylabel('Average Intra-Task (full func) Time (s)')
            plt.title('Average Intra-Task (full func) Time per Data Set Description ' + vl_dataset_memory_size_title,fontstyle='italic',fontweight="bold")
            plt.grid(zorder=0)
            plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=len(df_filtered_mean["ds_dataset"].drop_duplicates()))
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+str(vl_dataset_memory_size)+'_avg_intra_task_execution_time_full_func_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

            # VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC
            plt.figure()
            X_axis = np.arange(len(df_filtered_mean["ds_dataset"].drop_duplicates()))
            plt.bar(X_axis - 0.2, df_filtered_mean[(df_filtered_mean.ds_device=="CPU")]["vl_intra_task_execution_time_device_func"], 0.3, label = "CPU", color='C3', hatch='.', zorder=3)
            plt.bar(X_axis + 0.2, df_filtered_mean[(df_filtered_mean.ds_device=="GPU")]["vl_intra_task_execution_time_device_func"], 0.3, label = "GPU", color='C3', hatch='x', zorder=3)
            plt.xticks(X_axis, df_filtered_mean["ds_dataset"].drop_duplicates(), rotation=0)
            plt.xlabel('Data Set Description')
            plt.ylabel('Average Intra-Task (device func) Time (s)')
            plt.title('Average Intra-Task (device func) Time per Data Set Description ' + vl_dataset_memory_size_title,fontstyle='italic',fontweight="bold")
            plt.grid(zorder=0)
            plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=len(df_filtered_mean["ds_dataset"].drop_duplicates()))
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+str(vl_dataset_memory_size)+'_avg_intra_task_execution_time_device_func_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)


    elif mode == 7:
        
        print("\nMode ",mode,": Ploting an overview of all execution times filtered by data set description and grouped by parameter attribute")
        
        ds_dataset_list = ["S_A_1","S_A_2","S_A_3","S_A_4","S_B_1","S_B_2","S_B_3","S_B_4","S_C_1","S_C_2","S_C_3","S_C_4"]

        for ds_dataset in ds_dataset_list:

            df_filtered_loop = df_filtered[(df_filtered.ds_dataset==ds_dataset)]
            df_filtered_mean = df_filtered_loop.groupby(["ds_device","ds_dataset","ds_parameter_attribute"], as_index=False).mean()

            df_filtered_mean = df_filtered_mean[["ds_device","ds_dataset","ds_parameter_attribute","vl_total_execution_time","vl_inter_task_execution_time","vl_intra_task_execution_time_full_func","vl_intra_task_execution_time_device_func"]].sort_values(by=["ds_parameter_attribute"], ascending=True)
            
            df_filtered_mean['ds_parameter_attribute'] = np.where(df_filtered_mean['ds_parameter_attribute'] == 'MIN_INTER_MAX_INTRA', 'MIN_I',
                          np.where(df_filtered_mean['ds_parameter_attribute'] == 'MAX_INTER_MIN_INTRA', 'MAX_I', df_filtered_mean['ds_parameter_attribute']))

            # VL_TOTAL_EXECUTION_TIME
            plt.figure()
            X_axis = np.arange(len(df_filtered_mean["ds_parameter_attribute"].drop_duplicates()))
            plt.bar(X_axis - 0.2, df_filtered_mean[(df_filtered_mean.ds_device=="CPU")]["vl_total_execution_time"], 0.3, label = "CPU", color='C0', hatch='.', zorder=3)
            plt.bar(X_axis + 0.2, df_filtered_mean[(df_filtered_mean.ds_device=="GPU")]["vl_total_execution_time"], 0.3, label = "GPU", color='C0', hatch='x', zorder=3)
            plt.xticks(X_axis, df_filtered_mean["ds_parameter_attribute"].drop_duplicates(), rotation=0)
            plt.xlabel('Block Dimension')
            plt.ylabel('Average Total Execution Time (s)')
            plt.title('Average Total Execution Time per Block Dimension (' + ds_dataset + ')',fontstyle='italic',fontweight="bold")
            plt.grid(zorder=0)
            plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=len(df_filtered_mean["ds_parameter_attribute"].drop_duplicates()))
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+ds_dataset+'_avg_total_execution_time_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

            # VL_INTER_TASK_EXECUTION_TIME
            plt.figure()
            X_axis = np.arange(len(df_filtered_mean["ds_parameter_attribute"].drop_duplicates()))
            plt.bar(X_axis - 0.2, df_filtered_mean[(df_filtered_mean.ds_device=="CPU")]["vl_inter_task_execution_time"], 0.3, label = "CPU", color='C1', hatch='.', zorder=3)
            plt.bar(X_axis + 0.2, df_filtered_mean[(df_filtered_mean.ds_device=="GPU")]["vl_inter_task_execution_time"], 0.3, label = "GPU", color='C1', hatch='x', zorder=3)
            plt.xticks(X_axis, df_filtered_mean["ds_parameter_attribute"].drop_duplicates(), rotation=0)
            plt.xlabel('Block Dimension')
            plt.ylabel('Average Inter-Task Execution Time (s)')
            plt.title('Average Inter-Task Execution Time per Block Dimension (' + ds_dataset + ')',fontstyle='italic',fontweight="bold")
            plt.grid(zorder=0)
            plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=len(df_filtered_mean["ds_parameter_attribute"].drop_duplicates()))
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+ds_dataset+'_avg_inter_task_execution_time_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

            # VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC
            plt.figure()
            X_axis = np.arange(len(df_filtered_mean["ds_parameter_attribute"].drop_duplicates()))
            plt.bar(X_axis - 0.2, df_filtered_mean[(df_filtered_mean.ds_device=="CPU")]["vl_intra_task_execution_time_full_func"], 0.3, label = "CPU", color='C2', hatch='.', zorder=3)
            plt.bar(X_axis + 0.2, df_filtered_mean[(df_filtered_mean.ds_device=="GPU")]["vl_intra_task_execution_time_full_func"], 0.3, label = "GPU", color='C2', hatch='x', zorder=3)
            plt.xticks(X_axis, df_filtered_mean["ds_parameter_attribute"].drop_duplicates(), rotation=0)
            plt.xlabel('Block Dimension')
            plt.ylabel('Average Intra-Task (full func) Time (s)')
            plt.title('Average Intra-Task (full func) Time per Block Dimension (' + ds_dataset + ')',fontstyle='italic',fontweight="bold")
            plt.grid(zorder=0)
            plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=len(df_filtered_mean["ds_parameter_attribute"].drop_duplicates()))
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+ds_dataset+'_avg_intra_task_execution_time_full_func_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

            # VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC
            plt.figure()
            X_axis = np.arange(len(df_filtered_mean["ds_parameter_attribute"].drop_duplicates()))
            plt.bar(X_axis - 0.2, df_filtered_mean[(df_filtered_mean.ds_device=="CPU")]["vl_intra_task_execution_time_device_func"], 0.3, label = "CPU", color='C3', hatch='.', zorder=3)
            plt.bar(X_axis + 0.2, df_filtered_mean[(df_filtered_mean.ds_device=="GPU")]["vl_intra_task_execution_time_device_func"], 0.3, label = "GPU", color='C3', hatch='x', zorder=3)
            plt.xticks(X_axis, df_filtered_mean["ds_parameter_attribute"].drop_duplicates(), rotation=0)
            plt.xlabel('Block Dimension')
            plt.ylabel('Average Intra-Task (device func) Time (s)')
            plt.title('Average Intra-Task (device func) Time per Block Dimension (' + ds_dataset + ')',fontstyle='italic',fontweight="bold")
            plt.grid(zorder=0)
            plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=len(df_filtered_mean["ds_parameter_attribute"].drop_duplicates()))
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+ds_dataset+'_avg_intra_task_execution_time_device_func_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)


    elif mode == 8:
        
        print("\nMode ",mode,": Ploting an overview of CPU speedup over GPU per vl_dataset_memory_size, ds_parameter_type, ds_parameter_attribute, ds_dataset")

        # Speedup CPU Per vl_dataset_memory_size
        df_filtered_mean = df_filtered.groupby(["vl_dataset_memory_size"], as_index=False).mean()
        df_filtered_mean = df_filtered_mean[["vl_dataset_memory_size","speedup_cpu_total_execution_time","speedup_cpu_inter_task_execution_time","speedup_cpu_intra_task_execution_time_full_func","speedup_cpu_intra_task_execution_time_device_func"]].sort_values(by=["speedup_cpu_total_execution_time"], ascending=False)

        plt.figure(1)
        ax = plt.gca()
        df_filtered_mean.set_index('vl_dataset_memory_size').plot(kind = 'bar', hatch='.', zorder=3)
        plt.legend(['Total', 'Inter', 'Intra (Full Function)', 'Intra (Device Function)'])
        plt.xlabel('Data Set Size (B)')
        plt.ylabel('Speedup')
        plt.title('Speedup CPU over GPU x Data Set Size',fontstyle='italic',fontweight="bold")
        plt.grid(zorder=0)
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_speedup_cpu_per_dataset_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)
    
        # Speedup CPU Per ds_parameter_type
        df_filtered_mean = df_filtered.groupby(["ds_parameter_type"], as_index=False).mean()
        df_filtered_mean = df_filtered_mean[["ds_parameter_type","speedup_cpu_total_execution_time","speedup_cpu_inter_task_execution_time","speedup_cpu_intra_task_execution_time_full_func","speedup_cpu_intra_task_execution_time_device_func"]].sort_values(by=["speedup_cpu_total_execution_time"], ascending=False)

        plt.figure(2)
        ax = plt.gca()
        df_filtered_mean.set_index('ds_parameter_type').plot(kind = 'bar', hatch='.', zorder=3)
        plt.legend(['Total', 'Inter', 'Intra (Full Function)', 'Intra (Device Function)'])
        plt.xlabel('Parameter Type')
        plt.ylabel('Speedup')
        plt.title('Speedup CPU over GPU x Parameter Type',fontstyle='italic',fontweight="bold")
        plt.grid(zorder=0)
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_speedup_cpu_per_ds_parameter_type_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)
    
        # Speedup CPU Per ds_parameter_attribute
        df_filtered_mean = df_filtered.groupby(["ds_parameter_attribute"], as_index=False).mean()
        df_filtered_mean = df_filtered_mean[["ds_parameter_attribute","speedup_cpu_total_execution_time","speedup_cpu_inter_task_execution_time","speedup_cpu_intra_task_execution_time_full_func","speedup_cpu_intra_task_execution_time_device_func"]].sort_values(by=["speedup_cpu_total_execution_time"], ascending=False)

        df_filtered_mean['ds_parameter_attribute'] = np.where(df_filtered_mean['ds_parameter_attribute'] == 'MIN_INTER_MAX_INTRA', 'MIN_I',
                          np.where(df_filtered_mean['ds_parameter_attribute'] == 'MAX_INTER_MIN_INTRA', 'MAX_I', df_filtered_mean['ds_parameter_attribute']))

        plt.figure(3)
        ax = plt.gca()
        df_filtered_mean.set_index('ds_parameter_attribute').plot(kind = 'bar', hatch='.', zorder=3)
        plt.yticks(np.arange(0, 3.1, 0.5))
        plt.xticks(rotation=0)
        plt.legend(['Total', 'Inter', 'Intra (Full Function)', 'Intra (Device Function)'])
        plt.xlabel('Block Dimension')
        plt.ylabel('Speedup')
        plt.title('Speedup CPU over GPU x Block Dimension',fontstyle='italic',fontweight="bold")
        plt.grid(zorder=0)
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_speedup_cpu_per_ds_parameter_attribute_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

        # Speedup CPU Per ds_dataset
        df_filtered_mean = df_filtered.groupby(["ds_dataset"], as_index=False).mean()
        df_filtered_mean = df_filtered_mean[["ds_dataset","speedup_cpu_total_execution_time","speedup_cpu_inter_task_execution_time","speedup_cpu_intra_task_execution_time_full_func","speedup_cpu_intra_task_execution_time_device_func"]].sort_values(by=["speedup_cpu_total_execution_time"], ascending=False)

        plt.figure(4)
        ax = plt.gca()
        df_filtered_mean.set_index('ds_dataset').plot(kind = 'bar', hatch='.', zorder=3)
        plt.legend(['Total', 'Inter', 'Intra (Full Function)', 'Intra (Device Function)'])
        plt.xlabel('Data Set Type')
        plt.ylabel('Speedup')
        plt.title('Speedup CPU over GPU x Data Set Type',fontstyle='italic',fontweight="bold")
        plt.grid(zorder=0)
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_speedup_cpu_per_ds_dataset_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)


        # Heatmap CPU Speedups over GPU
        df_filtered_heatmap = df_filtered[["ds_dataset","ds_parameter_attribute","speedup_cpu_total_execution_time"]].sort_values(by=["speedup_cpu_total_execution_time"], ascending=False)
        df_filtered_heatmap['ds_parameter_attribute'] = np.where(df_filtered_heatmap['ds_parameter_attribute'] == 'MIN_INTER_MAX_INTRA', 'MIN_I',
                np.where(df_filtered_heatmap['ds_parameter_attribute'] == 'MAX_INTER_MIN_INTRA', 'MAX_I', df_filtered_heatmap['ds_parameter_attribute']))

        x = pd.DataFrame(df_filtered_heatmap['ds_parameter_attribute'].unique())
        heatmap_pt = pd.pivot_table(df_filtered_heatmap,values ='speedup_cpu_total_execution_time', index=['ds_dataset'], columns='ds_parameter_attribute')
        
        plt.figure(5)
        fig, ax = plt.subplots(figsize=(16,8))
        sns.set()
        sns.heatmap(heatmap_pt, cmap='YlGnBu')
        plt.xticks(rotation=15)
        plt.xlabel('Block Dimension')
        plt.ylabel('Data Set Type')
        plt.title('Speedup CPU over GPU',fontstyle='italic',fontweight="bold")
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_heatmap_speedup_cpu_per_ds_dataset_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)


    elif mode == 9:
        
        print("\nMode ",mode,": Ploting an overview of GPU speedup over CPU per vl_dataset_memory_size, ds_parameter_type, ds_parameter_attribute, ds_dataset")

        # Speedup GPU Per vl_dataset_memory_size
        df_filtered_mean = df_filtered.groupby(["vl_dataset_memory_size"], as_index=False).mean()
        df_filtered_mean = df_filtered_mean[["vl_dataset_memory_size","speedup_gpu_total_execution_time","speedup_gpu_inter_task_execution_time","speedup_gpu_intra_task_execution_time_full_func","speedup_gpu_intra_task_execution_time_device_func"]].sort_values(by=["speedup_gpu_total_execution_time"], ascending=False)

        plt.figure(1)
        ax = plt.gca()
        df_filtered_mean.set_index('vl_dataset_memory_size').plot(kind = 'bar', hatch='x', zorder=3)
        plt.legend(['Total', 'Inter', 'Intra (Full Function)', 'Intra (Device Function)'])
        plt.xlabel('Data Set Size (B)')
        plt.ylabel('Speedup')
        plt.title('Speedup GPU over CPU x Data Set Size',fontstyle='italic',fontweight="bold")
        plt.grid(zorder=0)
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_speedup_gpu_per_dataset_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)
    
        # Speedup CPU Per ds_parameter_type
        df_filtered_mean = df_filtered.groupby(["ds_parameter_type"], as_index=False).mean()
        df_filtered_mean = df_filtered_mean[["ds_parameter_type","speedup_gpu_total_execution_time","speedup_gpu_inter_task_execution_time","speedup_gpu_intra_task_execution_time_full_func","speedup_gpu_intra_task_execution_time_device_func"]].sort_values(by=["speedup_gpu_total_execution_time"], ascending=False)

        plt.figure(2)
        ax = plt.gca()
        df_filtered_mean.set_index('ds_parameter_type').plot(kind = 'bar', hatch='x', zorder=3)
        plt.legend(['Total', 'Inter', 'Intra (Full Function)', 'Intra (Device Function)'])
        plt.xlabel('Parameter Type')
        plt.ylabel('Speedup')
        plt.title('Speedup GPU over CPU x Parameter Type',fontstyle='italic',fontweight="bold")
        plt.grid(zorder=0)
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_speedup_gpu_per_ds_parameter_type_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)
    
        # Speedup CPU Per ds_parameter_attribute
        df_filtered_mean = df_filtered.groupby(["ds_parameter_attribute"], as_index=False).mean()
        df_filtered_mean = df_filtered_mean[["ds_parameter_attribute","speedup_gpu_total_execution_time","speedup_gpu_inter_task_execution_time","speedup_gpu_intra_task_execution_time_full_func","speedup_gpu_intra_task_execution_time_device_func"]].sort_values(by=["speedup_gpu_total_execution_time"], ascending=False)

        df_filtered_mean['ds_parameter_attribute'] = np.where(df_filtered_mean['ds_parameter_attribute'] == 'MIN_INTER_MAX_INTRA', 'MIN_I',
                          np.where(df_filtered_mean['ds_parameter_attribute'] == 'MAX_INTER_MIN_INTRA', 'MAX_I', df_filtered_mean['ds_parameter_attribute']))

        plt.figure(3)
        ax = plt.gca()
        df_filtered_mean.set_index('ds_parameter_attribute').plot(kind = 'bar', hatch='x', zorder=3)
        plt.yticks(np.arange(0, 31, 5))
        plt.xticks(rotation=0)
        plt.legend(['Total', 'Inter', 'Intra (Full Function)', 'Intra (Device Function)'])
        plt.xlabel('Block Dimension')
        plt.ylabel('Speedup')
        plt.title('Speedup GPU over CPU x Block Dimension',fontstyle='italic',fontweight="bold")
        plt.grid(zorder=0)
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_speedup_gpu_per_ds_parameter_attribute_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

        # Speedup CPU Per ds_dataset
        df_filtered_mean = df_filtered.groupby(["ds_dataset"], as_index=False).mean()
        df_filtered_mean = df_filtered_mean[["ds_dataset","speedup_gpu_total_execution_time","speedup_gpu_inter_task_execution_time","speedup_gpu_intra_task_execution_time_full_func","speedup_gpu_intra_task_execution_time_device_func"]].sort_values(by=["speedup_gpu_total_execution_time"], ascending=False)

        plt.figure(4)
        ax = plt.gca()
        df_filtered_mean.set_index('ds_dataset').plot(kind = 'bar', hatch='x', zorder=3)
        plt.legend(['Total', 'Inter', 'Intra (Full Function)', 'Intra (Device Function)'])
        plt.xlabel('Data Set Type')
        plt.ylabel('Speedup')
        plt.title('Speedup GPU over CPU x Data Set Type',fontstyle='italic',fontweight="bold")
        plt.grid(zorder=0)
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_speedup_gpu_per_ds_dataset_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

        # Heatmap GPU Speedups over CPU
        df_filtered_heatmap = df_filtered[["ds_dataset","ds_parameter_attribute","speedup_gpu_total_execution_time"]].sort_values(by=["speedup_gpu_total_execution_time"], ascending=False)
        df_filtered_heatmap['ds_parameter_attribute'] = np.where(df_filtered_heatmap['ds_parameter_attribute'] == 'MIN_INTER_MAX_INTRA', 'MIN_I',
                np.where(df_filtered_heatmap['ds_parameter_attribute'] == 'MAX_INTER_MIN_INTRA', 'MAX_I', df_filtered_heatmap['ds_parameter_attribute']))

        x = pd.DataFrame(df_filtered_heatmap['ds_parameter_attribute'].unique())
        heatmap_pt = pd.pivot_table(df_filtered_heatmap,values ='speedup_gpu_total_execution_time', index=['ds_dataset'], columns='ds_parameter_attribute')
        
        plt.figure(5)
        fig, ax = plt.subplots(figsize=(16,8))
        sns.set()
        sns.heatmap(heatmap_pt, cmap='YlGnBu')
        plt.xticks(rotation=15)
        plt.xlabel('Block Dimension')
        plt.ylabel('Data Set Type')
        plt.title('Speedup GPU over CPU',fontstyle='italic',fontweight="bold")
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_heatmap_speedup_gpu_per_ds_dataset_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

        # # Speedup CPU Per ds_parameter_attribute
        # df_filtered_mean = df_filtered_mean[["vl_dataset_memory_size","ds_dataset","ds_parameter_attribute","speedup_gpu_total_execution_time","speedup_gpu_inter_task_execution_time","speedup_gpu_intra_task_execution_time_full_func","speedup_gpu_intra_task_execution_time_device_func"]].sort_values(by=["speedup_gpu_total_execution_time"], ascending=False)

        # df_filtered_mean['ds_parameter_attribute'] = np.where(df_filtered_mean['ds_parameter_attribute'] == 'MIN_INTER_MAX_INTRA', 'MIN_I',
        #                   np.where(df_filtered_mean['ds_parameter_attribute'] == 'MAX_INTER_MIN_INTRA', 'MAX_I', df_filtered_mean['ds_parameter_attribute']))

        # plt.figure(3)
        # ax = plt.gca()
        # df_filtered_mean.set_index('ds_parameter_attribute').plot(kind = 'bar', hatch='x', zorder=3)
        # plt.yticks(np.arange(0, 31, 5))
        # plt.xticks(rotation=0)
        # plt.legend(['Total', 'Inter', 'Intra (Full Function)', 'Intra (Device Function)'])
        # plt.xlabel('Block Dimension')
        # plt.ylabel('Speedup')
        # plt.title('Speedup GPU over CPU x Block Dimension',fontstyle='italic',fontweight="bold")
        # plt.grid(zorder=0)
        # plt.savefig(dst_path_figs+'mode_'+str(mode)+'_speedup_gpu_per_ds_parameter_attribute_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)



        # df_filtered = df_filtered[["vl_dataset_memory_size","ds_dataset","ds_parameter_attribute","speedup_gpu_intra_task_execution_time_full_func","speedup_gpu_intra_task_execution_time_device_func"]]

        # df_filtered['ds_parameter_attribute'] = np.where(df_filtered['ds_parameter_attribute'] == 'MIN_INTER_MAX_INTRA', 'MIN_I',
        #                   np.where(df_filtered['ds_parameter_attribute'] == 'MAX_INTER_MIN_INTRA', 'MAX_I', df_filtered['ds_parameter_attribute']))

        # vl_dataset_memory_size_list = [400,400000,400000000]

        
        # for vl_dataset_memory_size in vl_dataset_memory_size_list:

        #     if vl_dataset_memory_size == 400:
        #         vl_dataset_memory_size_title = str(int(vl_dataset_memory_size)) + " B"
        #         ds_dataset_list = ['S_A_1','S_A_2','S_A_3','S_A_4']
        #     elif vl_dataset_memory_size == 400000:
        #         vl_dataset_memory_size_title = str(int(vl_dataset_memory_size*1e-3)) + " KB"
        #         ds_dataset_list = ['S_B_1','S_B_2','S_B_3','S_B_4']
        #     elif vl_dataset_memory_size == 400000000:
        #         vl_dataset_memory_size_title = str(int(vl_dataset_memory_size*1e-6)) + " MB"
        #         ds_dataset_list = ['S_C_1','S_C_2','S_C_3','S_C_4']

        #     for ds_dataset in ds_dataset_list:

                
        #         df_filtered_2 = df_filtered[(df_filtered.vl_dataset_memory_size==vl_dataset_memory_size) & (df_filtered.ds_dataset==ds_dataset)]
                

        #         plt.figure()
        #         ax = plt.gca()
        #         df_filtered_2.set_index('ds_parameter_attribute').plot(kind = 'bar', hatch='x', zorder=3)
        #         plt.legend(['Total', 'Inter', 'Intra (Full Function)', 'Intra (Device Function)'])
        #         plt.xlabel('Block Dimension')
        #         plt.ylabel('Speedup')
        #         plt.title('Speedup GPU over CPU x Block Dimension - '+vl_dataset_memory_size_title+' - '+ds_dataset,fontstyle='italic',fontweight="bold")
        #         plt.grid(zorder=0)
        #         plt.savefig(dst_path_figs+'mode_'+str(mode)+'_speedup_gpu_per_ds_parameter_attribute_'+vl_dataset_memory_size_title+'_'+ds_dataset+'_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)


    elif mode == 10:

        plt.figure()
        plt.title('Experiments Overview',fontstyle='italic',fontweight="bold")
        labels = ['Done', 'Not Done']
        values = [90.28, 9.72]
        colors = ["green","red"]
        plt.pie(values, labels = labels, autopct='%1.2f%%', colors = colors, pctdistance=1.35)
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_experiments_overview_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)


        plt.figure()
        plt.title('Experiments With Lowest Total Execution Time per Device',fontstyle='italic',fontweight="bold")
        labels = ['GPU', 'CPU']
        values = [61.54, 38.46]
        colors = ["#1B4F72","#21618C"]
        plt.pie(values, labels = labels, autopct='%1.2f%%', colors = colors, pctdistance=1.2)
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_experiments_total_exec_time_device_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

        plt.figure()
        plt.title('Experiments With Lowest Total Execution Time in CPU per Data Set Size',fontstyle='italic',fontweight="bold")
        labels = ['400B', '400KB', '400MB']
        values = [52, 36, 12]
        colors = ["#1B4F72","#21618C","#2874A6"]
        plt.pie(values, labels = labels, autopct='%1.2f%%', colors = colors, pctdistance=1.25, labeldistance=1.05)
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_experiments_total_exec_time_dataset_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

        
        dataset_list = ['400B', '400KB', '400MB']
        for dataset in dataset_list:
            if dataset == '400B':
                labels = ['0.75', '1.00', 'MIN_I', '0.50', 'MAX_I']
                values = [23.08, 23.08, 23.08, 15.38, 15.38]
                colors = ["#1B4F72","#21618C","#2874A6","#2E86C1","#3498DB"]
            
            if dataset == '400KB':

                labels = ['0.25', '0.50', 'MIN_I', '1.00', 'MAX_I']
                values = [33.33, 22.22, 22.22, 11.11, 11.11]
                colors = ["#1B4F72","#21618C","#2874A6","#2E86C1","#3498DB"]
                
            if dataset == '400MB':
                
                labels = ['0.50', '1.00', 'MIN_I']
                values = [33.33, 33.33, 33.33]
                colors = ["#1B4F72","#21618C","#2874A6"]


            # plt.figure()
            # plt.title('Experiments With Lowest Total Execution Time in CPU per Block Dimension - ' + dataset)
            # plt.pie(values, labels = labels, autopct='%1.2f%%', colors = colors, pctdistance=1.2, labeldistance=1.4)
            # plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+dataset+'_experiments_total_exec_time_parameter_type_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)
            
            plt.figure()
            fig, ax = plt.subplots()
            ax.bar(labels, values, color=colors, zorder=3)
            plt.xlabel('Block Dimension')
            plt.ylabel('%')
            plt.title('% Experiments With Lowest Total Execution Time in CPU per Block Dimension - ' + dataset, fontstyle='italic', fontweight="bold")
            plt.yticks(np.arange(0, 101, 50))
            plt.grid(zorder=0)
            for bars in ax.containers:
                ax.bar_label(bars)
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+dataset+'_experiments_total_exec_time_parameter_type_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)


        dataset_list = ['400B', '400KB', '400MB']
        for dataset in dataset_list:
            if dataset == '400B':
                labels = ['S_A_4', 'S_A_3', 'S_A_1', 'S_A_2']
                values = [38.46, 30.77, 15.38, 15.38]
                colors = ["#1B4F72","#21618C","#2874A6","#2E86C1"]
            
            if dataset == '400KB':

                labels = ['S_B_4','S_B_2','S_B_1']
                values = [44.44, 33.33, 22.22]
                colors = ["#1B4F72","#21618C","#2874A6"]
                
            if dataset == '400MB':
                
                labels = ['S_C_4']
                values = [100.00]
                colors = ["#1B4F72","#21618C","#2874A6"]


            # plt.figure()
            # plt.title('Experiments With Lowest Total Execution Time in CPU per Data Set Type - ' + dataset)
            # plt.pie(values, labels = labels, autopct='%1.2f%%', colors = colors, pctdistance=1.2, labeldistance=1.4)
            # plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+dataset+'_experiments_total_exec_time_dataset_type_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)
            
            plt.figure()
            fig, ax = plt.subplots()
            ax.bar(labels, values, color=colors, zorder=3)
            plt.xlabel('Data Set Type')
            plt.ylabel('%')
            plt.title('% Experiments With Lowest Total Execution Time in CPU per Data Set Type - ' + dataset, fontstyle='italic', fontweight="bold")
            plt.yticks(np.arange(0, 101, 50))
            plt.grid(zorder=0)
            for bars in ax.containers:
                ax.bar_label(bars)
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+dataset+'_experiments_total_exec_time_dataset_type_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)



    elif mode == 11:

        print("\nMode ",mode,": Ploting all execution times x block row and block column dimension, without parameter filters")

        x_value_list = ['vl_block_row_dimension','vl_block_column_dimension']

        for x_value in x_value_list:

            if x_value == 'vl_block_row_dimension':
                x_value_title = 'Block Rows'
            if x_value == 'vl_block_column_dimension':
                x_value_title = 'Block Columns'

            df_filtered_mean = df_filtered.groupby(['ds_device', x_value], as_index=False).mean()

            df_filtered_mean_cpu = df_filtered_mean[(df_filtered_mean.ds_device=="CPU")]
            df_filtered_mean_gpu = df_filtered_mean[(df_filtered_mean.ds_device=="GPU")]

            # VL_TOTAL_EXECUTION_TIME
            plt.figure()
            ax = plt.gca()
            df_filtered_mean_cpu.plot(x = x_value, y = 'vl_total_execution_time', kind = 'line', color='C0', linestyle = 'dotted', ax=ax, label='CPU', zorder=3)
            df_filtered_mean_gpu.plot(x = x_value, y = 'vl_total_execution_time', kind = 'line', color='C0', linestyle = 'solid', ax=ax, label='GPU', zorder=3)
            plt.xlabel('# Block Rows')
            plt.ylabel('Average Total Execution Time (s)')
            plt.title('Average Total Execution Time x Number of '+ x_value_title,fontstyle='italic',fontweight="bold")
            plt.grid(zorder=0)
            plt.yscale("log")
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_avg_total_execution_time_per_'+x_value+'_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)
            
            # VL_INTER_TASK_EXECUTION_TIME
            plt.figure()
            ax = plt.gca()
            df_filtered_mean_cpu.plot(x = x_value, y = 'vl_inter_task_execution_time', kind = 'line', color='C1', linestyle = 'dotted', ax=ax, label='CPU', zorder=3)
            df_filtered_mean_gpu.plot(x = x_value, y = 'vl_inter_task_execution_time', kind = 'line', color='C1', linestyle = 'solid', ax=ax, label='GPU', zorder=3)
            plt.xlabel('# ' + x_value_title)
            plt.ylabel('Average Inter-Task Time (s)')
            plt.title('Average Inter-Task Time x Number of '+ x_value_title,fontstyle='italic',fontweight="bold")
            plt.grid(zorder=0)
            plt.yscale("log")
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_avg_inter_task_execution_time_per_'+x_value+'_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

            # VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC
            plt.figure()
            ax = plt.gca()
            df_filtered_mean_cpu.plot(x = x_value, y = 'vl_intra_task_execution_time_full_func', kind = 'line', color='C2', linestyle = 'dotted', ax=ax, label='CPU', zorder=3)
            df_filtered_mean_gpu.plot(x = x_value, y = 'vl_intra_task_execution_time_full_func', kind = 'line', color='C2', linestyle = 'solid', ax=ax, label='GPU', zorder=3)
            plt.xlabel('# ' + x_value_title)
            plt.ylabel('Average Intra-Task (full func) Time (s)')
            plt.title('Average Intra-Task (full func) Time x Number of ' + x_value_title,fontstyle='italic',fontweight="bold")
            plt.grid(zorder=0)
            plt.yscale("log")
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_avg_intra_task_execution_time_full_func_per_'+x_value+'_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

            # VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC
            plt.figure()
            ax = plt.gca()
            df_filtered_mean_cpu.plot(x = x_value, y = 'vl_intra_task_execution_time_device_func', kind = 'line', color='C3', linestyle = 'dotted', ax=ax, label='CPU', zorder=3)
            df_filtered_mean_gpu.plot(x = x_value, y = 'vl_intra_task_execution_time_device_func', kind = 'line', color='C3', linestyle = 'solid', ax=ax, label='GPU', zorder=3)
            plt.xlabel('# ' + x_value_title)
            plt.ylabel('Average Intra-Task (device func) Time (s)')
            plt.title('Average Intra-Task (device func) Time x Number of ' + x_value_title,fontstyle='italic',fontweight="bold")
            plt.grid(zorder=0)
            plt.yscale("log")
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_avg_intra_task_execution_time_device_func_per_'+x_value+'_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

            # VL_COMMUNICATION_TIME
            plt.figure()
            ax = plt.gca()
            df_filtered_mean_cpu.plot(x = x_value, y = 'vl_communication_time', kind = 'line', color='C4', linestyle = 'dotted', ax=ax, label='CPU', zorder=3)
            df_filtered_mean_gpu.plot(x = x_value, y = 'vl_communication_time', kind = 'line', color='C4', linestyle = 'solid', ax=ax, label='GPU', zorder=3)
            plt.xlabel('# ' + x_value_title)
            plt.ylabel('Average Communication Time (s)')
            plt.title('Average Communication Time x Number of ' + x_value_title,fontstyle='italic',fontweight="bold")
            plt.grid(zorder=0)
            plt.yscale("log")
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_avg_communication_time_per_'+x_value+'_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)
 

    elif mode == 12:

        print("\nMode ",mode,": Ploting all execution times x grid row and column dimension, without parameter filters")

        x_value_list = ['vl_grid_row_dimension','vl_grid_column_dimension']

        for x_value in x_value_list:

            if x_value == 'vl_grid_row_dimension':
                x_value_title = 'Grid Rows'
            if x_value == 'vl_grid_column_dimension':
                x_value_title = 'Grid Columns'
        
            df_filtered_mean = df_filtered.groupby(['ds_device', x_value], as_index=False).mean()

            df_filtered_mean_cpu = df_filtered_mean[(df_filtered_mean.ds_device=="CPU")]
            df_filtered_mean_gpu = df_filtered_mean[(df_filtered_mean.ds_device=="GPU")]

            # VL_TOTAL_EXECUTION_TIME
            plt.figure()
            ax = plt.gca()
            df_filtered_mean_cpu.plot(x = x_value, y = 'vl_total_execution_time', kind = 'line', color='C0', linestyle = 'dotted', ax=ax, label='CPU', zorder=3)
            df_filtered_mean_gpu.plot(x = x_value, y = 'vl_total_execution_time', kind = 'line', color='C0', linestyle = 'solid', ax=ax, label='GPU', zorder=3)
            plt.xlabel(x_value_title)
            plt.ylabel('Average Total Execution Time (s)')
            plt.title('Average Total Execution Time x '+x_value_title,fontstyle='italic',fontweight="bold")
            plt.grid(zorder=0)
            # plt.yscale("log")
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_avg_total_execution_time_per_'+x_value+'_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)
            
            # VL_INTER_TASK_EXECUTION_TIME
            plt.figure()
            ax = plt.gca()
            df_filtered_mean_cpu.plot(x = x_value, y = 'vl_inter_task_execution_time', kind = 'line', color='C1', linestyle = 'dotted', ax=ax, label='CPU', zorder=3)
            df_filtered_mean_gpu.plot(x = x_value, y = 'vl_inter_task_execution_time', kind = 'line', color='C1', linestyle = 'solid', ax=ax, label='GPU', zorder=3)
            plt.xlabel(x_value_title)
            plt.ylabel('Average Inter-Task Time (s)')
            plt.title('Average Inter-Task Time x '+x_value_title,fontstyle='italic',fontweight="bold")
            plt.grid(zorder=0)
            # plt.yscale("log")
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_avg_inter_task_execution_time_per_'+x_value+'_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

            # VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC
            plt.figure()
            ax = plt.gca()
            df_filtered_mean_cpu.plot(x = x_value, y = 'vl_intra_task_execution_time_full_func', kind = 'line', color='C2', linestyle = 'dotted', ax=ax, label='CPU', zorder=3)
            df_filtered_mean_gpu.plot(x = x_value, y = 'vl_intra_task_execution_time_full_func', kind = 'line', color='C2', linestyle = 'solid', ax=ax, label='GPU', zorder=3)
            plt.xlabel(x_value_title)
            plt.ylabel('Average Intra-Task (full func) Time (s)')
            plt.title('Average Intra-Task (full func) Time x '+x_value_title,fontstyle='italic',fontweight="bold")
            plt.grid(zorder=0)
            # plt.yscale("log")
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_avg_intra_task_execution_time_full_func_per_'+x_value+'_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

            # VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC
            plt.figure()
            ax = plt.gca()
            df_filtered_mean_cpu.plot(x = x_value, y = 'vl_intra_task_execution_time_device_func', kind = 'line', color='C3', linestyle = 'dotted', ax=ax, label='CPU', zorder=3)
            df_filtered_mean_gpu.plot(x = x_value, y = 'vl_intra_task_execution_time_device_func', kind = 'line', color='C3', linestyle = 'solid', ax=ax, label='GPU', zorder=3)
            plt.xlabel(x_value_title)
            plt.ylabel('Average Intra-Task (device func) Time (s)')
            plt.title('Average Intra-Task (device func) Time x '+x_value_title,fontstyle='italic',fontweight="bold")
            plt.grid(zorder=0)
            # plt.yscale("log")
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_avg_intra_task_execution_time_device_func_per_'+x_value+'_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

            # VL_COMMUNICATION_TIME
            plt.figure()
            ax = plt.gca()
            df_filtered_mean_cpu.plot(x = x_value, y = 'vl_communication_time', kind = 'line', color='C4', linestyle = 'dotted', ax=ax, label='CPU', zorder=3)
            df_filtered_mean_gpu.plot(x = x_value, y = 'vl_communication_time', kind = 'line', color='C4', linestyle = 'solid', ax=ax, label='GPU', zorder=3)
            plt.xlabel(x_value_title)
            plt.ylabel('Average Communication Time (s)')
            plt.title('Average Communication Time x '+x_value_title,fontstyle='italic',fontweight="bold")
            plt.grid(zorder=0)
            # plt.yscale("log")
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_avg_communication_time_per_'+x_value+'_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

    else:

        print("\nInvalid mode.")


def parse_args():
    import argparse
    description = 'Generating graphs for the experiments'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-a', '--ds_algorithm', type=str, default="KMEANS",
                        help='Algorithm description'
                        )
    parser.add_argument('-r', '--ds_resource', type=str, default="MINOTAURO_1",
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
