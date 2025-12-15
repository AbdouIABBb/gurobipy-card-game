import sys
from gurobipy import *
from read_instance import read_instance
from save_submission import save_submission
 
def solve_exact(filename):
    print(f"--- Processing {filename} ---")
 
    # 1. Lecture des données
    try:
        V, E, R, C, X, video_size, LD, connections, requests = read_instance(filename)
        print(f"Data loaded: {V} videos, {E} endpoints, {R} requests, {C} caches.")
    except Exception as e:
        print(f"Error reading input: {e}")
        return
 
    # 2. Construction du Modèle
    model = Model("HashCodeExact")
 
    # 👉 PARAMÈTRES IMPOSÉS PAR LE PROF
    model.Params.MIPGap = 5e-3      # 0.5% d'écart accepté
    model.Params.OutputFlag = 1     # Afficher les traces
 
    # Variables
    x = model.addVars(V, C, vtype=GRB.BINARY, name="x")
    y = model.addVars(R, C, vtype=GRB.BINARY, name="y")
 
    # 3. Objectif
    obj = 0
    for r, (v, e, n) in enumerate(requests):
        for c in range(C):
            if c in connections[e]:    # Si le cache est connecté
                dc_lat = LD[e]
                cache_lat = connections[e][c]
                saving = (dc_lat - cache_lat) * n
                if saving > 0:
                    obj += saving * y[r, c]
            # else: y[r,c] sera contraint à 0 plus bas
 
    model.setObjective(obj, GRB.MAXIMIZE)
 
    # 4. Contraintes
 
    # C1. Une requête servie au maximum une fois
    for r in range(R):
        model.addConstr(sum(y[r, c] for c in range(C)) <= 1)
 
    # C2. Contrainte de couplage y[r,c] <= x[v(r),c]
    for r, (v, e, n) in enumerate(requests):
        for c in range(C):
            model.addConstr(y[r, c] <= x[v, c])
 
    # C3. Capacité des caches
    for c in range(C):
        model.addConstr(sum(video_size[v] * x[v, c] for v in range(V)) <= X)
 
    # C4. y[r,c] = 0 si le cache n'est pas connecté
    for r, (v, e, n) in enumerate(requests):
        for c in range(C):
            if c not in connections[e]:
                model.addConstr(y[r, c] == 0)
 
    #  Générer le fichier videos.mps
    print("Generating videos.mps...")
    model.write("videos.mps")
 
    # 5. Résolution
    print("Starting optimization...")
    model.optimize()
 
    # 6. Sauvegarde des résultats
    if model.status == GRB.OPTIMAL or model.status == GRB.TIME_LIMIT:
        print(f"\nOptimal objective = {model.objVal:,.0f}")
        #  Le fichier  'videos.out'
        output_filename = "videos.out"
        save_submission(output_filename, x, C, V)
        print(f"File '{output_filename}' created successfully.")
    else:
        print("No feasible solution found.")
 
    return model, x, y
 
if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print("Usage: python videos.py <path_to_dataset>")
        sys.exit(1)
    input_file = sys.argv[1]
    solve_exact(input_file)