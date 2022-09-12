import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from config import open_connection, close_connection

def main():

    dst_path_figs = '../../results/figures/'

    # Open connection to the database
    cur, conn = open_connection()

    # Set sql query
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
                    ORDER BY A.ID_PARAMETER;"""
    
    # Get dataframe from query
    df = get_df_from_query(sql_query,conn)

    # Close connection to the database
    close_connection(cur, conn)

    # Generate graph (mode 1)
    generate_graph(df, dst_path_figs, mode=1)

# Function that takes in a PostgreSQL query and outputs a pandas dataframe 
def get_df_from_query(sql_query, conn):
    df = pd.read_sql_query(sql_query, conn)
    return df

# Function that generates a graph according to the mode specified
def generate_graph(df, dst_path_figs, mode):
    
    # Varying dataset size 
    if mode == 1:
        # Filtering and sorting parameters
        df_filtered = df[
                        (df["ds_algorithm"] == "KMEANS") # FIXED VALUE
                        & (df["nr_iterations"] == 5) # FIXED VALUE
                        & (df["ds_resource"] == "MINOTAURO_1") # FIXED VALUE
                        & (df["ds_tp_parameter"] == "VAR_BLOCK_CAPACITY_SIZE") # 1.1, 1.2, 1.3, 1.4
                        # & (df_parameters["ds_tp_parameter"] == "VAR_PARALLELISM_LEVEL") # 2.1, 2.2
                        # & (df["vl_block_size_percent_dataset"] == 0.25) # 1.1
                        # & (df_parameters["vl_block_size_percent_dataset"] == 0.5) # 1.2
                        # & (df_parameters["vl_block_size_percent_dataset"] == 0.75) # 1.3
                        # & (df_parameters["vl_block_size_percent_dataset"] == 1) # 1.4
                        # & (df_parameters["ds_status_parallelism"] == "MIN_INTER_MAX_INTRA") # 2.1
                        # & (df_parameters["ds_status_parallelism"] == "MAX_INTER_MIN_INTRA") # 2.2
                        ].sort_values(by=["id_parameter"])
        
        df_filtered_mean = df_filtered.groupby(['ds_device', 'vl_dataset_memory_size'], as_index=False).mean()

        df_filtered_mean_cpu = df_filtered_mean[(df_filtered_mean.ds_device=="CPU")]
        df_filtered_mean_gpu = df_filtered_mean[(df_filtered_mean.ds_device=="GPU")]


        # VL_TOTAL_EXECUTION_TIME
        plt.figure(1)
        ax = plt.gca()
        df_filtered_mean_cpu.plot(x = 'vl_dataset_memory_size', y = 'vl_total_execution_time', kind = 'line', color='red', ax=ax, label='CPU')
        df_filtered_mean_gpu.plot(x = 'vl_dataset_memory_size', y = 'vl_total_execution_time', kind = 'line', color='blue', ax=ax, label='GPU')
        plt.xlabel('Data Set Size (B)')
        plt.ylabel('Average Total Execution Time (s)')
        plt.title('Average Total Execution Time x Data Set Size',fontstyle='italic',fontweight="bold")
        plt.savefig(dst_path_figs+'mode_1_vl_total_execution_time.png',bbox_inches='tight',dpi=100)

        
        # VL_INTER_TASK_EXECUTION_TIME
        plt.figure(2)
        ax = plt.gca()
        df_filtered_mean_cpu.plot(x = 'vl_dataset_memory_size', y = 'vl_inter_task_execution_time', kind = 'line', color='red', ax=ax, label='CPU')
        df_filtered_mean_gpu.plot(x = 'vl_dataset_memory_size', y = 'vl_inter_task_execution_time', kind = 'line', color='blue', ax=ax, label='GPU')
        plt.xlabel('Data Set Size (B)')
        plt.ylabel('Average Inter-Task Time (s)')
        plt.title('Average Inter-Task Time x Data Set Size',fontstyle='italic',fontweight="bold")
        plt.savefig(dst_path_figs+'mode_1_vl_inter_task_execution_time.png',bbox_inches='tight',dpi=100)


        # VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC
        plt.figure(3)
        ax = plt.gca()
        df_filtered_mean_cpu.plot(x = 'vl_dataset_memory_size', y = 'vl_intra_task_execution_time_full_func', kind = 'line', color='red', ax=ax, label='CPU')
        df_filtered_mean_gpu.plot(x = 'vl_dataset_memory_size', y = 'vl_intra_task_execution_time_full_func', kind = 'line', color='blue', ax=ax, label='GPU')
        plt.xlabel('Data Set Size (B)')
        plt.ylabel('Average Intra-Task (full func) Time (s)')
        plt.title('Average Intra-Task (full func) Time x Data Set Size',fontstyle='italic',fontweight="bold")
        plt.savefig(dst_path_figs+'mode_1_vl_intra_task_execution_time_full_func.png',bbox_inches='tight',dpi=100)


        # VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC
        plt.figure(4)
        ax = plt.gca()
        df_filtered_mean_cpu.plot(x = 'vl_dataset_memory_size', y = 'vl_intra_task_execution_time_device_func', kind = 'line', color='red', ax=ax, label='CPU')
        df_filtered_mean_gpu.plot(x = 'vl_dataset_memory_size', y = 'vl_intra_task_execution_time_device_func', kind = 'line', color='blue', ax=ax, label='GPU')
        plt.xlabel('Data Set Size (B)')
        plt.ylabel('Average Intra-Task (device func) Time (s)')
        plt.title('Average Intra-Task (device func) Time x Data Set Size',fontstyle='italic',fontweight="bold")
        plt.savefig(dst_path_figs+'mode_1_vl_intra_task_execution_time_device_func.png',bbox_inches='tight',dpi=100)


        # VL_COMMUNICATION_TIME
        plt.figure(5)
        ax = plt.gca()
        df_filtered_mean_cpu.plot(x = 'vl_dataset_memory_size', y = 'vl_communication_time', kind = 'line', color='red', ax=ax, label='CPU')
        df_filtered_mean_gpu.plot(x = 'vl_dataset_memory_size', y = 'vl_communication_time', kind = 'line', color='blue', ax=ax, label='GPU')
        plt.xlabel('Data Set Size (B)')
        plt.ylabel('Average Communication Time (s)')
        plt.title('Average Communication Time x Data Set Size',fontstyle='italic',fontweight="bold")
        plt.savefig(dst_path_figs+'mode_1_vl_communication_time.png',bbox_inches='tight',dpi=100)



if __name__ == "__main__":
    main()
