# Tapezilla
Tapezilla acts as a betamax cassete repository which can be recoded and replayed via an api

## Concept
1. Wraps a betamax in an API form [https://betamax.readthedocs.io/en/latest/introduction.html]
2. Turn betamax recodings of mocks into a containerised mock server for use in dev / qa environments.


## Example usage for recording

1. start in record mode
`poetry run fastapi dev record.py`

2. register for a new recording
`curl -vv -H 'Content-Type: application/json' -XPOST --data '{"name": "vehicle-makes", "method": "get", "url": "https://vpic.nhtsa.dot.gov/api/vehicles/getallmakes?format=json"}' localhost:8000/recordings`

3. get the record id for the recording
`curl -vv -H 'Content-Type: application/json' -XGET localhost:8000/recordings`

4. do the recording
`curl -vv -H 'Content-Type: application/json' -XGET localhost:8000/recording/{id}`

5. checkin the new cassette and updated recordings.json

## Example usage for replay / mock mode

1. get the replay
`curl -vv -H 'Content-Type: application/json' -XGET localhost:8000/replay/{id}`

2. use this in a config url to replay
