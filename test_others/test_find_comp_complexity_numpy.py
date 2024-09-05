import numpy as np
import inspect
import big_o
# from big_o import datagen, complexities

# Initialize BigO
# big_o = Big_o()
print('HERE')
# best, others = big_o.big_o(np.matmul, big_o.datagen.n_, max_n=100000, n_repeats=100)
# best, others = big_o.big_o(sorted, lambda n: big_o.datagen.integers(n, 10000, 50000))
print(big_o.big_o(np.matmul, big_o.datagen.n_, max_n=100000, n_repeats=100)[0])

# # Function to check if an object is a callable function
# def is_function(obj):
#     return callable(obj)

# # Get all routines/functions from NumPy
# numpy_functions = {name: func for name, func in np.__dict__.items() if is_function(func)}

# # List to hold function names and their computational complexity
# function_complexities = []

# # Iterate over each NumPy function to determine its computational complexity
# for func_name, func in numpy_functions.items():
#     try:
#         # Create a sample input for complexity estimation
#         # Using a simple array input, assuming most functions can handle this
#         sample_input = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        
#         # Some NumPy functions require specific inputs, we use default arguments where possible
#         func_to_test = lambda x: func(x) if 'x' in inspect.signature(func).parameters else func()

#         # print('HERE')
#         # # print(func_name)
#         # print(big_o.datagen.n_)
        
#         # Get the computational complexity
#         best, _ = big_o.big_o(func_to_test, sample_input, n_repeats=10, min_n=1, max_n=1000)
#         complexity_class = best.__class__.__name__
        
#         # Store the function name and its complexity
#         function_complexities.append((func_name, complexity_class))
    
#     except Exception as e:
#         # If an error occurs, store the function name with a note that it couldn't be tested
#         function_complexities.append((func_name, f"Could not determine complexity: {str(e)}"))

# # Print the results
# for func_name, complexity in function_complexities:
#     print(f"Function: {func_name}, Complexity: {complexity}")