import psycopg2
import pandas as pd
from pathlib import Path
from config import open_connection, close_connection

def main():

    dst_path_parameters = '../../parameters/tb_parameters.csv'

    # Open connection to the database
    cur, conn = open_connection()

    # Set sql query
    sql_query = """SELECT
                        A.ID_PARAMETER,
                        A.CD_PARAMETER,
                        A.CD_CONFIGURATION,
                        A.CD_ALGORITHM,
                        (SELECT DISTINCT X.DS_ALGORITHM FROM ALGORITHM X WHERE X.CD_ALGORITHM = A.CD_ALGORITHM) AS DS_ALGORITHM,
                        A.CD_FUNCTION,
                        (SELECT DISTINCT X.DS_FUNCTION FROM FUNCTION X WHERE X.CD_FUNCTION = A.CD_FUNCTION) AS DS_FUNCTION,
                        A.ID_DEVICE,
                        (SELECT DISTINCT X.DS_DEVICE FROM DEVICE X WHERE X.ID_DEVICE = A.ID_DEVICE) AS DS_DEVICE,
                        A.CD_DATASET,
                        A.CD_RESOURCE,
                        A.NR_ITERATIONS,
                        A.DS_TP_PARAMETER,
                        A.VL_DATASET_ROW_SIZE,
                        A.VL_DATASET_COLUMN_SIZE,
                        A.VL_GRID_ROW_SIZE,
                        A.VL_GRID_COLUMN_SIZE,
                        A.VL_BLOCK_ROW_SIZE,
                        A.VL_BLOCK_COLUMN_SIZE,
                        A.VL_BLOCK_MEMORY_SIZE,
                        A.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                        A.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                        A.DS_STATUS_PARALLELISM,
                        A.VL_BLOCK_SIZE_PERCENT_DATASET,
                        B.DS_RESOURCE,
                        B.NR_NODES,
                        B.NR_COMPUTING_UNITS_CPU,
                        B.NR_COMPUTING_UNITS_GPU,
                        B.VL_MEMORY_PER_CPU_COMPUTING_UNIT,
                        B.VL_MEMORY_PER_GPU_COMPUTING_UNIT,
                        C.DS_DATASET,
                        C.VL_DATASET_MEMORY_SIZE,
                        C.DS_DATA_TYPE,
                        C.VL_DATA_TYPE_MEMORY_SIZE,
                        C.VL_DATASET_SIZE,
                        C.VL_DATASET_ROW_SIZE,
                        C.VL_DATASET_COLUMN_SIZE,
                        C.NR_RANDOM_STATE
                    FROM PARAMETER A
                    INNER JOIN RESOURCE B ON (A.CD_RESOURCE = B.CD_RESOURCE)
                    INNER JOIN DATASET C ON (A.CD_DATASET = C.CD_DATASET)
                    ORDER BY A.ID_PARAMETER;"""
    
    # Get dataframe from query
    df = get_df_from_query(sql_query,conn)

    # Save dataframe in default path
    save_dataframe(df, dst_path_parameters)

    # Close connection to the database
    close_connection(cur, conn)

# Function that takes in a PostgreSQL query and outputs a pandas dataframe 
def get_df_from_query(sql_query, conn):
    df = pd.read_sql_query(sql_query, conn)
    return df

# Function that saves a pandas dataframe as a csv file in a default folder
def save_dataframe(df, dst_path_parameters):
    filepath = Path(dst_path_parameters)  
    df.to_csv(filepath, index=False)


if __name__ == "__main__":
    main()
