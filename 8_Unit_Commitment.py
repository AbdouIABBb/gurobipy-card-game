import gurobipy as gp
from gurobipy import GRB

# 24 Hour Load Forecast (MW)
load_forecast = [
     4,  4,  4,  4,  4,  4,   6,   6,
    12, 12, 12, 12, 12,  4,   4,   4,
     4, 16, 16, 16, 16,  6.5, 6.5, 6.5,
]

# solar energy forecast (MW)
solar_forecast = [
    0,   0,   0,   0,   0,   0,   0.5, 1.0,
    1.5, 2.0, 2.5, 3.5, 3.5, 2.5, 2.0, 1.5,
    1.0, 0.5, 0,   0,   0,   0,   0,   0,
]

# global number of time intervals
nTimeIntervals = len(load_forecast)

# thermal units
thermal_units = ["gen1", "gen2", "gen3"]

# thermal units' costs  (a + b*p + c*p^2), (startup and shutdown costs)
thermal_units_cost, a, b, c, sup_cost, sdn_cost = gp.multidict(
    {
        "gen1": [5.0, 0.5, 1.0, 2, 1],
        "gen2": [5.0, 0.5, 0.5, 2, 1],
        "gen3": [5.0, 3.0, 2.0, 2, 1],
    }
)

# thermal units operating limits
thermal_units_limits, pmin, pmax = gp.multidict(
    {"gen1": [1.5, 5.0], "gen2": [2.5, 10.0], "gen3": [1.0, 3.0]}
)

# thermal units dynamic data (initial commitment status)
thermal_units_dyn_data, init_status = gp.multidict(
    {"gen1": [0], "gen2": [0], "gen3": [0]}
)


with gp.Env() as env, gp.Model(env=env) as model:

    # --- Variables indexées par (g,t) ---
    thermal_units_out_power = model.addVars(
        thermal_units, range(nTimeIntervals),
        lb=0.0, vtype=GRB.CONTINUOUS, name="p"
    )  # p[g,t]

    thermal_units_startup_status = model.addVars(
        thermal_units, range(nTimeIntervals),
        vtype=GRB.BINARY, name="v"
    )  # v[g,t]

    thermal_units_shutdown_status = model.addVars(
        thermal_units, range(nTimeIntervals),
        vtype=GRB.BINARY, name="w"
    )  # w[g,t]

    thermal_units_comm_status = model.addVars(
        thermal_units, range(nTimeIntervals),
        vtype=GRB.BINARY, name="u"
    )  # u[g,t]

    # === Fonction objectif (quadratique) ===
    obj = gp.QuadExpr()
    for g in thermal_units:
        for t in range(nTimeIntervals):
            pgt = thermal_units_out_power[g, t]
            ugt = thermal_units_comm_status[g, t]
            vgt = thermal_units_startup_status[g, t]
            wgt = thermal_units_shutdown_status[g, t]

            # terme quadratique c[g] * p^2
            obj.addTerms(c[g], pgt, pgt)  # ajoute c[g]*pgt*pgt
            # terme linéaire b[g]*p
            obj.add(pgt * b[g])
            # coût fixe a[g]*u
            obj.add(ugt * a[g])
            # start/stop costs
            obj.add(vgt * sup_cost[g])
            obj.add(wgt * sdn_cost[g])

    model.setObjective(obj, GRB.MINIMIZE)

    # === Power balance (pour chaque t) ===
    for t in range(nTimeIntervals):
        model.addConstr(
            gp.quicksum(thermal_units_out_power[g, t] for g in thermal_units)
            + solar_forecast[t]
            == load_forecast[t],
            name=f"power_balance_{t}"
        )

    # === Logical constraints (u, v, w) ===
    for g in thermal_units:
        for t in range(nTimeIntervals):
            if t == 0:
                # u_0 - u_init = v_0 - w_0
                model.addConstr(
                    thermal_units_comm_status[g, 0] - init_status[g]
                    == thermal_units_startup_status[g, 0] - thermal_units_shutdown_status[g, 0],
                    name=f"logic_{g}_{0}"
                )
            else:
                model.addConstr(
                    thermal_units_comm_status[g, t] - thermal_units_comm_status[g, t - 1]
                    == thermal_units_startup_status[g, t] - thermal_units_shutdown_status[g, t],
                    name=f"logic_{g}_{t}"
                )

            # pas de start + stop simultané
            model.addConstr(
                thermal_units_startup_status[g, t] + thermal_units_shutdown_status[g, t] <= 1,
                name=f"no_simul_{g}_{t}"
            )

    # === Physical constraints via indicator constraints ===
    # If u[g,t] == 1 => pmin[g] <= p[g,t] <= pmax[g]
    # If u[g,t] == 0 => p[g,t] == 0
    for g in thermal_units:
        for t in range(nTimeIntervals):
            pgt = thermal_units_out_power[g, t]
            ugt = thermal_units_comm_status[g, t]

            # active quand u == 1 -> lower bound
            model.addGenConstrIndicator(
                ugt, True,
                pgt >= pmin[g],
                name=f"min_if_on_{g}_{t}"
            )
            # active quand u == 1 -> upper bound
            model.addGenConstrIndicator(
                ugt, True,
                pgt <= pmax[g],
                name=f"max_if_on_{g}_{t}"
            )
            # active quand u == 0 -> p == 0
            model.addGenConstrIndicator(
                ugt, False,
                pgt == 0.0,
                name=f"zero_if_off_{g}_{t}"
            )

    # --- Optionnel : paramètres et optimisation ---
    model.params.OutputFlag = 1
    model.optimize()

    # --- Affichage des résultats ---
    if model.status == GRB.OPTIMAL or model.status == GRB.TIME_LIMIT:
        print(f"\nOverAll Cost = {model.ObjVal:.2f}\n")
        print("%5s" % "time", end=" ")
        for t in range(nTimeIntervals):
            print("%4s" % t, end=" ")
        print("\n")

        for g in thermal_units:
            print("%5s" % g, end=" ")
            for t in range(nTimeIntervals):
                print("%4.1f" % thermal_units_out_power[g, t].X, end=" ")
            print("\n")

        print("%5s" % "Solar", end=" ")
        for t in range(nTimeIntervals):
            print("%4.1f" % solar_forecast[t], end=" ")
        print("\n")

        print("%5s" % "Load", end=" ")
        for t in range(nTimeIntervals):
            print("%4.1f" % load_forecast[t], end=" ")
        print("\n")
    else:
        print("Pas de solution optimale trouvée. Statut:", model.status)
