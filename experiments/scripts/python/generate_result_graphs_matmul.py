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

    sql_query = """SELECT
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
                        Y.VL_CONCAT_NR_TASK_BLOCK_SIZE_MB,
                        Y.VL_CONCAT_GRID_ROW_X_COLUMN_DIMENSION_BLOCK_SIZE_MB,
                        Y.VL_CONCAT_BLOCK_SIZE_MB_GRID_ROW_X_COLUMN_DIMENSION,
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
                        Y.NR_RANDOM_STATE,
                        Y.VL_DATA_SPARSITY,
                        CASE
                            WHEN Y.DS_DEVICE = 'CPU' AND Y.VL_DATA_SPARSITY = 0 THEN 'CPU dense'
                            WHEN Y.DS_DEVICE = 'CPU' AND Y.VL_DATA_SPARSITY = 1 THEN 'CPU sparse'
                            WHEN Y.DS_DEVICE = 'GPU' AND Y.VL_DATA_SPARSITY = 0 THEN 'GPU dense'
                            WHEN Y.DS_DEVICE = 'GPU' AND Y.VL_DATA_SPARSITY = 1 THEN 'GPU sparse'
                            ELSE ''
                        END AS DEVICE_SPARSITY
                        FROM
                        (
                            SELECT
                                AVG(W.VL_TOTAL_EXECUTION_TIME) AS VL_TOTAL_EXECUTION_TIME,
                                AVG(W.VL_INTER_TASK_EXECUTION_TIME) AS VL_INTER_TASK_EXECUTION_TIME,
                                AVG(W.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC) AS VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                                AVG(W.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC) AS VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                                AVG(W.VL_COMMUNICATION_TIME_1) AS VL_COMMUNICATION_TIME_1,
                                AVG(W.VL_COMMUNICATION_TIME_2) AS VL_COMMUNICATION_TIME_2,
                                AVG(W.VL_COMMUNICATION_TIME) AS VL_COMMUNICATION_TIME,
                                AVG(W.VL_ADDITIONAL_TIME_1) AS VL_ADDITIONAL_TIME_1,
                                AVG(W.VL_ADDITIONAL_TIME_2) AS VL_ADDITIONAL_TIME_2,
                                AVG(W.VL_ADDITIONAL_TIME) AS VL_ADDITIONAL_TIME,
                                STDDEV(W.VL_TOTAL_EXECUTION_TIME) AS VL_STD_TOTAL_EXECUTION_TIME,
                                STDDEV(W.VL_INTER_TASK_EXECUTION_TIME) AS VL_STD_INTER_TASK_EXECUTION_TIME,
                                STDDEV(W.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC) AS VL_STD_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                                STDDEV(W.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC) AS VL_STD_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                                STDDEV(W.VL_COMMUNICATION_TIME) AS VL_STD_COMMUNICATION_TIME,
                                W.ID_PARAMETER,
                                W.CD_PARAMETER,
                                W.CD_CONFIGURATION,
                                W.ID_ALGORITHM,
                                W.DS_ALGORITHM,
                                W.ID_FUNCTION,
                                W.DS_FUNCTION,
                                W.ID_DEVICE,
                                W.DS_DEVICE,
                                W.ID_DATASET,
                                W.ID_RESOURCE,
                                W.ID_PARAMETER_TYPE,
                                W.DS_PARAMETER_TYPE,
                                W.DS_PARAMETER_ATTRIBUTE,
                                W.NR_ITERATIONS,
                                W.VL_GRID_ROW_DIMENSION,
                                W.VL_GRID_COLUMN_DIMENSION,
                                W.VL_GRID_ROW_X_COLUMN_DIMENSION,
                                W.VL_CONCAT_NR_TASK_BLOCK_SIZE_MB,
                                W.VL_CONCAT_GRID_ROW_X_COLUMN_DIMENSION_BLOCK_SIZE_MB,
                                W.VL_CONCAT_BLOCK_SIZE_MB_GRID_ROW_X_COLUMN_DIMENSION,
                                W.VL_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                W.VL_CONCAT_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                W.VL_BLOCK_ROW_DIMENSION,
                                W.VL_BLOCK_COLUMN_DIMENSION,
                                W.VL_BLOCK_ROW_X_COLUMN_DIMENSION,
                                W.VL_BLOCK_MEMORY_SIZE,
                                W.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                                W.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                                W.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                W.VL_CONCAT_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                W.DS_RESOURCE,
                                W.NR_NODES,
                                W.NR_COMPUTING_UNITS_CPU,
                                W.NR_COMPUTING_UNITS_GPU,
                                W.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                                W.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
                                W.DS_DATASET,
                                W.VL_DATASET_MEMORY_SIZE,
                                W.DS_DATA_TYPE,
                                W.VL_DATA_TYPE_MEMORY_SIZE,
                                W.VL_DATASET_DIMENSION,
                                W.VL_DATASET_ROW_DIMENSION,
                                W.VL_DATASET_COLUMN_DIMENSION,
                                W.VL_DATASET_ROW_X_COLUMN_DIMENSION,
                                W.NR_RANDOM_STATE,
                                W.VL_DATA_SPARSITY
                                FROM
                                (
                                    SELECT
                                    AVG(X.VL_TOTAL_EXECUTION_TIME) AS VL_TOTAL_EXECUTION_TIME,
                                    MAX(X.VL_INTER_TASK_EXECUTION_TIME) AS VL_INTER_TASK_EXECUTION_TIME,
                                    AVG(X.VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC) AS VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC,
                                    AVG(X.VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC) AS VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC,
                                    AVG(X.VL_COMMUNICATION_TIME_1) AS VL_COMMUNICATION_TIME_1,
                                    AVG(X.VL_COMMUNICATION_TIME_2) AS VL_COMMUNICATION_TIME_2,
                                    AVG(X.VL_COMMUNICATION_TIME) AS VL_COMMUNICATION_TIME,
                                    AVG(X.VL_ADDITIONAL_TIME_1) AS VL_ADDITIONAL_TIME_1,
                                    AVG(X.VL_ADDITIONAL_TIME_2) AS VL_ADDITIONAL_TIME_2,
                                    AVG(X.VL_ADDITIONAL_TIME) AS VL_ADDITIONAL_TIME,
                                    X.NR_ALGORITHM_ITERATION,
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
                                    X.VL_CONCAT_NR_TASK_BLOCK_SIZE_MB,
                                    X.VL_CONCAT_GRID_ROW_X_COLUMN_DIMENSION_BLOCK_SIZE_MB,
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
                                    X.VL_DATA_SPARSITY
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
                                            A.NR_ALGORITHM_ITERATION,
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
                                            CASE
                                                WHEN (SELECT DISTINCT X.DS_FUNCTION FROM FUNCTION X WHERE X.ID_FUNCTION = B.ID_FUNCTION) = 'MATMUL_FUNC' THEN B.VL_GRID_ROW_DIMENSION*B.VL_GRID_ROW_DIMENSION*B.VL_GRID_COLUMN_DIMENSION || ' (' || ROUND(B.VL_BLOCK_MEMORY_SIZE*1e-6,2) || ')'
                                                WHEN (SELECT DISTINCT X.DS_FUNCTION FROM FUNCTION X WHERE X.ID_FUNCTION = B.ID_FUNCTION) = 'ADD_FUNC' THEN B.VL_GRID_ROW_DIMENSION*B.VL_GRID_ROW_DIMENSION*(B.VL_GRID_COLUMN_DIMENSION-1) || ' (' || ROUND(B.VL_BLOCK_MEMORY_SIZE*1e-6,2) || ')'
                                                ELSE NULL
                                            END AS VL_CONCAT_NR_TASK_BLOCK_SIZE_MB,
                                            B.VL_GRID_ROW_DIMENSION || ' x ' || B.VL_GRID_COLUMN_DIMENSION || ' (' || ROUND(B.VL_BLOCK_MEMORY_SIZE*1e-6,2) || ')' AS VL_CONCAT_GRID_ROW_X_COLUMN_DIMENSION_BLOCK_SIZE_MB,
                                            ROUND(B.VL_BLOCK_MEMORY_SIZE*1e-6,2) || ' (' || B.VL_GRID_ROW_DIMENSION || ' x ' || B.VL_GRID_COLUMN_DIMENSION  || ')' AS VL_CONCAT_BLOCK_SIZE_MB_GRID_ROW_X_COLUMN_DIMENSION,
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
                                            D.NR_RANDOM_STATE,
                                            D.VL_DATA_SPARSITY
                                        FROM EXPERIMENT_RAW A
                                        INNER JOIN PARAMETER B ON (A.ID_PARAMETER = B.ID_PARAMETER)
                                        INNER JOIN RESOURCE C ON (B.ID_RESOURCE = C.ID_RESOURCE)
                                        INNER JOIN DATASET D ON (B.ID_DATASET = D.ID_DATASET)
                                        WHERE
                                        A.NR_ALGORITHM_ITERATION <> 0
                                    ) X
                                    GROUP BY
                                    X.NR_ALGORITHM_ITERATION,
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
                                    X.VL_CONCAT_NR_TASK_BLOCK_SIZE_MB,
                                    X.VL_CONCAT_GRID_ROW_X_COLUMN_DIMENSION_BLOCK_SIZE_MB,
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
                                    X.VL_DATA_SPARSITY
                                ) W
                                GROUP BY
                                W.ID_PARAMETER,
                                W.CD_PARAMETER,
                                W.CD_CONFIGURATION,
                                W.ID_ALGORITHM,
                                W.DS_ALGORITHM,
                                W.ID_FUNCTION,
                                W.DS_FUNCTION,
                                W.ID_DEVICE,
                                W.DS_DEVICE,
                                W.ID_DATASET,
                                W.ID_RESOURCE,
                                W.ID_PARAMETER_TYPE,
                                W.DS_PARAMETER_TYPE,
                                W.DS_PARAMETER_ATTRIBUTE,
                                W.NR_ITERATIONS,
                                W.VL_GRID_ROW_DIMENSION,
                                W.VL_GRID_COLUMN_DIMENSION,
                                W.VL_GRID_ROW_X_COLUMN_DIMENSION,
                                W.VL_CONCAT_NR_TASK_BLOCK_SIZE_MB,
                                W.VL_CONCAT_GRID_ROW_X_COLUMN_DIMENSION_BLOCK_SIZE_MB,
                                W.VL_CONCAT_BLOCK_SIZE_MB_GRID_ROW_X_COLUMN_DIMENSION,
                                W.VL_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                W.VL_CONCAT_GRID_COLUMN_DIMENSION_PERCENT_DATASET,
                                W.VL_BLOCK_ROW_DIMENSION,
                                W.VL_BLOCK_COLUMN_DIMENSION,
                                W.VL_BLOCK_ROW_X_COLUMN_DIMENSION,
                                W.VL_BLOCK_MEMORY_SIZE,
                                W.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                                W.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                                W.VL_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                W.VL_CONCAT_BLOCK_MEMORY_SIZE_PERCENT_DATASET,
                                W.DS_RESOURCE,
                                W.NR_NODES,
                                W.NR_COMPUTING_UNITS_CPU,
                                W.NR_COMPUTING_UNITS_GPU,
                                W.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                                W.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
                                W.DS_DATASET,
                                W.VL_DATASET_MEMORY_SIZE,
                                W.DS_DATA_TYPE,
                                W.VL_DATA_TYPE_MEMORY_SIZE,
                                W.VL_DATASET_DIMENSION,
                                W.VL_DATASET_ROW_DIMENSION,
                                W.VL_DATASET_COLUMN_DIMENSION,
                                W.VL_DATASET_ROW_X_COLUMN_DIMENSION,
                                W.NR_RANDOM_STATE,
                                W.VL_DATA_SPARSITY
                        ) Y
                        ORDER BY ID_PARAMETER;"""
    
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

    # General filtering and sorting parameters - V2 (VAR_GRID_ROW)
    df_filtered = df[
                    (df["ds_algorithm"] == ds_algorithm.upper()) # FIXED VALUE
                    & (df["nr_iterations"] == int(nr_iterations)) # FIXED VALUE
                    & (df["ds_resource"] == ds_resource.upper()) # FIXED VALUE
                    # & (df["ds_dataset"].isin(["S_128MB_1","S_512MB_1","S_2GB_1","S_8GB_1","S_32GB_1"])) # FIXED VALUE
                    & (df["ds_dataset"].isin(["S_2GB_1","S_2GB_2"])) #mode 155 and 1555 only
                    # & (df["ds_dataset"] == "S_128MB_1")
                    # VAR_GRID_SHAPE_MATMUL_1, VAR_GRID_SHAPE_MATMUL_2
                    & (df["ds_parameter_type"] == "VAR_GRID_SHAPE_MATMUL_2")
                    # MATMUL_FUNC, ADD_FUNC
                    & (df["ds_function"] == "MATMUL_FUNC")
                    # & (df["vl_concat_grid_row_x_column_dimension_block_size_mb"] != "16 x 16 (8.00)")
                    ]


    if mode == 15:
        
        print("\nMode ",mode,": Ploting all execution times x grid and block shapes, without parameter filters")
        
        ds_dataset = df_filtered["ds_dataset"].unique()

        ds_dataset = '(' + ', '.join(ds_dataset) + ')'

        x_value_list = ['vl_concat_block_size_mb_grid_row_x_column_dimension']

        for x_value in x_value_list:

            if x_value == 'vl_concat_grid_row_x_column_dimension_block_size_mb':
                x_value_title = 'Grid Shape (Block Size MB)'
            elif x_value == 'vl_concat_block_size_mb_grid_row_x_column_dimension':
                x_value_title = 'Block Size MB (Grid Shape)'
        
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

            if (x_value == 'vl_block_row_x_column_dimension') | (x_value == 'vl_concat_block_size_mb_grid_row_x_column_dimension'):
                df_filtered_mean_cpu.sort_values('vl_block_row_dimension', inplace=True)
                df_filtered_mean_gpu.sort_values('vl_block_row_dimension', inplace=True)
                # df_filtered_mean_cpu.sort_values(by=['vl_block_row_dimension'])
                # df_filtered_mean_gpu.sort_values(by=['vl_block_row_dimension'])

            # if x_value == 'vl_concat_block_size_mb_grid_row_x_column_dimension':
            #     df_filtered_mean_cpu.sort_values('vl_block_memory_size', inplace=True)
            #     df_filtered_mean_gpu.sort_values('vl_block_memory_size', inplace=True)

            # VL_TOTAL_EXECUTION_TIME
            fig = plt.figure()
            ax = plt.gca()
            for frame in [df_filtered_mean_cpu, df_filtered_mean_gpu]:
                if frame.name == 'df_filtered_mean_cpu':
                    # plt.xticks(frame[x_value], frame['vl_grid_row_x_column_dimension'])
                    plt.plot(frame[x_value], frame['vl_total_execution_time'], color='C0', linestyle = 'dotted', label='$T_{w\_inter}$ CPU', zorder=3)
                    # plt.plot(frame[x_value], frame['vl_inter_task_overhead_time'], color='C9', linestyle = 'dotted', label='$T_{o\_inter}$ CPU', zorder=3)
                    # plt.plot(frame[x_value], frame['vl_intra_task_execution_time_full_func'], color='C2', linestyle = 'dotted', label='$T_{w\_intra}$  CPU', zorder=3)
                if frame.name == 'df_filtered_mean_gpu':
                    # plt.xticks(frame[x_value], frame['vl_grid_row_x_column_dimension'])
                    plt.plot(frame[x_value], frame['vl_total_execution_time'], color='C0', linestyle = 'solid', label='$T_{w\_inter}$ GPU', zorder=3)
                    # plt.plot(frame[x_value], frame['vl_inter_task_overhead_time'], color='C9', linestyle = 'solid', label='$T_{o\_inter}$  GPU', zorder=3)
                    # plt.plot(frame[x_value], frame['vl_intra_task_execution_time_full_func'], color='C2', linestyle = 'solid', label='$T_{w\_intra}$ GPU', zorder=3)
            plt.legend(loc='best')
            plt.xlabel(x_value_title)
            plt.ylabel('Time (s)')
            plt.title('$T_{w\_inter}$ Time x '+x_value_title+' ' + ds_dataset,fontstyle='italic',fontweight="bold")
            plt.grid(zorder=0)
            ax.tick_params(axis='x', labelrotation = 90)
            # # # NORMAL SCALE
            # # plt.ylim([0.0000, 265.0000])
            # if x_value == 'vl_grid_row_dimension' or x_value == 'vl_block_row_dimension':
            #     ax.ticklabel_format(scilimits=(-5, 1))
            # # LOG SCALE
            plt.ylim([1e1, 1e3])
            plt.yscale("log")
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_avg_total_execution_time_per_'+x_value+'_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

            
        #     # plt.legend(loc='best')
        #     # df_filtered_mean_cpu.plot(x = x_value, y = 'vl_total_execution_time', kind = 'line', color='C0', linestyle = 'dotted', ax=ax, label='CPU', zorder=3)
        #     # df_filtered_mean_gpu.plot(x = x_value, y = 'vl_total_execution_time', kind = 'line', color='C0', linestyle = 'solid', ax=ax, label='GPU', zorder=3)
        #     # plt.xlabel(x_value_title)
        #     # plt.ylabel('Average Total Execution Time (s)')
        #     # plt.title('Average Total Execution Time x '+x_value_title+' ' + ds_dataset,fontstyle='italic',fontweight="bold")
        #     # plt.grid(zorder=0)
        #     # ax.tick_params(axis='x', labelrotation = 90)
        #     # # # NORMAL SCALE
        #     # # plt.ylim([0, 1000])
        #     # # LOG SCALE
        #     # plt.ylim([1e0, 1e4])
        #     # plt.yscale("log")
        #     # plt.savefig(dst_path_figs+'mode_'+str(mode)+'_avg_total_execution_time_per_'+x_value+'_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)
            

            # BREAKING VL_INTER_TASK_EXECUTION_TIME = VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC + VL_INTER_TASK_OVERHEAD_TIME
            fig = plt.figure()
            ax = plt.gca()
            for frame in [df_filtered_mean_cpu, df_filtered_mean_gpu]:
                if frame.name == 'df_filtered_mean_cpu':
                    # plt.xticks(frame[x_value], frame['vl_grid_row_x_column_dimension'])
                    plt.plot(frame[x_value], frame['vl_inter_task_execution_time'], color='C1', linestyle = 'dotted', label='$T_{w\_inter}$ CPU', zorder=3)
                    # plt.plot(frame[x_value], frame['vl_inter_task_overhead_time'], color='C9', linestyle = 'dotted', label='$T_{o\_inter}$ CPU', zorder=3)
                    # plt.plot(frame[x_value], frame['vl_intra_task_execution_time_full_func'], color='C2', linestyle = 'dotted', label='$T_{w\_intra}$ CPU', zorder=3)
                if frame.name == 'df_filtered_mean_gpu':
                    # plt.xticks(frame[x_value], frame['vl_grid_row_x_column_dimension'])
                    plt.plot(frame[x_value], frame['vl_inter_task_execution_time'], color='C1', linestyle = 'solid', label='$T_{w\_inter}$ GPU', zorder=3)
                    # plt.plot(frame[x_value], frame['vl_inter_task_overhead_time'], color='C9', linestyle = 'solid', label='$T_{o\_inter}$ GPU', zorder=3)
                    # plt.plot(frame[x_value], frame['vl_intra_task_execution_time_full_func'], color='C2', linestyle = 'solid', label='$T_{w\_intra}$ GPU', zorder=3)
            
            plt.legend(loc='best')
            plt.xlabel(x_value_title)
            plt.ylabel('Time (s)')
            plt.title('$T_{w\_inter}$ Time Composition x '+x_value_title+' ' + ds_dataset,fontstyle='italic',fontweight="bold")
            plt.grid(zorder=0)
            ax.tick_params(axis='x', labelrotation = 90)
            # # # NORMAL SCALE
            # # plt.ylim([0.0000, 265.0000])
            # if x_value == 'vl_grid_row_dimension' or x_value == 'vl_block_row_dimension':
            #     ax.ticklabel_format(scilimits=(-5, 1))
            # # LOG SCALE
            plt.ylim([1e-1, 1e4])
            plt.yscale("log")
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_avg_inter_task_composition_time_per_'+x_value+'_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

            # # BREAKING VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC = VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC + VL_COMMUNICATION_TIME + VL_ADDITIONAL_TIME
            fig = plt.figure()
            ax = plt.gca()
            for frame in [df_filtered_mean_cpu, df_filtered_mean_gpu]:
                if frame.name == 'df_filtered_mean_cpu':
                    # plt.xticks(frame[x_value], frame['vl_grid_row_x_column_dimension'])
                    plt.plot(frame[x_value], frame['vl_intra_task_execution_time_full_func'], color='C2', linestyle = 'dotted', label='$T_{w\_intra}$ CPU', zorder=3)
                    # plt.plot(frame[x_value], frame['vl_intra_task_execution_time_device_func'], color='C3', linestyle = 'dotted', label='$T_{p\_intra}$ CPU', zorder=3)
                    # plt.plot(frame[x_value], frame['vl_communication_time'], color='C4', linestyle = 'dotted', label='$T_{c\_intra}$ CPU', zorder=3)
                    # plt.plot(frame[x_value], frame['vl_additional_time'], color='C8', linestyle = 'dotted', label='$T_{s\_intra}$ CPU', zorder=3)
                if frame.name == 'df_filtered_mean_gpu':
                    # plt.xticks(frame[x_value], frame['vl_grid_row_x_column_dimension'])
                    plt.plot(frame[x_value], frame['vl_intra_task_execution_time_full_func'], color='C2', linestyle = 'solid', label='$T_{w\_intra}$ GPU', zorder=3)
                    plt.plot(frame[x_value], frame['vl_intra_task_execution_time_device_func'], color='C3', linestyle = 'solid', label='$T_{p\_intra}$ GPU', zorder=3)
                    plt.plot(frame[x_value], frame['vl_communication_time'], color='C4', linestyle = 'solid', label='$T_{c\_intra}$ GPU', zorder=3)
                    # plt.plot(frame[x_value], frame['vl_additional_time'], color='C8', linestyle = 'solid', label='$T_{s\_intra}$ GPU', zorder=3)

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


    elif mode == 155:
        
        print("\nMode ",mode,": Ploting intra-task execution times x grid and block shapes, without parameter filters")
        
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
                if frame.name == 'df_filtered_mean_cpu_dense':
                    plt.plot(frame[x_value], frame['vl_intra_task_execution_time_full_func'], color='C2', linestyle = 'dotted', label='$T_{w\_intra}$ CPU dense', zorder=3)
                if frame.name == 'df_filtered_mean_gpu_dense':
                    plt.plot(frame[x_value], frame['vl_intra_task_execution_time_full_func'], color='C2', linestyle = 'solid', label='$T_{w\_intra}$ GPU dense', zorder=3)
                    # plt.plot(frame[x_value], frame['vl_intra_task_execution_time_device_func'], color='C3', linestyle = 'solid', label='$T_{p\_intra}$ GPU dense', zorder=3)
                    # plt.plot(frame[x_value], frame['vl_communication_time'], color='C4', linestyle = 'solid', label='$T_{c\_intra}$ GPU dense', zorder=3)
                if frame.name == 'df_filtered_mean_cpu_sparse':
                    plt.plot(frame[x_value], frame['vl_intra_task_execution_time_full_func'], color='C2', linestyle = 'dashed', label='$T_{w\_intra}$ CPU sparse', zorder=3)
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


    elif mode == 1555:
        
        print("\nMode ",mode,": Ploting intra-task execution times x grid and block shapes, without parameter filters")
        
        ds_dataset = df_filtered["ds_dataset"].unique()
        ds_dataset = '(' + ', '.join(ds_dataset) + ')'

        x_value_list = ['vl_concat_block_size_mb_grid_row_x_column_dimension']

        for x_value in x_value_list:

            if x_value == 'vl_concat_grid_row_x_column_dimension_block_size_mb':
                x_value_title = 'Grid Shape (Block Size MB)'
            elif x_value == 'vl_concat_block_size_mb_grid_row_x_column_dimension':
                x_value_title = 'Block Size MB (Grid Shape)'
        
            df_filtered_mean = df_filtered.groupby([x_value,'device_sparsity'], as_index=False).mean()


            df_filtered_mean = df_filtered_mean[[x_value,'device_sparsity','vl_intra_task_execution_time_full_func']]
            
            plt.figure(1)
            X_axis = np.arange(len(df_filtered_mean[x_value].drop_duplicates()))
            plt.bar(X_axis - 0.2, df_filtered_mean[(df_filtered_mean.device_sparsity=="CPU dense")]["vl_intra_task_execution_time_full_func"], 0.3, label = "CPU dense", color='C2', zorder=3)
            plt.bar(X_axis + 0.2, df_filtered_mean[(df_filtered_mean.device_sparsity=="CPU sparse")]["vl_intra_task_execution_time_full_func"], 0.3, label = "CPU sparse", color='C2', hatch='oo', zorder=3)
            plt.xticks(X_axis, df_filtered_mean[x_value].drop_duplicates(), rotation=0)
            plt.xlabel(x_value_title)
            plt.ylabel('Time (s)')
            plt.title('$T_{w\_intra}$ Time x '+x_value_title+' ' + ds_dataset,fontstyle='italic',fontweight="bold")
            plt.grid(zorder=0)
            plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=len(df_filtered_mean[x_value].drop_duplicates()))
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_CPU_avg_intra_task_composition_time_per_'+x_value+'_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

            plt.figure(2)
            X_axis = np.arange(len(df_filtered_mean[x_value].drop_duplicates()))
            plt.bar(X_axis - 0.2, df_filtered_mean[(df_filtered_mean.device_sparsity=="GPU dense")]["vl_intra_task_execution_time_full_func"], 0.3, label = "GPU dense", color='C2', zorder=3)
            plt.bar(X_axis + 0.2, df_filtered_mean[(df_filtered_mean.device_sparsity=="GPU sparse")]["vl_intra_task_execution_time_full_func"], 0.3, label = "GPU sparse", color='C2', hatch='oo', zorder=3)
            plt.xticks(X_axis, df_filtered_mean[x_value].drop_duplicates(), rotation=0)
            plt.xlabel(x_value_title)
            plt.ylabel('Time (s)')
            plt.title('$T_{w\_intra}$ Time x '+x_value_title+' ' + ds_dataset,fontstyle='italic',fontweight="bold")
            plt.grid(zorder=0)
            plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=len(df_filtered_mean[x_value].drop_duplicates()))
            plt.savefig(dst_path_figs+'mode_'+str(mode)+'_GPU_avg_intra_task_composition_time_per_'+x_value+'_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

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
