def save_submission(output_filename, x, C, V):
   
    print("Génération du fichier de soumission...")
    
    # Dictionnaire pour stocker les résultats : {cache_id: [liste_video_ids]}
    used_caches = {}

    for c in range(C):
        videos_on_c = []
        for v in range(V):
            # On vérifie si la variable binaire est à 1 (avec une tolérance flottante > 0.5)
            # x[v, c] est l'objet Gurobi, x[v, c].X est sa valeur
            try:
                if x[v, c].X > 0.5:
                    videos_on_c.append(str(v))
            except AttributeError:
                # Cas où la variable n'est pas dans le modèle (si filtrée) ou modèle non résolu
                pass
        
        # Si le cache contient au moins une vidéo, on l'ajoute à la liste
        if videos_on_c:
            used_caches[c] = videos_on_c

    # Écriture dans le fichier
    with open(output_filename, 'w') as f:
        # Ligne 1 : Nombre de caches décrits
        f.write(f"{len(used_caches)}\n")
        
        # Lignes suivantes : ID_Cache ID_Video1 ID_Video2 ...
        for c, videos in used_caches.items():
            line = f"{c} " + " ".join(videos)
            f.write(line + "\n")

    print(f"Fichier '{output_filename}' généré avec succès.")