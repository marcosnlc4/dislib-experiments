import itertools

def print_combinations(N):
    variables = ['X', 'Y', 'Z', 'W']
    
    # Generate all combinations of the variables with repetition for N spots
    combinations = itertools.product(variables, repeat=N)
    
    # Print all combinations
    for combo in combinations:
        print(''.join(combo))

# Example usage:
N = int(input("Enter the number of spots (N): "))
print_combinations(N)