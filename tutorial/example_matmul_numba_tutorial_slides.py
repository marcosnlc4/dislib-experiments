import math
from numba import cuda, float64
import numpy as np
from pycompss.api.task import task
from pycompss.api.api import compss_wait_on
from pycompss.api.constraint import constraint

@cuda.jit
def matmul(A, B, C):
    """Perform square matrix multiplication of C = A * B
    """
    i, j = cuda.grid(2)
    if i < C.shape[0] and j < C.shape[1]:
        tmp = 0.
        for k in range(A.shape[1]):
            tmp += A[i, k] * B[k, j]
        C[i, j] = tmp

TPB = 16
@constraint(processors=[{'ProcessorType':'CPU', 'ComputingUnits':'1'},
                        {'ProcessorType':'GPU', 'ComputingUnits':'1'}])
@task(returns=1)
def do_matmul(a, b, c):
    gpu_a = cuda.to_device(a)
    gpu_b = cuda.to_device(b)
    gpu_c = cuda.to_device(c)

    threadsperblock = (TPB, TPB)
    blockspergrid_x = math.ceil(gpu_c.shape[0] / threadsperblock[0])
    blockspergrid_y = math.ceil(gpu_c.shape[1] / threadsperblock[1])
    blockspergrid = (blockspergrid_x, blockspergrid_y)

    matmul[blockspergrid, threadsperblock](gpu_a, gpu_b, gpu_c)
    c = gpu_c.copy_to_host()
    return c

def main():
    a = np.random.uniform(1, 2, (4, 4))
    b = np.random.uniform(1, 2, (4, 4))
    c = np.zeros((4, 4))

    result = do_matmul(a, b, c)
    result = compss_wait_on(result)

    print("a: \n %s" % str(a))
    print("b: \n %s" % str(b))
    print("Result: \n %s" % str(result))

    print("Verification result: ")
    print(a @ b)


if __name__=="__main__":
    main()
