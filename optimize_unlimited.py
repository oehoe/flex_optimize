"""Perform optimization on set of swaprequest matches using a method not restricting cycle length."""
import time

import pulp


def optimize_unlimited(pool, matches):
    """Output set of cycles (array of matches) which gives the highest number of matches
         and the highest weight for that number of matches."""
    start = time.monotonic()
    print(matches)
    requests, lim_matches, total_weight = requests_and_matches(matches)

    swaps = pulp.LpVariable.dicts('Swap', lim_matches, cat='Binary')

    model = pulp.LpProblem("DutySwap", pulp.LpMaximize)
    model += pulp.lpSum(swaps[(p1, p2)] * total_weight + weight for (match_id, p1, p2, weight) in matches)

    for p in requests:
        model += pulp.lpSum(swaps[(p1, p2)] for (p1, p2) in lim_matches if p1 == p) <= 1
        model += pulp.lpSum(swaps[(p1, p2)] for (p1, p2) in lim_matches if p2 == p) <= 1
        model += (pulp.lpSum(swaps[(p1, p2)] for (p1, p2) in lim_matches if p1 == p)
                  == pulp.lpSum(swaps[(p1, p2)] for (p1, p2) in lim_matches if p2 == p))

    model.solve()

    # Exception is raised when no optimal solution is found
    assert model.status == pulp.LpStatusOptimal

    swap_count = 0
    chosen_matches = []
    for (match_id, p1, p2, weight) in matches:
        if pulp.value(swaps[(p1, p2)]) == 1:
            chosen_matches.append((match_id, p1, p2))
            swap_count += 1
            print(f"{p1}'s duty goes to {p2}")
    print("Total swaps: ", swap_count)

    result, max_steps = create_result_array(chosen_matches)

    runtime = round(time.monotonic() - start, 1)
    print(f'Duration: {runtime} seconds')

    return {
        'type': 'unlimited',
        'pool': pool,
        'success': True,
        'swapCount': swap_count,
        'maxSteps': max_steps,
        'runtime': runtime,
        'result': result
    }


def requests_and_matches(matches):
    """Preprocess matches to create list of requests and matches"""
    # find sum of all weights to be used to prioritize max swaps
    total_weight = sum(weight for (match_id, a, b, weight) in matches) + 1

    requests = []
    lim_matches = []
    for (match_id, a, b, weight) in matches:
        lim_matches.append((a, b))
        if a not in requests:
            requests.append(a)
        if b not in requests:
            requests.append(b)
    return requests, lim_matches, total_weight


def create_result_array(chosen_matches):
    """Create output array from selected matches"""
    result = []
    this_cycle = []
    max_steps = 0
    while len(chosen_matches) > 0:
        if len(this_cycle) == 0:
            this_cycle.append({'id': chosen_matches[0][0], 'from': chosen_matches[0][1], 'to': chosen_matches[0][2]})
            chosen_matches.pop(0)

        for index, (match_id, p1, p2) in enumerate(chosen_matches):
            if this_cycle[0]['from'] == p2 and this_cycle[-1]['to'] == p1:
                this_cycle.append({'id': match_id, 'from': p1, 'to': p2})
                chosen_matches.pop(index)
                result.append(this_cycle)
                if len(this_cycle) > max_steps:
                    max_steps = len(this_cycle)
                this_cycle = []
                break
            elif this_cycle[-1]['to'] == p1:
                this_cycle.append({'id': match_id, 'from': p1, 'to': p2})
                chosen_matches.pop(index)
                break
    return result, max_steps


# test_matches = [
#     ('id1', 'Amy', 'Blake', 2), ('id2', 'Blake', 'Claire', 5),
#     ('id3', 'Claire', 'Drew', 5), ('id4', 'Drew', 'Emma', 7),
#     ('id5', 'Emma', 'Flynn', 3), ('id6', 'Flynn', 'Gabi', 4),
#     ('id7', 'Gabi', 'Hana', 5), ('id8', 'Hana', 'Izzy', 3),
#     ('id16', 'Izzy', 'Jill', 6), ('id17', 'Jill', 'Amy', 3),
#     # one on one
#     ('id9', 'Blake', 'Amy', 3), ('id10', 'Claire', 'Blake', 2),
#     ('id11', 'Emma', 'Drew', 5),
#     # three point
#     ('id12', 'Gabi', 'Emma', 7), ('id13', 'Drew', 'Blake', 7),
#     # four point
#     ('id14', 'Flynn', 'Claire', 1), ('id15', 'Jill', 'Gabi', 4)
# ]
#
# test_matches2 = [
#     ('id1', 'Anna', 'Bert', 2), ('id2', 'Bert', 'Coen', 5),
#     ('id3', 'Coen', 'Bert', 2), ('id4', 'Coen', 'Anna', 7),
#     ('id5', 'Bert', 'Daan', 8), ('id6', 'Daan', 'Coen', 5)
# ]

# print(optimize_unlimited('test', test_matches3))
