import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from config import open_connection, close_connection
import numpy as np
import csv
import os
import math
import matplotlib
from sklearn.feature_selection import mutual_info_regression, mutual_info_classif
import statsmodels.api as sm

def main(ds_algorithm, ds_resource, nr_iterations, mode):

    dst_path_figs = '../../results/figures/'

    # Open connection to the database
    cur, conn = open_connection()

    # Set sql query according to mode
    sql_query = """SELECT 1"""
    
    # Get dataframe from query
    df = get_df_from_query(sql_query,conn)

    # Close connection to the database
    close_connection(cur, conn)

    # Generate graph (mode 2)
    generate_graph(df, dst_path_figs, ds_algorithm, ds_resource, nr_iterations, mode)

# Function that takes in a PostgreSQL query and outputs a pandas dataframe 
def get_df_from_query(sql_query, conn):
    df = pd.read_sql_query(sql_query, conn)
    return df

# Function that generates a graph according to the mode
def generate_graph(df, dst_path_figs, ds_algorithm, ds_resource, nr_iterations, mode):
    
    if (mode == 300):
        # Path of the "tb_experiments_motivation" table - CSV file
        dst_path_dataset_raw = "/home/marcos/Dev/project/dev_env/dislib-experiments/experiments/results/tb_example_dataset_raw.csv"

        dst_path_dataset_final = "/home/marcos/Dev/project/dev_env/dislib-experiments/experiments/results/tb_example_dataset_final.csv"

        # Reading "tb_experiments_motivation" csv table
        param_file = os.path.join(dst_path_dataset_raw)
        df_filtered = pd.read_csv(param_file)

    if mode == 300:

        # PRE-PROCESSING (NORMALIZING DATA)
        min_value = df_filtered["Block size"].min()
        max_value = df_filtered["Block size"].max()
        df_filtered["Block size"] = (df_filtered["Block size"] - min_value) / (max_value - min_value)

        min_value = df_filtered["Computational complexity"].min()
        max_value = df_filtered["Computational complexity"].max()
        df_filtered["Computational complexity"] = (df_filtered["Computational complexity"] - min_value) / (max_value - min_value)
        
        min_value = df_filtered["DAG maximum width"].min()
        max_value = df_filtered["DAG maximum width"].max()
        df_filtered["DAG maximum width"] = (df_filtered["DAG maximum width"] - min_value) / (max_value - min_value)
        
        min_value = df_filtered["DAG maximum height"].min()
        max_value = df_filtered["DAG maximum height"].max()
        df_filtered["DAG maximum height"] = (df_filtered["DAG maximum height"] - min_value) / (max_value - min_value)

        min_value = df_filtered["Dataset size"].min()
        max_value = df_filtered["Dataset size"].max()
        df_filtered["Dataset size"] = (df_filtered["Dataset size"] - min_value) / (max_value - min_value)

        min_value = df_filtered["CPU cache size"].min()
        max_value = df_filtered["CPU cache size"].max()
        df_filtered["CPU cache size"] = (df_filtered["CPU cache size"] - min_value) / (max_value - min_value)

        min_value = df_filtered["GPU cache size"].min()
        max_value = df_filtered["GPU cache size"].max()
        df_filtered["GPU cache size"] = (df_filtered["GPU cache size"] - min_value) / (max_value - min_value)

        
        filepath = Path(dst_path_dataset_final)  
        df_filtered.to_csv(filepath, index=False)


def interpolate_gaps(values, limit=None):
    """
    Fill gaps using linear interpolation, optionally only fill gaps up to a
    size of `limit`.
    """
    values = np.asarray(values)
    i = np.arange(values.size)
    print("HERE")
    print(values)
    valid = np.isfinite(values)
    filled = np.interp(i, i[valid], values[valid])

    if limit is not None:
        invalid = ~valid
        for n in range(1, limit+1):
            invalid[:-n] &= invalid[n:]
        filled[invalid] = np.nan

    return filled

def parse_args():
    import argparse
    description = 'Generating graphs for the experiments'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-a', '--ds_algorithm', type=str, default="KMEANS",
                        help='Algorithm description'
                        )
    parser.add_argument('-r', '--ds_resource', type=str, default="MINOTAURO_1",
                        help='Resource description'
                        )
    parser.add_argument('-i', '--nr_iterations', type=int, default=5,
                        help='Number of iterations'
                        )
    parser.add_argument('-m', '--mode', type=int, default=1,
                        help='Graph mode'
                        )
    return parser.parse_args()




def mk_groups(data):
    try:
        newdata = data.items()
    except:
        return

    thisgroup = []
    groups = []
    for key, value in newdata:
        newgroups = mk_groups(value)
        if newgroups is None:
            thisgroup.append((key, value))
        else:
            thisgroup.append((key, len(newgroups[-1])))
            if groups:
                groups = [g + n for n, g in zip(newgroups, groups)]
            else:
                groups = newgroups
    return [thisgroup] + groups

def add_line(ax, xpos, ypos):
    line = plt.Line2D([xpos, xpos], [ypos + .1, ypos],
                      transform=ax.transAxes, color='black')
    line.set_clip_on(False)
    ax.add_line(line)

def label_group_bar(ax, data):
    groups = mk_groups(data)
    xy = groups.pop()
    x, y = zip(*xy)
    ly = len(y)
    xticks = range(1, ly + 1)

    # colors = ["#E6DAA6","#008000","#E6DAA6","#008000"]
    # colors = ["#E6DAA6","#006400","#E6DAA6","#006400"]
    colors = ["#ADD8E6","#006400","#ADD8E6","#006400"]
    # hatches=['','xxx','','xxx','','xxx']

    ax.bar(xticks, y, align='center', color=colors, zorder=3)
    ax.set_xticks(xticks)
    ax.set_xticklabels(x)
    ax.set_xlim(.5, ly + .5)
    ax.yaxis.grid(True)
    plt.ylabel('Average Execution Time (s)')
    

    # labels = ['CPU Single Node', 'GPU Single Node', 'CPU Distributed', 'GPU Distributed']
    # values = [0.47, 0.03, 690.38, 842.68]

    # ax.bar(labels, values, color=colors, hatch=hatches, zorder=3)

    scale = 1. / ly
    for pos in range(ly + 1):  # change xrange to range for python3
        add_line(ax, pos * scale, -.1)
    ypos = -.2
    while groups:
        group = groups.pop()
        pos = 0
        for label, rpos in group:
            lxpos = (pos + .5 * rpos) * scale
            ax.text(lxpos, ypos, label, ha='center', transform=ax.transAxes)
            add_line(ax, pos * scale, ypos)
            pos += rpos
        add_line(ax, pos * scale, ypos)
        ypos -= .1


if __name__ == "__main__":
    opts = parse_args()
    main(**vars(opts))
