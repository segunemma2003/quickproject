#!/usr/bin/env python3
"""
Test complet du système EVA avec génération de rapport
"""
from pathlib import Path
import pandas as pd
import numpy as np
from eva_detecteur import analyser_et_generer_rapport

def create_test_mdf():
    """Créer un fichier de test CSV (simulant un MDF)."""
    # Créer des données de test réalistes
    time_data = np.linspace(0, 10, 1000)  # 10 secondes, 1000 échantillons
    
    # Signaux de test
    data = {
        "Time": time_data,
        "SOC_BMS": 80 + 5 * np.sin(time_data * 0.5) + np.random.normal(0, 0.5, 1000),
        "SOC_Affiche": 80 + 5 * np.sin(time_data * 0.5) + np.random.normal(0, 1.0, 1000),
        "Temperature_Battery": 25 + 10 * np.sin(time_data * 0.2) + np.random.normal(0, 2, 1000),
        "Battery_Voltage": 350 + 20 * np.sin(time_data * 0.3) + np.random.normal(0, 5, 1000),
        "HevcWakeUpSleepcommand": np.random.choice([0, 1], 1000),
        "Powerrelaystate": np.random.choice([0, 1], 1000),
        # Signaux de Feuil3 (premiers de la liste)
        "TimeHour": np.random.uniform(0, 24, 1000),
        "TimeMinute": np.random.uniform(0, 60, 1000),
        "TimeSeconde": np.random.uniform(0, 60, 1000),
        "CustomerApproachDetected": np.random.choice([0, 1], 1000),
        "V_WakeUpSleepCommand": np.random.choice([0, 1], 1000),
        "WakeUpType": np.random.randint(0, 4, 1000),
    }
    
    df = pd.DataFrame(data)
    
    # Créer le fichier CSV
    test_file = Path("test_data.csv")
    df.to_csv(test_file, index=False)
    
    return test_file

def main():
    print("🧪 Test complet du système EVA")
    print("=" * 50)
    
    # Créer le fichier de test
    print("📊 Création du fichier de données de test...")
    test_file = create_test_mdf()
    print(f"✓ Fichier créé: {test_file}")
    
    # Lancer l'analyse complète
    print("\n🔬 Lancement de l'analyse complète...")
    try:
        results = analyser_et_generer_rapport(str(test_file))
        
        print("✅ Analyse terminée avec succès!")
        
        # Afficher les résultats
        print("\n📋 Résultats:")
        for uc, info in results.items():
            if not uc.startswith("_"):
                status_icon = "🟢" if info.get("status") == "detected" else "🟡"
                print(f"  {status_icon} {uc}: {info.get('status', 'unknown')}")
                if "required" in info:
                    print(f"      Requis: {info['required']}, Présents: {info['present']}")
        
        # Afficher les exigences
        if "_requirements" in results:
            req_info = results["_requirements"]
            print(f"\n📊 Exigences vérifiées:")
            print(f"  📈 Total: {req_info['total']}")
            print(f"  ✅ OK: {req_info['ok']}")
            print(f"  ❌ NOK: {req_info['nok']}")
            print(f"  ⚠️ Erreur: {req_info['error']}")
        
        # Vérifier si le rapport a été généré
        rapport_path = Path("rapport_eva.html")
        if rapport_path.exists():
            print(f"\n📄 Rapport HTML généré: {rapport_path}")
            print(f"   Taille: {rapport_path.stat().st_size / 1024:.1f} KB")
        else:
            print("\n❌ Rapport HTML non généré")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")
        return False
    
    finally:
        # Nettoyer
        if test_file.exists():
            test_file.unlink()
            print(f"\n🧹 Fichier de test supprimé: {test_file}")
    
    print("\n" + "=" * 50)
    print("✨ Test complet terminé!")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Le système EVA est opérationnel!")
        print("💡 Vous pouvez maintenant utiliser:")
        print("   - interface_simple.py pour l'interface graphique")
        print("   - eva_detecteur.py en ligne de commande")
        print("   - rapport_eva.html pour voir les résultats")
    else:
        print("\n⚠️ Des problèmes ont été détectés. Vérifiez les erreurs ci-dessus.")
