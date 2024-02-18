from fastapi import FastAPI, HTTPException
from typing import Optional
from pydantic import ValidationError
from utils import connect_to_duckdb, insert_into_table, read_from_table, create_tables_on_start
from models import Event, User
app = FastAPI()


# Run script on startup
@app.on_event("startup")
async def startup_event():
    """
    Run script on startup.
    """
    # Connect to duckdb
    try: 
        conn = connect_to_duckdb()
        print('Connected to duckdb 🦆')
        ##  Create tables if they don't exist
        create_tables_on_start(conn)
        return None
    except Exception as e:
        print(f'Error connecting to duckdb: {e}')
        raise e

## Enable another services to post data to this service on endpoint /receive_event and print it
@app.post("//receive_event")
async def receive_event(event: Event) -> dict:
    """
    Receive an event and insert it into the database.
    """
    try:
        conn = connect_to_duckdb()
        insert_into_table(conn, 'events', event)
        return {"message": "Event received"}
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Invalid data: {e}")
        

@app.get("//monitor")
async def monitor(country: Optional[str] = None) -> list[dict]:
    """
    Return the number of events per country.
    """
    try:
        conn = connect_to_duckdb()
        res = read_from_table(conn, 'monitor_events', country)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not retrieve data for {{'country':'{country}'}}: {e}")