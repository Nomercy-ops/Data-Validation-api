import json
import urllib.parse
import pandas as pd
from sqlalchemy import create_engine
import dask.dataframe as dd
from dask import delayed
from app.validate import calculate_validation_results
from sqlalchemy import create_engine


def parse_credentials(data):
    """
    Parse credentials from data and return the source and target database names.
    
    Parameters:
        data (str): The data containing the credentials in JSON format.
        
    Returns:
        tuple: A tuple containing the source database name (str) and the target database name (str).
    """
    parsed_data = json.loads(data)
    return parsed_data['source_db'], parsed_data['target_db']


def generate_query(database_type, db_details, schema, table, order_by, limit):
    """
    Generate the SQL query based on the provided database type and details.

    Args:
        database_type (str): The type of the database.
        db_details (dict): A dictionary containing the database details.
        schema (str): The name of the schema.
        table (str): The name of the table.
        order_by (str): The column to use for ordering.
        limit (int): The maximum number of rows to fetch.

    Returns:
        str: The generated SQL query.

    Raises:
        ValueError: If an invalid database type is provided.
    """
    query_format = {
        'postgres': 'SELECT * FROM "{}"."{}"."{}" ORDER BY {} LIMIT {}',
        'mysql': 'SELECT * FROM `{}`.`{}`.`{}` ORDER BY {} LIMIT {}',
        'snowflake': 'SELECT * FROM {}.{}.{} ORDER BY {} LIMIT {}',
        'sql server': 'SELECT TOP {} * FROM "{}"."{}"."{}"."{}" ORDER BY {}'
    }

    if database_type in query_format:
        return query_format[database_type].format(
            db_details,schema, table, order_by, limit
        )
    else:
        raise ValueError("Invalid database type")


def fetch_data(database_type, db_details, query):
    engine = None

    try:
        if database_type == 'postgres':
            conn_str = f"postgresql://{db_details['username']}:{db_details['password']}@{db_details['host']}/{db_details['database-name']}"
            engine = create_engine(conn_str)
        elif database_type == 'mysql':
            conn_str = f"mysql+pymysql://{db_details['username']}:{db_details['password']}@{db_details['host']}/{db_details['database-name']}"
            engine = create_engine(conn_str)
        elif database_type == 'snowflake':
            conn_str = f"snowflake://{db_details['username']}:{urllib.parse.quote_plus(db_details['password'])}@{db_details['host']}/{db_details['database-name']}/'COMPUTE_WH'"
            engine = create_engine(conn_str)
        elif database_type == 'sql server':
            conn_str = f"mssql+pyodbc://{db_details['username']}:{db_details['password']}@{db_details['host']}/{db_details['database-name']}?driver=SQL+Server"
            engine = create_engine(conn_str)
        else:
            raise ValueError("Invalid database type")

        df = pd.read_sql_query(query, engine)
        return df
    except Exception as e:
        raise Exception(f"Error fetching data from the database: {str(e)}") from e
    finally:
        if engine is not None:
            engine.dispose()

def process_database_data(data):
    try:
        source_db_details, target_db_details = parse_credentials(data)

        # Generate the SQL query for the source database
        source_query = generate_query(
            source_db_details['source-database-type'],
            source_db_details['database-name'],
            "dev",
            "customer",
            "c_custkey",
            50000
        )

        # Generate the SQL query for the target database
        target_query = generate_query(
            target_db_details['target-database-type'],
            target_db_details['database-name'],
            "public",
            "customer",
            "c_custkey",
            50000
        )

        # Use Dask to parallelize data fetching
        source_data_future = delayed(fetch_data)(
            source_db_details['source-database-type'],
            source_db_details,
            source_query
        )
        target_data_future = delayed(fetch_data)(
            target_db_details['target-database-type'],
            target_db_details,
            target_query
        )

        # Compute the Dask delayed objects to get the results
        source_data = source_data_future.compute()
        target_data = target_data_future.compute()

        # Convert data to Dask DataFrames
        source_df = dd.from_pandas(source_data, npartitions=1)
        target_df = dd.from_pandas(target_data, npartitions=1)

        # Perform further processing or validation
        validation_results = calculate_validation_results(source_df, target_df)
        return validation_results

    except (json.JSONDecodeError, KeyError) as e:
        raise ValueError("Invalid data format or missing keys in the JSON response") from e
    except ConnectionError as e:
        raise ConnectionError(f"Error connecting to the database: {str(e)}") from e
    except Exception as e:
        raise Exception(f"Error processing database data: {str(e)}") from e







# # Example usage
# data = '''
# {
#   "source_db": {
#     "host": "cg68563.central-india.azure",
#     "database-name": "demo",
#     "username": "RIKESH08",
#     "password": "Nomercy786@",
#     "source-database-type": "snowflake"
#   },
#   "target_db": {
#     "host": "localhost",
#     "database-name": "Demo",
#     "username": "postgres",
#     "password": "1234",
#     "target-database-type": "postgres"
#   }
# }
# '''

# process_database_data(data)