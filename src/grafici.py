import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib.ticker as ticker
import warnings

warnings.filterwarnings("ignore")

sns.set_theme(style="whitegrid")
plt.rcParams.update({'font.size': 12, 'figure.titlesize': 15, 'axes.titlesize': 13})

# Funzione per formattare l'asse logaritmico della Figura 2 con numeri reali invece che potenze
def format_log_ticks(y, pos):
    if y >= 1:
        return f"{int(y)}"
    else:
        return f"{y:g}"

print("=== AVVIO GENERAZIONE GRAFICI (REPORT COMPLETO VRP) ===")

# Caricamento del dataset
df = pd.read_csv("esperimenti_amod_vrp.csv")
df['Stato_Esatto'] = df['Stato_Esatto'].replace('Ottimalita', 'Ottimo')

df['Baseline'] = df['Stato_Esatto'].map({
    'Ottimo': 'GAP Reale (vs Ottimo)', 
    'Time-Out': 'GAP Apparente (vs Lower Bound)'
})

scenari = [
    {
        "K": 5, 
        "titolo": "Flotta K=5 (Alta Frammentazione)", 
        "N_labels": {15: "N=15\n(Piccola)", 30: "N=30\n(Media)", 45: "N=45\n(Grande)"}
    },
    {
        "K": 3, 
        "titolo": "Flotta K=3 (Alta Capacità)", 
        "N_labels": {50: "N=50\n(Piccola)", 100: "N=100\n(Media)", 150: "N=150\n(Grande)"}
    }
]

for scenario in scenari:
    K = scenario["K"]
    titolo = scenario["titolo"]
    n_labels = scenario["N_labels"]
    ordine_x = list(n_labels.values())
    
    # Filtraggio dei dati specifici per la flotta corrente
    df_k = df[df['Flotta_K'] == K].copy()
    df_k['Fascia_N'] = df_k['Clienti_N'].map(n_labels)
    
    print(f"\nGenerazione set di grafici per Flotta K = {K}...")

    
    # FIGURA 1: Successi vs Time-Out
    fig1, axes1 = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
    fig1.suptitle(f"Scalabilità del Modello PLI: {titolo}", fontsize=16, fontweight='bold', y=1.05)
    
    for idx, dist in enumerate(["Uniforme", "Cluster"]):
        df_dist = df_k[df_k['Distribuzione'] == dist]
        # Calcolo frequenze assolute degli stati
        succ_data = df_dist.groupby(['Fascia_N', 'Stato_Esatto']).size().unstack(fill_value=0)
        for col in ['Ottimo', 'Time-Out']:
            if col not in succ_data.columns: succ_data[col] = 0
        succ_data = succ_data[['Ottimo', 'Time-Out']].reindex(ordine_x)
        
        # Grafico a barre impilate (Verde = Ottimo, Rosso = Timeout)
        succ_data.plot(kind='bar', stacked=True, color=['#2ca02c', '#d62728'], edgecolor='black', ax=axes1[idx], legend=False)
        axes1[idx].set_title(f"Distribuzione: {dist}")
        axes1[idx].set_xlabel("Numero Clienti (N)")
        axes1[idx].tick_params(axis='x', rotation=0)
    
    axes1[0].set_ylabel("Numero di Istanze")
    handles, labels = axes1[0].get_legend_handles_labels()
    fig1.legend(handles, ["Ottimo Trovato", "Time-Out (300s)"], loc='upper right', bbox_to_anchor=(0.95, 1.02))
    plt.tight_layout()
    plt.savefig(f"Fig1_Scalabilita_PLI_K{K}.png", dpi=300, bbox_inches='tight')
    plt.close()

    # FIGURA 2: tempi di esecuzione
    fig2, axes2 = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
    fig2.suptitle(f"Tempi di Esecuzione (Scala Log) : {titolo}", fontsize=16, fontweight='bold', y=1.05)
    
    for idx, dist in enumerate(["Uniforme", "Cluster"]):
        df_dist = df_k[df_k['Distribuzione'] == dist]
        # Calcolo tempo medio per approccio
        time_data = df_dist.groupby('Fascia_N')[['Tempo_Esatto_s', 'Tempo_CW_s']].mean().reindex(ordine_x)
        
        axes2[idx].plot(time_data.index, time_data['Tempo_Esatto_s'], marker='o', color='#d62728', linewidth=2, label="Modello Esatto (PLI)")
        axes2[idx].plot(time_data.index, time_data['Tempo_CW_s'], marker='s', linestyle='--', color='#1f77b4', linewidth=2, label="Clarke-Wright")
        
        axes2[idx].set_yscale("log")
        axes2[idx].yaxis.set_major_formatter(ticker.FuncFormatter(format_log_ticks))
        
        axes2[idx].set_ylim(bottom=None, top=900) 
        
        axes2[idx].axhline(y=300, color='gray', linestyle=':', linewidth=1.5, zorder=0)
    
        if idx == 0:
            axes2[idx].text(0, 330, "Limite Time-Out (300s)", color='dimgray', fontsize=9, style='italic', va='bottom', ha='left')

        for i, (x_val, row) in enumerate(time_data.iterrows()):
            t_esatto = row['Tempo_Esatto_s']
            t_cw = row['Tempo_CW_s']
            
            testo_esatto = "> 300s" if t_esatto > 290 else f"{t_esatto:.1f}s"
            axes2[idx].annotate(testo_esatto, (i, t_esatto), textcoords="offset points", xytext=(0, 8), 
                               ha='center', fontsize=9, color='#d62728', weight='bold')
            
            testo_cw = f"{t_cw:.3f}s" if t_cw < 0.1 else f"{t_cw:.2f}s"
            axes2[idx].annotate(testo_cw, (i, t_cw), textcoords="offset points", xytext=(0, -15), 
                               ha='center', fontsize=9, color='#1f77b4', weight='bold')

        axes2[idx].set_title(f"Distribuzione: {dist}")
        axes2[idx].set_xlabel("Numero Clienti (N)")
        axes2[idx].grid(True, which="both", ls="--", alpha=0.3)
        
    axes2[0].set_ylabel("Tempo Medio (secondi)")
    handles, labels = axes2[0].get_legend_handles_labels()
    fig2.legend(handles, labels, loc='upper right', bbox_to_anchor=(0.95, 1.02))
    plt.tight_layout()
    plt.savefig(f"Fig2_Tempi_Esecuzione_K{K}.png", dpi=300, bbox_inches='tight')
    plt.close()

    # FIGURA 3: grafico del GAP totale
    plt.figure(figsize=(9, 6))
    gap_trend = df_k.groupby('Fascia_N')['GAP_%'].mean().reindex(ordine_x)

    plt.plot(gap_trend.index, gap_trend.values, marker='D', linestyle='-', color='#9467bd', linewidth=3, markersize=8)
    plt.fill_between(gap_trend.index, gap_trend.values, color='#9467bd', alpha=0.2)

    plt.title(f"Stabilità dell'Euristica: Trend GAP Medio Globale (K={K})")
    plt.ylabel("GAP Medio (%)")
    plt.xlabel("Dimensione Istanza")
    
    if not gap_trend.empty and max(gap_trend.values) > 0:
        plt.ylim(0, max(gap_trend.values) * 1.3)
    else:
        plt.ylim(0, 10)
    
    for i, v in enumerate(gap_trend.values):
        if pd.notna(v):
            plt.text(i, v + 0.5, f"{v:.1f}%", ha='center', fontweight='bold')

    plt.tight_layout()
    plt.savefig(f"Fig3_Trend_GAP_K{K}.png", dpi=300, bbox_inches='tight')
    plt.close()

    # FIGURA 4: GAP Reale vs GAP Apparente
    agg = df_k.groupby(['Fascia_N', 'Distribuzione', 'Baseline']).agg(
        GAP_mean=('GAP_%', 'mean'),
        Count=('Istanza_ID', 'count')
    ).reset_index()
    
    fig4, axes4 = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
    fig4.suptitle(f"Qualità della Soluzione: {titolo}\nOttimo Globale vs Lower Bound (su 10 occorrenze)", fontsize=16, fontweight='bold', y=1.08)
    
    palette = {'GAP Reale (vs Ottimo)': '#33a02c', 'GAP Apparente (vs Lower Bound)': '#e31a1c'}
    
    for idx, dist in enumerate(["Uniforme", "Cluster"]):
        ax = axes4[idx]
        data_dist = agg[agg['Distribuzione'] == dist]
        
        sns.barplot(
            data=data_dist, x='Fascia_N', y='GAP_mean', hue='Baseline',
            hue_order=['GAP Reale (vs Ottimo)', 'GAP Apparente (vs Lower Bound)'],
            palette=palette, edgecolor='black', ax=ax, order=ordine_x
        )
        
        ax.set_title(f"Distribuzione: {dist}", fontsize=14)
        ax.set_xlabel("Dimensione Istanza", fontsize=12)
        
        if idx == 0:
            ax.set_ylabel("GAP % Medio", fontsize=12)
            ax.legend(title="Termine di Paragone:", loc='upper left')
        else:
            ax.set_ylabel("")
            if ax.get_legend() is not None: ax.get_legend().remove()
                
        for p in ax.patches:
            height = p.get_height()
            if np.isnan(height) or height == 0:
                continue
                
            x_center = p.get_x() + p.get_width() / 2
            x_idx = int(round(x_center))
            
            if x_idx < 0 or x_idx >= len(ordine_x): continue
            
            current_x = ordine_x[x_idx]
            match_x = data_dist[data_dist['Fascia_N'] == current_x]
            match = match_x[np.isclose(match_x['GAP_mean'], height, atol=1e-3)]
            
            if not match.empty:
                count = match['Count'].values[0]
                label_text = f"{height:.1f}%\n({count}/10)"
                ax.text(p.get_x() + p.get_width()/2., height + 0.25, label_text, ha='center', va='bottom', fontweight='bold', fontsize=10)

    axes4[0].margins(y=0.25) 
    plt.tight_layout()
    plt.savefig(f"Fig4_Qualita_Soluzione_K{K}.png", dpi=300, bbox_inches='tight')
    plt.close()

print("\n=== FATTO! Tutti gli 8 grafici sono stati generati e salvati correttamente. ===")
