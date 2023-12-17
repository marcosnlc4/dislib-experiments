import psycopg2
from configparser import ConfigParser
 
def config(filename='database.ini', section='postgresql'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)
 
    # get section, default to postgresql
    db = {}
    
    # Checks to see if section (postgresql) parser exists
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
         
    # Returns an error if a parameter is called that is not listed in the initialization file
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
 
    return db

def open_connection():
    try:
        # Obtain the configuration parameters
        params = config()
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**params)

        # Open a cursor to perform database operations
        cur = conn.cursor()

        # Set schema
        # cur.execute("SET search_path = user_dev,schema_dev;") #KMEANS
        # cur.execute("SET search_path = user_dev,schema_dev_matmul;") #MATMUL
        cur.execute("SET search_path = user_dev,schema_dev_matmul_fma;") #MATMUL FMA

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    return cur, conn
    
def close_connection(cur, conn):
    # Close the cursor and connection
    cur.close()
    conn.close()