from pycompss.api.api import compss_wait_on, compss_barrier
from tasks import cpu_task, gpu_task
from dag_generator import generate_random_dag, assign_tasks_to_nodes

def execute_dag(dag, tasks):
    results = [None] * len(dag)
    pending_tasks = list(range(len(dag)))
    
    while pending_tasks:
        for i in pending_tasks[:]:
            if all(results[dep] is not None for dep in dag[i]):
                if tasks[i] == 'cpu':
                    results[i] = cpu_task()
                else:
                    results[i] = gpu_task()
                pending_tasks.remove(i)
                
    results = [compss_wait_on(r) for r in results]
    return results

if __name__ == "__main__":
    num_nodes = 10
    dag = generate_random_dag(num_nodes)
    tasks = assign_tasks_to_nodes(num_nodes)

    compss_barrier()

    results = execute_dag(dag, tasks)
    print(f"Execution results: {results}")

    compss_barrier()
