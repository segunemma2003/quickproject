#!/usr/bin/env python3
"""
Script de test pour eva_detecteur.py
"""
from pathlib import Path
from eva_detecteur import *

def test_basic_functionality():
    """Test des fonctions de base."""
    print("=== Test des fonctions de base ===")
    
    # Test 1: Lecture Feuil3
    try:
        labels_path = Path("Labels Exemple (3).xlsx")
        if labels_path.exists():
            print(f"✓ Fichier {labels_path} trouvé")
            f3 = read_feuil3(labels_path)
            print(f"✓ Feuil3 lu: {len(f3)} lignes, colonnes: {list(f3.columns)}")
            
            uc_map = uc_signals_from_feuil3(f3)
            print(f"✓ Use Cases extraits: {list(uc_map.keys())}")
        else:
            print(f"✗ Fichier {labels_path} non trouvé")
    except Exception as e:
        print(f"✗ Erreur lecture Feuil3: {e}")
    
    # Test 2: Catalogue des exigences
    print(f"\n✓ Catalogue exigences: {len(EXIGENCES_CATALOG)} exigences définies")
    for req_id, req in EXIGENCES_CATALOG.items():
        print(f"  - {req_id}: {req['label']}")
    
    # Test 3: Configuration
    print(f"\n✓ CONFIG initialisé: {CONFIG}")
    
def test_with_sample_data():
    """Test avec des données d'exemple."""
    print("\n=== Test avec données d'exemple ===")
    
    # Simuler des données de signaux
    import numpy as np
    sample_data = {
        "SOC_BMS": np.array([80.0, 81.0, 82.0, 83.0, 82.5]),
        "SOC_Affiche": np.array([79.5, 80.5, 81.5, 82.5, 82.0]),
        "Temperature_Battery": np.array([25.0, 26.0, 25.5, 24.8, 25.2]),
        "Battery_Voltage": np.array([350.0, 352.0, 351.5, 350.8, 351.2])
    }
    
    # Test des exigences
    for req_id in EXIGENCES_CATALOG.keys():
        result = verify_requirement(req_id, sample_data)
        status_symbol = "✓" if result["status"] == "OK" else "✗"
        print(f"{status_symbol} {req_id}: {result['status']} - {result['message']}")

def test_mdf_files():
    """Test avec les fichiers MDF présents."""
    print("\n=== Test fichiers MDF ===")
    
    # Chercher des fichiers MDF
    mdf_files = list(Path(".").glob("*.mdf")) + list(Path("..").glob("*.mdf"))
    
    if mdf_files:
        for mdf_file in mdf_files[:3]:  # Limiter à 3 fichiers
            print(f"\nTest avec {mdf_file}:")
            channels = list_mdf_channels(mdf_file)
            print(f"  Canaux trouvés: {len(channels)}")
            if channels:
                print(f"  Exemples: {list(channels)[:10]}")
    else:
        print("Aucun fichier MDF trouvé dans le répertoire")

def test_requirements_verification():
    """Test de la vérification des exigences."""
    print("\n=== Test vérification exigences ===")
    
    # Créer un fichier CSV temporaire pour test
    import pandas as pd
    test_data = pd.DataFrame({
        "SOC_BMS": [80.0, 81.0, 82.0, 83.0, 82.5],
        "SOC_Affiche": [79.5, 80.5, 81.5, 82.5, 82.0],
        "Temperature_Battery": [25.0, 26.0, 25.5, 24.8, 25.2],
        "Battery_Voltage": [350.0, 352.0, 351.5, 350.8, 351.2],
        "Time": [0.1, 0.2, 0.3, 0.4, 0.5]
    })
    
    test_csv = Path("test_data.csv")
    test_data.to_csv(test_csv, index=False)
    
    try:
        requirements_table = verify_all_requirements(test_csv)
        print(f"✓ Tableau d'exigences généré: {len(requirements_table)} lignes")
        print(requirements_table.to_string(index=False))
    except Exception as e:
        print(f"✗ Erreur vérification exigences: {e}")
    finally:
        # Nettoyer
        if test_csv.exists():
            test_csv.unlink()

if __name__ == "__main__":
    print("🔬 Test du système EVA")
    print("=" * 50)
    
    test_basic_functionality()
    test_with_sample_data()
    test_mdf_files()
    test_requirements_verification()
    
    print("\n" + "=" * 50)
    print("🎯 Tests terminés!")
