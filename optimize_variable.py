"""Perform optimization on set of swaprequest matches."""
# https://stackoverflow.com/questions/78292364/linear-programming-problem-with-variable-multi-way-duty-swap
import time

import networkx as nx
import pulp


def optimize_variable(pool, matches, max_steps=2):
    """Output set of cycles (array of matches) which gives the highest number of matches
     and the highest weight for that number of matches."""
    start = time.monotonic()

    cycles, swap_requests = find_all_cycles(matches, max_steps)
    cycle_names = ['_'.join(c) for c in cycles]

    print(f'Duration simple cycles: {time.monotonic() - start}')

    cycle_orders = weights_for_cycles(matches, cycles)

    selectors = pulp.LpVariable.matrix(
        name='cycle', indices=cycle_names, cat=pulp.LpBinary,
    )

    prob = pulp.LpProblem(name='swaps', sense=pulp.LpMaximize)
    prob.setObjective(pulp.lpDot(selectors, cycle_orders))

    for request in swap_requests:
        # create list of all cycles where request is used
        group = [
            selector
            for selector, cycle in zip(selectors, cycles)
            if request in cycle
        ]
        # maximize total of these cycles to 1 or smaller to not double use a request
        prob.addConstraint(
            name=f'excl_{request}',
            constraint=pulp.lpSum(group) <= 1,
        )

    # prob.solve(pulp.PULP_CBC_CMD(timeLimit=1))
    prob.solve()

    # Exception is raised when no optimal solution is found
    assert prob.status == pulp.LpStatusOptimal

    result, swap_count = create_result_array(matches, cycles, selectors)

    runtime = round(time.monotonic() - start, 1)
    print(f'Duration: {runtime} seconds')

    return {
        'type': 'variable',
        'pool': pool,
        'success': True,
        'swapCount': swap_count,
        'maxSteps': max_steps,
        'runtime': runtime,
        'result': result
    }


def find_all_cycles(matches, max_steps):
    """Find all possible cycles within matches with length limited by max_steps."""
    graph = nx.DiGraph()
    for (match_id, a, b, weight) in matches:
        graph.add_edge(a, b)

    cycles = tuple(nx.simple_cycles(graph, length_bound=max_steps))
    swap_requests = graph.nodes
    return cycles, swap_requests


def weights_for_cycles(matches, cycles):
    """Calculate weights for all cycles based on number of requests in cycles and weight of individual requests."""
    # find sum of all weights to be used to prioritize max swaps
    total_weight = sum(weight for (match_id, a, b, weight) in matches) + 1

    cycle_orders = []
    for c in cycles:
        cycle_weights = 0
        for vertex in c:
            for (match_id, v1, v2, weight) in matches:
                if vertex == v2:
                    cycle_weights += weight
                    break
        cycle_orders.append((total_weight * len(c)) + cycle_weights + (1 / len(c)))
    return cycle_orders


def create_result_array(matches, cycles, selectors):
    """Find selected cycles and add array of matches in these cycles to the result array."""
    print('Selected cycles:')
    swap_count = 0
    result = []
    for cycle, selector in zip(cycles, selectors):
        if selector.value() > 0.5:
            len_cycle = len(cycle)
            cycle_result = []
            swap_count += len_cycle
            print(', '.join(cycle))
            for c in range(len_cycle):
                d = c + 1
                if d > len_cycle - 1:
                    d = 0
                for (match_id, r1, r2, weight) in matches:
                    if cycle[c] == r1 and cycle[d] == r2:
                        cycle_result.append({'id': match_id, 'from': r1, 'to': r2})
                        break
            result.append(cycle_result)
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
#     ('id5', 'Bert', 'Daan', 8), ('id6', 'Daan', 'Coen', 5),
#     ('id3', 'Coen', 'Bert', 3)
# ]

# print(optimize(test_matches2, 2))
# print(optimize(test_matches, 3))
