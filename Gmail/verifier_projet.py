#!/usr/bin/env python3
"""
🔍 GUIDE DE VÉRIFICATION DU PROJET EVA
=====================================

Ce script vous guide pour vérifier que tout fonctionne correctement.
"""

import os
from pathlib import Path
import sys

def check_file_exists(path, description):
    """Vérifier qu'un fichier existe."""
    if Path(path).exists():
        print(f"✅ {description}: {path}")
        return True
    else:
        print(f"❌ {description}: {path} - MANQUANT")
        return False

def check_import(module_name):
    """Vérifier qu'un module peut être importé."""
    try:
        __import__(module_name)
        print(f"✅ Module {module_name}: Importation OK")
        return True
    except ImportError as e:
        print(f"❌ Module {module_name}: Erreur d'importation - {e}")
        return False

def main():
    print("🔍 VÉRIFICATION DU PROJET EVA")
    print("=" * 50)
    
    # 1. Vérifier les fichiers Python
    print("\n📁 1. FICHIERS PYTHON:")
    files_ok = True
    files_ok &= check_file_exists("eva_detecteur.py", "Script principal")
    files_ok &= check_file_exists("interface_simple.py", "Interface graphique")
    files_ok &= check_file_exists("eva_graphics.py", "Module graphiques")
    files_ok &= check_file_exists("test_eva.py", "Tests unitaires")
    files_ok &= check_file_exists("test_complet.py", "Test complet")
    
    # 2. Vérifier les fichiers de données
    print("\n📊 2. FICHIERS DE DONNÉES:")
    data_ok = True
    data_ok &= check_file_exists("Labels Exemple (3).xlsx", "Fichier Labels/Feuil3")
    data_ok &= check_file_exists("EVA_flux_equivalence_sweet400_500 (1).xlsx", "Fichier SWEET")
    data_ok &= check_file_exists("PVAL_SYS_ROBUSTNESS.005_copie_outil.xlsm", "Fichier PVAL")
    
    # 3. Vérifier les imports Python
    print("\n🐍 3. MODULES PYTHON:")
    imports_ok = True
    imports_ok &= check_import("pandas")
    imports_ok &= check_import("numpy")
    imports_ok &= check_import("tkinter")
    
    try:
        import eva_detecteur
        print("✅ eva_detecteur: Import OK")
        # Tester une fonction clé
        if hasattr(eva_detecteur, 'analyser_et_generer_rapport'):
            print("✅ eva_detecteur: Fonction principale disponible")
        else:
            print("❌ eva_detecteur: Fonction principale manquante")
            imports_ok = False
    except Exception as e:
        print(f"❌ eva_detecteur: Erreur - {e}")
        imports_ok = False
    
    # 4. Tests fonctionnels
    print("\n🧪 4. TESTS FONCTIONNELS:")
    print("Lancement du test complet...")
    
    try:
        # Importer et lancer le test
        from test_complet import main as test_main
        test_result = test_main()
        if test_result:
            print("✅ Test complet: RÉUSSI")
        else:
            print("❌ Test complet: ÉCHEC")
    except Exception as e:
        print(f"❌ Test complet: Erreur - {e}")
        test_result = False
    
    # 5. Vérifier les rapports générés
    print("\n📄 5. RAPPORTS GÉNÉRÉS:")
    reports = list(Path(".").glob("*.html"))
    if reports:
        print(f"✅ {len(reports)} rapport(s) HTML trouvé(s):")
        for report in reports:
            size_kb = report.stat().st_size / 1024
            print(f"   📄 {report.name} ({size_kb:.1f} KB)")
    else:
        print("❌ Aucun rapport HTML trouvé")
    
    # 6. Synthèse finale
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DE LA VÉRIFICATION:")
    
    all_ok = files_ok and data_ok and imports_ok and test_result
    
    if all_ok:
        print("🎉 TOUTES LES VÉRIFICATIONS SONT PASSÉES !")
        print("\n✨ Le projet EVA est complètement fonctionnel.")
        print("\n🚀 COMMENT UTILISER :")
        print("   1. Interface graphique:")
        print("      python interface_simple.py")
        print("   2. Ligne de commande:")
        print("      python eva_detecteur.py --help")
        print("   3. Tests:")
        print("      python test_complet.py")
        
    else:
        print("⚠️ CERTAINES VÉRIFICATIONS ONT ÉCHOUÉ")
        print("\n🔧 Actions à effectuer :")
        if not files_ok:
            print("   - Vérifier que tous les fichiers Python sont présents")
        if not data_ok:
            print("   - Vérifier que tous les fichiers Excel/données sont présents")
        if not imports_ok:
            print("   - Installer les modules Python manquants")
        if not test_result:
            print("   - Corriger les erreurs détectées lors des tests")
    
    print("\n" + "=" * 50)
    return all_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
