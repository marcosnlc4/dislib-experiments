from pycompss.api.task import task
from pycompss.api.parameter import *
from pycompss.api.api import compss_wait_on

import dislib as ds
import random
import networkx as nx

# Template tasks
@task(returns=int)
def task_a(x, y=1, z=1):
    print("Executing Task A")
    return 1

@task(returns=int)
def task_b(x, y=1, z=1):
    print("Executing Task B")
    return 2

@task(returns=int)
def task_c(x, y=1, z=1):
    print("Executing Task C")
    return 3

@task(returns=int)
def task_d(x, y=1, z=1):
    print("Executing Task D")
    return 4

# List of available tasks
TASKS = {
    'task_a': task_a,
    'task_b': task_b,
    'task_c': task_c,
    'task_d': task_d
}

def generate_dataset():
    input_matrix_rows = 20
    input_matrix_columns = 20
    start_random_state = 170
    block_row_size = 20
    block_column_size = 20
    transpose_a = transpose_b = bl_transpose = False

    shape = (input_matrix_rows, input_matrix_columns)
    block_size = (block_row_size, block_column_size)

    # CPU COLD
    id_device=1
    id_cache=1
    # # CPU HOT
    # id_device=1
    # id_cache=2
    # # GPU COLD
    # id_device=2
    # id_cache=1
    # # GPU HOT
    # id_device=2
    # id_cache=2

    # DATASET GENERATION
    return ds.random_array(shape, block_size, random_state=start_random_state, id_device=id_device, id_cache=id_cache)

def generate_sequential_workflow(num_tasks=2, dependency_probability=1):
    """
    Generate a sequential DAG with a given number of tasks and dependencies.
    :param num_tasks: Number of tasks to generate.
    :param dependency_probability: not used (keep it only for standardization of DAG generators)
    :return: Directed Acyclic Graph (DAG) representing the task dependencies.
    """
    dag = nx.DiGraph()

    # Choose random tasks from the available tasks list
    task_names = random.choices(list(TASKS.keys()), k=num_tasks)

    # Add nodes (tasks)
    for i, task_name in enumerate(task_names):
        dag.add_node(f'task_{i}', task_name=task_name)

    # Add edges (dependencies)
    for i in range(num_tasks-1):
        j = i + 1
        dag.add_edge(f'task_{i}', f'task_{j}')

    return dag

# TODO: treat multiples inputs in a task (if the input is 1 it means it is not used. Otherwise merge inputs)
def generate_random_workflow(num_tasks=5, dependency_probability=0.3):
    """
    Generate a random DAG with a given number of tasks and dependencies.
    :param num_tasks: Number of tasks to generate.
    :param dependency_probability: Probability of creating a dependency between two tasks.
    :return: Directed Acyclic Graph (DAG) representing the task dependencies.
    """
    dag = nx.DiGraph()

    # Choose random tasks from the available tasks list
    task_names = random.choices(list(TASKS.keys()), k=num_tasks)

    # Add nodes (tasks)
    for i, task_name in enumerate(task_names):
        dag.add_node(f'task_{i}', task_name=task_name)

    # Add edges (dependencies)
    for i in range(num_tasks):
        for j in range(i+1, num_tasks):
            if random.random() < dependency_probability or len(dag.in_edges(f'task_{j}')) < 1:
                dag.add_edge(f'task_{i}', f'task_{j}')

    return dag

def execute_task(task_name, task_args):
    """
    Executes a task by its name with given arguments.
    :param task_name: Name of the task (string).
    :param task_args: List of arguments to pass to the task.
    :return: The result of the task execution.
    """
    task_function = TASKS.get(task_name)
    if not task_function:
        raise ValueError(f"Unknown task name: {task_name}")
    
    # Call the task with the correct number of arguments
    return task_function(*task_args)

def run_workflow(dag, input_dataset):
    """
    Execute the workflow based on the DAG of tasks and dependencies.
    :param dag: Directed Acyclic Graph (DAG) representing the task dependencies.
    :return: None
    """
    task_results = {}  # To store results of each task after execution

    for node in nx.topological_sort(dag):
        task_name = dag.nodes[node]['task_name']  # Get the actual task name for the node
        predecessors = list(dag.predecessors(node))  # Get dependencies for the current task

        # Get task_args for the first node from the input dataset 
        if node == "task_0":
            task_args = [input_dataset]
        # Get task_args for remaining tasks from results of the predecessor tasks
        else:
            task_args = [task_results[pred] for pred in predecessors]

        print("VALIDATION")
        print("task name:", task_name)
        print("predecessors:", predecessors)
        print("task_args:", task_args)

        # Execute the current task
        result = execute_task(task_name, task_args)

        # Store the task result
        task_results[node] = result

    # Synchronize the final tasks
    for node, result in task_results.items():
        task_results[node] = compss_wait_on(result)
    
    print("Workflow execution complete.")
    print("Final task results: ", task_results)

if __name__ == "__main__":
    # Generate a random workflow with 5 tasks and 30% chance of dependency between any two tasks
    # dag = generate_random_workflow(num_tasks=4, dependency_probability=0.3)
    dag = generate_sequential_workflow(num_tasks=4, dependency_probability=1)

    print("Generated DAG with tasks and dependencies:")
    print("edges:", dag.edges)
    print("nodes", dag.nodes)
    print("name", dag.name)

    for node in nx.topological_sort(dag):
        task_name = dag.nodes[node]['task_name']  # Get the actual task name for the node
        print("node",node)
        print("task_name",task_name)

    # TODO: Replace this dataset by a ds-array
    input_dataset = 1

    # Run the generated workflow
    run_workflow(dag, input_dataset)
