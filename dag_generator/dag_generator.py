import random

def generate_random_dag(num_nodes, max_out_degree=3):
    dag = {i: [] for i in range(num_nodes)}
    for i in range(num_nodes):
        num_edges = random.randint(0, max_out_degree)
        for _ in range(num_edges):
            target = random.randint(i+1, num_nodes-1)
            dag[i].append(target)
    return dag

def assign_tasks_to_nodes(num_nodes, gpu_ratio=0.5):
    tasks = []
    for i in range(num_nodes):
        if random.random() < gpu_ratio:
            tasks.append('gpu')
        else:
            tasks.append('cpu')
    return tasks
