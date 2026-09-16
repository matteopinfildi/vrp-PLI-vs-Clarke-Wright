import time
import pulp
from istanza import IstanzaVRP
from modello import modello_pli

valori_n_da_testare = [10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130, 135, 140, 145, 150, 155, 160, 165, 170, 175]
k_veicoli_list = [3, 5]  
n_repliche = 5
TIME_LIMIT_MAX = 300
SOGLIA_MURA = TIME_LIMIT_MAX - 2.0

tutti_i_risultati = {}

print("=== AVVIO STRESS TEST DEFINITIVO (FLOTTA MASSIMA <= K) ===", flush=True)

for k in k_veicoli_list:
    print(f"\n==================================================", flush=True)
    print(f"=== FLOTTA MASSIMA: K = {k} ===", flush=True)
    print(f"==================================================", flush=True)

    risultati = {}

    for n in valori_n_da_testare:
        successi_ottimo = 0
        fallimenti_timeout = 0
        lb_estratti = 0
        tempi_registrati = []
        
        for r in range(1, n_repliche + 1):
            start_time = time.time()
            try:
                # generazione istanza di tipo cluster
                istanza = IstanzaVRP(n_clienti=n, k_veicoli=k)
                istanza.genera_cluster(n_cluster=3)

                # risoluzione tramite il modello PLI
                stato_soluzione, lb, ub, x = modello_pli(istanza, time_limit=TIME_LIMIT_MAX)
                end_time = time.time()

                tempo = round(end_time - start_time, 2)

                # se si trova l'ottimo entro 300 secondi si entra in questo ramo
                if stato_soluzione == "Ottimalita" and tempo < SOGLIA_MURA:
                    print(f"  -> Replica {r}/5 (N={n}, K={k}): OTTIMO VERO in {tempo}s (Valore: {lb})", flush=True)
                    successi_ottimo += 1
                    tempi_registrati.append(tempo)
                else:
                    # altrimenti il test viene catalogato come Time-Out
                    fallimenti_timeout += 1
                    if lb is not None:
                        # caso in cui il modello va in Time-Out e trova un LB
                        costo_lb = round(lb, 2)
                        print(f"  -> Replica {r}/5 (N={n}, K={k}): TIME-OUT ({tempo}s) - Lower Bound estratto: {costo_lb}", flush=True)
                        lb_estratti += 1
                    else:
                        # caso in cui il modello va in Time-Out e non trova un LB
                        print(f"  -> Replica {r}/5 (N={n}, K={k}): TIME-OUT ({tempo}s) - Nessun LB trovato", flush=True)
                    
                    # in caso di timeout, si registra il tempo massimo per il calcolo delle medie
                    tempi_registrati.append(float(TIME_LIMIT_MAX))

            except Exception as e:
                # intercetta eventuali errori di sistema evitando crash e perdite di tempo
                end_time = time.time()
                tempo = round(end_time - start_time, 2)
                print(f"  -> Replica {r}/5 (N={n}, K={k}): [ERRORE DI SISTEMA CATTURATO] {e}", flush=True)
                fallimenti_timeout += 1
                tempi_registrati.append(float(TIME_LIMIT_MAX))

        # Calcolo della media dei tempi registrati per la taglia N corrente
        media_tempo = round(sum(tempi_registrati) / len(tempi_registrati), 2)
        risultati[n] = {
            "successi": successi_ottimo,
            "timeout": fallimenti_timeout,
            "lb_estratti": lb_estratti,
            "media_tempo": media_tempo
        }

        # EARLY STOPPING: Se su 5 repliche abbiamo 5 Timeout, fermiamo il test per N più grandi
        if fallimenti_timeout == n_repliche:
            print(f"\n[!] LIMITE COMPUTAZIONALE RAGGIUNTO PER K={k}. Sospensione test per N > {n}.\n", flush=True)
            break  # Interrompe correttamente il ciclo delle taglie N
        
    tutti_i_risultati[k] = risultati

# STAMPA TABELLE FINALI
print("\n\n=======================================================================", flush=True)
print("=== TABELLE FINALI ===", flush=True)
print("=======================================================================", flush=True)

for k, risultati in tutti_i_risultati.items():
    print(f"\n--- Flotta K = {k} ---", flush=True)
    print(f"{'Clienti (N)':<12} | {'Ottimi':<10} | {'Time-Out':<10} | {'LB Estratti':<20} | {'Tempo Medio (s)':<15}", flush=True)
    print("-" * 75, flush=True)
    for n, dati in risultati.items():
        print(f"{n:<12} | {dati['successi']}/5{'':<6} | {dati['timeout']}/5{'':<6} | {dati['lb_estratti']} su {dati['timeout']}{'':<14} | {dati['media_tempo']:<15.2f}", flush=True)