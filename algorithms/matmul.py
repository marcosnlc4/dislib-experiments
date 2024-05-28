import csv
import os
import time
import datetime
import dislib as ds
from dislib.data.array import Array
from pycompss.api.api import compss_barrier


def run_matmul(experiment, dst_path_experiments):

    transpose_a = transpose_b = experiment.parameter.bl_transpose_matrix
    
    if experiment.parameter.ds_device == "GPU":

        # execution 1 - extract intra execution times with CUDA events
        result = ds.matmul(experiment.dataset, experiment.dataset, transpose_a, transpose_b, id_device=4, id_parameter=experiment.parameter.id_parameter, nr_algorithm_iteration=experiment.nr_algorithm_iteration)

        # execution 2 - extract total and inter execution times with synchornized function calls
        result = ds.matmul(experiment.dataset, experiment.dataset, transpose_a, transpose_b, id_device=6, id_parameter=experiment.parameter.id_parameter, nr_algorithm_iteration=experiment.nr_algorithm_iteration)

    else:

        # execution 1 - extract intra execution times with synchornized function calls
        result = ds.matmul(experiment.dataset, experiment.dataset, transpose_a, transpose_b, id_device=3, id_parameter=experiment.parameter.id_parameter, nr_algorithm_iteration=experiment.nr_algorithm_iteration)

        # execution 2 - extract total and inter execution times with synchornized function calls
        result = ds.matmul(experiment.dataset, experiment.dataset, transpose_a, transpose_b, id_device=5, id_parameter=experiment.parameter.id_parameter, nr_algorithm_iteration=experiment.nr_algorithm_iteration)

    # execution 3 - extract total execution time for:
    # CPU COLD (id_device = 1, id_cache = 1)
    # CPU HOT (id_device = 1, id_cache = 2)
    # GPU COLD (id_device = 2, id_cache = 1)
    # GPU HOT (id_device = 2, id_cache = 2)
    compss_barrier()
    start_total_execution_time = time.perf_counter()

    result = ds.matmul(experiment.dataset, experiment.dataset, transpose_a, transpose_b, id_device=experiment.parameter.id_device, id_parameter=experiment.parameter.id_parameter, nr_algorithm_iteration=experiment.nr_algorithm_iteration)

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