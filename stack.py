import pulp

# Sample data: List of requests
participants = ['Adam', 'Beth', 'Cleo', 'Drew', 'Emma', 'Finn', 'Gabi', 'Hana', 'Izzy', 'Jill']

# Sample data: Define which swaps are allowed based on your constraints. e.g. Alice to Bob
allowed_swaps = [('Adam', 'Beth'), ('Beth', 'Cleo'), ('Cleo', 'Drew'), ('Drew', 'Emma'),
                 ('Emma', 'Finn'), ('Finn', 'Gabi'), ('Gabi', 'Hana'), ('Hana', 'Izzy'),
                 ('Izzy', 'Jill'), ('Jill', 'Adam'),
                 # one on one
                 ('Beth', 'Adam'), ('Emma', 'Drew'),
                 # three point
                 ('Gabi', 'Emma'),
                 # four point
                 ('Finn', 'Cleo'), ('Jill', 'Gabi')]


swaps = pulp.LpVariable.dicts('Swap', allowed_swaps, cat='Binary')


model = pulp.LpProblem("DutySwap", pulp.LpMaximize)

model += pulp.lpSum(swaps[(p1, p2)] for (p1, p2) in allowed_swaps)

for p in participants:
    model += pulp.lpSum(swaps[(p1, p2)] for (p1, p2) in allowed_swaps if p1 == p) <= 1
    model += pulp.lpSum(swaps[(p1, p2)] for (p1, p2) in allowed_swaps if p2 == p) <= 1
    model += (pulp.lpSum(swaps[(p1, p2)] for (p1, p2) in allowed_swaps if p1 == p)
              == pulp.lpSum(swaps[(p1, p2)] for (p1, p2) in allowed_swaps if p2 == p))
print(model)

status = model.solve()
for (p1, p2) in allowed_swaps:
    if pulp.value(swaps[(p1, p2)]) == 1:
        print(f"{p1}'s duty goes to {p2}")

# This will output
# Adam's duty goes to Beth
# Cleo's duty goes to Drew
# Drew's duty goes to Emma
# Emma's duty goes to Finn
# Gabi's duty goes to Hana
# Hana's duty goes to Izzy
# Izzy's duty goes to Jill
# Beth's duty goes to Adam
# Finn's duty goes to Cleo
# Jill's duty goes to Gabi