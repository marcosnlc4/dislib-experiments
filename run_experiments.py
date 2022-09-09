import sys
import os
import time
import datetime
from datetime import date
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.datasets import make_blobs

import dislib as ds
from dislib.cluster import KMeans

from pycompss.api.api import compss_barrier
from pycompss.api.api import compss_wait_on

def main():
    # Path of the "tb_parameters" table - CSV file
    src_path_parameters = "experiments/parameters/tb_parameters.csv"
    # Path of the "tb_experiments" table - CSV file
    dst_path_experiments = "experiments/results/tb_experiments.csv"
    # Path of the "log_time" table for temporary storing execution time logs during the execution - CSV file
    log_file_path = "experiments/logs/log_time.csv"

    # Reading "tb_parameters" table
    param_file = os.path.join(src_path_parameters)
    df_parameters = pd.read_csv(param_file)

    # Filtering and sorting parameters
    df_parameters = df_parameters[
                                    (df_parameters["ds_algorithm"] == "KMEANS") # FIXED VALUE
                                    & (df_parameters["nr_iterations"] == 5) # FIXED VALUE
                                    & (df_parameters["ds_resource"] == "MINOTAURO_1") # FIXED VALUE
                                    & (df_parameters["ds_tp_parameter"] == "VAR_BLOCK_CAPACITY_SIZE") # 1.1, 1.2, 1.3, 1.4
                                    # & (df_parameters["ds_tp_parameter"] == "VAR_PARALLELISM_LEVEL") # 2.1, 2.2
                                    & (df_parameters["vl_block_size_percent_dataset"] == 0.25) # 1.1
                                    # & (df_parameters["vl_block_size_percent_dataset"] == 0.5) # 1.2
                                    # & (df_parameters["vl_block_size_percent_dataset"] == 0.75) # 1.3
                                    # & (df_parameters["vl_block_size_percent_dataset"] == 1) # 1.4
                                    # & (df_parameters["ds_status_parallelism"] == "MIN_INTER_MAX_INTRA") # 2.1
                                    # & (df_parameters["ds_status_parallelism"] == "MAX_INTER_MIN_INTRA") # 2.2
                                ].sort_values(by=["id_parameter"])


    # Filtering and sorting parameters (TEST)
    # df_parameters = df_parameters[(df_parameters["id_parameter"] == 1) | (df_parameters["id_parameter"] == 2)].sort_values(by=["id_parameter"])

    # DataFrame to store final table
    df_experiments = pd.DataFrame(columns=["id_parameter", "vl_total_execution_time", "vl_inter_task_execution_time", "vl_intra_task_execution_time_device_func", "vl_intra_task_execution_time_full_func", "vl_communication_time"])
    # df_experiments.reset_index(drop=True, inplace=True)
    # array to store temporary results
    data = []

    print("\n\n df_experiments: \n")
    print(df_experiments)
    
    # Iterate over each row of the parameter table CSV file
    for index, row in df_parameters.iterrows():

        # Setting parameters variables
        id_parameter = row["id_parameter"]
        cd_parameter = row["cd_parameter"]
        cd_configuration = row["cd_configuration"]
        cd_algorithm = row["cd_algorithm"]
        ds_algorithm = row["ds_algorithm"]
        cd_function = row["cd_function"]
        ds_function = row["ds_function"]
        id_device = row["id_device"]
        ds_device = row["ds_device"]
        cd_dataset = row["cd_dataset"]
        cd_resource = row["cd_resource"]
        nr_iterations = row["nr_iterations"]
        ds_tp_parameter = row["ds_tp_parameter"]
        vl_dataset_row_size = row["vl_dataset_row_size"]
        vl_dataset_column_size = row["vl_dataset_column_size"]
        vl_grid_row_size = row["vl_grid_row_size"]
        vl_grid_column_size = row["vl_grid_column_size"]
        vl_block_row_size = row["vl_block_row_size"]
        vl_block_column_size = row["vl_block_column_size"]
        ds_status_parallelism = row["ds_status_parallelism"]
        vl_block_size_percent_dataset = row["vl_block_size_percent_dataset"]
        ds_resource = row["ds_resource"]
        nr_nodes = row["nr_nodes"]
        nr_computing_units_cpu = row["nr_computing_units_cpu"]
        nr_computing_units_gpu = row["nr_computing_units_gpu"]
        vl_memory_per_cpu_computing_unit = row["vl_memory_per_cpu_computing_unit"]
        vl_memory_per_gpu_computing_unit = row["vl_memory_per_gpu_computing_unit"]
        ds_dataset = row["ds_dataset"]
        vl_dataset_memory_size = row["vl_dataset_memory_size"]
        ds_data_type = row["ds_data_type"]
        vl_data_type_memory_size = row["vl_data_type_memory_size"]
        vl_dataset_size = row["vl_dataset_size"]
        vl_dataset_row_size = row["vl_dataset_row_size"]
        vl_dataset_column_size = row["vl_dataset_column_size"]
        nr_random_state = row["nr_random_state"]
        n_clusters = 100

        # Execute the experiment for N (nr_iterations) times with the same parameter set
        for i in range(nr_iterations):

            execution_progress = round(((index+1)/df_parameters.shape[0])*100,2)
            iteration_experiment_time_start = datetime.datetime.now()

            print("\nEXPERIMENT ", id_parameter,"-------------- ITERATION ", i+1, " STARTED AT "+str(iteration_experiment_time_start)+"------------------\n")
            print("\n@@@@@@ EXECUTION PROGRESS:",str(execution_progress),"%\n")
            print("nodes: ",str(nr_nodes),"\n")
            print("computing_units_cpu: ",str(nr_computing_units_cpu),"\n")
            print("mem_computing_units_cpu: ",str(vl_memory_per_cpu_computing_unit),"\n")
            print("computing_units_gpu: ",str(nr_computing_units_gpu),"\n")
            print("mem_computing_units_gpu: ",str(vl_memory_per_gpu_computing_unit),"\n")
            print("ds_device: ",str(ds_device),"\n")
            print("ds_status_parallelism: ",str(ds_status_parallelism),"\n")
            print("ds_tp_parameter: ",str(ds_tp_parameter),"\n")
            print("vl_dataset_memory_size: ",str(vl_dataset_memory_size),"\n")
            print("vl_block_size_percent_dataset: ",str(vl_block_size_percent_dataset),"\n")
            print("DATASET: vl_dataset_row_size x vl_dataset_column_size: ",str(vl_dataset_row_size)," x ",str(vl_dataset_column_size),"\n")
            print("GRID: vl_grid_row_size x vl_grid_column_size: ",str(vl_grid_row_size)," x ",str(vl_grid_column_size),"\n")
            print("BLOCK: vl_block_row_size x vl_block_column_size: ",str(vl_block_row_size)," x ",str(vl_block_column_size),"\n")
            
            if ds_algorithm == "KMEANS":

                # execution to compile gpu device code and to extract GPU execution times using CUDA events (id_device=3))
                # generate and load initial data into a ds-array and kmeans for the first time (compiling/warming up device code)
                x, y = make_blobs(n_samples=vl_dataset_row_size, n_features=vl_dataset_column_size, random_state=nr_random_state)
                dis_x = ds.array(x, block_size=(vl_block_row_size, vl_block_column_size))
                kmeans = KMeans(n_clusters=n_clusters, random_state=nr_random_state, id_device=id_device)
                y_pred = kmeans.fit_predict(dis_x).collect()

                x, y = make_blobs(n_samples=vl_dataset_row_size, n_features=vl_dataset_column_size, random_state=nr_random_state)
                dis_x = ds.array(x, block_size=(vl_block_row_size, vl_block_column_size))
                kmeans = KMeans(n_clusters=n_clusters, random_state=nr_random_state, id_device=3)
                y_pred = kmeans.fit_predict(dis_x).collect()
                
                if ds_device == "GPU":
                                        
                    # Run experiment separetely to extract GPU execution times using CUDA events (id_device=3))
                    # generate and load data into a ds-array
                    x, y = make_blobs(n_samples=vl_dataset_row_size, n_features=vl_dataset_column_size, random_state=nr_random_state)
                    dis_x = ds.array(x, block_size=(vl_block_row_size, vl_block_column_size))
                    # Run KMeans using dislib
                    kmeans = KMeans(n_clusters=n_clusters, random_state=nr_random_state, id_device=3)
                    y_pred = kmeans.fit_predict(dis_x).collect()


                # execution to extract all execution times for CPU (id_device = 1) and the remaining execution times (total_execution_time and inter_task_execution_time) for GPU (id_device = 2)
                # generate and load data into a ds-array
                x, y = make_blobs(n_samples=vl_dataset_row_size, n_features=vl_dataset_column_size, random_state=nr_random_state)
                dis_x = ds.array(x, block_size=(vl_block_row_size, vl_block_column_size))
                # Run KMeans using dislib
                start = time.perf_counter()
                kmeans = KMeans(n_clusters=n_clusters, random_state=nr_random_state, id_device=id_device)
                y_pred = kmeans.fit_predict(dis_x).collect()
                end = time.perf_counter()

            # log execution and communication times
            dict_time = kmeans.log_time()
            total_execution_time = end - start
            inter_task_execution_time = dict_time["inter_task_execution_time"]
            df_log_time = pd.read_csv(log_file_path)
            communication_time = df_log_time["communication_time"].mean()
            intra_task_execution_device_func = df_log_time["intra_task_execution_device_func"].mean()
            intra_task_execution_full_func = df_log_time["intra_task_execution_full_func"].mean()


            iteration_experiment_time_end = datetime.datetime.now()
            iteration_experiment_time = (iteration_experiment_time_end - iteration_experiment_time_start).total_seconds()
            print("\nEXPERIMENT ", index+1,"-------------- ITERATION ", i+1, " FINISHED AT "+str(iteration_experiment_time_end)+" (TOTAL TIME: "+str(iteration_experiment_time)+") ------------------\n")

            print("-----------------------------------------")
            print("-------------- RESULTS ------------------")
            print("-----------------------------------------")
            print("Communication time: %f" % (communication_time))
            print("Intra task execution time (device func): %f" % (intra_task_execution_device_func))
            print("Intra task execution time (full func): %f" % (intra_task_execution_full_func))
            print("Inter task execution time: %f" % (inter_task_execution_time))
            print("Total execution time: %f" % (total_execution_time))
            print("-----------------------------------------")

            # Update the array with the values obtained in the current execution
            data.append([id_parameter, total_execution_time, inter_task_execution_time, intra_task_execution_full_func, intra_task_execution_device_func, communication_time])
            
    # Saving experiments results
    df0 = pd.DataFrame(data, columns=["id_parameter", "vl_total_execution_time", "vl_inter_task_execution_time", "vl_intra_task_execution_time_device_func", "vl_intra_task_execution_time_full_func", "vl_communication_time"])    
    df_experiments = df0.groupby(["id_parameter"], as_index=False).mean()
    df_experiments["dt_processing"] = date.today()
    df_experiments.to_csv(dst_path_experiments, index=False)

if __name__ == "__main__":
    main()