from functools import partial
import gurobipy as gp
from gurobipy import GRB

class CallbackData:
    def __init__(self):
        self.last_gap_change_time = -GRB.INFINITY
        self.last_gap = GRB.INFINITY

def callback(model, where, *, cbdata):
    if where != GRB.Callback.MIP:
        return
    
    # On a besoin d'au moins une solution faisable
    if model.cbGet(GRB.Callback.MIP_SOLCNT) == 0:
        return

    # Récupérer le temps actuel et le MIPGap
    current_time = model.cbGet(GRB.Callback.RUNTIME)
    current_gap = model.cbGet(GRB.Callback.MIP_GAP)  # ← CORRECTION ICI

    # Si le gap a diminué de plus que epsilon
    if abs(current_gap - cbdata.last_gap) > 1e-4:  # epsilon
        cbdata.last_gap = current_gap
        cbdata.last_gap_change_time = current_time
    else:
        # Si le gap est stable depuis plus de 15 secondes, on arrête
        if current_time - cbdata.last_gap_change_time > 15:
            print(f"⏹️ Arrêt demandé : MIPGap stable ({current_gap:.6f}) depuis 15s")
            model.terminate()

# Avec votre fichier MPS
with gp.Env() as env, gp.Model(env=env) as model:
    model = gp.read("data/mkp.mps", env=env)
    
    # Initialize data passed to the callback function
    callback_data = CallbackData()
    callback_func = partial(callback, cbdata=callback_data)

    model.optimize(callback_func)
