"""Perform optimization on set of swaprequest matches using a bipartite graph."""
import time

import networkx as nx


def greedy(pool, matches):
    """Find maximal_matching (greedy) set of matches."""
    start = time.monotonic()

    graph = nx.Graph()
    requests, pairs = requests_and_pairs(matches)

    graph.add_nodes_from(requests, bipartite=0)
    graph.add_nodes_from(requests, bipartite=1)

    for (r1, r2) in pairs:
        graph.add_edge(r1, r2)

    maximal_matching = nx.maximal_matching(graph)

    result, swap_count = create_result_array(matches, maximal_matching, pool)

    runtime = round(time.monotonic() - start, 1)
    print(f'Duration: {runtime} seconds')

    return {
        'type': 'maximal_matching',
        'pool': pool,
        'success': True,
        'swapCount': swap_count,
        'maxSteps': 2,
        'runtime': runtime,
        'result': result
    }


def max_weight_matching(pool, matches):
    """Find max weight matched set of matches. (Optimized one-on-one)."""
    start = time.monotonic()

    graph = nx.Graph()
    requests, pairs = requests_and_pairs(matches)

    graph.add_nodes_from(requests, bipartite=0)
    graph.add_nodes_from(requests, bipartite=1)

    for (r1, r2) in pairs:
        counter = 0
        avg_weight = 0
        for (match_id, a, b, weight) in matches:
            if b == r1 or b == r2:
                avg_weight += weight / 2
                counter += 1
            if counter > 1:
                break
        graph.add_edge(r1, r2, weight=avg_weight)
        print(r1, r2, avg_weight)

    max_weight = nx.max_weight_matching(graph)

    result, swap_count = create_result_array(matches, max_weight, pool)

    runtime = round(time.monotonic() - start, 1)
    print(f'Duration: {runtime} seconds')

    return {
        'type': 'bipartite',
        'pool': pool,
        'success': True,
        'swapCount': swap_count,
        'maxSteps': 2,
        'runtime': runtime,
        'result': result
    }


def requests_and_pairs(matches):
    requests = []
    pairs = []
    check_matches = []
    for (match_id, a, b, weight) in matches:
        check_matches.append((a, b))
        if a not in requests:
            requests.append(a)
        if b not in requests:
            requests.append(b)
        if (b, a) in check_matches:
            if (a, b) not in pairs and (b, a) not in pairs:
                pairs.append((a, b))
    return requests, pairs


def create_result_array(matches, matching, pool):
    result = []
    swap_count = len(matching) * 2
    for (r1, r2) in matching:
        cycle_result = []
        for (match_id, a, b, weight) in matches:
            if (r1 == a and r2 == b) or (r1 == b and r2 == a):
                cycle_result.append({'id': match_id, 'from': a, 'to': b})
            if len(cycle_result) == 2:
                break
        result.append({'pool': pool, 'cycle': cycle_result})
    return result, swap_count


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

# print(greedy('test', test_matches))
# print(max_weight_matching('test', test_matches))
