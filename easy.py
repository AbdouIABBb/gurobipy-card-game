import gurobipy as gp
import random

# Liste complète des cartes rouges (concepts d'optimisation)
cartes_rouges = [
    "variable", 
    "contrainte", 
    "objectif",
    "variable binaire",
    "variable entière",
    "variable continue",
    "maximiser",
    "minimiser",
    "somme des variables",
    "expression linéaire",
    "modèle"
]

# Liste complète des cartes bleues (commandes Gurobi)
cartes_bleues = [
    "m.addVar()",
    "m.addConstr()",
    "m.setObjective()",
    "m.addVar(vtype=gp.GRB.BINARY)",
    "m.addVar(vtype=gp.GRB.INTEGER)",
    "m.addVar(vtype=gp.GRB.CONTINUOUS)",
    "gp.GRB.MAXIMIZE",
    "gp.GRB.MINIMIZE",
    "gp.quicksum()",
    "gp.LinExpr()",
    "gp.Model()"
]

# Correspondances correctes
correspondances = {
    "variable": "m.addVar()",
    "contrainte": "m.addConstr()",
    "objectif": "m.setObjective()",
    "variable binaire": "m.addVar(vtype=gp.GRB.BINARY)",
    "variable entière": "m.addVar(vtype=gp.GRB.INTEGER)",
    "variable continue": "m.addVar(vtype=gp.GRB.CONTINUOUS)",
    "maximiser": "gp.GRB.MAXIMIZE",
    "minimiser": "gp.GRB.MINIMIZE",
    "somme des variables": "gp.quicksum()",
    "expression linéaire": "gp.LinExpr()",
    "modèle": "gp.Model()"
}

print("=== Jeu de cartes Gurobipy - Mode Facile (Toutes les cartes) ===")
score = 0

# Mélanger les cartes rouges pour chaque partie
random.shuffle(cartes_rouges)

# Boucle principale du jeu
for rouge in cartes_rouges:
    print(f"\nCarte rouge : {rouge}")
    print("Choisis la carte bleue correspondante :")
    # Mélanger les cartes bleues pour chaque question
    cartes_melangees = cartes_bleues.copy()
    random.shuffle(cartes_melangees)
    for i, bleu in enumerate(cartes_melangees):
        print(f"{i}: {bleu}")
    
    choix = int(input("Ton choix (indice) : "))
    
    if cartes_melangees[choix] == correspondances[rouge]:
        print("✅ Correct !")
        score += 1
    else:
        print(f"❌ Faux ! La bonne réponse était {correspondances[rouge]}")

print(f"\nTon score final : {score}/{len(cartes_rouges)}")
