from flask import Flask, request, json
from optimize import Optimize
from json import dumps

api = Flask(__name__)

@api.post('/optimize')
def get_results():
    print(request.json)
    matches = []
    for match in request.json['requestData']:
        matches.append((match['from'], match['to'], match['id'], match['weight']))
    print(matches)
    op = Optimize(matches)
    output = {}
    output['greedy'] = op.greedy()
    output['nx'] = op.nx_optimize()
    output['one_on_one'] = op.one_on_one()
    output['multipoint'] = op.optimize()
    print(len(output['greedy']), len(output['nx']), len(output['one_on_one']), len(output['multipoint']))
    return dumps(output)

if __name__ == '__main__':
    api.run()