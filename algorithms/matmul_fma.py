import csv
import os
import time
import datetime
import dislib as ds
from dislib.data.array import Array
from pycompss.api.api import compss_barrier


# def run_matmul_fma(A, C, id_device, id_parameter, nr_algorithm_iteration):
def run_matmul_fma(experiment, dst_path_experiments):

    # Generate empty output matrix C to receive the result of the multiplication
    num_blocks = experiment.parameter.vl_grid_row_dimension
    elems_per_block = experiment.parameter.vl_block_row_dimension

    C = []
    for i in range(num_blocks):
        for l in [C]:
            l.append([])
        # Keep track of blockId to initialize with different random seeds
        bid = 0
        for j in range(num_blocks):
            C[-1].append(ds.generate_block(elems_per_block,
                                        num_blocks,
                                        set_to_zero=True))
    

    if experiment.parameter.ds_device == "GPU":

        # execution 1 - extract intra execution times with CUDA events
        compss_barrier()
        ds.dot(experiment.dataset, experiment.dataset, C, id_device=4, id_parameter=experiment.parameter.id_parameter, nr_algorithm_iteration=experiment.nr_algorithm_iteration)
        compss_barrier()

        # execution 2 - extract total and inter execution times with synchornized function calls
        compss_barrier()
        ds.dot(experiment.dataset, experiment.dataset, C, id_device=6, id_parameter=experiment.parameter.id_parameter, nr_algorithm_iteration=experiment.nr_algorithm_iteration)
        compss_barrier()

    else:

        # execution 1 - extract intra execution times with synchornized function calls
        compss_barrier()
        ds.dot(experiment.dataset, experiment.dataset, C, id_device=3, id_parameter=experiment.parameter.id_parameter, nr_algorithm_iteration=experiment.nr_algorithm_iteration)
        compss_barrier()

        # execution 2 - extract total and inter execution times with synchornized function calls
        compss_barrier()
        ds.dot(experiment.dataset, experiment.dataset, C, id_device=5, id_parameter=experiment.parameter.id_parameter, nr_algorithm_iteration=experiment.nr_algorithm_iteration)
        compss_barrier()

    # execution 3 - extract total execution time for:
    # CPU COLD (id_device = 1, id_cache = 1)
    # CPU HOT (id_device = 1, id_cache = 2)
    # GPU COLD (id_device = 2, id_cache = 1)
    # GPU HOT (id_device = 2, id_cache = 2)
    compss_barrier()
    start_total_execution_time = time.perf_counter()

    ds.dot(experiment.dataset, experiment.dataset, C, id_device=experiment.parameter.id_device, id_parameter=experiment.parameter.id_parameter, nr_algorithm_iteration=experiment.nr_algorithm_iteration)

    compss_barrier()
    end_total_execution_time = time.perf_counter()

    # open the log file in the append mode
    f = open(dst_path_experiments, "a", encoding='UTF8', newline='')

    # create a csv writer
    writer = csv.writer(f)

    # write the time data 
    var_null = 'NULL'
    data = [experiment.parameter.id_parameter, experiment.nr_algorithm_iteration, var_null, var_null, start_total_execution_time, end_total_execution_time, var_null, var_null, var_null, var_null, var_null, var_null, var_null, var_null, var_null, var_null, var_null, var_null, datetime.datetime.now()]
    writer.writerow(data)
    f.close()