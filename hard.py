import numpy as np 
import gurobipy as gp
from gurobipy import GRB

def generate_knapsack(num_items): 
    # Fix seed value 
    rng = np.random.default_rng(seed=0)

    # Item Values and Weights 
    values = rng.uniform(low=1, high=25, size=num_items)
    weights = rng.uniform(low=5, high=100, size=num_items)

    # Knapsack capacity 
    capacity = 0.7 * weights.sum()

    return values, weights, capacity 


def solve_knapsack_model(values, weights, capacity): 
    num_items = len(values)

    # Turn numpy arrays to dictionaries
    val = {i: values[i] for i in range(num_items)}
    wei = {i: weights[i] for i in range(num_items)}

    # Create environment and model
    with gp.Env(empty=True) as env:
        env.start()
        with gp.Model("Knapsack", env=env) as model:

            # Decision variables: x[i] = 1 if item i is taken
            x = model.addVars(num_items, vtype=GRB.BINARY, name="x")

            # Objective: maximize total value
            model.setObjective(gp.quicksum(val[i] * x[i] for i in range(num_items)), GRB.MAXIMIZE)

            # Capacity constraint
            model.addConstr(gp.quicksum(wei[i] * x[i] for i in range(num_items)) <= capacity, name="capacity")

            # Optimize model
            model.optimize()

            # Show results
            selected_items = [i for i in range(num_items) if x[i].x > 0.5]
            total_value = sum(val[i] for i in selected_items)
            total_weight = sum(wei[i] for i in selected_items)

            print(f"\nValeur totale : {total_value:.2f}")
            print(f"Poids total   : {total_weight:.2f}")
            print(f"Articles choisis : {selected_items}")

            return selected_items, total_value, total_weight


# Exemple d’utilisation
values, weights, capacity = generate_knapsack(10)
solve_knapsack_model(values, weights, capacity)
