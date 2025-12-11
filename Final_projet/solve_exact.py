from gurobipy import *
from data_parser import read_instance
 
 
def solve_exact(filename):
 
   
    # -----------------------------
    # Load data
    # -----------------------------
    V, E, R, C, X, video_size, LD, connections, requests = read_instance(filename)
 
    # -----------------------------
    # Build model
    # -----------------------------
    model = Model("HashCodeExact")
 
    # Variables
    x = model.addVars(V, C, vtype=GRB.BINARY, name="x")
    y = model.addVars(R, C, vtype=GRB.BINARY, name="y")
 
    # -----------------------------
    # Objective
    # -----------------------------
    obj = 0
    for r, (v, e, n) in enumerate(requests):
        for c in range(C):
            if c in connections[e]:    # cache is connected
                dc_lat = LD[e]
                cache_lat = connections[e][c]
                saving = (dc_lat - cache_lat) * n
                if saving > 0:
                    obj += saving * y[r, c]
            # else: y[r,c] must be constrained to 0 later
 
    model.setObjective(obj, GRB.MAXIMIZE)
 
    # -----------------------------
    # Constraints
    # -----------------------------
 
    # 1. One cache at most serves a request
    for r in range(R):
        model.addConstr(sum(y[r, c] for c in range(C)) <= 1)
 
    # 2. Coupling constraints y[r,c] ≤ x[v(r),c]
    for r, (v, e, n) in enumerate(requests):
        for c in range(C):
            model.addConstr(y[r, c] <= x[v, c])
 
    # 3. Caches capacity
    for c in range(C):
        model.addConstr(sum(video_size[v] * x[v, c] for v in range(V)) <= X)
 
    # 4. y[r,c] = 0 if cache not connected
    for r, (v, e, n) in enumerate(requests):
        for c in range(C):
            if c not in connections[e]:
                model.addConstr(y[r, c] == 0)
 
    # -----------------------------
    # Solve
    # -----------------------------
    model.optimize()
 
    # -----------------------------
    # Print solution summary
    # -----------------------------
    print("\nOptimal objective =", model.objVal)
 
    return model, x, y
 
 
 
if __name__ == "__main__":
    solve_exact("trending_4000_10k.in")