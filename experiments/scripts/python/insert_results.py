import os
import psycopg2
import psycopg2.extras as extras
import pandas as pd
import math
from config import open_connection, close_connection

def main():
    # Path of the "tb_experiments" table - CSV file
    src_path_experiments = "../../results/tb_experiments.csv"

    # Reading "tb_experiments" table
    param_file = os.path.join(src_path_experiments)
    df_experiments = pd.read_csv(param_file)

    tuples = [tuple(x) for x in df_experiments.to_numpy()]
    
    cols = ','.join(list(df_experiments.columns))

    # Open connection to the database
    cur, conn = open_connection()

    # Set sql query - on conflict with the database values, do nothing
    # sql_query = "INSERT INTO EXPERIMENT(%s) VALUES %%s" % (cols)
    sql_query = "INSERT INTO EXPERIMENT_RAW(%s) VALUES %%s ON CONFLICT (%s) DO NOTHING" % (cols,cols)

    new_tuples = [tuple(None if isinstance(i, float) and math.isnan(i) else i for i in t) for t in tuples]

    # print(new_tuples)
    # Get dataframe from query
    insert_experiment_result(sql_query, cur, conn, new_tuples)

# Function that takes in a PostgreSQL query and outputs a pandas dataframe 
def insert_experiment_result(sql_query, cur, conn, tuples):
    try:
        extras.execute_values(cur, sql_query, tuples)
        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        conn.rollback()
        close_connection(cur, conn)

    print("Values inserted successfully!")
    close_connection(cur, conn)

if __name__ == "__main__":
    main()