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
                        A.ID_ALGORITHM,
                        (SELECT DISTINCT X.DS_ALGORITHM FROM ALGORITHM X WHERE X.ID_ALGORITHM = A.ID_ALGORITHM) AS DS_ALGORITHM,
                        A.ID_FUNCTION,
                        (SELECT DISTINCT X.DS_FUNCTION FROM FUNCTION X WHERE X.ID_FUNCTION = A.ID_FUNCTION) AS DS_FUNCTION,
                        (SELECT DISTINCT Y.ID_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = A.ID_FUNCTION) AS ID_DEVICE,
                        (SELECT DISTINCT Y.DS_DEVICE FROM FUNCTION X INNER JOIN DEVICE Y ON (X.ID_DEVICE = Y.ID_DEVICE) WHERE X.ID_FUNCTION = A.ID_FUNCTION) AS DS_DEVICE,
                        A.ID_DATASET,
                        A.ID_RESOURCE,
                        A.ID_PARAMETER_TYPE,
                        (SELECT X.DS_PARAMETER_TYPE FROM PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = A.ID_PARAMETER_TYPE) AS DS_PARAMETER_TYPE,
                        (SELECT X.DS_PARAMETER_ATTRIBUTE FROM PARAMETER_TYPE X WHERE X.ID_PARAMETER_TYPE = A.ID_PARAMETER_TYPE) AS DS_PARAMETER_ATTRIBUTE,
                        A.NR_ITERATIONS,
                        A.VL_GRID_ROW_DIMENSION,
                        A.VL_GRID_COLUMN_DIMENSION,
                        A.VL_BLOCK_ROW_DIMENSION,
                        A.VL_BLOCK_COLUMN_DIMENSION,
                        A.VL_BLOCK_MEMORY_SIZE,
                        A.VL_BLOCK_MEMORY_SIZE_PERCENT_CPU,
                        A.VL_BLOCK_MEMORY_SIZE_PERCENT_GPU,
                        B.DS_RESOURCE,
                        B.NR_NODES,
                        B.NR_COMPUTING_UNITS_CPU,
                        B.NR_COMPUTING_UNITS_GPU,
                        B.VL_MEMORY_SIZE_PER_CPU_COMPUTING_UNIT,
                        B.VL_MEMORY_SIZE_PER_GPU_COMPUTING_UNIT,
                        C.DS_DATASET,
                        C.VL_DATASET_MEMORY_SIZE,
                        C.DS_DATA_TYPE,
                        C.VL_DATA_TYPE_MEMORY_SIZE,
                        C.VL_DATASET_DIMENSION,
                        C.VL_DATASET_ROW_DIMENSION,
                        C.VL_DATASET_COLUMN_DIMENSION,
                        C.NR_RANDOM_STATE
                    FROM PARAMETER A
                    INNER JOIN RESOURCE B ON (A.ID_RESOURCE = B.ID_RESOURCE)
                    INNER JOIN DATASET C ON (A.ID_DATASET = C.ID_DATASET)
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
