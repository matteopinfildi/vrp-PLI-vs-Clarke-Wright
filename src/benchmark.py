import random
import time
import pandas as pd
from istanza import IstanzaVRP
from modello import modello_pli
from euristica import algoritmo_clarke_wright

# configurazioni suddivise per numero massimo di veicoli K, numero di clienti N e categoria dimensionale
configurazioni = [
    {"K": 5, "N": 15,  "Categoria": "Piccola"},
    {"K": 5, "N": 30,  "Categoria": "Media"},
    {"K": 5, "N": 45,  "Categoria": "Grande"},
    {"K": 3, "N": 50,  "Categoria": "Piccola"},
    {"K": 3, "N": 100, "Categoria": "Media"},
    {"K": 3, "N": 150, "Categoria": "Grande"}
]


distribuzioni = ["Uniforme", "Cluster"]
repliche = 10
TIME_LIMIT = 300
dati_raccolti = []

for conf in configurazioni:
    K = conf["K"]
    N = conf["N"]
    categoria = conf["Categoria"]
    
    print(f"\n--- Analisi Flotta K={K} | N={N} ({categoria}) ---")
    
    for dist in distribuzioni:
        for r in range(1, repliche + 1):
            # fissare un seed univoco per ogni singola replica garantisce che le coordinate 
            # e le domande generate siano perfettamente replicabili da chiunque esegua il codice
            random.seed(f"cvrp_proj_{K}_{N}_{dist}_{r}") 

            # generazione istanza
            istanza = IstanzaVRP(n_clienti=N, k_veicoli=K)
            if dist == "Uniforme":
                istanza.genera_uniforme()
            else:
                istanza.genera_cluster()
            
            # esecuzione del modello
            start = time.time()
            risultati = modello_pli(istanza, time_limit=TIME_LIMIT)
            tempo = round(time.time() - start, 2)

            stato = risultati[0]
            lb_o_ottimo = risultati[1]

            # esecuzione dell'Euristica di Clarke-Wright
            start_cw = time.time()
            rotte_cw = algoritmo_clarke_wright(
                n_clienti=istanza.n_clienti, 
                matrice_costi=istanza.matrice_costi, 
                domande=istanza.domande, 
                capacita_veicolo=istanza.capacita
            )

            tempo_cw = round(time.time() - start_cw, 4)

            costo_cw = 0
            for rotta in rotte_cw:
                # tratta di andata
                costo_cw += istanza.matrice_costi[0][rotta[0]]
                # tratte intermedie
                for k in range(len(rotta) - 1):
                    costo_cw += istanza.matrice_costi[rotta[k]][rotta[k+1]]
                #tratta di ritorno
                costo_cw += istanza.matrice_costi[rotta[-1]][0]

            # calcolo del Gap
            if lb_o_ottimo > 0:
                gap_perc = ((costo_cw - lb_o_ottimo) / lb_o_ottimo) * 100
            else:
                gap_perc = 0.0
                
            dati_raccolti.append({
                "Flotta_K": K,
                "Clienti_N": N,
                "Categoria": categoria,
                "Distribuzione": dist,
                "Istanza_ID": r,
                "Stato_Esatto": stato,
                "LB_o_Ottimo": lb_o_ottimo,
                "Tempo_Esatto_s": tempo,
                "Costo_ClarkeWright": costo_cw,
                "Tempo_CW_s": tempo_cw,
                "GAP_%": round(gap_perc, 2)
            })

            print(f"[{dist} {r}/10] {stato} ({lb_o_ottimo}) in {tempo}s | CW: {costo_cw} | GAP: {round(gap_perc, 2)}%")

# Salvataggio su file CSV
df_risultati = pd.DataFrame(dati_raccolti)
df_risultati.to_csv("esperimenti_amod_vrp.csv", index=False)

print("\n=== ESPERIMENTO COMPLETATO ===")
print("I risultati di tutte le 120 istanze sono stati salvati nel file 'esperimenti_amod_vrp.csv'")