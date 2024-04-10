# https://stackoverflow.com/questions/78292364/linear-programming-problem-with-variable-multi-way-duty-swap

import networkx
import pulp


def optimize(matches, max_steps=2):
    # find sum of all weights to be used to prioritize max swaps
    max_weight = sum(weight for (match_id, a, b, weight) in matches) + 1

    graph = networkx.DiGraph()
    for (match_id, a, b, weight) in matches:
        graph.add_edge(a, b)

    # default is one-on-one swaps (max_cycle_order = 2)
    max_cycle_order = 2
    if isinstance(max_steps, int):
        max_cycle_order = abs(max_steps)
    cycles = tuple(networkx.simple_cycles(graph, length_bound=max_cycle_order))

    cycle_names = ['_'.join(c) for c in cycles]

    # Create weight for each cycle to be used by LP solver
    cycle_orders = []
    for c in cycles:
        sum_weights = 0
        for vertex in c:
            for (match_id, v1, v2, weight) in matches:
                if vertex == v2:
                    sum_weights += weight
                    break
        cycle_orders.append(max_weight * len(c) + sum_weights)

    selectors = pulp.LpVariable.matrix(
        name='cycle', indices=cycle_names, cat=pulp.LpBinary,
    )

    prob = pulp.LpProblem(name='swaps', sense=pulp.LpMaximize)
    prob.setObjective(pulp.lpDot(selectors, cycle_orders))

    for vertex in graph.nodes:
        # create list of all cycles where vertex (request) is used
        group = [
            selector
            for selector, cycle in zip(selectors, cycles)
            if vertex in cycle
        ]
        # maximize total of these cycles to 1 or smaller to not double use a request
        prob.addConstraint(
            name=f'excl_{vertex}',
            constraint=pulp.lpSum(group) <= 1,
        )

    prob.solve()
    assert prob.status == pulp.LpStatusOptimal

    # process selected cycles for output
    print('Selected cycles:')
    swap_count = 0
    result = []
    for cycle, selector in zip(cycles, selectors):
        if selector.value() > 0.5:
            cycle_result = []
            swap_count += len(cycle)
            print(', '.join(cycle))
            for c in range(0, len(cycle)):
                d = c + 1
                if d > len(cycle) - 1:
                    d = 0
                for (match_id, r1, r2, weight) in matches:
                    if cycle[c] == r1 and cycle[d] == r2:
                        cycle_result.append(match_id)
                        break
            result.append(cycle_result)

    output = {
        "status": 1,
        "result": result,
        "swapCount": swap_count
    }
    return output


# test function call
# optimize([
#     ('id1', 'Amy', 'Blake', 2), ('id2', 'Blake', 'Claire', 5), ('id3', 'Claire', 'Drew', 5), ('id4', 'Drew', 'Emma', 7),
#     ('id5', 'Emma', 'Flynn', 3), ('id6', 'Flynn', 'Gabi', 4), ('id7', 'Gabi', 'Hana', 5), ('id8', 'Hana', 'Izzy', 3),
#     ('id16', 'Izzy', 'Jill', 6), ('id17', 'Jill', 'Amy', 3),
#     # one on one
#     ('id9', 'Blake', 'Amy', 3), ('id10', 'Claire', 'Blake', 2), ('id11', 'Emma', 'Drew', 5),
#     # three point
#     ('id12', 'Gabi', 'Emma', 7), ('id13', 'Drew', 'Blake', 7),
#     # four point
#     ('id14', 'Flynn', 'Claire', 1), ('id15', 'Jill', 'Gabi', 4)
# ], 4)
