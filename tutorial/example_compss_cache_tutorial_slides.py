--python_worker_cache=true:4GB

import cupy as cp
@constraint(processors=[{"processorType": "GPU"}])
@task(x={Cache: True}, y={Cache: False},
      returns=cp.array, cache_returns=True)
def mytask(x, y):
    
