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

if __name__ == '__main__':

    # samples = 125000000
    # features = 1
    # start_random_state = 170
    # block_row_size = 125000000
    # block_column_size = 1
    # n_clusters = 100

    samples = 1000
    features = 1
    start_random_state = 170
    block_row_size = 500
    block_column_size = 1
    n_clusters = 10
    # generate and load data into a ds-array
    x, y = make_blobs(n_samples=samples, n_features=features, random_state=start_random_state)
    
    print("\nx.nbytes: ")
    print(x.nbytes)

    print("\ny.nbytes: ")
    print(y.nbytes)
    
    dis_x = ds.array(x, block_size=(block_row_size, block_column_size))


    # Run KMeans using dislib
    kmeans = KMeans(n_clusters=n_clusters, random_state=start_random_state, id_device=1)
    y_pred = kmeans.fit_predict(dis_x).collect()
    print(y_pred)
    print(kmeans.centers)

    print("\ny_pred.nbytes: ")
    print(y_pred.nbytes)

    print("\nkmeans.centers.nbytes: ")
    print(kmeans.centers.nbytes)