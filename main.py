from fastapi import Body,FastAPI
from betamax import Betamax
from requests import Session
from loguru import logger
from pydantic import BaseModel, Field
from typing import Annotated
import json

import ulid
import duckdb


app = FastAPI()
with Betamax.configure() as config:
    config.cassette_library_dir = 'cassettes'
    config.default_cassette_options['record_mode'] = 'none'

@app.get("/recordings")
def get_recordings():
    duck_conn = duckdb.connect()
    return json.loads(duck_conn.sql("SELECT id,name,method,url from read_ndjson('recordings.json');").df().to_json(orient='records', lines=False))


@app.get("/replay/{r_id}")
def replay_get(r_id: str):
    recording_info = duckdb.sql(f"SELECT name, method, url from read_ndjson('./recordings.json') where id = '{r_id}';").df().to_dict()
    logger.debug(f"Recording info: {recording_info}")
    logger.debug(f"Recording info: {recording_info['name'][0]}")
    with Betamax(Session()) as vcr:
        vcr.use_cassette(recording_info['name'][0])
        response = vcr.session.get(recording_info['url'][0])
        return response.json()

@app.post("/replay/{r_id}")
def replay_post(r_id: str):
    recording_info = duckdb.sql(f"SELECT name, method, url from read_ndjson('recordings.json') where id = '{r_id}';").df().to_dict()
    logger.debug(f"Recording info: {recording_info['name'][0]}")
    
    with Betamax(Session()) as vcr:
        vcr.use_cassette(recording_info['name'][0])
        response = vcr.session.post(recording_info['url'][0])
        return response.json()