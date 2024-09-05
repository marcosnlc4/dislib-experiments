@constraint(computing_units="1")
@task(returns=np.array)
def matmul_cpu(a, b):
    return a @ b
    
    
    

@constraint(processors=[
                {"processorType": "CPU", "computingUnits": "1"},
                {"processorType": "GPU", "computingUnits": "1"},
            ])
@task(returns=np.array)
def matmul_gpu(a, b):
    import cupy as cp

    a_gpu, b_gpu = cp.asarray(a), cp.asarray(b)

    res = cp.asnumpy(cp.matmul(a_gpu, b_gpu))
    del a_gpu, b_gpu
    return res