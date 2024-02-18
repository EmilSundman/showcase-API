from fastapi import FastAPI
from typing import Optional
from utils import connect_to_duckdb, insert_into_table, read_from_table
from models import Event, User
app = FastAPI()


# Run script on startup
@app.on_event("startup")
async def startup_event():
    conn = connect_to_duckdb()
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

## Enable another services to post data to this service on endpoint /receive_event and print it
# ! Sending to // which is a bit weird? 
@app.post("//receive_event")
async def receive_event(event: Event) -> dict:
    print(event)
    conn = connect_to_duckdb()
    insert_into_table(conn, 'events', event)
    return {"message": "Event received"}

@app.get("//monitor")
async def monitor(country: Optional[str] = None):
    conn = connect_to_duckdb()
    res = read_from_table(conn, 'monitor_events', country)
    return res
