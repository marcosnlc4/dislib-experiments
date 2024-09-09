import subprocess as sp
import os

# Units in MiB

def get_cpu_memory():
    memory_total_values, memory_used_values, memory_free_values = map(
    int, os.popen('free -t -m').readlines()[-1].split()[1:])
    return memory_total_values

def get_gpu_memory():
    command = "nvidia-smi --query-gpu=memory.total --format=csv"
    memory_total_info = sp.check_output(command.split()).decode('ascii').split('\n')[:-1][1:]
    memory_total_values = [int(x.split()[0]) for i, x in enumerate(memory_total_info)]
    return memory_total_values[0]

print(get_cpu_memory())
print(get_gpu_memory())