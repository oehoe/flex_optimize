import pulp
import json

f = open('optimize.json')
jsonData = json.load(f)
f.close()

# PROCESS SWAP DATA. CREATE LIST OF MATCHES AND LIST OF REQUESTS
complete_matches = []
matches = []
requests = []
for match in jsonData['matchData']:
    complete_matches.append((match['from'], match['to'], match['id'], match['weight']))
    matches.append((match['from'], match['to']))
    if match['from'] not in requests:
        requests.append(match['from'])
    if match['to'] not in requests:
        requests.append(match['to'])


def optimize():
    swaps = pulp.LpVariable.dicts('Swap', matches, cat='Binary')
    model = pulp.LpProblem("DutySwap", pulp.LpMaximize)
    model += pulp.lpSum(swaps[(p1, p2)] for (p1, p2) in matches)
    # MODEL restrictions.
    # - Every request can only be in the result one time (first two restrictions)
    # - Every person swapping a duty away needs to get a duty back
    for p in requests:
        model += pulp.lpSum(swaps[(p1, p2)] for (p1, p2) in matches if p1 == p) <= 1
        model += pulp.lpSum(swaps[(p1, p2)] for (p1, p2) in matches if p2 == p) <= 1
        model += (pulp.lpSum(swaps[(p1, p2)] for (p1, p2) in matches if p1 == p)
                  == pulp.lpSum(swaps[(p1, p2)] for (p1, p2) in matches if p2 == p))
    model.solve()
    a = 0
    opt_matches = []
    for (p1, p2) in matches:
        if pulp.value(swaps[(p1, p2)]) == 1:
            a += 1
            for (q1, q2, match_id, weight) in complete_matches:
                if p1 == q1 and p2 == q2:
                    opt_matches.append((q1, q2, match_id, weight))
                    break
    print("Total swaps: ", a)
    return opt_matches


def one_on_one():
    swaps = pulp.LpVariable.dicts('Swap', matches, cat='Binary')
    model = pulp.LpProblem("DutySwap", pulp.LpMaximize)
    model += pulp.lpSum(swaps[(p1, p2)] for (p1, p2) in matches)
    # Limit to one on one swaps
    for (p1, p2) in matches:
        if (p2, p1) in matches:
            model += pulp.lpSum(swaps[(p1, p2)]) == pulp.lpSum(swaps[(p2, p1)])
        else:
            model += swaps[(p1, p2)] == 0

    # MODEL restrictions.
    # - Every request can only be in the result one time (first two restrictions)
    # - Every person swapping a duty away needs to get a duty back
    for p in requests:
        model += pulp.lpSum(swaps[(p1, p2)] for (p1, p2) in matches if p1 == p) <= 1
        model += pulp.lpSum(swaps[(p1, p2)] for (p1, p2) in matches if p2 == p) <= 1
        model += (pulp.lpSum(swaps[(p1, p2)] for (p1, p2) in matches if p1 == p)
                  == pulp.lpSum(swaps[(p1, p2)] for (p1, p2) in matches if p2 == p))
    model.solve()
    a = 0
    opt_matches = []
    for (p1, p2) in matches:
        if pulp.value(swaps[(p1, p2)]) == 1:
            a += 1
            for (q1, q2, match_id, weight) in complete_matches:
                if p1 == q1 and p2 == q2:
                    opt_matches.append((q1, q2, match_id, weight))
                    break
    return opt_matches


optimize()
# one_on_one()
