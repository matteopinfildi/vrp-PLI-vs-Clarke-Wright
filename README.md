# vrp-PLI-vs-Clarke-Wright
Progetto di Algoritmi e Modelli di Ottimizzazione Discreta (AMOD). Progetto accademico realizzato per il corso di Laurea Magistrale in Ingegneria Informatica, indirizzo Cybersecurity, presso l'Università di Roma Tor Vergata.

L'obiettivo del progetto è implementare, testare e confrontare le prestazioni di un modello PLI rispetto all'Euristica di Clarke-Wright per la risoluzione del CVRP, valutando il trade-off tra la qualità della soluzione trovata ed il tempo di calcolo necessario per ottenerla.

## Algoritmi Implementati

Nel progetto sono stati sviluppati i seguenti approcci risolutivi interamente in Python:

*   **Modello PLI:** Formulazione a due indici risolta con PuLP (solver CBC). Utilizza NetworkX per la generazione dinamica dei vincoli GSEC tramite approccio Cutting Plane.
*   **Euristica di Clarke-Wright:** L'algoritmo parte da una soluzione di base, ovvero un veicolo per ogni cliente, e unisce progressivamente le rotte valutando il massimo saving in termini di distanza, rispettando il vincolo di capacità dei veicoli.

## Dataset e Generazione delle Istanze

Le istanze sono state generate randomicamente raggruppandole per caratteristiche simili. Per simulare diversi scenari reali, sono state create due topologie:
1.  **Distribuzione Uniforme:** I clienti sono dispersi casualmente sulla mappa.
2.  **Distribuzione a Cluster:** I clienti sono raggruppati in specifiche zone.

Gli esperimenti sono stati condotti fissando una flotta di veicoli pari a K = 3 e K = 5 e aumentando progressivamente il numero di clienti (N). 

## Guida all'Uso del Progetto

### Struttura del Repository
Il progetto è stato suddiviso in moduli. Di seguito la descrizione di tutti i file presenti:

**Moduli Core:**
*   **`istanza.py`**: Contiene la classe `IstanzaVRP` che genera algoritmicamente le topologie spaziali, calcola la matrice dei costi euclidei e imposta dinamicamente la capacità dei veicoli.
*   **`modello.py`**: Contiene l'implementazione del PLI. 
*   **`euristica.py`**: Contiene l'implementazione dell'algoritmo di Clarke-Wright.

**Script di Esecuzione:**
*   **`stress_test.py`**: Script che testa istanze con N incrementale per valutare le prestazioni del modello.
*   **`benchmark.py`**: Lo script principale. Genera e risolve in batch 120 istanze uniche utilizzando sia il modello PLI che l'euristica. Raccoglie tempi, costi, Lower Bound e GAP, salvando tutto in un file CSV.
*   **`grafici.py`**: Legge i risultati dal CSV e genera in automatico dei grafici usati per l'analisi dei risultati.

**Configurazione e Output:**
*   **`requirements.txt`**: Elenco delle dipendenze Python per riprodurre l'ambiente di lavoro.
*   **`esperimenti_amod_vrp.csv`** e **`Fig*.png`**: File generati automaticamente a runtime durante l'esecuzione degli script.

**Documentazione:**
*   **`Progetto_AMOD_Pinfildi.pdf`**: Presentazione del progetto (Slide).

### Prerequisiti
Assicurarsi di avere Python 3.8+ installato sul sistema. Le librerie necessarie sono elencate nel file `requirements.txt`. Si possono installare rapidamente eseguendo da terminale:
```bash
pip install -r requirements.txt
```

### Esecuzione
L'intero studio è riproducibile. Dopo aver installato i prerequisiti, eseguire i file dal terminale nel seguente ordine sequenziale:

```bash
cd src
python stress_test.py
python benchmark.py
python grafici.py
```
