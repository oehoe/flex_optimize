import networkx as nx
import pulp


class Optimize:
    def __init__(self, matches):
        self.all_matches = matches
        #self.matches = [('Alice', 'Charlie'), ('Charlie', 'Alice'), ('Alice', 'David'), ('David', 'Alice'), ('Bob', 'Charlie'), ('Charlie', 'Bob'), ('David', 'Charlie'), ('Charlie', 'David')]
        # self.matches = [('Alice', 'Bob'), ('Bob', 'Alice'), ('Bob', 'Charlie'), ('Charlie', 'David'), ('Charlie', 'Alice'), ('Charlie', 'Bob'), ('David', 'Alice')]
        self.requests = []
        self.pairs = []
        self.matches = []
        for (r1, r2, match_id, weight) in matches:
            self.matches.append((r1, r2))
        for (r1, r2) in self.matches:
            if r1 not in self.requests:
                self.requests.append(r1)
            if r2 not in self.requests:
                self.requests.append(r2)
            if (r2, r1) in self.matches:
                if (r1, r2) not in self.pairs and (r2, r1) not in self.pairs:
                    self.pairs.append((r1, r2))
                    print((r1, r2))


    def greedy(self):
        G = nx.Graph()
        G.add_nodes_from(self.requests, bipartite=0)
        G.add_nodes_from(self.requests, bipartite=1)
        for (r1, r2) in self.pairs:
            G.add_edge(r1, r2)
        matching_greedy = nx.maximal_matching(G)
        # matching_weight = nx.max_weight_matching(G)
        print(self.pairs)
        print(matching_greedy)
        output = []
        for (r1, r2) in matching_greedy:
            for (q1, q2, match_id, weight) in self.all_matches:
                if (r1 == q1 and r2 == q2) or (r1 == q2 and r2 == q1):
                    output.append((q1, q2, match_id, weight))

        #print(dumps(output))
        #print(matching_weight)
        #for (r1, r2) in matching_weight:
        #    output.append({'from':r1, 'to':r2})
        return output

    def nx_optimize(self):
        G = nx.Graph()
        G.add_nodes_from(self.requests, bipartite=0)
        G.add_nodes_from(self.requests, bipartite=1)
        for (r1, r2) in self.pairs:
            G.add_edge(r1, r2)
        matching = nx.max_weight_matching(G)
        print(self.pairs)
        print(matching)
        output = []
        for (r1, r2) in matching:
            for (q1, q2, match_id, weight) in self.all_matches:
                if (r1 == q1 and r2 == q2) or (r1 == q2 and r2 == q1):
                    output.append((q1, q2, match_id, weight))

        #print(dumps(output))
        #print(matching_weight)
        #for (r1, r2) in matching_weight:
        #    output.append({'from':r1, 'to':r2})
        return output

    def optimize(self):
        swaps = pulp.LpVariable.dicts('Swap', self.matches, cat='Binary')
        # print(swaps)
        model = pulp.LpProblem("DutySwap", pulp.LpMaximize)
        model += pulp.lpSum(swaps[(p1, p2)] for (p1, p2) in self.matches)
        # print(self.requests)
        for p in self.requests:
            model += pulp.lpSum(swaps[(p1, p2)] for (p1, p2) in self.matches if p1 == p) <= 1
            model += pulp.lpSum(swaps[(p1, p2)] for (p1, p2) in self.matches if p2 == p) <= 1
            model += (pulp.lpSum(swaps[(p1, p2)] for (p1, p2) in self.matches if p1 == p)
                      == pulp.lpSum(swaps[(p1, p2)] for (p1, p2) in self.matches if p2 == p))
        # print(model)
        status = model.solve()
        a = 0
        output = []
        for (p1, p2) in self.matches:
            if pulp.value(swaps[(p1, p2)]) == 1:
                a += 1
                for (q1, q2, match_id, weight) in self.all_matches:
                    if p1 == q1 and p2 == q2:
                        output.append((q1, q2, match_id, weight))
                        break
                print(f"{p1}'s duty goes to {p2}")
        print("Total swaps: ", a)
        return output

    def one_on_one(self):
        swaps = pulp.LpVariable.dicts('Swap', self.matches, cat='Binary')
        # print(swaps)
        model = pulp.LpProblem("DutySwap", pulp.LpMaximize)
        model += pulp.lpSum(swaps[(p1, p2)] for (p1, p2) in self.matches)
        # print(self.requests)
        for (p1, p2) in self.matches:
            if (p2, p1) in self.matches:
                model += pulp.lpSum(swaps[(p1, p2)]) == pulp.lpSum(swaps[(p2, p1)])
            else:
                model += swaps[(p1, p2)] == 0

        for p in self.requests:
            model += pulp.lpSum(swaps[(p1, p2)] for (p1, p2) in self.matches if p1 == p) <= 1
            model += pulp.lpSum(swaps[(p1, p2)] for (p1, p2) in self.matches if p2 == p) <= 1
            model += (pulp.lpSum(swaps[(p1, p2)] for (p1, p2) in self.matches if p1 == p)
                      == pulp.lpSum(swaps[(p1, p2)] for (p1, p2) in self.matches if p2 == p))
        # print(model)
        status = model.solve()
        a = 0
        output = []
        for (p1, p2) in self.matches:
            if pulp.value(swaps[(p1, p2)]) == 1:
                a += 1
                for (q1, q2, match_id, weight) in self.all_matches:
                    if p1 == q1 and p2 == q2:
                        output.append((q1, q2, match_id, weight))
                        break
                print(f"{p1}'s duty goes to {p2}")
        print("Total swaps: ", a)
        return output

# op = Optimize("test")
#op.greedy()
#op.optimize()
