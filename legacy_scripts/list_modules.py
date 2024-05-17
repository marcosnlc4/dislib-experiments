import subprocess

def list_installed_packages():
    try:
        # Use the subprocess module to run the 'pip list' command
        result = subprocess.run(['pip', 'list'], capture_output=True, text=True, check=True)

        # Print the output of the 'pip list' command
        print(result.stdout)

    except subprocess.CalledProcessError as e:
        # If an error occurs, print the error message
        print(f"Error: {e.stderr}")

if __name__ == "__main__":
    list_installed_packages()
