import os
import pandas as pd
import re

def extract_data(file_path, filename):
    method_name = None
    compss_hostnames = None
    cache_miss_count = 0
    cache_hit_count = 0
    cache_return_count = 0

    with open(file_path, 'r') as file:
        for line in file:
            if "METHOD NAME=" in line:
                method_name = re.search(r'METHOD NAME=(.*)]\n', line).group(1)
            elif "COMPSS_HOSTNAMES:" in line:
                compss_hostnames = re.search(r'COMPSS_HOSTNAMES:(.*)\n', line).group(1)
            elif "(Cache miss)" in line:
                cache_miss_count += 1
            elif "(Cache hit)" in line:
                cache_hit_count += 1
            elif "Storing return in cache" in line:
                for line2 in file:
                    if "Inserted into cache" in line2:
                        cache_return_count += 1


    return filename, method_name, compss_hostnames, cache_miss_count, cache_hit_count, cache_return_count

def process_folder(folder_path):
    data = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".out"):
            file_path = os.path.join(folder_path, filename)
            filename, method_name, compss_hostnames, cache_miss_count, cache_hit_count, cache_return_count = extract_data(file_path, filename)
            data.append([filename, method_name, compss_hostnames, cache_miss_count, cache_hit_count, cache_return_count])

    df = pd.DataFrame(data, columns=['Filename', 'Method Name', 'COMPSS_HOSTNAMES', 'Cache Miss Count', 'Cache Hit Count', 'Cache Return Count'])
    return df

def main():
    folder_path = "../../results/cache_logs/jobs/"
    df = process_folder(folder_path)
    df.to_csv("../../results/cache_logs/output.csv", index=False)

if __name__ == "__main__":
    main()
