from flask import Flask, request
from optimize import Optimize
from json import dumps
from waitress import serve
from jsonschema import validate, ValidationError
import logging
import sys
from copy import deepcopy

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
schema = {
    "type": "object",
    "properties": {
        "requestPool": {"type": "string"},
        "requestData": {"type": "array",
                        "items": {"type": "object",
                                  "properties": {
                                      "id": {"type": "string"},
                                      "from": {"type": "string"},
                                      "to": {"type": "string"},
                                      "weight": {"type": "number"}
                                  },
                                  "required": ["id", "from", "to", "weight"]
                                  }
                        },
        "maxSteps": {"type": "number"},
    },
    "required": ["requestPool", "requestData"],
}

# CREATE FLASK APP
api = Flask(__name__)


@api.post('/optimize')
def get_results():
    matches = []
    try:
        # print(request.json)
        validate(instance=request.json, schema=schema)
        for match in request.json['requestData']:
            matches.append((match['from'], match['to'], match['id'], match['weight']))
        op = Optimize(matches)
        one_on_one = op.one_on_one()
        multipoint = op.optimize()
        output = {"status": 1,
                  'one_on_one': group_results(one_on_one),
                  'one_on_one_count': len(one_on_one),
                  'multipoint': group_results(multipoint),
                  'multipoint_count': len(multipoint)
                  }
        # print(len(output['greedy']), len(output['nx']), len(output['one_on_one']), len(output['multipoint']))
        log.info("Success")
        return dumps(output)
    except ValidationError:
        log.error("Request body incorrect format")
        return '{"status": 0, "error":"Request body incorrect format"}'
    except:
        log.error("Unknown error")
        return '{"status": 0, "error":"Error in optimization"}'


def group_results(results):
    opt_matches = deepcopy(results)
    grouped = []
    current_match = ("", "", "", 0)
    current_set = []
    while len(opt_matches) > 0:
        found = False
        for (q1, q2, match_id, weight) in opt_matches:
            if current_match[1] == q1:
                found = True
                current_set.append((q1, q2, match_id, weight))
                current_match = (q1, q2, match_id, weight)
                opt_matches.remove((q1, q2, match_id, weight))
                break
        if found is False:
            if len(current_set) > 0:
                # print("Length current set", len(current_set))
                grouped.append(current_set)
            current_match = opt_matches[0]
            opt_matches.remove(opt_matches[0])
            current_set = [current_match]
    if len(current_set) > 0:
        # print("Length current set", len(current_set))
        grouped.append(current_set)
    return grouped


if __name__ == '__main__':
    serve(api, host="0.0.0.0", port=5001)
    # api.run()
