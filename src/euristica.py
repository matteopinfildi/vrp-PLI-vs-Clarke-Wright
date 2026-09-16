def algoritmo_clarke_wright(n_clienti, matrice_costi, domande, capacita_veicolo):

    # 1. calcolo del saving per ogni coppia (i, j)
    lista_savings = []
    for i in range(1, n_clienti + 1):
        for j in range(i + 1, n_clienti + 1):
            # la formula è: S_ij = c_0i + c_0j - c_ij (0 è il deposito)
            saving = matrice_costi[0, i] + matrice_costi[0, j] - matrice_costi[i, j]
            lista_savings.append((saving, i, j))

    # 2. ordinamento delle coppie in base al saving ottenuto, dal più alto al più basso (decrescente)
    lista_savings.sort(key=lambda x: x[0], reverse=True)

    # 3. si parte dalla soluzione base: ogni cliente è servito da un singolo veicolo con un viaggio di andata e ritorno dal deposito
    rotte = [[i] for i in range(1, n_clienti + 1)]

    # individuazione rotta in cui si trova attualmente il cliente e la sua posizione
    def trova_stato_cliente(cliente):
        for idx_rotta, rotta in enumerate(rotte):
            if cliente in rotta:
                if cliente == rotta[0]: return idx_rotta, 'inizio'
                elif cliente == rotta[-1]: return idx_rotta, 'fine'
                else: return idx_rotta, 'interno'
        return None, None

    # 4: Fusione delle Rotte in caso vengono rispettati i vincoli
    for saving, i, j in lista_savings:
        idx_rotta_i, pos_i = trova_stato_cliente(i)
        idx_rotta_j, pos_j = trova_stato_cliente(j)

        # i nodi i e j appartengono a due rotte distinte
        if idx_rotta_i == idx_rotta_j:
            continue

        # i nodi i e j si trovano agli estremi delle rispettive rotte
        if pos_i == 'interno' or pos_j == 'interno':
            continue

        # l'unione rispetta la capacità massima del veicolo.
        carico_i = sum(domande[cliente] for cliente in rotte[idx_rotta_i])
        carico_j = sum(domande[cliente] for cliente in rotte[idx_rotta_j])
        if carico_i + carico_j <= capacita_veicolo:
            # tutti i vincoli sono rispettati, dunque si uniscono le rotte
            rotta_i = rotte[idx_rotta_i]
            rotta_j = rotte[idx_rotta_j]

            if pos_i == 'fine' and pos_j == 'inizio':
                nuova_rotta = rotta_i + rotta_j
            elif pos_i == 'inizio' and pos_j == 'fine':
                nuova_rotta = rotta_j + rotta_i
            elif pos_i == 'fine' and pos_j == 'fine':
                nuova_rotta = rotta_i + rotta_j[::-1] 
            elif pos_i == 'inizio' and pos_j == 'inizio':
                nuova_rotta = rotta_i[::-1] + rotta_j
                
            rotte.pop(max(idx_rotta_i, idx_rotta_j))
            rotte.pop(min(idx_rotta_i, idx_rotta_j))
            rotte.append(nuova_rotta)
            
    # 5. terminazione
    return rotte