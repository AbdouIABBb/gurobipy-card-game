import json
import gurobipy as gp
from gurobipy import GRB
from pathlib import Path

# === Charger les données ===
with open("data/lot_sizing_data.json") as f:
    data = json.load(f)

name = data["name"]
H = int(data["H"])  # nombre de périodes
D = [float(val) for val in data["demand"]]
C = [float(val) for val in data["var_cost"]]
F = [float(val) for val in data["setup_cost"]]
h = [float(val) for val in data["hold_cost"]]
Q_min = float(data["Qmin"])
Q_max = float(data["Qmax"])
I0 = float(data["I0"])

# === Validation basique ===
assert len(D) == H and len(C) == H and len(F) == H and len(h) == H, "Longueurs incohérentes"
assert 0 <= Q_min <= Q_max, "Qmin doit être inférieur ou égal à Qmax"

# === Création du modèle ===
with gp.Env() as env, gp.Model(name, env=env) as model:
    
    # Variables de décision
    x = model.addVars(H, lb=0.0, vtype=GRB.CONTINUOUS, name="x")  # production
    y = model.addVars(H, vtype=GRB.BINARY, name="y")               # production ou non
    I = model.addVars(H, lb=0.0, vtype=GRB.CONTINUOUS, name="I")   # inventaire

    # Fonction objectif 
    obj = gp.quicksum(C[t] * x[t] + F[t] * y[t] + h[t] * I[t] for t in range(H))
    model.setObjective(obj, GRB.MINIMIZE)

    # = Contraintes ==

    # Bilan des stocks
    for t in range(H):
        if t == 0:
            model.addConstr(I0 + x[t] - D[t] == I[t], name=f"inv_balance_{t}")
        else:
            model.addConstr(I[t-1] + x[t] - D[t] == I[t], name=f"inv_balance_{t}")

    # Capacité min et max liées à y_t
    for t in range(H):
        model.addConstr(x[t] <= Q_max * y[t], name=f"cap_max_{t}")
        model.addConstr(x[t] >= Q_min * y[t], name=f"cap_min_{t}")

    # === Optimisation ===
    model.optimize()

    # === Résultats ===
    if model.SolCount > 0:
        print(f"\n✅ Solution trouvée : coût total = {model.ObjVal:.2f}")
        for t in range(H):
            print(f"t={t:2d}: y={int(y[t].X)} x={x[t].X:.1f} I={I[t].X:.1f}")
    else:
        print("⚠️ Pas de solution trouvée.")
