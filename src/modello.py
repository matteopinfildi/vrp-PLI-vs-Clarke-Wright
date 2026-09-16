import pulp
import networkx as nx
import math
import time

def modello_pli(istanza, time_limit = 300):
    start_time = time.time()
    n_nodi = istanza.n_clienti + 1 # sarebbero i clienti + il deposito
    tutti = range(n_nodi) # clienti + deposito
    clienti = range(1, n_nodi) # clienti
    C = istanza.capacita
    d = istanza.domande
    costi = istanza.matrice_costi
    K = istanza.k_veicoli

    # inizializzo un problema di ottimizzazione in PuLP specificando che l'obiettivo è minimizzare
    prob = pulp.LpProblem("CVRP_Cutting_Plane", pulp.LpMinimize)

    x = {}
    for i in tutti:
        for j in tutti:
            if i < j:
                # Limite archi: 2 se collegato al deposito (nodo 0), 1 tra normali clienti
                up_bound = 2 if i == 0 else 1
                x[i, j] = pulp.LpVariable(f"x_{i}_{j}", lowBound=0, upBound=up_bound, cat='Integer')

    # Funzione Obiettivo
    prob += pulp.lpSum(costi[i][j] * x[i, j] for i in tutti for j in tutti if i < j)

    # per ogni cliente, la somma degli archi incidenti deve essere esattamente 2 
    for k in clienti:
        prob += pulp.lpSum(x[i, k] for i in tutti if i < k) + pulp.lpSum(x[k, j] for j in tutti if k < j) == 2, f"Grado_{k}"

    # calcola matematicamente quanti furgoni servono almeno e
    # impone che gli archi collegati al deposito siano compresi tra il minimo teorico e il massimo della flotta disponibile
    veicoli_minimi = math.ceil(sum(d[i] for i in clienti) / C)
    archi_deposito = pulp.lpSum(x[0, j] for j in clienti)
    prob += archi_deposito <= 2 * K, "Max_Veicoli"
    prob += archi_deposito >= 2 * veicoli_minimi, "Min_Veicoli"

    # controlla tutte le coppie di clienti: se la somma delle loro domande supera la capacità del furgone,
    # significa che non possono viaggiare insieme. Il codice vieta in partenza l'arco diretto tra di essi
    tagli_incompatibilita = 0
    for i in clienti:
        for j in clienti:
            if i < j:
                if d[i] + d[j] > C:
                    prob += x[i, j] == 0, f"Incomp_{i}_{j}"
                    tagli_incompatibilita += 1
    
    if tagli_incompatibilita > 0:
        print(f"Aggiunti {tagli_incompatibilita} tagli a priori per alleggerire il solutore.")




    iterazione = 0
    # inizializzazione del solutore CBC
    solver = pulp.PULP_CBC_CMD(msg=False, timeLimit=time_limit) 
    
    lower_bound = 0

    # CUTTING PLANE: il modello è risolto iterativamente: se la soluzione contiene dei 
    # sottocicli, si aggiunge un taglio e si ripete
    while True:
        iterazione += 1
        tempo_trascorso = time.time() - start_time
        
        # ferma il ciclo se si superano i 300s
        if tempo_trascorso >= time_limit:
            print(f"Time-Out Globale Raggiunto. LB: {lower_bound}")
            return "Time-Out", lower_bound, None, x

        prob.solve(solver)
        
        if prob.status != pulp.LpStatusOptimal:
            print(f"Time-Out CBC o Nessuna sol. trovata. LB: {lower_bound}")
            return "Time-Out", lower_bound, None, x

        # salvataggio del Lower Bound dell'iterazione corrente
        lower_bound = pulp.value(prob.objective)

        # costruzione del grafo della soluzione corrente con NetworkX
        G = nx.Graph()
        G.add_nodes_from(tutti)
        for i in tutti:
            for j in tutti:
                if i < j and pulp.value(x[i, j]) is not None and pulp.value(x[i, j]) > 0.5:
                    G.add_edge(i, j)

        # rimuozione del nodo 0 così da individuare i sottocicli
        G_no_depot = G.copy()
        G_no_depot.remove_node(0)
        
        componenti = list(nx.connected_components(G_no_depot))
        tagli_aggiunti = 0

        # implementazione GSEC
        for S in componenti:
            domanda_S = sum(d[n] for n in S)
            gamma_S = math.ceil(domanda_S / C) 
            
            archi_interni = []
            for i in S:
                for j in S:
                    if i < j:
                        archi_interni.append(x[i, j])
            
            valore_taglio = len(S) - gamma_S
            somma_corrente = sum(pulp.value(arco) for arco in archi_interni)
            
            if somma_corrente > valore_taglio:
                prob += pulp.lpSum(archi_interni) <= valore_taglio, f"GSEC_Iter_{iterazione}_Set_{list(S)[0]}"
                tagli_aggiunti += 1

        print(f"Iterazione {iterazione}: Trovati {tagli_aggiunti} tagli violati. LB: {lower_bound}")
        
        # se dopo aver esaminato tutti i percorsi non si trova nessun sottociclo o
        #violazione di capacità, significa che il modello converge
        if tagli_aggiunti == 0:
            print(f"Ottimo VERO trovato in {iterazione} iterazioni!")
            return "Ottimalita", lower_bound, lower_bound, x