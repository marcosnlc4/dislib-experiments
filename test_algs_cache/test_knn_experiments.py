import dislib as ds
from dislib.neighbors import NearestNeighbors

if __name__ == '__main__':
    data = ds.random_array((100, 5), block_size=(25, 5))
    knn = NearestNeighbors(n_neighbors=10)
    knn.fit(data)
    distances, indices = knn.kneighbors(data)