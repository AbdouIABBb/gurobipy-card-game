import gurobipy as gp
from gurobipy import GRB
import math

with gp.Env() as env, gp.Model(env=env) as model:

    # --- Variables de décision ---
    r = model.addVar(lb=0.0,ub=1 , vtype=GRB.CONTINUOUS, name="r")
    R = model.addVar(lb=0.0,ub=1 , vtype=GRB.CONTINUOUS, name="R")
    h = model.addVar(lb=0.0,ub=1 , vtype=GRB.CONTINUOUS, name="h")
    obj1 = model.addVar(lb=0.0,ub=1 , vtype=GRB.CONTINUOUS, name="obj1")
    A_bot1 = model.addVar(lb=0.0,ub=1 , vtype=GRB.CONTINUOUS)
    A_lat1= model.addVar(lb=0.0,ub=1 , vtype=GRB.CONTINUOUS)


   
    # --- Fonction objectif : maximiser le volume ---
    # V = (π * h / 3) * (R² + Rr + r²)
    obj = (math.pi / 3.0) * h * (gp.nlfunc.square(R) + R * r + gp.nlfunc.square(r))
    model.addConstr( obj1==obj  )
    model.setObjective(obj1, GRB.MAXIMIZE)
    
    # --- Contraintes de surface ---
    # A_bot + A_lat = 1
    A_bot = math.pi * gp.nlfunc.square(r)
    A_lat = math.pi * (R + r) * gp.nlfunc.sqrt(gp.nlfunc.square(R - r) + gp.nlfunc.square(h))

    model.addConstr( A_bot1==A_bot  )
    model.addConstr( A_lat1==A_lat  )

    model.addConstr(A_bot1 + A_lat1 == 1, name="surface")

    # --- Optimisation ---
    model.optimize()

    # --- Résultats ---
    if model.status == GRB.OPTIMAL:
        print("\n✅ Solution optimale trouvée :")
        print(f"r = {r.X:.4f}")
        print(f"R = {R.X:.4f}")
        print(f"h = {h.X:.4f}")
        print(f"Volume = {model.ObjVal:.6f}")
    else:
        print("⚠️ Aucune solution optimale trouvée.")
