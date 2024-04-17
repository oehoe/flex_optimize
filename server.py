"""Start server to create an endpoint to post optimization requests to."""
import logging
import sys
import json

from flask import Flask, request
from waitress import serve
from jsonschema import validate, ValidationError

from optimize import optimize


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
    """Return optimization results on posted swap request matches."""
    matches = []
    try:
        # check for valid data
        # TODO validate weights 0 - 100 ?
        validate(instance=request.json, schema=schema)

        # create tuples from input
        for match in request.json['matchData']:
            matches.append((match['id'], match['from'], match['to'], match['weight']))

        # get optimized result
        output = optimize(request.json['pool'], matches, request.json['maxSteps'])
        log.info('Optimization completed')
        return json.dumps(output)
    except ValidationError:
        log.error('Request body incorrect format')
        return json.dumps({'success': False, 'error': 'Request body incorrect format'})
    except AssertionError:
        log.error('Optimal solution not found')
        return json.dumps({'success': False, 'error': 'Optimal solution not found'})
    except Exception as error:
        log.error('Unknown error', error)
        return json.dumps({'success': False, 'error': 'Error in optimization'})


if __name__ == '__main__':
    serve(api, host='0.0.0.0', port=5001)
