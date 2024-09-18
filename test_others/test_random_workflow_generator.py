from pycompss.api.task import task
from pycompss.api.parameter import *
from pycompss.api.api import compss_wait_on

import dislib as ds
import random
import networkx as nx

# Template tasks
# Each task must be of have a different computational complexity
# Each task must receive at least one input and return one output
# If a task has more than one input, merge the the inputs into a single value. Otherwise, ignore non used inputs
# TODO: treat multiples inputs in a task (if the input is None it means it is not used. Otherwise merge inputs)
# TODO: arrays as input/output
# TODO: implement algorithms with different computational complexity for each task
# TODO: add support to CPU/GPU cold/hot
@task(returns=int)
def task_a(arg0, arg1=None, arg2=None, arg3=None, arg4=None, arg5=None, arg6=None, arg7=None, arg8=None, arg9=None, arg10=None, arg11=None, arg12=None):
    print("Executing Task A")
    return 1

@task(returns=int)
def task_b(arg0, arg1=None, arg2=None, arg3=None, arg4=None, arg5=None, arg6=None, arg7=None, arg8=None, arg9=None, arg10=None, arg11=None, arg12=None):
    print("Executing Task B")
    return 2

@task(returns=int)
def task_c(arg0, arg1=None, arg2=None, arg3=None, arg4=None, arg5=None, arg6=None, arg7=None, arg8=None, arg9=None, arg10=None, arg11=None, arg12=None):
    print("Executing Task C")
    return 3

@task(returns=int)
def task_d(arg0, arg1=None, arg2=None, arg3=None, arg4=None, arg5=None, arg6=None, arg7=None, arg8=None, arg9=None, arg10=None, arg11=None, arg12=None):
    print("Executing Task D")
    return 4

# Maximum number of task inputs
NR_TASK_INPUT = 13

# List of available tasks
TASKS = {
    'task_a': task_a,
    'task_b': task_b,
    'task_c': task_c,
    'task_d': task_d
}

def generate_dag_workflow(dag_pattern=0, num_tasks=5, dependency_probability=0.5):
    """
    Generate a random DAG with a given number of tasks and dependencies.
    :param dag_pattern: DAG shape pattern(default 0)
                        0: sequential
                        1: independent
                        2: reduction
                        3: tree
                        4: random
    :param num_tasks: Number of tasks to generate (default 10)
    :param dependency_probability: [only used in random DAG pattern] Probability of creating a dependency between two tasks (default 0.5)
    :return: Directed Acyclic Graph (DAG) representing the task dependencies.
    """
    dag = nx.DiGraph()

    # Choose random tasks from the available tasks list
    task_names = random.choices(list(TASKS.keys()), k=num_tasks)

    # 0: sequential pattern
    if dag_pattern == 0:
        # Add nodes (tasks)
        for i, task_name in enumerate(task_names):
            dag.add_node(f'task_{i}', task_name=task_name)

        # Add edges (dependencies)
        for i in range(num_tasks-1):
            j = i + 1
            dag.add_edge(f'task_{i}', f'task_{j}')

    # 1: independent pattern
    elif dag_pattern == 1:
        # Add nodes (tasks)
        for i, task_name in enumerate(task_names):
            dag.add_node(f'task_{i}', task_name=task_name)

    # 2: tree pattern
    elif dag_pattern == 2:
        # Add nodes (tasks)
        for i, task_name in enumerate(task_names):
            dag.add_node(f'task_{i}', task_name=task_name)

        # Add edges (dependencies)
        for i in range(num_tasks):
            left_child = 2 * i + 1
            right_child = 2 * i + 2
            if left_child < num_tasks:
                dag.add_edge(f'task_{i}', f'task_{left_child}')
            if right_child < num_tasks:
                dag.add_edge(f'task_{i}', f'task_{right_child}')

    # 3: reduction tree pattern
    elif dag_pattern == 3:
        # Add nodes (tasks)
        for i, task_name in enumerate(task_names):
            dag.add_node(f'task_{i}', task_name=task_name)

        current_task = 0  # Start with the first task as the root of the reduction tree

        # Add edges (dependencies)
        while current_task < (num_tasks - 1):
            left_child = current_task
            right_child = current_task + 1
            parent = current_task + 2  # Parent is the next task after the two children

            # Parent depends on its two children
            if parent < num_tasks:
                dag.add_edge(f'task_{left_child}', f'task_{parent}')
                dag.add_edge(f'task_{right_child}', f'task_{parent}')

            # Move to the next two tasks for the next parent
            current_task += 2

    # 4: random pattern
    elif dag_pattern == 4:
        # Add nodes (tasks)
        for i, task_name in enumerate(task_names):
            dag.add_node(f'task_{i}', task_name=task_name)

        # Add edges (dependencies)
        for i in range(num_tasks):
            for j in range(i+1, num_tasks):
                # Only add a new edge in a node if #input edges is below the max #inputs of a task
                if len(dag.in_edges(f'task_{j}')) < NR_TASK_INPUT:
                    # Only add a new edge in a node if the dependency probability is satisfied or the node has no input edge
                    if random.random() < dependency_probability or len(dag.in_edges(f'task_{j}')) < 1:
                        dag.add_edge(f'task_{i}', f'task_{j}')

    else:
        raise ValueError(f"Unknown pattern type: {dag_pattern}")

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
            task_args = [input_dataset] if not predecessors else [task_results[pred] for pred in predecessors]

        #DEBUG
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
    # Generate a workflow
    dag = generate_dag_workflow(dag_pattern=3, num_tasks=13, dependency_probability=0.5)
    
    # #debug
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
