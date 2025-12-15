import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from read_instance import read_instance

def analyze_dataset(filename):
    print(f"--- ANALYSE DÉTAILLÉE : {filename} ---")
    
    # 1. Chargement
    V, E, R, C, X, video_size, LD, connections, requests = read_instance(filename)
    
    # --- A. ANALYSE DU STOCKAGE (Cache vs Vidéos) ---
    total_video_size = sum(video_size)
    total_cache_capacity = C * X
    avg_video_size = sum(video_size) / V
    
    print("\n[1] STOCKAGE & CAPACITÉ")
    print(f"Nombre de Vidéos (V)      : {V}")
    print(f"Nombre de Caches (C)      : {C}")
    print(f"Taille par Cache (X)      : {X} MB")
    print(f"Taille Moyenne Vidéo      : {avg_video_size:.2f} MB")
    print(f"Taille Totale de toutes les vidéos : {total_video_size:,.0f} MB")
    print(f"Capacité Totale du réseau (C*X)    : {total_cache_capacity:,.0f} MB")
    
    ratio = (total_cache_capacity / total_video_size) * 100
    print(f"-> Taux de couverture possible : {ratio:.2f}%")
    if ratio < 100:
        print("   (!) On ne peut pas tout stocker. Le choix des vidéos est CRITIQUE.")
    else:
        print("   (i) Large capacité. Le problème est surtout le routage.")

    # --- B. ANALYSE DES REQUÊTES (Popularité) ---
    # Création d'un DataFrame pour faciliter l'analyse
    df_req = pd.DataFrame(requests, columns=['video_id', 'endpoint_id', 'count'])
    
    # Ajout de la taille de la vidéo à chaque requête
    df_req['video_size'] = df_req['video_id'].apply(lambda vid: video_size[vid])
    
    total_requests = df_req['count'].sum()
    unique_requested_videos = df_req['video_id'].nunique()
    
    print("\n[2] DEMANDE & POPULARITÉ")
    print(f"Nombre total de requêtes (descriptions) : {R}")
    print(f"Volume total de demandes (somme des n)  : {total_requests:,.0f}")
    print(f"Vidéos jamais demandées : {V - unique_requested_videos} vidéos")
    
    # Top vidéos
    video_popularity = df_req.groupby('video_id')['count'].sum().sort_values(ascending=False)
    print("\n-> Top 3 Vidéos les plus demandées :")
    print(video_popularity.head(3))
    
    # --- C. ANALYSE RÉSEAU (Latence & Connexions) ---
    print("\n[3] TOPOLOGIE RÉSEAU")
    
    # Densité des connexions
    nb_connexions = sum(len(c) for c in connections)
    densite = (nb_connexions / (E * C)) * 100
    print(f"Densité de connexion (Endpoints <-> Caches) : {densite:.2f}%")
    
    # Gain potentiel moyen
    gains = []
    for r_idx, row in df_req.iterrows():
        e = row['endpoint_id']
        dc_lat = LD[e]
        
        # Trouver la meilleure latence cache possible pour cet endpoint
        if connections[e]:
            best_cache_lat = min(connections[e].values())
            # Gain max possible pour cette requête (si la vidéo est là)
            gains.append((dc_lat - best_cache_lat))
        else:
            gains.append(0) # Pas de cache connecté
            
    avg_gain_potential = sum(gains) / len(gains)
    print(f"Gain de latence moyen possible par requête : {avg_gain_potential:.2f} ms")

    # --- D. VISUALISATIONS ---
    print("\n[4] GÉNÉRATION DES GRAPHIQUES...")
    
    fig, axs = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f'Analyse du Dataset : {filename}', fontsize=16)
    
    # 1. Distribution des tailles de vidéos
    sns.histplot(video_size, bins=30, ax=axs[0, 0], color='skyblue')
    axs[0, 0].set_title('Distribution des Tailles de Vidéos (MB)')
    axs[0, 0].set_xlabel('Taille (MB)')
    
    # 2. Popularité des vidéos (Log scale souvent utile)
    # On prend seulement les vidéos demandées
    sns.lineplot(data=video_popularity.values, ax=axs[0, 1], color='orange')
    axs[0, 1].set_title('Popularité des Vidéos (Courbe "Long Tail")')
    axs[0, 1].set_xlabel('Rang de la vidéo')
    axs[0, 1].set_ylabel('Nombre de requêtes')
    axs[0, 1].set_yscale('log') # Souvent une loi de puissance
    
    # 3. Latence DC vs Latence Cache Moyenne
    lat_dc = LD
    lat_cache_avg = [sum(c.values())/len(c) if c else 0 for c in connections]
    # On filtre pour le plot ceux qui ont des caches
    comparison_data = pd.DataFrame({
        'DC Latency': lat_dc,
        'Avg Cache Latency': lat_cache_avg
    })
    # On enlève les endpoints sans cache (latence cache 0) pour ne pas fausser
    comparison_data = comparison_data[comparison_data['Avg Cache Latency'] > 0]
    
    sns.scatterplot(x='DC Latency', y='Avg Cache Latency', data=comparison_data, ax=axs[1, 0], alpha=0.5)
    axs[1, 0].set_title('Latence DataCenter vs Cache (Scatter)')
    axs[1, 0].plot([0, max(LD)], [0, max(LD)], 'r--') # Ligne diagonale
    
    # 4. Nombre de caches par endpoint
    caches_per_endpoint = [len(c) for c in connections]
    sns.histplot(caches_per_endpoint, bins=range(0, max(caches_per_endpoint)+2), ax=axs[1, 1], color='green')
    axs[1, 1].set_title('Nombre de Caches connectés par Endpoint')
    axs[1, 1].set_xlabel('Nombre de Caches')
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()
    print("Terminé.")

if __name__ == "__main__":
    # Remplace par ton fichier
    analyze_dataset("trending_4000_10k.in")