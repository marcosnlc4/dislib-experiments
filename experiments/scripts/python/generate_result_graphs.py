import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from config import open_connection, close_connection
import numpy as np

def main(ds_algorithm, ds_resource, nr_iterations, mode):

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
    

    # Filtering and sorting parameters
    df_filtered = df[
                    (df["ds_algorithm"] == ds_algorithm.upper()) # FIXED VALUE
                    & (df["nr_iterations"] == int(nr_iterations)) # FIXED VALUE
                    & (df["ds_resource"] == ds_resource.upper()) # FIXED VALUE
                    # & (df["ds_parameter_type"] == "VAR_BLOCK_CAPACITY_SIZE") # 1.1, 1.2, 1.3, 1.4
                    # & (df["ds_parameter_type"] == "VAR_PARALLELISM_LEVEL") # 2.1, 2.2
                    # & (df["ds_parameter_attribute"] == "0.25") # 1.1
                    # & (df["ds_parameter_attribute"] == "0.50") # 1.2
                    # & (df["ds_parameter_attribute"] == "0.75") # 1.3
                    # & (df["ds_parameter_attribute"] == "1.00") # 1.4
                    # & (df["ds_parameter_attribute"] == "MIN_INTER_MAX_INTRA") # 2.1
                    # & (df["ds_parameter_attribute"] == "MAX_INTER_MIN_INTRA") # 2.2
                    # & (df_parameters["vl_dataset_memory_size"] == 400) # 2.2.1
                    # & (df_parameters["vl_dataset_memory_size"] == 400000) # 2.2.2
                    # & (df_parameters["vl_dataset_memory_size"] == 400000000) # 2.2.3
                    # & (df["ds_dataset"] == "SYNTHETIC_A_400B_1")
                    ].sort_values(by=["id_parameter"])

    

    if mode == 1:

        print("\nMode ",mode,": Ploting an overview of all execution times, without parameter filters")

        df_filtered_mean = df_filtered.groupby(["ds_device"], as_index=False).mean()

        df_filtered_mean = df_filtered_mean[["ds_device","vl_total_execution_time","vl_inter_task_execution_time","vl_intra_task_execution_time_full_func","vl_intra_task_execution_time_device_func"]]

        df_filtered_mean_cpu = df_filtered_mean[(df_filtered_mean.ds_device=="CPU")].sort_values("vl_total_execution_time")
        df_filtered_mean_gpu = df_filtered_mean[(df_filtered_mean.ds_device=="GPU")].sort_values("vl_total_execution_time")

        # OVERVIEW OF ALL EXECUTION TIMES
        plt.figure(1)
        ax = plt.gca()
        df_filtered_mean.set_index('ds_device').plot(kind = 'bar')
        plt.legend(['Total Execution Time', 'Inter Task Execution Time', 'Intra Task Execution Time (Full Function)', 'Intra Task Execution Time (Device Function)'])
        plt.xlabel('Device')
        plt.ylabel('Average Execution Times (s)')
        plt.title('Average Execution Times per Device',fontstyle='italic',fontweight="bold")
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_overview_avg_execution_times_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

        # VL_TOTAL_EXECUTION_TIME
        plt.figure(2)
        fig, ax = plt.subplots()
        ax.bar(df_filtered_mean_cpu['ds_device'], df_filtered_mean_cpu['vl_total_execution_time'], color='C0', hatch='.')
        ax.bar(df_filtered_mean_gpu['ds_device'], df_filtered_mean_gpu['vl_total_execution_time'], color='C0', hatch='|')
        plt.legend(['Total Execution Time CPU','Total Execution Time GPU'])
        plt.xlabel('Device')
        plt.ylabel('Average Total Execution Time (s)')
        plt.title('Average Total Execution Time per Device',fontstyle='italic',fontweight="bold")
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_overview_avg_total_execution_time_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

        # VL_INTER_TASK_EXECUTION_TIME
        df_filtered_mean_cpu = df_filtered_mean[(df_filtered_mean.ds_device=="CPU")].sort_values("vl_inter_task_execution_time")
        df_filtered_mean_gpu = df_filtered_mean[(df_filtered_mean.ds_device=="GPU")].sort_values("vl_inter_task_execution_time")
        plt.figure(3)
        fig, ax = plt.subplots()
        ax.bar(df_filtered_mean_cpu['ds_device'], df_filtered_mean_cpu['vl_inter_task_execution_time'], color='C1', hatch='.')
        ax.bar(df_filtered_mean_gpu['ds_device'], df_filtered_mean_gpu['vl_inter_task_execution_time'], color='C1', hatch='x')
        plt.legend(['Inter Task Execution Time CPU','Inter Task Execution Time GPU'])
        plt.xlabel('Device')
        plt.ylabel('Average Inter-Task Time (s)')
        plt.title('Average Inter-Task Time per Device',fontstyle='italic',fontweight="bold")
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_overview_avg_inter_task_execution_time_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

        # VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC
        df_filtered_mean_cpu = df_filtered_mean[(df_filtered_mean.ds_device=="CPU")].sort_values("vl_intra_task_execution_time_full_func")
        df_filtered_mean_gpu = df_filtered_mean[(df_filtered_mean.ds_device=="GPU")].sort_values("vl_intra_task_execution_time_full_func")
        plt.figure(4)
        fig, ax = plt.subplots()
        ax.bar(df_filtered_mean_cpu['ds_device'], df_filtered_mean_cpu['vl_intra_task_execution_time_full_func'], color='C2', hatch='.')
        ax.bar(df_filtered_mean_gpu['ds_device'], df_filtered_mean_gpu['vl_intra_task_execution_time_full_func'], color='C2', hatch='x')
        plt.legend(['Intra Task Execution Time (Full Function) CPU','Intra Task Execution Time (Full Function) GPU'])
        plt.xlabel('Device')
        plt.ylabel('Average Intra-Task (full func) Time (s)')
        plt.title('Average Intra-Task (full func)Time per Device',fontstyle='italic',fontweight="bold")
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_overview_avg_intra_task_execution_time_full_func_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

        # VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC
        df_filtered_mean_cpu = df_filtered_mean[(df_filtered_mean.ds_device=="CPU")].sort_values("vl_intra_task_execution_time_device_func")
        df_filtered_mean_gpu = df_filtered_mean[(df_filtered_mean.ds_device=="GPU")].sort_values("vl_intra_task_execution_time_device_func")
        plt.figure(5)
        fig, ax = plt.subplots()
        ax.bar(df_filtered_mean_cpu['ds_device'], df_filtered_mean_cpu['vl_intra_task_execution_time_device_func'], color='C3', hatch='.')
        ax.bar(df_filtered_mean_gpu['ds_device'], df_filtered_mean_gpu['vl_intra_task_execution_time_device_func'], color='C3', hatch='x')
        plt.legend(['Intra Task Execution Time (Device Function) CPU','Intra Task Execution Time (Device Function) GPU'])
        plt.xlabel('Device')
        plt.ylabel('Average Intra-Task (device func) Time (s)')
        plt.title('Average Intra-Task (device func) Time per Device',fontstyle='italic',fontweight="bold")
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_overview_avg_intra_task_execution_time_device_func_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)


    elif mode == 2:

        print("\nMode ",mode,": Ploting all execution times x data set memory size, without parameter filters")

        df_filtered_mean = df_filtered.groupby(['ds_device', 'vl_dataset_memory_size'], as_index=False).mean()

        df_filtered_mean_cpu = df_filtered_mean[(df_filtered_mean.ds_device=="CPU")]
        df_filtered_mean_gpu = df_filtered_mean[(df_filtered_mean.ds_device=="GPU")]

        # VL_TOTAL_EXECUTION_TIME
        plt.figure(1)
        ax = plt.gca()
        df_filtered_mean_cpu.plot(x = 'vl_dataset_memory_size', y = 'vl_total_execution_time', kind = 'line', color='C0', linestyle = 'dotted', ax=ax, label='CPU')
        df_filtered_mean_gpu.plot(x = 'vl_dataset_memory_size', y = 'vl_total_execution_time', kind = 'line', color='C0', linestyle = 'solid', ax=ax, label='GPU')
        plt.xlabel('Data Set Size (B)')
        plt.ylabel('Average Total Execution Time (s)')
        plt.title('Average Total Execution Time x Data Set Size',fontstyle='italic',fontweight="bold")
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_avg_total_execution_time_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)
        # plt.savefig(dst_path_figs+'avg_total_execution_time_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+int(nr_iterations)+'_'+ds_parameter_type+'_'+ds_parameter_attribute+'_mode_'+str(mode)+'.png',bbox_inches='tight',dpi=100)
        
        # VL_INTER_TASK_EXECUTION_TIME
        plt.figure(2)
        ax = plt.gca()
        df_filtered_mean_cpu.plot(x = 'vl_dataset_memory_size', y = 'vl_inter_task_execution_time', kind = 'line', color='C1', linestyle = 'dotted', ax=ax, label='CPU')
        df_filtered_mean_gpu.plot(x = 'vl_dataset_memory_size', y = 'vl_inter_task_execution_time', kind = 'line', color='C1', linestyle = 'solid', ax=ax, label='GPU')
        plt.xlabel('Data Set Size (B)')
        plt.ylabel('Average Inter-Task Time (s)')
        plt.title('Average Inter-Task Time x Data Set Size',fontstyle='italic',fontweight="bold")
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_avg_inter_task_execution_time_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

        # VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC
        plt.figure(3)
        ax = plt.gca()
        df_filtered_mean_cpu.plot(x = 'vl_dataset_memory_size', y = 'vl_intra_task_execution_time_full_func', kind = 'line', color='C2', linestyle = 'dotted', ax=ax, label='CPU')
        df_filtered_mean_gpu.plot(x = 'vl_dataset_memory_size', y = 'vl_intra_task_execution_time_full_func', kind = 'line', color='C2', linestyle = 'solid', ax=ax, label='GPU')
        plt.xlabel('Data Set Size (B)')
        plt.ylabel('Average Intra-Task (full func) Time (s)')
        plt.title('Average Intra-Task (full func) Time x Data Set Size',fontstyle='italic',fontweight="bold")
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_avg_intra_task_execution_time_full_func_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

        # VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC
        plt.figure(4)
        ax = plt.gca()
        df_filtered_mean_cpu.plot(x = 'vl_dataset_memory_size', y = 'vl_intra_task_execution_time_device_func', kind = 'line', color='C3', linestyle = 'dotted', ax=ax, label='CPU')
        df_filtered_mean_gpu.plot(x = 'vl_dataset_memory_size', y = 'vl_intra_task_execution_time_device_func', kind = 'line', color='C3', linestyle = 'solid', ax=ax, label='GPU')
        plt.xlabel('Data Set Size (B)')
        plt.ylabel('Average Intra-Task (device func) Time (s)')
        plt.title('Average Intra-Task (device func) Time x Data Set Size',fontstyle='italic',fontweight="bold")
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_avg_intra_task_execution_time_device_func_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

        # VL_COMMUNICATION_TIME
        plt.figure(5)
        ax = plt.gca()
        df_filtered_mean_cpu.plot(x = 'vl_dataset_memory_size', y = 'vl_communication_time', kind = 'line', color='C4', linestyle = 'dotted', ax=ax, label='CPU')
        df_filtered_mean_gpu.plot(x = 'vl_dataset_memory_size', y = 'vl_communication_time', kind = 'line', color='C4', linestyle = 'solid', ax=ax, label='GPU')
        plt.xlabel('Data Set Size (B)')
        plt.ylabel('Average Communication Time (s)')
        plt.title('Average Communication Time x Data Set Size',fontstyle='italic',fontweight="bold")
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_avg_communication_time_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)


    elif mode == 3:

        print("\nMode ",mode,": Ploting an overview of all execution times, filtering data set memory size")

        df_filtered_mean = df_filtered.groupby(["ds_device","vl_dataset_memory_size"], as_index=False).mean()

        df_filtered_mean = df_filtered_mean[["ds_device","vl_dataset_memory_size","vl_total_execution_time","vl_inter_task_execution_time","vl_intra_task_execution_time_full_func","vl_intra_task_execution_time_device_func"]]
        
        vl_dataset_memory_size = 400000000

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
        plt.figure(1)
        ax = plt.gca()
        df_filtered_mean.set_index('ds_device').plot(kind = 'bar')
        plt.legend(['Total Execution Time', 'Inter Task Execution Time', 'Intra Task Execution Time (Full Function)', 'Intra Task Execution Time (Device Function)'])
        plt.xlabel('Device')
        plt.ylabel('Average Execution Times (s)')
        plt.title('Average Execution Times per Device - '+vl_dataset_memory_size_title, fontstyle='italic',fontweight="bold")
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+str(vl_dataset_memory_size)+'_dataset_overview_avg_execution_times_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

        # VL_TOTAL_EXECUTION_TIME
        plt.figure(2)
        fig, ax = plt.subplots()
        ax.bar(df_filtered_mean_cpu['ds_device'], df_filtered_mean_cpu['vl_total_execution_time'], color='C0', hatch='.')
        ax.bar(df_filtered_mean_gpu['ds_device'], df_filtered_mean_gpu['vl_total_execution_time'], color='C0', hatch='|')
        plt.legend(['Total Execution Time CPU','Total Execution Time GPU'])
        plt.xlabel('Device')
        plt.ylabel('Average Total Execution Time (s)')
        plt.title('Average Total Execution Time per Device - '+vl_dataset_memory_size_title, fontstyle='italic',fontweight="bold")
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+str(vl_dataset_memory_size)+'_dataset_overview_avg_total_execution_time_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

        # VL_INTER_TASK_EXECUTION_TIME
        df_filtered_mean_cpu = df_filtered_mean[(df_filtered_mean.ds_device=="CPU") & (df_filtered_mean.vl_dataset_memory_size==vl_dataset_memory_size)].sort_values("vl_inter_task_execution_time")
        df_filtered_mean_gpu = df_filtered_mean[(df_filtered_mean.ds_device=="GPU") & (df_filtered_mean.vl_dataset_memory_size==vl_dataset_memory_size)].sort_values("vl_inter_task_execution_time")
        plt.figure(3)
        fig, ax = plt.subplots()
        ax.bar(df_filtered_mean_cpu['ds_device'], df_filtered_mean_cpu['vl_inter_task_execution_time'], color='C1', hatch='.')
        ax.bar(df_filtered_mean_gpu['ds_device'], df_filtered_mean_gpu['vl_inter_task_execution_time'], color='C1', hatch='x')
        plt.legend(['Inter Task Execution Time CPU','Inter Task Execution Time GPU'])
        plt.xlabel('Device')
        plt.ylabel('Average Inter-Task Time (s)')
        plt.title('Average Inter-Task Time per Device - '+vl_dataset_memory_size_title, fontstyle='italic',fontweight="bold")
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+str(vl_dataset_memory_size)+'_dataset_overview_avg_inter_task_execution_time_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

        # VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC
        df_filtered_mean_cpu = df_filtered_mean[(df_filtered_mean.ds_device=="CPU") & (df_filtered_mean.vl_dataset_memory_size==vl_dataset_memory_size)].sort_values("vl_intra_task_execution_time_full_func")
        df_filtered_mean_gpu = df_filtered_mean[(df_filtered_mean.ds_device=="GPU") & (df_filtered_mean.vl_dataset_memory_size==vl_dataset_memory_size)].sort_values("vl_intra_task_execution_time_full_func")
        plt.figure(4)
        fig, ax = plt.subplots()
        ax.bar(df_filtered_mean_cpu['ds_device'], df_filtered_mean_cpu['vl_intra_task_execution_time_full_func'], color='C2', hatch='.')
        ax.bar(df_filtered_mean_gpu['ds_device'], df_filtered_mean_gpu['vl_intra_task_execution_time_full_func'], color='C2', hatch='x')
        plt.legend(['Intra Task Execution Time (Full Function) CPU','Intra Task Execution Time (Full Function) GPU'])
        plt.xlabel('Device')
        plt.ylabel('Average Intra-Task (full func) Time (s)')
        plt.title('Average Intra-Task (full func)Time per Device - '+vl_dataset_memory_size_title, fontstyle='italic',fontweight="bold")
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+str(vl_dataset_memory_size)+'_dataset_overview_avg_intra_task_execution_time_full_func_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

        # VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC
        df_filtered_mean_cpu = df_filtered_mean[(df_filtered_mean.ds_device=="CPU") & (df_filtered_mean.vl_dataset_memory_size==vl_dataset_memory_size)].sort_values("vl_intra_task_execution_time_device_func")
        df_filtered_mean_gpu = df_filtered_mean[(df_filtered_mean.ds_device=="GPU") & (df_filtered_mean.vl_dataset_memory_size==vl_dataset_memory_size)].sort_values("vl_intra_task_execution_time_device_func")
        plt.figure(5)
        fig, ax = plt.subplots()
        ax.bar(df_filtered_mean_cpu['ds_device'], df_filtered_mean_cpu['vl_intra_task_execution_time_device_func'], color='C3', hatch='.')
        ax.bar(df_filtered_mean_gpu['ds_device'], df_filtered_mean_gpu['vl_intra_task_execution_time_device_func'], color='C3', hatch='x')
        plt.legend(['Intra Task Execution Time (Device Function) CPU','Intra Task Execution Time (Device Function) GPU'])
        plt.xlabel('Device')
        plt.ylabel('Average Intra-Task (device func) Time (s)')
        plt.title('Average Intra-Task (device func) Time per Device - '+vl_dataset_memory_size_title, fontstyle='italic',fontweight="bold")
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+str(vl_dataset_memory_size)+'_dataset_overview_avg_intra_task_execution_time_device_func_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)


    elif mode == 4:

        print("\nMode ",mode,": Ploting an overview of all execution times, filtering block dimension")

        df_filtered_mean = df_filtered.groupby(["ds_device","ds_parameter_attribute"], as_index=False).mean()

        df_filtered_mean = df_filtered_mean[["ds_device","ds_parameter_attribute","vl_total_execution_time","vl_inter_task_execution_time","vl_intra_task_execution_time_full_func","vl_intra_task_execution_time_device_func"]]
        
        ds_parameter_attribute = "1.00"
        ds_parameter_attribute_title = str(float(ds_parameter_attribute)*100) + "% of dataset"

        df_filtered_mean_cpu = df_filtered_mean[(df_filtered_mean.ds_device=="CPU") & (df_filtered_mean.ds_parameter_attribute==ds_parameter_attribute)].sort_values("vl_total_execution_time")
        df_filtered_mean_gpu = df_filtered_mean[(df_filtered_mean.ds_device=="GPU") & (df_filtered_mean.ds_parameter_attribute==ds_parameter_attribute)].sort_values("vl_total_execution_time")

        
        # OVERVIEW OF ALL EXECUTION TIMES
        plt.figure(1)
        ax = plt.gca()
        df_filtered_mean.set_index('ds_device').plot(kind = 'bar')
        plt.legend(['Total Execution Time', 'Inter Task Execution Time', 'Intra Task Execution Time (Full Function)', 'Intra Task Execution Time (Device Function)'])
        plt.xlabel('Device')
        plt.ylabel('Average Execution Times (s)')
        plt.title('Average Execution Times per Device - '+ds_parameter_attribute_title, fontstyle='italic',fontweight="bold")
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+ds_parameter_attribute+'_dataset_overview_avg_execution_times_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

        # VL_TOTAL_EXECUTION_TIME
        plt.figure(2)
        fig, ax = plt.subplots()
        ax.bar(df_filtered_mean_cpu['ds_device'], df_filtered_mean_cpu['vl_total_execution_time'], color='C0', hatch='.')
        ax.bar(df_filtered_mean_gpu['ds_device'], df_filtered_mean_gpu['vl_total_execution_time'], color='C0', hatch='|')
        plt.legend(['Total Execution Time CPU','Total Execution Time GPU'])
        plt.xlabel('Device')
        plt.ylabel('Average Total Execution Time (s)')
        plt.title('Average Total Execution Time per Device - '+ds_parameter_attribute_title, fontstyle='italic',fontweight="bold")
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+ds_parameter_attribute+'_dataset_overview_avg_total_execution_time_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

        # VL_INTER_TASK_EXECUTION_TIME
        df_filtered_mean_cpu = df_filtered_mean[(df_filtered_mean.ds_device=="CPU") & (df_filtered_mean.ds_parameter_attribute==ds_parameter_attribute)].sort_values("vl_inter_task_execution_time")
        df_filtered_mean_gpu = df_filtered_mean[(df_filtered_mean.ds_device=="GPU") & (df_filtered_mean.ds_parameter_attribute==ds_parameter_attribute)].sort_values("vl_inter_task_execution_time")
        plt.figure(3)
        fig, ax = plt.subplots()
        ax.bar(df_filtered_mean_cpu['ds_device'], df_filtered_mean_cpu['vl_inter_task_execution_time'], color='C1', hatch='.')
        ax.bar(df_filtered_mean_gpu['ds_device'], df_filtered_mean_gpu['vl_inter_task_execution_time'], color='C1', hatch='x')
        plt.legend(['Inter Task Execution Time CPU','Inter Task Execution Time GPU'])
        plt.xlabel('Device')
        plt.ylabel('Average Inter-Task Time (s)')
        plt.title('Average Inter-Task Time per Device - '+ds_parameter_attribute_title, fontstyle='italic',fontweight="bold")
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+ds_parameter_attribute+'_dataset_overview_avg_inter_task_execution_time_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

        # VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC
        df_filtered_mean_cpu = df_filtered_mean[(df_filtered_mean.ds_device=="CPU") & (df_filtered_mean.ds_parameter_attribute==ds_parameter_attribute)].sort_values("vl_intra_task_execution_time_full_func")
        df_filtered_mean_gpu = df_filtered_mean[(df_filtered_mean.ds_device=="GPU") & (df_filtered_mean.ds_parameter_attribute==ds_parameter_attribute)].sort_values("vl_intra_task_execution_time_full_func")
        plt.figure(4)
        fig, ax = plt.subplots()
        ax.bar(df_filtered_mean_cpu['ds_device'], df_filtered_mean_cpu['vl_intra_task_execution_time_full_func'], color='C2', hatch='.')
        ax.bar(df_filtered_mean_gpu['ds_device'], df_filtered_mean_gpu['vl_intra_task_execution_time_full_func'], color='C2', hatch='x')
        plt.legend(['Intra Task Execution Time (Full Function) CPU','Intra Task Execution Time (Full Function) GPU'])
        plt.xlabel('Device')
        plt.ylabel('Average Intra-Task (full func) Time (s)')
        plt.title('Average Intra-Task (full func)Time per Device - '+ds_parameter_attribute_title, fontstyle='italic',fontweight="bold")
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+ds_parameter_attribute+'_dataset_overview_avg_intra_task_execution_time_full_func_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

        # VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC
        df_filtered_mean_cpu = df_filtered_mean[(df_filtered_mean.ds_device=="CPU") & (df_filtered_mean.ds_parameter_attribute==ds_parameter_attribute)].sort_values("vl_intra_task_execution_time_device_func")
        df_filtered_mean_gpu = df_filtered_mean[(df_filtered_mean.ds_device=="GPU") & (df_filtered_mean.ds_parameter_attribute==ds_parameter_attribute)].sort_values("vl_intra_task_execution_time_device_func")
        plt.figure(5)
        fig, ax = plt.subplots()
        ax.bar(df_filtered_mean_cpu['ds_device'], df_filtered_mean_cpu['vl_intra_task_execution_time_device_func'], color='C3', hatch='.')
        ax.bar(df_filtered_mean_gpu['ds_device'], df_filtered_mean_gpu['vl_intra_task_execution_time_device_func'], color='C3', hatch='x')
        plt.legend(['Intra Task Execution Time (Device Function) CPU','Intra Task Execution Time (Device Function) GPU'])
        plt.xlabel('Device')
        plt.ylabel('Average Intra-Task (device func) Time (s)')
        plt.title('Average Intra-Task (device func) Time per Device - '+ds_parameter_attribute_title, fontstyle='italic',fontweight="bold")
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+ds_parameter_attribute+'_dataset_overview_avg_intra_task_execution_time_device_func_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)


    elif mode == 5:

        print("\nMode ",mode,": Ploting an overview of all execution times, filtering parallelism level (extreme cases)")

        df_filtered_mean = df_filtered.groupby(["ds_device","ds_parameter_attribute"], as_index=False).mean()

        df_filtered_mean = df_filtered_mean[["ds_device","ds_parameter_attribute","vl_total_execution_time","vl_inter_task_execution_time","vl_intra_task_execution_time_full_func","vl_intra_task_execution_time_device_func"]]
        
        ds_parameter_attribute = "MAX_INTER_MIN_INTRA"

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
        plt.figure(1)
        ax = plt.gca()
        df_filtered_mean.set_index('ds_device').plot(kind = 'bar')
        plt.legend(['Total Execution Time', 'Inter Task Execution Time', 'Intra Task Execution Time (Full Function)', 'Intra Task Execution Time (Device Function)'])
        plt.xlabel('Device')
        plt.ylabel('Average Execution Times (s)')
        plt.title('Average Execution Times per Device - '+ds_parameter_attribute_title, fontstyle='italic',fontweight="bold")
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+ds_parameter_attribute+'_dataset_overview_avg_execution_times_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

        # VL_TOTAL_EXECUTION_TIME
        plt.figure(2)
        fig, ax = plt.subplots()
        ax.bar(df_filtered_mean_cpu['ds_device'], df_filtered_mean_cpu['vl_total_execution_time'], color='C0', hatch='.')
        ax.bar(df_filtered_mean_gpu['ds_device'], df_filtered_mean_gpu['vl_total_execution_time'], color='C0', hatch='|')
        plt.legend(['Total Execution Time CPU','Total Execution Time GPU'])
        plt.xlabel('Device')
        plt.ylabel('Average Total Execution Time (s)')
        plt.title('Average Total Execution Time per Device - '+ds_parameter_attribute_title, fontstyle='italic',fontweight="bold")
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+ds_parameter_attribute+'_dataset_overview_avg_total_execution_time_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

        # VL_INTER_TASK_EXECUTION_TIME
        df_filtered_mean_cpu = df_filtered_mean[(df_filtered_mean.ds_device=="CPU") & (df_filtered_mean.ds_parameter_attribute==ds_parameter_attribute)].sort_values("vl_inter_task_execution_time")
        df_filtered_mean_gpu = df_filtered_mean[(df_filtered_mean.ds_device=="GPU") & (df_filtered_mean.ds_parameter_attribute==ds_parameter_attribute)].sort_values("vl_inter_task_execution_time")
        plt.figure(3)
        fig, ax = plt.subplots()
        ax.bar(df_filtered_mean_cpu['ds_device'], df_filtered_mean_cpu['vl_inter_task_execution_time'], color='C1', hatch='.')
        ax.bar(df_filtered_mean_gpu['ds_device'], df_filtered_mean_gpu['vl_inter_task_execution_time'], color='C1', hatch='x')
        plt.legend(['Inter Task Execution Time CPU','Inter Task Execution Time GPU'])
        plt.xlabel('Device')
        plt.ylabel('Average Inter-Task Time (s)')
        plt.title('Average Inter-Task Time per Device - '+ds_parameter_attribute_title, fontstyle='italic',fontweight="bold")
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+ds_parameter_attribute+'_dataset_overview_avg_inter_task_execution_time_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

        # VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC
        df_filtered_mean_cpu = df_filtered_mean[(df_filtered_mean.ds_device=="CPU") & (df_filtered_mean.ds_parameter_attribute==ds_parameter_attribute)].sort_values("vl_intra_task_execution_time_full_func")
        df_filtered_mean_gpu = df_filtered_mean[(df_filtered_mean.ds_device=="GPU") & (df_filtered_mean.ds_parameter_attribute==ds_parameter_attribute)].sort_values("vl_intra_task_execution_time_full_func")
        plt.figure(4)
        fig, ax = plt.subplots()
        ax.bar(df_filtered_mean_cpu['ds_device'], df_filtered_mean_cpu['vl_intra_task_execution_time_full_func'], color='C2', hatch='.')
        ax.bar(df_filtered_mean_gpu['ds_device'], df_filtered_mean_gpu['vl_intra_task_execution_time_full_func'], color='C2', hatch='x')
        plt.legend(['Intra Task Execution Time (Full Function) CPU','Intra Task Execution Time (Full Function) GPU'])
        plt.xlabel('Device')
        plt.ylabel('Average Intra-Task (full func) Time (s)')
        plt.title('Average Intra-Task (full func)Time per Device - '+ds_parameter_attribute_title, fontstyle='italic',fontweight="bold")
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+ds_parameter_attribute+'_dataset_overview_avg_intra_task_execution_time_full_func_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

        # VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC
        df_filtered_mean_cpu = df_filtered_mean[(df_filtered_mean.ds_device=="CPU") & (df_filtered_mean.ds_parameter_attribute==ds_parameter_attribute)].sort_values("vl_intra_task_execution_time_device_func")
        df_filtered_mean_gpu = df_filtered_mean[(df_filtered_mean.ds_device=="GPU") & (df_filtered_mean.ds_parameter_attribute==ds_parameter_attribute)].sort_values("vl_intra_task_execution_time_device_func")
        plt.figure(5)
        fig, ax = plt.subplots()
        ax.bar(df_filtered_mean_cpu['ds_device'], df_filtered_mean_cpu['vl_intra_task_execution_time_device_func'], color='C3', hatch='.')
        ax.bar(df_filtered_mean_gpu['ds_device'], df_filtered_mean_gpu['vl_intra_task_execution_time_device_func'], color='C3', hatch='x')
        plt.legend(['Intra Task Execution Time (Device Function) CPU','Intra Task Execution Time (Device Function) GPU'])
        plt.xlabel('Device')
        plt.ylabel('Average Intra-Task (device func) Time (s)')
        plt.title('Average Intra-Task (device func) Time per Device - '+ds_parameter_attribute_title, fontstyle='italic',fontweight="bold")
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+ds_parameter_attribute+'_dataset_overview_avg_intra_task_execution_time_device_func_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

    
    elif mode == 6:
        
        print("\nMode ",mode,": Ploting an overview of all execution times grouped by data set description")
        
        vl_dataset_memory_size = 400

        if vl_dataset_memory_size == 400:
            vl_dataset_memory_size_title = str(int(vl_dataset_memory_size)) + " B"
        elif vl_dataset_memory_size == 400000:
            vl_dataset_memory_size_title = str(int(vl_dataset_memory_size*1e-3)) + " KB"
        elif vl_dataset_memory_size == 400000000:
            vl_dataset_memory_size_title = str(int(vl_dataset_memory_size*1e-6)) + " MB"

        df_filtered = df_filtered[df_filtered.vl_dataset_memory_size==vl_dataset_memory_size]

        df_filtered_mean = df_filtered.groupby(["ds_device","ds_dataset"], as_index=False).mean().sort_values(by=["vl_total_execution_time"], ascending=False)

        df_filtered_mean = df_filtered_mean[["ds_device","ds_dataset","vl_total_execution_time","vl_inter_task_execution_time","vl_intra_task_execution_time_full_func","vl_intra_task_execution_time_device_func"]]

        df_filtered_mean_cpu = df_filtered_mean[(df_filtered_mean.ds_device=="CPU")]
        df_filtered_mean_gpu = df_filtered_mean[(df_filtered_mean.ds_device=="GPU")]
        
        # VL_TOTAL_EXECUTION_TIME
        plt.figure(1)
        X_axis = np.arange(len(df_filtered_mean_cpu["ds_dataset"]))
        plt.bar(X_axis - 0.2, df_filtered_mean_cpu["vl_total_execution_time"], 0.3, label = "CPU", color='C0', hatch='.')
        plt.bar(X_axis + 0.2, df_filtered_mean_gpu["vl_total_execution_time"], 0.3, label = "GPU", color='C0', hatch='x')
        plt.xticks(X_axis, df_filtered_mean_cpu["ds_dataset"], rotation=90)
        plt.xlabel('Data Set Description')
        plt.ylabel('Average Total Execution Time (s)')
        plt.title('Average Total Execution Time per Data Set Description ' + vl_dataset_memory_size_title,fontstyle='italic',fontweight="bold")
        plt.legend()
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+str(vl_dataset_memory_size)+'_avg_total_execution_time_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

        # VL_INTER_TASK_EXECUTION_TIME
        plt.figure(2)
        X_axis = np.arange(len(df_filtered_mean_cpu["ds_dataset"]))
        plt.bar(X_axis - 0.2, df_filtered_mean_cpu["vl_inter_task_execution_time"], 0.3, label = "CPU", color='C1', hatch='.')
        plt.bar(X_axis + 0.2, df_filtered_mean_gpu["vl_inter_task_execution_time"], 0.3, label = "GPU", color='C1', hatch='x')
        plt.xticks(X_axis, df_filtered_mean_cpu["ds_dataset"], rotation=90)
        plt.xlabel('Data Set Description')
        plt.ylabel('Average Inter Task Execution Time (s)')
        plt.title('Average Inter Task Execution Time per Data Set Description ' + vl_dataset_memory_size_title,fontstyle='italic',fontweight="bold")
        plt.legend()
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+str(vl_dataset_memory_size)+'_avg_inter_task_execution_time_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

        # VL_INTRA_TASK_EXECUTION_TIME_FULL_FUNC
        plt.figure(3)
        X_axis = np.arange(len(df_filtered_mean_cpu["ds_dataset"]))
        plt.bar(X_axis - 0.2, df_filtered_mean_cpu["vl_intra_task_execution_time_full_func"], 0.3, label = "CPU", color='C2', hatch='.')
        plt.bar(X_axis + 0.2, df_filtered_mean_gpu["vl_intra_task_execution_time_full_func"], 0.3, label = "GPU", color='C2', hatch='x')
        plt.xticks(X_axis, df_filtered_mean_cpu["ds_dataset"], rotation=90)
        plt.xlabel('Data Set Description')
        plt.ylabel('Average Intra-Task (full func) Time (s)')
        plt.title('Average Intra-Task (full func) Time per Data Set Description ' + vl_dataset_memory_size_title,fontstyle='italic',fontweight="bold")
        plt.legend()
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+str(vl_dataset_memory_size)+'_avg_intra_task_execution_time_full_func_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)

        # VL_INTRA_TASK_EXECUTION_TIME_DEVICE_FUNC
        plt.figure(4)
        X_axis = np.arange(len(df_filtered_mean_cpu["ds_dataset"]))
        plt.bar(X_axis - 0.2, df_filtered_mean_cpu["vl_intra_task_execution_time_device_func"], 0.3, label = "CPU", color='C3', hatch='.')
        plt.bar(X_axis + 0.2, df_filtered_mean_gpu["vl_intra_task_execution_time_device_func"], 0.3, label = "GPU", color='C3', hatch='x')
        plt.xticks(X_axis, df_filtered_mean_cpu["ds_dataset"], rotation=90)
        plt.xlabel('Data Set Description')
        plt.ylabel('Average Intra-Task (device func) Time (s)')
        plt.title('Average Intra-Task (device func) Time per Data Set Description ' + vl_dataset_memory_size_title,fontstyle='italic',fontweight="bold")
        plt.legend()
        plt.savefig(dst_path_figs+'mode_'+str(mode)+'_'+str(vl_dataset_memory_size)+'_avg_intra_task_execution_time_device_func_'+ds_algorithm+'_'+ds_resource+'_nr_it_'+str(nr_iterations)+'.png',bbox_inches='tight',dpi=100)



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
