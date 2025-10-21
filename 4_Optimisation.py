import json 
import pandas as pd 
import numpy as np 
import gurobipy as gp
from gurobipy import GRB 

with open("data/portfolio-example.json", "r") as f : 
    data = json.load(f) 


n = data["num_assets"]
sigma = np.array(data["covariance"])
mu = np.array(data["expected_return"])
mu_0 = data["target_return"]
k = data["portfolio_max_size"]


with gp.Model("portfolio") as model : 
    x= model.addVars(n,lb=0 , ub=1 , vtype=GRB.CONTINUOUS , name="x")
    y= model.addVars(n, vtype=GRB.BINARY , name="y")


    risk = gp.quicksum(sigma[i,j]*x[i]*x[j] for i in range(n) for j in range (n))
    model.setObjective(risk,GRB.MINIMIZE)


      # --- Contraintes ---
    # Rendement minimal
    model.addConstr(
        gp.quicksum(mu[j] * x[j] for j in range(n)) >= mu_0,
        name="return"
    )

    # Tout le capital est investi
    model.addConstr(gp.quicksum(x[j] for j in range(n)) == 1, name="budget")

    # Maximum k actifs sélectionnés
    model.addConstr(gp.quicksum(y[j] for j in range(n)) <= k, name="max_assets") 

    # Lien entre x et y
    for j in range(n):
        model.addConstr(x[j] <= y[j], name=f"link_{j}")

    # --- Résolution ---
    model.optimize()

    # --- Résultats ---
    portfolio = [x[j].X for j in range(n)]
    risk = model.ObjVal
    expected_return = sum(mu[j] * x[j].X for j in range(n))

    df = pd.DataFrame(
        data=portfolio + [risk, expected_return],
        index=[f"asset_{i}" for i in range(n)] + ["risk", "return"],
        columns=["Portfolio"],
    )
    print(df)

