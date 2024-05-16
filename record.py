from fastapi import Body,FastAPI
from betamax import Betamax
from requests import Session
from loguru import logger
from pydantic import BaseModel, Field
from typing import Annotated
from betamax_serializers import pretty_json
import json

import ulid
import duckdb

class RecordingResuest(BaseModel):
    id: str = Field(default_factory=ulid.ulid)
    name: str
    method: str
    url: str

app = FastAPI()

Betamax.register_serializer(pretty_json.PrettyJSONSerializer)
with Betamax.configure() as config:
    config.cassette_library_dir = 'cassettes'
    config.default_cassette_options['serialize_with'] = 'prettyjson'

@app.get("/recordings")
def get_recordings():
    duck_conn = duckdb.connect()
    return json.loads(duck_conn.sql("SELECT id,name,method from read_ndjson('recordings.json');").df().to_json(orient='records', lines=False))

@app.post("/recordings")
def create_record_request(recording_resuest: RecordingResuest):
    duck_conn = duckdb.connect()
    duck_conn.sql("CREATE TABLE recordings (id VARCHAR PRIMARY KEY, name VARCHAR, method VARCHAR, url VARCHAR);")
    duck_conn.sql("COPY recordings from 'recordings.json';")
    duck_conn.sql(f"INSERT INTO recordings VALUES ('{recording_resuest.id}', '{recording_resuest.name}', '{recording_resuest.method}', '{recording_resuest.url}');")
    duck_conn.sql("COPY (SELECT * FROM recordings) TO 'recordings.json';")
    duck_conn.close()
    return {"id": recording_resuest.id, 
            "method": recording_resuest.method, 
            "url": "/record/" + recording_resuest.id}

@app.get("/record/{r_id}")
def record_get(r_id: str):
    recording_info = duckdb.sql(f"SELECT name, method, url from read_ndjson('./recordings.json') where id = '{r_id}';").df().to_dict()
    logger.debug(f"Recording info: {recording_info}")
    logger.debug(f"Recording info: {recording_info['name'][0]}")
    with Betamax(Session()) as vcr:
        vcr.use_cassette(recording_info['name'][0], record='new_episodes')
        response = vcr.session.get(recording_info['url'][0])
        return response.json()

@app.post("/record/{r_id}")
def record_put(r_id: str, body: dict):
    recording_info = duckdb.sql(f"SELECT name, method, url from read_ndjson('recordings.json') where id = '{r_id}';").df().to_dict()
    logger.debug(f"Recording info: {recording_info['name'][0]}")
    
    with Betamax(Session()) as vcr:
        vcr.use_cassette(recording_info['name'][0], record='new_episodes')
        response = vcr.session.post(recording_info['url'][0], json=body.to_json(), headers={"Content-Type": "application/json"})
        return response.json()