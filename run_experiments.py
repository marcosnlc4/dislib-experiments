import sys
import os
import time
import datetime
import pandas as pd
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
                                    & (df_parameters["ds_parameter_type"] == "VAR_BLOCK_CAPACITY_SIZE") # 1.1, 1.2, 1.3, 1.4
                                    # & (df_parameters["ds_parameter_type"] == "VAR_PARALLELISM_LEVEL") # 2.1, 2.2
                                    & (df_parameters["ds_parameter_attribute"] == "0.25") # 1.1
                                    # & (df_parameters["ds_parameter_attribute"] == "0.50") # 1.2
                                    # & (df_parameters["ds_parameter_attribute"] == "0.75") # 1.3
                                    # & (df_parameters["ds_parameter_attribute"] == "1.00") # 1.4
                                    # & (df_parameters["ds_parameter_attribute"] == "MIN_INTER_MAX_INTRA") # 2.1
                                    # & (df_parameters["ds_parameter_attribute"] == "MAX_INTER_MIN_INTRA") # 2.2
                                    # & (df_parameters["vl_dataset_memory_size"] == 400) # 2.2.1
                                    # & (df_parameters["vl_dataset_memory_size"] == 400000) # 2.2.2
                                    # & (df_parameters["vl_dataset_memory_size"] == 400000000) # 2.2.3
                                ].sort_values(by=["id_parameter"])


    # Filtering and sorting parameters (TEST)
    # df_parameters = df_parameters[(df_parameters["id_parameter"] == 1) | (df_parameters["id_parameter"] == 2)].sort_values(by=["id_parameter"])
    # df_parameters = df_parameters[(df_parameters["id_parameter"] == 1)]
    # df_parameters = df_parameters[(df_parameters["id_parameter"] == 2)]

    # DataFrame to store final table
    df_experiments = pd.DataFrame(columns=["id_parameter", "vl_total_execution_time", "vl_inter_task_execution_time", "vl_intra_task_execution_time_device_func", "vl_intra_task_execution_time_full_func", "vl_communication_time"])
    
    # array to store temporary results
    data = []

    # Variable to store the current execution to measure the progress of the experiment
    current_execution = 0

    # Iterate over each row of the parameter table CSV file
    for index, row in df_parameters.iterrows():

        current_execution = current_execution + 1

        # Setting parameters variables
        id_parameter = row["id_parameter"]
        cd_parameter = row["cd_parameter"]
        cd_configuration = row["cd_configuration"]
        id_algorithm = row["id_algorithm"]
        ds_algorithm = row["ds_algorithm"]
        id_function = row["id_function"]
        ds_function = row["ds_function"]
        id_device = row["id_device"]
        ds_device = row["ds_device"]
        id_dataset = row["id_dataset"]
        id_resource = row["id_resource"]
        id_parameter_type = row["id_parameter_type"]
        ds_parameter_type = row["ds_parameter_type"]
        ds_parameter_attribute = row["ds_parameter_attribute"] #vl_block_size_percent_dataset = row["vl_block_size_percent_dataset"]
        nr_iterations = row["nr_iterations"]
        vl_grid_row_dimension = row["vl_grid_row_dimension"]
        vl_grid_column_dimension = row["vl_grid_column_dimension"]
        vl_block_row_dimension = row["vl_block_row_dimension"]
        vl_block_column_dimension = row["vl_block_column_dimension"]
        vl_block_memory_size = row["vl_block_memory_size"]
        vl_block_memory_size_percent_cpu = row["vl_block_memory_size_percent_cpu"]
        vl_block_memory_size_percent_gpu = row["vl_block_memory_size_percent_gpu"]
        ds_resource = row["ds_resource"]
        nr_nodes = row["nr_nodes"]
        nr_computing_units_cpu = row["nr_computing_units_cpu"]
        nr_computing_units_gpu = row["nr_computing_units_gpu"]
        vl_memory_size_per_cpu_computing_unit = row["vl_memory_size_per_cpu_computing_unit"]
        vl_memory_size_per_gpu_computing_unit = row["vl_memory_size_per_gpu_computing_unit"]
        ds_dataset = row["ds_dataset"]
        vl_dataset_memory_size = row["vl_dataset_memory_size"]
        ds_data_type = row["ds_data_type"]
        vl_data_type_memory_size = row["vl_data_type_memory_size"]
        vl_dataset_dimension = row["vl_dataset_dimension"]
        vl_dataset_row_dimension = row["vl_dataset_row_dimension"]
        vl_dataset_column_dimension = row["vl_dataset_column_dimension"]
        nr_random_state = row["nr_random_state"]
        n_clusters = 10

        # Execute the experiment for N (nr_iterations) times with the same parameter set
        for i in range(nr_iterations + 1):
            
            execution_progress = round((current_execution/df_parameters.shape[0])*100,2)
            iteration_experiment_time_start = datetime.datetime.now()

            # Without log for the first execution (compiling/warming up device code)
            if i != 0:
                print("\nEXPERIMENT ", id_parameter,"-------------- ITERATION ", i, " STARTED AT "+str(iteration_experiment_time_start)+"------------------\n")
                print("\n@@@@@@ EXECUTION PROGRESS:",str(execution_progress),"%\n")
                print("nodes: ",str(nr_nodes),"\n")
                print("computing_units_cpu: ",str(nr_computing_units_cpu),"\n")
                print("vl_memory_size_per_cpu_computing_unit: ",str(vl_memory_size_per_cpu_computing_unit),"\n")
                print("computing_units_gpu: ",str(nr_computing_units_gpu),"\n")
                print("vl_memory_size_per_gpu_computing_unit: ",str(vl_memory_size_per_gpu_computing_unit),"\n")
                print("ds_device: ",str(ds_device),"\n")
                print("ds_parameter_type: ",str(ds_parameter_type),"\n")
                print("ds_parameter_type: ",str(ds_parameter_type),"\n")
                print("vl_dataset_memory_size: ",str(vl_dataset_memory_size),"\n")
                print("DATASET: vl_dataset_row_size x vl_dataset_column_size: ",str(vl_dataset_row_dimension)," x ",str(vl_dataset_column_dimension),"\n")
                print("GRID: vl_grid_row_size x vl_grid_column_size: ",str(vl_grid_row_dimension)," x ",str(vl_grid_column_dimension),"\n")
                print("BLOCK: vl_block_row_size x vl_block_column_size: ",str(vl_block_row_dimension)," x ",str(vl_block_column_dimension),"\n")
                print("vl_block_memory_size: ",str(vl_block_memory_size),"\n")
                print("vl_block_memory_size_percent_cpu: ",str(vl_block_memory_size_percent_cpu*100),"%\n")
                print("vl_block_memory_size_percent_gpu: ",str(vl_block_memory_size_percent_gpu*100),"%\n")

            if ds_algorithm == "KMEANS":

                # generate and load data into a ds-array
                x, y = make_blobs(n_samples=vl_dataset_row_dimension, n_features=vl_dataset_column_dimension, random_state=nr_random_state)
                dis_x = ds.array(x, block_size=(vl_block_row_dimension, vl_block_column_dimension))

                if ds_device == "GPU":

                    # execution 1 - extract intra execution times with CUDA events
                    kmeans = KMeans(n_clusters=n_clusters, random_state=nr_random_state, id_device=4, max_iter=5, tol=0, arity=48)
                    y_pred = kmeans.fit_predict(dis_x).collect()

                    # execution 2 - extract total and inter execution times with synchornized function calls
                    kmeans = KMeans(n_clusters=n_clusters, random_state=nr_random_state, id_device=6, max_iter=5, tol=0, arity=48)
                    y_pred = kmeans.fit_predict(dis_x).collect()

                else:

                    # execution 1 - extract intra execution times with synchornized function calls
                    kmeans = KMeans(n_clusters=n_clusters, random_state=nr_random_state, id_device=3, max_iter=5, tol=0, arity=48)
                    y_pred = kmeans.fit_predict(dis_x).collect()


                    # execution 2 - extract total and inter execution times with synchornized function calls
                    kmeans = KMeans(n_clusters=n_clusters, random_state=nr_random_state, id_device=5, max_iter=5, tol=0, arity=48)
                    y_pred = kmeans.fit_predict(dis_x).collect()


                # log inter and intra execution times and communication time
                dict_time = kmeans.log_time()
                inter_task_execution_time = dict_time["inter_task_execution_time"]
                df_log_time = pd.read_csv(log_file_path)
                communication_time = df_log_time["communication_time"].mean()
                intra_task_execution_device_func = df_log_time["intra_task_execution_device_func"].mean()
                intra_task_execution_full_func = df_log_time["intra_task_execution_full_func"].mean()

                # execution 3 - extract total execution time for CPU (id_device = 1) and GPU (id_device = 2)
                compss_barrier()
                start = time.perf_counter()
                kmeans = KMeans(n_clusters=n_clusters, random_state=nr_random_state, id_device=id_device, max_iter=5, tol=0, arity=48)
                y_pred = kmeans.fit_predict(dis_x).collect()
                compss_barrier()
                end = time.perf_counter()

                # log total execution time
                total_execution_time = end - start

            # Update result values obtained in the current execution, without the first execution (compiling/warming up device code)
            if i != 0:
            
                iteration_experiment_time_end = datetime.datetime.now()
                iteration_experiment_time = (iteration_experiment_time_end - iteration_experiment_time_start).total_seconds()
                print("\nEXPERIMENT ", index+1,"-------------- ITERATION ", i, " FINISHED AT "+str(iteration_experiment_time_end)+" (TOTAL TIME: "+str(iteration_experiment_time)+") ------------------\n")

                print("-----------------------------------------")
                print("-------------- RESULTS ------------------")
                print("-----------------------------------------")
                print("Communication time: %f" % (communication_time))
                print("Intra task execution time (device func): %f" % (intra_task_execution_device_func))
                print("Intra task execution time (full func): %f" % (intra_task_execution_full_func))
                print("Inter task execution time: %f" % (inter_task_execution_time))
                print("Total execution time: %f" % (total_execution_time))
                print("-----------------------------------------")

                data.append([id_parameter, total_execution_time, inter_task_execution_time, intra_task_execution_full_func, intra_task_execution_device_func, communication_time])

    # Saving experiments results
    df0 = pd.DataFrame(data, columns=["id_parameter", "vl_total_execution_time", "vl_inter_task_execution_time", "vl_intra_task_execution_time_full_func", "vl_intra_task_execution_time_device_func", "vl_communication_time"])
    df_experiments = df0.groupby(["id_parameter"], as_index=False).mean()
    df_experiments["dt_processing"] = datetime.datetime.now()
    df_experiments.to_csv(dst_path_experiments, index=False)

if __name__ == "__main__":
    main()