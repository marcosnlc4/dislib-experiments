import csv
import os
import time
import dislib as ds
import numpy as np
import cupy as cp
from dislib.cluster import KMeans
from pycompss.api.api import compss_barrier

import subprocess as sp
import threading
from threading import Thread , Timer
import sched, time, datetime


dst_path_output = "results/output.txt"
# Path of the "tb_experiments_raw" table - CSV file
dst_path_experiments = "experiments/results/tb_experiments_raw.csv"
# Path of the "tb_memory_monitor" table - CSV file
dst_path_memory_monitor = "experiments/results/tb_memory_monitor.csv"
# Path of the "tb_gpu_monitor" table - CSV file
dst_path_gpu_monitor = "experiments/results/tb_gpu_monitor.csv"

def main():

    # Defining the structure of "tb_experiments_raw" to log time metrics
    header = read_column_names_csv(dst_path_experiments)[0]
    # open "tb_experiments_raw" in the write mode to clean previous results
    f = open(dst_path_experiments, "w", encoding='UTF8', newline='')
    writer = csv.writer(f)
    writer.writerow(header)
    f.close()

    # Defining the structure of "tb_memory_monitor" to log memory metrics
    header = read_column_names_csv(dst_path_memory_monitor)[0]
    # open "tb_memory_monitor" in the write mode to clean previous results
    f = open(dst_path_memory_monitor, "w", encoding='UTF8', newline='')
    writer = csv.writer(f)
    writer.writerow(header)
    f.close()

    # Defining the structure of "tb_gpu_monitor" to log GPU metrics
    header = read_column_names_csv(dst_path_gpu_monitor)[0]
    # open "tb_gpu_monitor" in the write mode to clean previous results
    f = open(dst_path_gpu_monitor, "w", encoding='UTF8', newline='')
    writer = csv.writer(f)
    writer.writerow(header)
    f.close()

# # CLEAN CODE (FOR TRACE GENERATION)
#     input_matrix_rows = 12500000
#     input_matrix_columns = 100
#     start_random_state = 170
#     block_row_size = 12500000#single task
#     # block_row_size = 1250000#625000#416667#multitask
#     block_column_size = 100
#     n_clusters = 10

    # tests
    input_matrix_rows = 3#125000
    input_matrix_columns = 1
    start_random_state = 170
    block_row_size = 1 #single task
    # block_row_size = 15625 #multitask
    block_column_size = 1
    n_clusters = 10

    shape = (input_matrix_rows, input_matrix_columns)
    block_size = (block_row_size, block_column_size)

    # # GPU SINGLE TASK
    # id_device=5
    # id_cache=1
    # GPU MULTI TASK
    # id_device=6 #no profiler
    # id_device=7 #memory profiler
    id_device=8 #cupyx profiler
    id_cache=1

    start = time.perf_counter()
    x = ds.random_array(shape, block_size, random_state=start_random_state, id_device=1, id_cache=1)
    
    # #GPU warmup execution
    # compss_barrier()
    # kmeans = KMeans(n_clusters=n_clusters, random_state=start_random_state, id_device=2, id_cache=1, max_iter=1, tol=0)
    # kmeans.fit(x)
    # compss_barrier()

    nr_iterations = 0

    for i in range(nr_iterations + 1):

        print("\nSTART\n")
        compss_barrier()
        start = time.perf_counter()
        kmeans = KMeans(n_clusters=n_clusters, random_state=start_random_state, id_device=id_device, id_cache=id_cache, max_iter=1, tol=0)
        kmeans.fit(x)
        compss_barrier()
        total_time = time.perf_counter()-start
        print("==== TIME ==== ", total_time)
        file = open(dst_path_output, 'w')
        file.write("==== TIME ==== \n %s" % total_time)
        file.close()
        print("\END\n")


def read_column_names_csv(dst_path):
    with open(dst_path) as csv_file:
        # creating an object of csv reader with the delimiter as ,
        csv_reader = csv.reader(csv_file, delimiter = ',')
    
        # list to store the names of columns
        list_of_column_names = []
    
        # loop to iterate through the rows of csv
        for row in csv_reader:
    
            # adding the first row
            list_of_column_names.append(row)
    
            # breaking the loop after the first iteration itself
            break
    return list_of_column_names

if __name__ == "__main__":
    main()