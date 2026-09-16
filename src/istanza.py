import math
import random
import numpy as np
import matplotlib.pyplot as plt

class IstanzaVRP:
    def __init__(self, n_clienti, k_veicoli):
        self.n_clienti = n_clienti
        self.k_veicoli = k_veicoli
        self.capacita = 0
        self.domande = []
        self.coordinate = []
        self.matrice_costi = None

    # genero le istanze uniformi (bassa variabilità di distanze) in modo random, passandogli in input il valore massimo della coordinata
    # il valore minimo e massimo della domanda di ogni cliente.
    # Il numero di clienti da generare viene acquisito dinamicamente dall'attributo interno dell'oggetto (self.n_clienti).
    def genera_uniforme(self, max_coord=100, min_dom_val=10, max_dom_val=50):
        self._reset_dati()
        
        # genera il deposito al centro della mappa
        self.coordinate.append((max_coord / 2, max_coord / 2))
        self.domande.append(0)
        
        # genera i clienti con distribuzione uniforme
        for _ in range(self.n_clienti):
            x = random.uniform(0, max_coord)
            y = random.uniform(0, max_coord)
            self.coordinate.append((x, y))
            self.domande.append(random.randint(min_dom_val, max_dom_val))
            
        self._imposta_capacita()
        self._calcola_matrice_costi()

    # genero le istanze a cluster (alta variabilità di distanze) in modo random, passandogli in input
    # il numero di cluster, la deviazione standard per la dispersione dei punti, 
    # il valore massimo della coordinata, il valore minimo e massimo della domanda di ogni cliente.
    def genera_cluster(self, n_cluster=3, deviazione_std=8, max_coord=100, min_dom=10, max_dom=50):
        self._reset_dati()
        
        # Genera il deposito al centro
        self.coordinate.append((max_coord / 2, max_coord / 2))
        self.domande.append(0)
        
        # punti casuali che faranno da "centro" per i paesini
        centri = [(random.uniform(15, 85), random.uniform(15, 85)) for _ in range(n_cluster)]
        
        for _ in range(self.n_clienti):
            centro_scelto = random.choice(centri)
            # uso la curva di Gauss per posizionare il cliente vicino al centro scelto
            x = random.gauss(centro_scelto[0], deviazione_std)
            y = random.gauss(centro_scelto[1], deviazione_std)
            
            x = max(0, min(max_coord, x))
            y = max(0, min(max_coord, y))
            
            self.coordinate.append((x, y))
            self.domande.append(random.randint(min_dom, max_dom))
            
        self._imposta_capacita()
        self._calcola_matrice_costi()

    # calcola la capacità di carico dei veicoli in modo dinamico, passandogli in input il margine di sicurezza percentuale. 
    def _imposta_capacita(self, margine=1.15):
        somma_domande = sum(self.domande)
        base_necessaria = somma_domande / self.k_veicoli
        cap_proposta = math.ceil(base_necessaria * margine)
        domanda_massima = max(self.domande)
        
        self.capacita = max(cap_proposta, domanda_massima)

    # calcola la matrice dei costi (distanze) tra tutti i nodi della mappa, basandosi sulle coordinate generate.
    # calcola la distanza euclidea tra ogni coppia di nodi e la arrotonda per eccesso per preservare la disuguaglianza triangolare.
    def _calcola_matrice_costi(self):
        n_nodi = self.n_clienti + 1
        self.matrice_costi = np.zeros((n_nodi, n_nodi), dtype=int)
        
        for i in range(n_nodi):
            for j in range(n_nodi):
                if i == j:
                    self.matrice_costi[i][j] = 999999 
                else:
                    x1, y1 = self.coordinate[i]
                    x2, y2 = self.coordinate[j]
                    distanza = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
                    self.matrice_costi[i][j] = math.ceil(distanza)
    
    # puliamo le liste se riutilizziamo lo stesso oggetto
    def _reset_dati(self):
        self.coordinate = []
        self.domande = []
        self.matrice_costi = None

   # stampa l'istanza
    def plot_mappa(self, titolo="Mappa VRP"):
        plt.figure(figsize=(8, 6))
        
        cx = [p[0] for p in self.coordinate[1:]]
        cy = [p[1] for p in self.coordinate[1:]]
        plt.scatter(cx, cy, c='blue', label='Clienti', alpha=0.6)
        
        for i in range(1, self.n_clienti + 1):
            plt.annotate(str(i), (self.coordinate[i][0] + 1.5, self.coordinate[i][1] + 1.5), fontsize=9)
            
        dx, dy = self.coordinate[0]
        plt.scatter(dx, dy, c='red', marker='s', s=100, label='Deposito (0)')
        
        plt.title(f"{titolo} | N={self.n_clienti}, K={self.k_veicoli}, Cap={self.capacita}")
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.show()