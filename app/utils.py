import duckdb
from models import Event, User


# Connect to duckdb
def connect_to_duckdb():
    conn = duckdb.connect(database='apiService.duckdb')
    print('Connected to duckdb')
    return conn

# Insert into a table from a dictionary
def insert_into_table(conn, table, data:Event):
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
    if country is not None:
        res = conn.execute(f"SELECT * FROM {table} WHERE country = '{country}'").fetchall()
    else:
        res = conn.execute(f'SELECT * FROM {table}').fetchall()
    # Convert to list of dictionaries
    print(res)
    list_of_dictionaries = [
    {'country': country, 'version': version, 'nbr_events': nbr_events}
    for country, version, nbr_events in res]
    print(list_of_dictionaries)
    return list_of_dictionaries