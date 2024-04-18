"""Start server to create an endpoint to post optimization requests to."""
import logging
import sys
import json

from flask import Flask, request
from waitress import serve
from jsonschema import validate, ValidationError

from optimize_bipartite import max_weight_matching
from optimize_variable import optimize_variable
from optimize_unlimited import optimize_unlimited


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
        validate(instance=request.json, schema=schema)

        # create tuples from input
        for match in request.json['matchData']:
            matches.append((match['id'], match['from'], match['to'], match['weight']))

        pool = request.json['pool']
        optimizer = request.json['optimizer']

        # get optimized result
        if optimizer == 'bipartite':
            output = max_weight_matching(pool, matches)
        elif optimizer == 'variable' and 'maxSteps' in request.json.keys():
            output = optimize_variable(pool, matches, request.json['maxSteps'])
        elif optimizer == 'variable':
            raise ValidationError('\'maxSteps\' is a required property with optimizer \'variable\'')
        elif optimizer == 'unlimited':
            output = optimize_unlimited(pool, matches)

        log.info('Optimization completed')
        return json.dumps(output)
    except ValidationError as error:
        log.error('Request body incorrect format: ' + error.args[0])
        return json.dumps({'success': False, 'error': 'Request body incorrect format: ' + error.args[0]})
    except AssertionError:
        log.error('Optimal solution not found')
        return json.dumps({'success': False, 'error': 'Optimal solution not found'})
    except Exception as error:
        log.error('Unknown error', error)
        return json.dumps({'success': False, 'error': 'Error in optimization'})


if __name__ == '__main__':
    serve(api, host='0.0.0.0', port=5001)
