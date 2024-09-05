from pycompss.api.task import task
from pycompss.api.constraint import constraint
import time

@constraint(computing_units="1")
@task(returns=int)
def cpu_task():
    # Simulate CPU-bound work
    time.sleep(1)
    return 1

@constraint(processors=[{"processorType": "GPU", "computingUnits": 1}])
@task(returns=int)
def gpu_task():
    # Simulate GPU-bound work
    time.sleep(1)
    return 1
