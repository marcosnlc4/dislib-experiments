import json
import os
import pickle
import time
import csv

import numpy as np
import datetime

import dislib
from pycompss.api.api import compss_barrier
from pycompss.api.api import compss_wait_on
from pycompss.api.constraint import constraint
from pycompss.api.parameter import COLLECTION_IN, Depth, Type, Cache, Weight
from pycompss.api.task import task
from scipy.sparse import csr_matrix
from sklearn.base import BaseEstimator
from sklearn.metrics import pairwise_distances
from sklearn.metrics.pairwise import paired_distances
from sklearn.utils import check_random_state, validation

from dislib.data.array import Array
from dislib.data.util import encoder_helper, decoder_helper, sync_obj
import dislib.data.util.model as utilmodel

import subprocess as sp
import threading
from threading import Thread , Timer
import sched

# location of the csv log file
dst_path_experiments = os.path.dirname(os.path.abspath(__file__))
dst_path_experiments = dst_path_experiments.replace("/dislib/cluster/kmeans", "/experiments/results/tb_experiments_raw.csv")
dst_path_memory_monitor = os.path.dirname(os.path.abspath(__file__))
dst_path_memory_monitor = dst_path_memory_monitor.replace("/dislib/cluster/kmeans", "/experiments/results/tb_memory_monitor.csv")
dst_path_gpu_monitor = os.path.dirname(os.path.abspath(__file__))
dst_path_gpu_monitor = dst_path_gpu_monitor.replace("/dislib/cluster/kmeans", "/experiments/results/tb_gpu_monitor.csv")
var_null = "NULL"

class KMeans(BaseEstimator):
    """ Perform K-means clustering.

    Parameters
    ----------
    n_clusters : int, optional (default=8)
        The number of clusters to form as well as the number of centroids to
        generate.
    init : {'random', nd-array or sparse matrix}, optional (default='random')
        Method of initialization, defaults to 'random', which generates
        random centers at the beginning.

        If an nd-array or sparse matrix is passed, it should be of shape
        (n_clusters, n_features) and gives the initial centers.
    max_iter : int, optional (default=10)
        Maximum number of iterations of the k-means algorithm for a single run.
    tol : float, optional (default=1e-4)
        Tolerance for accepting convergence.
    arity : int, optional (default=50)
        Arity of the reduction carried out during the computation of the new
        centroids.
    random_state : int or RandomState, optional (default=None)
        Seed or numpy.random.RandomState instance to generate random numbers
        for centroid initialization.
    verbose: boolean, optional (default=False)
        Whether to print progress information.
    id_device: int (default=1)
        Flag to define the device type (CPU: 1, GPU: 2)
    id_cache: int (default=1)
        Flag to define the cache type (COLD: 1, HOT: 2)
    id_parameter: int (default=0)
        Variable to identify the parameter id
    nr_algorithm_iteration: int (default=0)
        Variable to identify the number of the execution of the algorithm


    Attributes
    ----------
    centers : ndarray
        Computed centroids.
    n_iter : int
        Number of iterations performed.

    Examples
    --------
    >>> import dislib as ds
    >>> from dislib.cluster import KMeans
    >>> import numpy as np
    >>>
    >>>
    >>> if __name__ == '__main__':
    >>>     x = np.array([[1, 2], [1, 4], [1, 0], [4, 2], [4, 4], [4, 0]])
    >>>     x_train = ds.array(x, (2, 2))
    >>>     kmeans = KMeans(n_clusters=2, random_state=0)
    >>>     labels = kmeans.fit_predict(x_train)
    >>>     print(labels)
    >>>     x_test = ds.array(np.array([[0, 0], [4, 4]]), (2, 2))
    >>>     labels = kmeans.predict(x_test)
    >>>     print(labels)
    >>>     print(kmeans.centers)
    """

    def __init__(self, n_clusters=8, init='random', max_iter=10, tol=1e-4,
                 arity=50, random_state=None, verbose=False,
                 id_device=1,
                 id_cache=1,
                 id_parameter=0, 
                 nr_algorithm_iteration=0):
        self.n_clusters = n_clusters
        self.max_iter = max_iter
        self.tol = tol
        self.random_state = random_state
        self.arity = arity
        self.verbose = verbose
        self.id_parameter = id_parameter
        self.id_device = id_device
        self.id_cache = id_cache
        self.nr_algorithm_iteration = nr_algorithm_iteration
        self.init = init

    def fit(self, x, y=None):
        """ Compute K-means clustering.

        Parameters
        ----------
        x : ds-array
            Samples to cluster.
        y : ignored
            Not used, present here for API consistency by convention.

        Returns
        -------
        self : KMeans
        """
        self.random_state = check_random_state(self.random_state)
        self._init_centers(x.shape[1], x._sparse)

        old_centers = None
        iteration = 0

        if self.id_device == 1 and self.id_cache == 1:
            partial_sum_func = _partial_sum_cpu_cold
        elif self.id_device == 1 and self.id_cache == 2:
            partial_sum_func = _partial_sum_cpu_hot
        elif self.id_device == 2 and self.id_cache == 1:
            partial_sum_func = _partial_sum_gpu_cold
        elif self.id_device == 2 and self.id_cache == 2:
            partial_sum_func = _partial_sum_gpu_hot
        elif self.id_device == 3 and self.id_cache == 1:
            partial_sum_func = _partial_sum_cpu_cold_intra_time
        elif self.id_device == 3 and self.id_cache == 2:
            partial_sum_func = _partial_sum_cpu_hot_intra_time
        elif self.id_device == 4 and self.id_cache == 1:
            partial_sum_func = _partial_sum_gpu_cold_intra_time
        elif self.id_device == 4 and self.id_cache == 2:
            partial_sum_func = _partial_sum_gpu_hot_intra_time
        elif self.id_device == 5 and self.id_cache == 1:
            partial_sum_func = _partial_sum_gpu_cold_single_task
        elif self.id_device == 6 and self.id_cache == 1:
            partial_sum_func = _partial_sum_gpu_cold_multi_task
        elif self.id_device == 7 and self.id_cache == 1:
            partial_sum_func = _partial_sum_gpu_cold_multi_task_memory
        elif self.id_device == 8 and self.id_cache == 1:
            partial_sum_func = _partial_sum_gpu_cold_multi_task_profile
        else:
            raise ValueError("Error. Invalid combination id_device+id_cache")

        while not self._converged(old_centers, iteration):
            old_centers = self.centers.copy()
            partials = []

            if self.id_device == 3 or self.id_device == 4 or self.id_device == 7:
                nr_task = 0
                for row in x._iterator(axis=0):
                    partial = partial_sum_func(row._blocks, old_centers, self.id_parameter, self.nr_algorithm_iteration, iteration, nr_task)
                    partials.append(partial)
                    nr_task += 1
            # elif self.id_device == 6:
            #     import cupy as cp
            #     cp.cuda.Stream.null.synchronize() # Synchronize to ensure operations are complete
            else:
                for row in x._iterator(axis=0):
                    partial = partial_sum_func(row._blocks, old_centers)
                    partials.append(partial)
    
            self._recompute_centers(partials)
            iteration += 1

        self.n_iter = iteration

        return self

    def fit_predict(self, x, y=None):
        """ Compute cluster centers and predict cluster index for each sample.

        Parameters
        ----------
        x : ds-array
            Samples to cluster.
        y : ignored
            Not used, present here for API consistency by convention.

        Returns
        -------
        labels : ds-array, shape=(n_samples, 1)
            Index of the cluster each sample belongs to.
        """

        self.fit(x)
        return self.predict(x)

    def predict(self, x):
        """ Predict the closest cluster each sample in the data belongs to.

        Parameters
        ----------
        x : ds-array
            New data to predict.

        Returns
        -------
        labels : ds-array, shape=(n_samples, 1)
            Index of the cluster each sample belongs to.
        """
        validation.check_is_fitted(self, 'centers')
        blocks = []

        for row in x._iterator(axis=0):
            blocks.append([_predict(row._blocks, self.centers)])

        return Array(blocks=blocks, top_left_shape=(x._top_left_shape[0], 1),
                     reg_shape=(x._reg_shape[0], 1), shape=(x.shape[0], 1),
                     sparse=False)

    def _converged(self, old_centers, iteration):
        if old_centers is None:
            return False

        diff = np.sum(paired_distances(self.centers, old_centers))

        if self.verbose:
            print("Iteration %s - Convergence crit. = %s" % (iteration, diff))

        return diff < self.tol ** 2 or iteration >= self.max_iter

    def _recompute_centers(self, partials):
        while len(partials) > 1:
            partials_subset = partials[:self.arity]
            partials = partials[self.arity:]
            partials.append(_merge(*partials_subset))

        partials = compss_wait_on(partials)

        for idx, sum_ in enumerate(partials[0]):
            if sum_[1] != 0:
                self.centers[idx] = sum_[0] / sum_[1]

    def _init_centers(self, n_features, sparse):
        if isinstance(self.init, np.ndarray) \
                or isinstance(self.init, csr_matrix):
            if self.init.shape != (self.n_clusters, n_features):
                raise ValueError("Init array must be of shape (n_clusters, "
                                 "n_features)")
            self.centers = self.init.copy()
        elif self.init == "random":
            shape = (self.n_clusters, n_features)
            self.centers = self.random_state.random_sample(shape)

            if sparse:
                self.centers = csr_matrix(self.centers)
        else:
            raise ValueError("Init must be random, an nd-array, "
                             "or an sp.matrix")

    def save_model(self, filepath, overwrite=True, save_format="json"):
        """Saves a model to a file.
        The model is synchronized before saving and can be reinstantiated in
        the exact same state, without any of the code used for model
        definition or fitting.
        Parameters
        ----------
        filepath : str
            Path where to save the model
        overwrite : bool, optional (default=True)
            Whether any existing model at the target
            location should be overwritten.
        save_format : str, optional (default='json)
            Format used to save the models.
        Examples
        --------
        >>> from dislib.cluster import KMeans
        >>> import numpy as np
        >>> import dislib as ds
        >>> x = np.array([[1, 2], [1, 4], [1, 0], [4, 2], [4, 4], [4, 0]])
        >>> x_train = ds.array(x, (2, 2))
        >>> model = KMeans(n_clusters=2, random_state=0)
        >>> model.fit(x_train)
        >>> model.save_model('/tmp/model')
        >>> loaded_model = KMeans()
        >>> loaded_model.load_model('/tmp/model')
        >>> x_test = ds.array(np.array([[0, 0], [4, 4]]), (2, 2))
        >>> model_pred = model.predict(x_test)
        >>> loaded_model_pred = loaded_model.predict(x_test)
        >>> assert np.allclose(model_pred.collect(),
        >>> loaded_model_pred.collect())
        """

        # Check overwrite
        if not overwrite and os.path.isfile(filepath):
            return

        sync_obj(self.__dict__)
        model_metadata = self.__dict__
        model_metadata["model_name"] = "kmeans"

        # Save model
        if save_format == "json":
            with open(filepath, "w") as f:
                json.dump(model_metadata, f, default=_encode_helper)
        elif save_format == "cbor":
            if utilmodel.cbor2 is None:
                raise ModuleNotFoundError("No module named 'cbor2'")
            with open(filepath, "wb") as f:
                utilmodel.cbor2.dump(model_metadata, f,
                                     default=_encode_helper_cbor)
        elif save_format == "pickle":
            with open(filepath, "wb") as f:
                pickle.dump(model_metadata, f)
        else:
            raise ValueError("Wrong save format.")

    def load_model(self, filepath, load_format="json"):
        """Loads a model from a file.
        The model is reinstantiated in the exact same state in which it was
        saved, without any of the code used for model definition or fitting.
        Parameters
        ----------
        filepath : str
            Path of the saved the model
        load_format : str, optional (default='json')
            Format used to load the model.
        Examples
        --------
        >>> from dislib.cluster import KMeans
        >>> import numpy as np
        >>> import dislib as ds
        >>> x = np.array([[1, 2], [1, 4], [1, 0], [4, 2], [4, 4], [4, 0]])
        >>> x_train = ds.array(x, (2, 2))
        >>> model = KMeans(n_clusters=2, random_state=0)
        >>> model.fit(x_train)
        >>> model.save_model('/tmp/model')
        >>> loaded_model = KMeans()
        >>> loaded_model.load_model('/tmp/model')
        >>> x_test = ds.array(np.array([[0, 0], [4, 4]]), (2, 2))
        >>> model_pred = model.predict(x_test)
        >>> loaded_model_pred = loaded_model.predict(x_test)
        >>> assert np.allclose(model_pred.collect(),
        >>> loaded_model_pred.collect())
        """
        # Load model
        if load_format == "json":
            with open(filepath, "r") as f:
                model_metadata = json.load(f, object_hook=_decode_helper)
        elif load_format == "cbor":
            if utilmodel.cbor2 is None:
                raise ModuleNotFoundError("No module named 'cbor2'")
            with open(filepath, "rb") as f:
                model_metadata = utilmodel.cbor2.\
                    load(f, object_hook=_decode_helper_cbor)
        elif load_format == "pickle":
            with open(filepath, "rb") as f:
                model_metadata = pickle.load(f)
        else:
            raise ValueError("Wrong load format.")

        for key, val in model_metadata.items():
            setattr(self, key, val)


def _encode_helper_cbor(encoder, obj):
    encoder.encode(_encode_helper(obj))


def _encode_helper(obj):
    encoded = encoder_helper(obj)
    if encoded is not None:
        return encoded


def _decode_helper_cbor(decoder, obj):
    """Special decoder wrapper for dislib using cbor2."""
    return _decode_helper(obj)


def _decode_helper(obj):
    if isinstance(obj, dict) and "class_name" in obj:
        class_name = obj["class_name"]
        decoded = decoder_helper(class_name, obj)
        if decoded is not None:
            return decoded
        elif class_name == "RandomState":
            random_state = np.random.RandomState()
            random_state.set_state(_decode_helper(obj["items"]))
            return random_state
    return obj

@constraint(computing_units="${ComputingUnitsCPU}")
@task(blocks={Type: COLLECTION_IN, Depth: 2, Cache: False}, centers={Cache: False},
      returns=np.array, cache_returns=False)
def _partial_sum_cpu_cold(blocks, centers):
    partials = np.zeros((centers.shape[0], 2), dtype=object)
    arr = Array._merge_blocks(blocks)

    close_centers = pairwise_distances(arr, centers).argmin(axis=1)

    for center_idx, _ in enumerate(centers):
        indices = np.argwhere(close_centers == center_idx).flatten()
        partials[center_idx][0] = np.sum(arr[indices], axis=0)
        partials[center_idx][1] = indices.shape[0]

    return partials

@constraint(computing_units="${ComputingUnitsCPU}")
@task(blocks={Type: COLLECTION_IN, Depth: 2, Cache: False}, centers={Cache: False},
      returns=np.array, cache_returns=False)
def _partial_sum_cpu_cold_intra_time(blocks, centers, id_parameter, nr_algorithm_iteration, iteration, row):
    # open the log file in the append mode
    f = open(dst_path_experiments, "a", encoding='UTF8', newline='')

    # create a csv writer
    writer = csv.writer(f)

    # Measure additional time 1
    start_additional_time_1 = time.perf_counter()
    partials = np.zeros((centers.shape[0], 2), dtype=object)
    arr = Array._merge_blocks(blocks)
    end_additional_time_1 = time.perf_counter()

    # Measure intra task execution time (device function) 
    start_intra_device = time.perf_counter()
    close_centers = pairwise_distances(arr, centers).argmin(axis=1)
    end_intra_device = time.perf_counter()
    intra_task_execution_device_func = end_intra_device - start_intra_device

    # Measure additional time 2
    start_additional_time_2 = time.perf_counter()
    for center_idx, _ in enumerate(centers):
        indices = np.argwhere(close_centers == center_idx).flatten()
        partials[center_idx][0] = np.sum(arr[indices], axis=0)
        partials[center_idx][1] = indices.shape[0]
    end_additional_time_2 = time.perf_counter()

    # write the time data
    data = [id_parameter, nr_algorithm_iteration, iteration, row, var_null, var_null, var_null, var_null, var_null, intra_task_execution_device_func, 0, 0, 0, 0, start_additional_time_1, end_additional_time_1, start_additional_time_2, end_additional_time_2, datetime.datetime.now()]
    writer.writerow(data)
    f.close()

    return partials

@constraint(computing_units="${ComputingUnitsCPU}")
@task(blocks={Type: COLLECTION_IN, Depth: 2, Cache: True}, centers={Cache: False},
      returns=np.array, cache_returns=False)
def _partial_sum_cpu_hot(blocks, centers):
    partials = np.zeros((centers.shape[0], 2), dtype=object)
    arr = Array._merge_blocks(blocks)

    close_centers = pairwise_distances(arr, centers).argmin(axis=1)

    for center_idx, _ in enumerate(centers):
        indices = np.argwhere(close_centers == center_idx).flatten()
        partials[center_idx][0] = np.sum(arr[indices], axis=0)
        partials[center_idx][1] = indices.shape[0]

    return partials

@constraint(computing_units="${ComputingUnitsCPU}")
@task(blocks={Type: COLLECTION_IN, Depth: 2, Cache: True}, centers={Cache: False},
      returns=np.array, cache_returns=False)
def _partial_sum_cpu_hot_intra_time(blocks, centers, id_parameter, nr_algorithm_iteration, iteration, row):
    # open the log file in the append mode
    f = open(dst_path_experiments, "a", encoding='UTF8', newline='')

    # create a csv writer
    writer = csv.writer(f)

    # Measure additional time 1
    start_additional_time_1 = time.perf_counter()
    partials = np.zeros((centers.shape[0], 2), dtype=object)
    arr = Array._merge_blocks(blocks)
    end_additional_time_1 = time.perf_counter()

    # Measure intra task execution time (device function) 
    start_intra_device = time.perf_counter()
    close_centers = pairwise_distances(arr, centers).argmin(axis=1)
    end_intra_device = time.perf_counter()
    intra_task_execution_device_func = end_intra_device - start_intra_device

    # Measure additional time 2
    start_additional_time_2 = time.perf_counter()
    for center_idx, _ in enumerate(centers):
        indices = np.argwhere(close_centers == center_idx).flatten()
        partials[center_idx][0] = np.sum(arr[indices], axis=0)
        partials[center_idx][1] = indices.shape[0]
    end_additional_time_2 = time.perf_counter()

    # write the time data
    data = [id_parameter, nr_algorithm_iteration, iteration, row, var_null, var_null, var_null, var_null, var_null, intra_task_execution_device_func, 0, 0, 0, 0, start_additional_time_1, end_additional_time_1, start_additional_time_2, end_additional_time_2, datetime.datetime.now()]
    writer.writerow(data)
    f.close()

    return partials

#####################################
# START CODE TEST SINGLE/MULTI GPU
#####################################
@constraint(processors=[
                {"processorType": "CPU", "computingUnits": "${ComputingUnitsCPU}"},
                {"processorType": "GPU", "computingUnits": "${ComputingUnitsGPU}"},
            ])
@task(blocks={Type: COLLECTION_IN, Depth: 2, Cache: False}, centers={Cache: False},
      returns=np.array, cache_returns=False)
def _partial_sum_gpu_cold_single_task(blocks, centers):
    import cupy as cp

    partials = np.zeros((centers.shape[0], 2), dtype=object)
    if len(blocks[0]) == 1:
        arr = blocks[0][0]
    else:
        arr = Array._merge_blocks(blocks)
    arr_gpu = cp.asarray(arr).astype(cp.float32)
    centers_gpu = cp.asarray(centers).astype(cp.float32)
    arr = None

    close_centers_gpu = cp.argmin(distance_gpu(arr_gpu, centers_gpu), axis=1)
    arr = cp.asnumpy(arr_gpu)
    arr_gpu, centers_gpu = None, None

    close_centers = cp.asnumpy(close_centers_gpu)

    for center_idx, _ in enumerate(centers):
        indices = np.argwhere(close_centers == center_idx).flatten()
        partials[center_idx][0] = np.sum(arr[indices], axis=0)
        partials[center_idx][1] = indices.shape[0]

    return partials

@constraint(processors=[
                {"processorType": "CPU", "computingUnits": "${ComputingUnitsCPU}"}
            ])
@task(blocks={Type: COLLECTION_IN, Depth: 2, Cache: False}, centers={Cache: False},
      returns=np.array, cache_returns=False)
def _partial_sum_gpu_cold_multi_task(blocks, centers):
    import cupy as cp
    # Automatically select the least saturated GPU
    # select_gpu()

    partials = np.zeros((centers.shape[0], 2), dtype=object)
    if len(blocks[0]) == 1:
        arr = blocks[0][0]
    else:
        arr = Array._merge_blocks(blocks)
    arr_gpu = cp.asarray(arr).astype(cp.float32)
    centers_gpu = cp.asarray(centers).astype(cp.float32)
    arr = None

    close_centers_gpu = cp.argmin(distance_gpu(arr_gpu, centers_gpu), axis=1)
    arr = cp.asnumpy(arr_gpu)
    arr_gpu, centers_gpu = None, None

    close_centers = cp.asnumpy(close_centers_gpu)

    for center_idx, _ in enumerate(centers):
        indices = np.argwhere(close_centers == center_idx).flatten()
        partials[center_idx][0] = np.sum(arr[indices], axis=0)
        partials[center_idx][1] = indices.shape[0]

    return partials

####################################################
# MEASURE GPU STATISTICS WITH NVIDIA-SMI
####################################################
@constraint(processors=[
                {"processorType": "CPU", "computingUnits": "${ComputingUnitsCPU}"}
            ])
@task(blocks={Type: COLLECTION_IN, Depth: 2, Cache: False}, centers={Cache: False},
      returns=np.array, cache_returns=False)
def _partial_sum_gpu_cold_multi_task_memory(blocks, centers, id_parameter, nr_algorithm_iteration, iteration, row):
    
    #start the thread to log GPU statistics every 1ns 
    thread = RepeatEvery(0.000000000001, monitor_gpu)
    thread.start()
    
    import cupy as cp

    # open the log file in the append mode
    f = open(dst_path_experiments, "a", encoding='UTF8', newline='')

    # create a csv writer
    writer = csv.writer(f)

    # creating CUDA events for intra device time measurement
    start_gpu_intra_device = cp.cuda.Event()
    end_gpu_intra_device = cp.cuda.Event()

    # Measure additional time 1
    start_additional_time_1 = time.perf_counter()
    partials = np.zeros((centers.shape[0], 2), dtype=object)
    if len(blocks[0]) == 1:
        arr = blocks[0][0]
    else:
        arr = Array._merge_blocks(blocks)
    end_additional_time_1 = time.perf_counter()

    # Measure communication time 1
    start_communication_time_1 = time.perf_counter()
    arr_gpu = cp.asarray(arr).astype(cp.float32)
    centers_gpu = cp.asarray(centers).astype(cp.float32)
    end_communication_time_1 = time.perf_counter()
    arr = None

    # Measure intra task execution time (device function) 
    start_gpu_intra_device.record()
    close_centers_gpu = cp.argmin(distance_gpu(arr_gpu, centers_gpu), axis=1)
    end_gpu_intra_device.record()
    end_gpu_intra_device.synchronize()
    intra_task_execution_device_func = cp.cuda.get_elapsed_time(start_gpu_intra_device, end_gpu_intra_device)*1e-3

    # Measure communication time 2
    start_communication_time_2 = time.perf_counter()
    arr = cp.asnumpy(arr_gpu)
    close_centers = cp.asnumpy(close_centers_gpu)
    end_communication_time_2 = time.perf_counter()

    # Measure additional time 2
    start_additional_time_2 = time.perf_counter()
    arr_gpu, centers_gpu = None, None

    for center_idx, _ in enumerate(centers):
        indices = np.argwhere(close_centers == center_idx).flatten()
        partials[center_idx][0] = np.sum(arr[indices], axis=0)
        partials[center_idx][1] = indices.shape[0]
    end_additional_time_2 = time.perf_counter()

    # write the time data
    data = [id_parameter, nr_algorithm_iteration, iteration, row, var_null, var_null, var_null, var_null, var_null, intra_task_execution_device_func, start_communication_time_1, end_communication_time_1, start_communication_time_2, end_communication_time_2, start_additional_time_1, end_additional_time_1, start_additional_time_2, end_additional_time_2, datetime.datetime.now()]
    writer.writerow(data)
    f.close()
    
    # last sync to ensure that all operations in the default stream are finished and stop the thread
    cp.cuda.stream.Stream.null.synchronize()
    thread.stop()

    return partials

####################################################
# MEASURE CUPY MEMORY POOL USAGE
####################################################
# @constraint(processors=[
#                 {"processorType": "CPU", "computingUnits": "${ComputingUnitsCPU}"}
#             ])
# @task(blocks={Type: COLLECTION_IN, Depth: 2, Cache: False}, centers={Cache: False},
#       returns=np.array, cache_returns=False)
# def _partial_sum_gpu_cold_multi_task_memory(blocks, centers, id_parameter, nr_algorithm_iteration, iteration, row):
#     import cupy as cp

#     # open the log file in the append mode
#     f = open(dst_path_experiments, "a", encoding='UTF8', newline='')
#     f2 = open(dst_path_memory_monitor, "a", encoding='UTF8', newline='')

#     # create a csv writer
#     writer = csv.writer(f)
#     writer2 = csv.writer(f2)

#     # creating CUDA events for intra device time measurement
#     start_gpu_intra_device = cp.cuda.Event()
#     end_gpu_intra_device = cp.cuda.Event()

#     # Measure additional time 1
#     start_additional_time_1 = time.perf_counter()
#     partials = np.zeros((centers.shape[0], 2), dtype=object)
#     if len(blocks[0]) == 1:
#         arr = blocks[0][0]
#     else:
#         arr = Array._merge_blocks(blocks)
#     end_additional_time_1 = time.perf_counter()

#     # Measure communication time 1
#     start_communication_time_1 = time.perf_counter()
#     arr_gpu = cp.asarray(arr).astype(cp.float32)
#     centers_gpu = cp.asarray(centers).astype(cp.float32)
#     end_communication_time_1 = time.perf_counter()
#     arr = None

#     # Measure intra task execution time (device function) 
#     start_gpu_intra_device.record()
#     close_centers_gpu = cp.argmin(distance_gpu(arr_gpu, centers_gpu), axis=1)
#     end_gpu_intra_device.record()
#     end_gpu_intra_device.synchronize()
#     intra_task_execution_device_func = cp.cuda.get_elapsed_time(start_gpu_intra_device, end_gpu_intra_device)*1e-3

#     # Measure communication time 2
#     start_communication_time_2 = time.perf_counter()
#     arr = cp.asnumpy(arr_gpu)
#     close_centers = cp.asnumpy(close_centers_gpu)
#     end_communication_time_2 = time.perf_counter()

#     # Measure additional time 2
#     start_additional_time_2 = time.perf_counter()
#     arr_gpu, centers_gpu = None, None

#     memory_pool = cp.get_default_memory_pool()
#     # Calculate the peak memory usage
#     peak_memory = memory_pool.total_bytes()  # Total allocated memory
#     used_memory = memory_pool.used_bytes()   # Currently used memory
#     # Convert bytes to MB
#     peak_memory_mb = peak_memory / (1024 ** 2)
#     used_memory_mb = used_memory / (1024 ** 2)

#     for center_idx, _ in enumerate(centers):
#         indices = np.argwhere(close_centers == center_idx).flatten()
#         partials[center_idx][0] = np.sum(arr[indices], axis=0)
#         partials[center_idx][1] = indices.shape[0]
#     end_additional_time_2 = time.perf_counter()

#     # write the time data
#     data = [id_parameter, nr_algorithm_iteration, iteration, row, var_null, var_null, var_null, var_null, var_null, intra_task_execution_device_func, start_communication_time_1, end_communication_time_1, start_communication_time_2, end_communication_time_2, start_additional_time_1, end_additional_time_1, start_additional_time_2, end_additional_time_2, datetime.datetime.now()]
#     writer.writerow(data)
#     f.close()

#     # write the memory data
#     data2 = [used_memory_mb, peak_memory_mb, datetime.datetime.now()]
#     writer2.writerow(data2)
#     f2.close()

#     return partials

####################################################
# MEASURE CUPY MEMORY POOL USAGE PER LINE (LINE PROFILER HOOK)
####################################################
# @constraint(processors=[
#                 {"processorType": "CPU", "computingUnits": "${ComputingUnitsCPU}"}
#             ])
# @task(blocks={Type: COLLECTION_IN, Depth: 2, Cache: False}, centers={Cache: False},
#       returns=np.array, cache_returns=False)
# def _partial_sum_gpu_cold_multi_task_hook(blocks, centers):
#     import cupy as cp
#     from cupy.cuda import memory_hooks
#     import io
#     from contextlib import redirect_stdout
#     dst_path_results = os.path.dirname(os.path.abspath(__file__))
#     dst_path_results = dst_path_results.replace("/dislib/cluster/kmeans", "results/hook_output.txt")

#     # Automatically select the least saturated GPU
#     # select_gpu()

#     partials = np.zeros((centers.shape[0], 2), dtype=object)
#     if len(blocks[0]) == 1:
#         arr = blocks[0][0]
#     else:
#         arr = Array._merge_blocks(blocks)

#     hook = memory_hooks.LineProfileHook()
#     with hook:
#         arr_gpu = cp.asarray(arr).astype(cp.float32)
#         centers_gpu = cp.asarray(centers).astype(cp.float32)
#         arr = None

#         close_centers_gpu = cp.argmin(distance_gpu(arr_gpu, centers_gpu), axis=1)
#         arr = cp.asnumpy(arr_gpu)
#         arr_gpu, centers_gpu = None, None

#         close_centers = cp.asnumpy(close_centers_gpu)

#     f = io.StringIO()
#     with redirect_stdout(f):
#         hook.print_report()

#     report_output = f.getvalue()
#     file = open(dst_path_results, 'w')
#     file.write(report_output)
#     file.close()

#     for center_idx, _ in enumerate(centers):
#         indices = np.argwhere(close_centers == center_idx).flatten()
#         partials[center_idx][0] = np.sum(arr[indices], axis=0)
#         partials[center_idx][1] = indices.shape[0]

#     return partials

@constraint(processors=[
                {"processorType": "CPU", "computingUnits": "${ComputingUnitsCPU}"}
            ])
@task(blocks={Type: COLLECTION_IN, Depth: 2, Cache: False}, centers={Cache: False},
      returns=np.array, cache_returns=False)
def _partial_sum_gpu_cold_multi_task_profile(blocks, centers):
    import cupy as cp
    import cupyx as cpx

    partials = np.zeros((centers.shape[0], 2), dtype=object)
    if len(blocks[0]) == 1:
        arr = blocks[0][0]
    else:
        arr = Array._merge_blocks(blocks)
    
    with cpx.profiler.profile():

        arr_gpu = cp.asarray(arr).astype(cp.float32)
        centers_gpu = cp.asarray(centers).astype(cp.float32)
        arr = None

        close_centers_gpu = cp.argmin(distance_gpu(arr_gpu, centers_gpu), axis=1)
        arr = cp.asnumpy(arr_gpu)
        arr_gpu, centers_gpu = None, None

        close_centers = cp.asnumpy(close_centers_gpu)

    for center_idx, _ in enumerate(centers):
        indices = np.argwhere(close_centers == center_idx).flatten()
        partials[center_idx][0] = np.sum(arr[indices], axis=0)
        partials[center_idx][1] = indices.shape[0]
        
    return partials

def monitor_gpu():
    output_to_list = lambda x: x.decode('ascii').split('\n')[:-1]
    ACCEPTABLE_AVAILABLE_MEMORY = 1024
    COMMAND = "nvidia-smi --query-gpu=index,memory.used,utilization.gpu,timestamp --format=csv"
    try:
        memory_use_info = output_to_list(sp.check_output(COMMAND.split(),stderr=sp.STDOUT))[1:]
    except sp.CalledProcessError as e:
        raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
    gpu_index_values = [x.split()[0].replace(',', '') for i, x in enumerate(memory_use_info)]
    memory_use_values = [int(x.split()[1]) for i, x in enumerate(memory_use_info)]
    gpu_use_values = [int(x.split()[3]) for i, x in enumerate(memory_use_info)]
    date_values = [x.split()[5] for i, x in enumerate(memory_use_info)]
    time_values = [x.split()[6] for i, x in enumerate(memory_use_info)]
    dt_processing = date_values[0] + ' ' +  time_values[0]
    dt_processing_f = datetime.datetime.strptime(dt_processing, "%Y/%m/%d %H:%M:%S.%f")

    f = open(dst_path_gpu_monitor, "a", encoding='UTF8', newline='')

    writer = csv.writer(f)
    print(gpu_index_values[0], memory_use_values[0], gpu_use_values[0], dt_processing_f)
    data = [gpu_index_values[0], memory_use_values[0], gpu_use_values[0], dt_processing_f]
    writer.writerow(data)
    f.close()

class RepeatEvery(threading.Thread):
    def __init__(self, interval, func, *args, **kwargs):
        threading.Thread.__init__(self)
        self.interval = interval  # seconds between calls
        self.func = func          # function to call
        self.args = args          # optional positional argument(s) for call
        self.kwargs = kwargs      # optional keyword argument(s) for call
        self.runable = True
    def run(self):
        while self.runable:
            try:
                self.func(*self.args, **self.kwargs)  # Call the function with arguments
                time.sleep(self.interval)             # Wait for the interval
            except Exception as e:
                print(f"Exception in thread: {e}")
                self.runable = False  # Stop the loop if there is an exception
    def stop(self):
        self.runable = False


# Function to get available memory on a given GPU device
def get_gpu_memory_info(gpu_id):
    import cupy as cp
    with cp.cuda.Device(gpu_id):
        mem_info = cp.cuda.Device(gpu_id).mem_info
        free_mem = mem_info[0]  # Free memory
        total_mem = mem_info[1]  # Total memory
        return free_mem, total_mem

# Function to select the GPU with enough available memory
def select_gpu(threshold_ratio=0.9):
    import cupy as cp
    # Check current GPU memory
    free_mem_current, total_mem_current = get_gpu_memory_info(cp.cuda.Device().id)
    utilization_current = 1 - free_mem_current / total_mem_current

    time_out_threshold=0

    for i in range(cp.cuda.runtime.getDeviceCount()):
        if i != cp.cuda.Device().id:
            # If current GPU ID is saturated, check if the next GPU ID in the list of GPUs is free
            if utilization_current > threshold_ratio:
                print(f"Switching to GPU {i} as GPU {cp.cuda.Device().id} is saturated")
                cp.cuda.Device(i).use()
                select_gpu()
            else:
                break

        # If all GPUs are fully used check again all available GPUs until one gets free or the threshold criteria is reached
        if i == cp.cuda.runtime.getDeviceCount():
            # Verification to avoid infinity loop (check all GPUs for 10 times and if none gets free, abort the execution)
            if time_out_threshold < 10:
                i = 0
                time_out_threshold += 1
            else:
                raise MemoryError("The memory of all GPUs are fully used. Abort to avoid out of memory")

#####################################
# END CODE TEST SINGLE/MULTI GPU
#####################################

@constraint(processors=[
                {"processorType": "CPU", "computingUnits": "${ComputingUnitsCPU}"},
                {"processorType": "GPU", "computingUnits": "${ComputingUnitsGPU}"},
            ])
@task(blocks={Type: COLLECTION_IN, Depth: 2, Cache: False}, centers={Cache: False},
      returns=np.array, cache_returns=False)
def _partial_sum_gpu_cold(blocks, centers):
    import cupy as cp

    partials = np.zeros((centers.shape[0], 2), dtype=object)
    if len(blocks[0]) == 1:
        arr = blocks[0][0]
    else:
        arr = Array._merge_blocks(blocks)
    arr_gpu = cp.asarray(arr).astype(cp.float32)
    centers_gpu = cp.asarray(centers).astype(cp.float32)
    arr = None

    close_centers_gpu = cp.argmin(distance_gpu(arr_gpu, centers_gpu), axis=1)
    arr = cp.asnumpy(arr_gpu)
    arr_gpu, centers_gpu = None, None

    close_centers = cp.asnumpy(close_centers_gpu)

    for center_idx, _ in enumerate(centers):
        indices = np.argwhere(close_centers == center_idx).flatten()
        partials[center_idx][0] = np.sum(arr[indices], axis=0)
        partials[center_idx][1] = indices.shape[0]

    return partials

@constraint(processors=[
                {"processorType": "CPU", "computingUnits": "${ComputingUnitsCPU}"},
                {"processorType": "GPU", "computingUnits": "${ComputingUnitsGPU}"},
            ])
@task(blocks={Type: COLLECTION_IN, Depth: 2, Cache: True}, centers={Cache: False},
      returns=np.array, cache_returns=False)
def _partial_sum_gpu_hot(blocks, centers):
    import cupy as cp

    partials = np.zeros((centers.shape[0], 2), dtype=object)
    if len(blocks[0]) == 1:
        arr = blocks[0][0]
    else:
        arr = Array._merge_blocks(blocks)
    arr_gpu = arr.astype(cp.float32)
    centers_gpu = cp.asarray(centers).astype(cp.float32)
    arr = None

    close_centers_gpu = cp.argmin(distance_gpu(arr_gpu, centers_gpu), axis=1)
    arr = cp.asnumpy(arr_gpu)
    arr_gpu, centers_gpu = None, None

    close_centers = cp.asnumpy(close_centers_gpu)

    for center_idx, _ in enumerate(centers):
        indices = np.argwhere(close_centers == center_idx).flatten()
        partials[center_idx][0] = np.sum(arr[indices], axis=0)
        partials[center_idx][1] = indices.shape[0]

    return partials


@constraint(processors=[
                {"processorType": "CPU", "computingUnits": "${ComputingUnitsCPU}"},
                {"processorType": "GPU", "computingUnits": "${ComputingUnitsGPU}"},
            ])
@task(blocks={Type: COLLECTION_IN, Depth: 2, Cache: False}, centers={Cache: False},
      returns=np.array, cache_returns=False)
def _partial_sum_gpu_cold_intra_time(blocks, centers, id_parameter, nr_algorithm_iteration, iteration, row):
    import cupy as cp

    # open the log file in the append mode
    f = open(dst_path_experiments, "a", encoding='UTF8', newline='')

    # create a csv writer
    writer = csv.writer(f)

    # creating CUDA events for intra device time measurement
    start_gpu_intra_device = cp.cuda.Event()
    end_gpu_intra_device = cp.cuda.Event()

    # Measure additional time 1
    start_additional_time_1 = time.perf_counter()
    partials = np.zeros((centers.shape[0], 2), dtype=object)
    if len(blocks[0]) == 1:
        arr = blocks[0][0]
    else:
        arr = Array._merge_blocks(blocks)
    end_additional_time_1 = time.perf_counter()

    # Measure communication time 1
    start_communication_time_1 = time.perf_counter()
    arr_gpu = cp.asarray(arr).astype(cp.float32)
    centers_gpu = cp.asarray(centers).astype(cp.float32)
    end_communication_time_1 = time.perf_counter()
    arr = None

    # Measure intra task execution time (device function) 
    start_gpu_intra_device.record()
    close_centers_gpu = cp.argmin(distance_gpu(arr_gpu, centers_gpu), axis=1)
    end_gpu_intra_device.record()
    end_gpu_intra_device.synchronize()
    intra_task_execution_device_func = cp.cuda.get_elapsed_time(start_gpu_intra_device, end_gpu_intra_device)*1e-3

    # Measure communication time 2
    start_communication_time_2 = time.perf_counter()
    arr = cp.asnumpy(arr_gpu)
    close_centers = cp.asnumpy(close_centers_gpu)
    end_communication_time_2 = time.perf_counter()

    # Measure additional time 2
    start_additional_time_2 = time.perf_counter()
    arr_gpu, centers_gpu = None, None

    for center_idx, _ in enumerate(centers):
        indices = np.argwhere(close_centers == center_idx).flatten()
        partials[center_idx][0] = np.sum(arr[indices], axis=0)
        partials[center_idx][1] = indices.shape[0]
    end_additional_time_2 = time.perf_counter()

    # write the time data
    data = [id_parameter, nr_algorithm_iteration, iteration, row, var_null, var_null, var_null, var_null, var_null, intra_task_execution_device_func, start_communication_time_1, end_communication_time_1, start_communication_time_2, end_communication_time_2, start_additional_time_1, end_additional_time_1, start_additional_time_2, end_additional_time_2, datetime.datetime.now()]
    writer.writerow(data)
    f.close()

    return partials

@constraint(processors=[
                {"processorType": "CPU", "computingUnits": "${ComputingUnitsCPU}"},
                {"processorType": "GPU", "computingUnits": "${ComputingUnitsGPU}"},
            ])
@task(blocks={Type: COLLECTION_IN, Depth: 2, Cache: True}, centers={Cache: False},
      returns=np.array, cache_returns=False)
def _partial_sum_gpu_hot_intra_time(blocks, centers, id_parameter, nr_algorithm_iteration, iteration, row):
    import cupy as cp

    # open the log file in the append mode
    f = open(dst_path_experiments, "a", encoding='UTF8', newline='')

    # create a csv writer
    writer = csv.writer(f)

    # creating CUDA events for intra device time measurement
    start_gpu_intra_device = cp.cuda.Event()
    end_gpu_intra_device = cp.cuda.Event()

    # Measure additional time 1
    start_additional_time_1 = time.perf_counter()
    partials = np.zeros((centers.shape[0], 2), dtype=object)
    if len(blocks[0]) == 1:
        arr = blocks[0][0]
    else:
        arr = Array._merge_blocks(blocks)
    end_additional_time_1 = time.perf_counter()

    # Measure communication time 1
    start_communication_time_1 = time.perf_counter()
    arr_gpu = cp.asarray(arr).astype(cp.float32)
    centers_gpu = cp.asarray(centers).astype(cp.float32)
    end_communication_time_1 = time.perf_counter()
    arr = None

    # Measure intra task execution time (device function) 
    start_gpu_intra_device.record()
    close_centers_gpu = cp.argmin(distance_gpu(arr_gpu, centers_gpu), axis=1)
    end_gpu_intra_device.record()
    end_gpu_intra_device.synchronize()
    intra_task_execution_device_func = cp.cuda.get_elapsed_time(start_gpu_intra_device, end_gpu_intra_device)*1e-3

    # Measure communication time 2
    start_communication_time_2 = time.perf_counter()
    arr = cp.asnumpy(arr_gpu)
    close_centers = cp.asnumpy(close_centers_gpu)
    end_communication_time_2 = time.perf_counter()

    # Measure additional time 2
    start_additional_time_2 = time.perf_counter()
    arr_gpu, centers_gpu = None, None

    for center_idx, _ in enumerate(centers):
        indices = np.argwhere(close_centers == center_idx).flatten()
        partials[center_idx][0] = np.sum(arr[indices], axis=0)
        partials[center_idx][1] = indices.shape[0]
    end_additional_time_2 = time.perf_counter()

    # write the time data
    data = [id_parameter, nr_algorithm_iteration, iteration, row, var_null, var_null, var_null, var_null, var_null, intra_task_execution_device_func, start_communication_time_1, end_communication_time_1, start_communication_time_2, end_communication_time_2, start_additional_time_1, end_additional_time_1, start_additional_time_2, end_additional_time_2, datetime.datetime.now()]
    writer.writerow(data)
    f.close()

    return partials


@constraint(computing_units="${ComputingUnitsCPU}")
@task(returns=dict)
def _merge(*data):
    accum = data[0].copy()

    for d in data[1:]:
        accum += d

    return accum


@constraint(computing_units="${ComputingUnitsCPU}")
@task(blocks={Type: COLLECTION_IN, Depth: 2}, returns=np.array)
def _predict(blocks, centers):
    arr = Array._merge_blocks(blocks)
    return pairwise_distances(arr, centers).argmin(axis=1).reshape(-1, 1)


def distance_gpu(a_gpu, b_gpu):
    import cupy as cp

    sq_sum_ker = get_sq_sum_kernel()

    aa_gpu = cp.empty(a_gpu.shape[0], dtype=cp.float32)
    bb_gpu = cp.empty(b_gpu.shape[0], dtype=cp.float32)

    sq_sum_ker(a_gpu, aa_gpu, axis=1)
    sq_sum_ker(b_gpu, bb_gpu, axis=1)

    size = len(aa_gpu) * len(bb_gpu)
    dist_gpu = cp.empty((len(aa_gpu), len(bb_gpu)), dtype=cp.float32)
    add_mix_kernel(len(b_gpu))(aa_gpu, bb_gpu, dist_gpu, size=size)
    aa_gpu, bb_gpu = None, None

    dist_gpu += -2.0 * cp.dot(a_gpu, b_gpu.T)

    return dist_gpu


def get_sq_sum_kernel():
    import cupy as cp

    return cp.ReductionKernel(
        'T x',  # input params
        'T y',  # output params
        'x * x',  # map
        'a + b',  # reduce
        'y = a',  # post-reduction map
        '0',  # identity value
        'sqsum'  # kernel name
    )


def add_mix_kernel(y_len):
    import cupy as cp

    return cp.ElementwiseKernel(
        'raw T x, raw T y', 'raw T z',
        f'z[i] = x[i / {y_len}] + y[i % {y_len}]',
        'add_mix')
