import duckdb
from models import Event, User
import os


# Connect to duckdb
def connect_to_duckdb():
    if os.getenv('ENVIRONMENT') == 'PROD':
        conn = duckdb.connect(database=os.getenv('MOTHERDUCK_PATH'))
        conn.sql('create database if not exists apiService;')
        conn.sql('USE apiService;')
        return conn
    else: 
        conn = duckdb.connect(database=os.getenv('DUCKDB_PATH', 'api-service.duckdb'))
        return conn

def create_tables_on_start(conn) -> None:
    ## Create tables if they don't exist
    conn.execute(f"""
                CREATE or replace table events (
                    user_id string, 
                    account_type STRING, 
                    date date, 
                    event_type STRING,
                    order_value float,
                    version string,
                    load_timestamp timestamp
                    );"""
                )
    conn.execute("""
                CREATE or replace table users as
                select
                    user_id,
                    country,
                    gender,
                    current_timestamp as load_timestamp
                from read_json(
                    ['user_info.json'],
                    columns={
                        user_id: 'varchar',
                        gender: 'varchar',
                        country: 'varchar'
                    },
                    sample_size=-1
                    ); 
                """
                )
    conn.execute("""
                CREATE or replace view monitor_events as
                select 
                    users.country,
                    coalesce(events.version, '') as version,
                    count(*) as nbr_events,
                from users 
                left join events on users.user_id = events.user_id
                group by all 
                """
                )
    print('Tables created and duckdb are ready for use 🦆')
    return None

# Insert into a table from a dictionary
def insert_into_table(conn, table, data:Event):
    """
    Insert into a table from the incoming dictionary
    """
    # Log the data
    print(data)
    conn.execute(f'''
                INSERT INTO {table} VALUES (
                    '{data.user_id}',
                    '{data.account_type}',
                    '{data.date}',
                    '{'' if data.event_type is None else data.event_type}',
                    {'null' if data.order_value is None else data.order_value},
                    '{data.version}',
                    current_timestamp
        )
        ''')

# Read from a table and return a list of dictionaries
def read_from_table(conn, table, country:str = None):
    """
    Read from a table and return a list of dictionaries
    """
    if country is not None:
        res = conn.execute(f"SELECT * FROM {table} WHERE country = '{country}'").fetchall()
    else:
        res = conn.execute(f'SELECT * FROM {table}').fetchall()
    # Convert to list of dictionaries
    list_of_dictionaries = [
    {'country': country, 'version': version, 'nbr_events': nbr_events}
    for country, version, nbr_events in res]
    print(list_of_dictionaries)
    return list_of_dictionaries