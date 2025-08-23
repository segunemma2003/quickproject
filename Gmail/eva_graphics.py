#!/usr/bin/env python3
"""
Module de génération de graphiques pour EVA
"""
import matplotlib
matplotlib.use('Agg')  # Backend non-interactif pour éviter les warnings
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd

def create_signal_plots(signal_data: Dict[str, np.ndarray], output_dir: Path = Path("plots")) -> List[Path]:
    """Génère des graphiques pour les signaux."""
    output_dir.mkdir(exist_ok=True)
    generated_plots = []
    
    # Style des graphiques
    try:
        plt.style.use('seaborn-v0_8')
    except:
        try:
            plt.style.use('seaborn')
        except:
            pass  # Utiliser le style par défaut
    
    for signal_name, data in signal_data.items():
        if len(data) == 0:
            continue
            
        try:
            # Créer le graphique
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Créer un axe temporel simple
            time_axis = np.linspace(0, len(data) * 0.01, len(data))  # 10ms par échantillon
            
            ax.plot(time_axis, data, linewidth=2, label=signal_name)
            ax.set_xlabel('Temps (s)')
            ax.set_ylabel('Valeur')
            ax.set_title(f'Signal: {signal_name}')
            ax.grid(True, alpha=0.3)
            ax.legend()
            
            # Ajouter des statistiques
            if len(data) > 0:
                stats_text = f'Min: {np.min(data):.2f}\nMax: {np.max(data):.2f}\nMoy: {np.mean(data):.2f}\nÉcart-type: {np.std(data):.2f}'
                ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
                       verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
            
            # Sauvegarder
            plot_path = output_dir / f"{signal_name.replace('/', '_')}.png"
            plt.savefig(plot_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            generated_plots.append(plot_path)
            
        except Exception as e:
            print(f"Erreur lors de la génération du graphique pour {signal_name}: {e}")
            plt.close()
    
    return generated_plots

def create_requirements_summary_plot(requirements_table: pd.DataFrame, output_path: Path = Path("requirements_summary.png")):
    """Génère un graphique de synthèse des exigences."""
    if requirements_table.empty:
        return None
        
    try:
        # Compter les statuts
        status_counts = requirements_table['Status'].value_counts()
        
        # Couleurs
        colors = {'OK': '#5CB85C', 'NOK': '#E74C3C', 'ERROR': '#F39C12'}
        plot_colors = [colors.get(status, '#BDC3C7') for status in status_counts.index]
        
        # Créer le graphique
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Graphique en secteurs
        ax1.pie(status_counts.values, labels=status_counts.index, autopct='%1.1f%%', 
                colors=plot_colors, startangle=90)
        ax1.set_title('Répartition des statuts des exigences')
        
        # Graphique en barres
        bars = ax2.bar(status_counts.index, status_counts.values, color=plot_colors)
        ax2.set_title('Nombre d\'exigences par statut')
        ax2.set_ylabel('Nombre d\'exigences')
        
        # Ajouter les valeurs sur les barres
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_path
        
    except Exception as e:
        print(f"Erreur lors de la génération du graphique de synthèse: {e}")
        plt.close()
        return None

def create_use_cases_plot(uc_table: pd.DataFrame, output_path: Path = Path("use_cases_summary.png")):
    """Génère un graphique de synthèse des Use Cases."""
    if uc_table.empty:
        return None
        
    try:
        # Données pour le graphique
        uc_names = [uc.replace("UC ", "").split(" — ")[0] for uc in uc_table['UC']]
        required = uc_table['Required'].values
        present = uc_table['Present'].values
        
        # Créer le graphique
        fig, ax = plt.subplots(figsize=(12, 8))
        
        x = np.arange(len(uc_names))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, required, width, label='Signaux requis', color='#3498DB', alpha=0.8)
        bars2 = ax.bar(x + width/2, present, width, label='Signaux présents', color='#2ECC71', alpha=0.8)
        
        ax.set_xlabel('Use Cases')
        ax.set_ylabel('Nombre de signaux')
        ax.set_title('Disponibilité des signaux par Use Case')
        ax.set_xticks(x)
        ax.set_xticklabels(uc_names, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Ajouter les valeurs sur les barres
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_path
        
    except Exception as e:
        print(f"Erreur lors de la génération du graphique Use Cases: {e}")
        plt.close()
        return None

def generate_all_plots(signal_data: Dict[str, np.ndarray], 
                      requirements_table: Optional[pd.DataFrame] = None,
                      uc_table: Optional[pd.DataFrame] = None) -> Dict[str, List[Path]]:
    """Génère tous les graphiques et retourne les chemins."""
    plots = {
        "signals": [],
        "summary": []
    }
    
    # Graphiques des signaux
    if signal_data:
        plots["signals"] = create_signal_plots(signal_data)
    
    # Graphiques de synthèse
    if requirements_table is not None and not requirements_table.empty:
        req_plot = create_requirements_summary_plot(requirements_table)
        if req_plot:
            plots["summary"].append(req_plot)
    
    if uc_table is not None and not uc_table.empty:
        uc_plot = create_use_cases_plot(uc_table)
        if uc_plot:
            plots["summary"].append(uc_plot)
    
    return plots

if __name__ == "__main__":
    # Test du module de graphiques
    print("🎨 Test du module de graphiques")
    
    # Données d'exemple
    sample_data = {
        "SOC_BMS": np.array([80.0, 81.0, 82.0, 83.0, 82.5, 81.8, 82.2]),
        "Temperature_Battery": np.array([25.0, 26.0, 25.5, 24.8, 25.2, 25.8, 25.1]),
        "Battery_Voltage": np.array([350.0, 352.0, 351.5, 350.8, 351.2, 351.9, 351.1])
    }
    
    requirements_data = pd.DataFrame({
        'Status': ['OK', 'OK', 'NOK', 'OK', 'ERROR'],
        'Exigence': ['REQ1', 'REQ2', 'REQ3', 'REQ4', 'REQ5']
    })
    
    uc_data = pd.DataFrame({
        'UC': ['UC 1.1', 'UC 1.2', 'UC 2.1'],
        'Required': [5, 8, 3],
        'Present': [5, 6, 3]
    })
    
    plots = generate_all_plots(sample_data, requirements_data, uc_data)
    
    print(f"✓ Graphiques générés:")
    print(f"  - Signaux: {len(plots['signals'])} fichiers")
    print(f"  - Synthèse: {len(plots['summary'])} fichiers")
    
    for plot_path in plots['summary']:
        print(f"    📊 {plot_path}")
