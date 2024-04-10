#import json
import json

from flask import Flask, request
from optimize import optimize
# from json import dumps
from waitress import serve
from jsonschema import validate, ValidationError
import logging
import sys

# SETUP LOGGING
root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)
log = logging.getLogger(__name__)

# REQUEST SCHEMA
f = open('request_schema.json')
schema = json.load(f)
f.close()

# CREATE FLASK APP
api = Flask(__name__)


@api.post('/optimize')
def get_results():
    matches = []
    try:
        # check for valid data
        validate(instance=request.json, schema=schema)

        # create tuples from inout
        for match in request.json['matchData']:
            matches.append((match['id'], match['from'], match['to'], match['weight']))

        # get optimized result
        output = optimize(matches, request.json['maxSteps'])

        log.info("Optimization completed")
        return json.dumps(output)
    except ValidationError:
        log.error("Request body incorrect format")
        return '{"status": 0, "error":"Request body incorrect format"}'
    except Exception:
        log.error("Unknown error")
        return '{"status": 0, "error":"Error in optimization"}'


if __name__ == '__main__':
    serve(api, host="0.0.0.0", port=5001)
