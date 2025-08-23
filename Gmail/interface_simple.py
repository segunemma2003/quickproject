import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading
import webbrowser
import os
from typing import Optional

# ====== Backend ======
from eva_detecteur import (
    analyser_et_generer_rapport,
    verifier_presence_mapping_0p01s,
    CONFIG,
)

# ====== Interface simplifiée ======
class EVAApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Interface EVA – Analyseur de données")
        self.root.geometry("800x600")
        
        # Variables d'état
        self.selected_file: Optional[str] = None
        self.detected_uc: str = "Non détecté"
        
        self._build_interface()

    def _build_interface(self):
        # Titre
        title_frame = tk.Frame(self.root, bg="white", pady=10)
        title_frame.pack(fill="x")
        tk.Label(title_frame, text="🔬 Interface EVA", font=("Arial", 18, "bold"), bg="white").pack()
        tk.Label(title_frame, text="Analyseur de données véhicule", font=("Arial", 12), bg="white").pack()
        
        # Section fichier
        file_frame = tk.LabelFrame(self.root, text="📁 Fichier de mesures", font=("Arial", 12, "bold"), padx=10, pady=10)
        file_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Button(file_frame, text="📂 Sélectionner un fichier MDF", 
                 command=self._select_file, font=("Arial", 11), bg="#007ACC", fg="white").pack(pady=5)
        
        self.file_label = tk.Label(file_frame, text="Aucun fichier sélectionné", 
                                  font=("Arial", 10), fg="gray")
        self.file_label.pack(pady=5)
        
        # Section analyse
        analysis_frame = tk.LabelFrame(self.root, text="🔍 Analyse", font=("Arial", 12, "bold"), padx=10, pady=10)
        analysis_frame.pack(fill="x", padx=20, pady=10)
        
        self.btn_analyze = tk.Button(analysis_frame, text="🚀 Lancer l'analyse", 
                                    command=self._run_analysis, font=("Arial", 11), 
                                    bg="#28A745", fg="white", state="disabled")
        self.btn_analyze.pack(pady=10)
        
        # Section résultats
        results_frame = tk.LabelFrame(self.root, text="📊 Résultats", font=("Arial", 12, "bold"), padx=10, pady=10)
        results_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Use Case détecté
        uc_frame = tk.Frame(results_frame)
        uc_frame.pack(fill="x", pady=5)
        tk.Label(uc_frame, text="Use Case détecté:", font=("Arial", 11, "bold")).pack(side="left")
        self.uc_result = tk.Label(uc_frame, text=self.detected_uc, font=("Arial", 11), 
                                 bg="#F8F9FA", relief="solid", padx=10)
        self.uc_result.pack(side="left", padx=(10, 0))
        
        # Barre de progression
        progress_frame = tk.Frame(results_frame)
        progress_frame.pack(fill="x", pady=10)
        tk.Label(progress_frame, text="Progression:", font=("Arial", 11)).pack(anchor="w")
        self.progress = ttk.Progressbar(progress_frame, mode="determinate", length=400)
        self.progress.pack(fill="x", pady=5)
        self.progress_label = tk.Label(progress_frame, text="0%", font=("Arial", 10))
        self.progress_label.pack(anchor="w")
        
        # Zone de texte pour les résultats
        text_frame = tk.Frame(results_frame)
        text_frame.pack(fill="both", expand=True, pady=10)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.results_text = tk.Text(text_frame, height=15, wrap="word", yscrollcommand=scrollbar.set)
        self.results_text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.results_text.yview)
        
        # Boutons d'action
        action_frame = tk.Frame(self.root)
        action_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Button(action_frame, text="📄 Ouvrir rapport HTML", 
                 command=self._open_report, font=("Arial", 10)).pack(side="left", padx=5)
        
        tk.Button(action_frame, text="❌ Quitter", 
                 command=self.root.quit, font=("Arial", 10)).pack(side="right", padx=5)

    def _select_file(self):
        """Sélectionner un fichier MDF."""
        filetypes = [
            ("Fichiers MDF", "*.mdf *.mf4 *.dat"),
            ("Tous les fichiers", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="Sélectionner un fichier de mesures",
            filetypes=filetypes
        )
        
        if file_path:
            self.selected_file = file_path
            filename = os.path.basename(file_path)
            self.file_label.config(text=f"Fichier: {filename}", fg="green")
            self.btn_analyze.config(state="normal")
            self._log("✓ Fichier sélectionné: " + filename)

    def _run_analysis(self):
        """Lancer l'analyse du fichier."""
        if not self.selected_file:
            messagebox.showerror("Erreur", "Aucun fichier sélectionné")
            return
        
        self.btn_analyze.config(state="disabled")
        self._update_progress(10)
        self._log("🔄 Démarrage de l'analyse...")
        
        def analyze():
            try:
                # Analyse principale
                self._log("📖 Lecture des fichiers de configuration...")
                self._update_progress(30)
                
                results = analyser_et_generer_rapport(self.selected_file)
                
                self._log("✅ Analyse terminée")
                self._update_progress(80)
                
                # Traitement des résultats
                detected_ucs = [uc for uc, info in results.items() 
                              if info.get("status") == "detected"]
                
                if detected_ucs:
                    self.detected_uc = detected_ucs[0]
                    self._log(f"🎯 Use Case détecté: {self.detected_uc}")
                else:
                    self.detected_uc = "Aucun UC détecté"
                    self._log("⚠️ Aucun Use Case détecté")
                
                # Exigences
                if "_requirements" in results:
                    req_info = results["_requirements"]
                    self._log(f"📋 Exigences vérifiées: {req_info['total']}")
                    self._log(f"   - OK: {req_info['ok']}")
                    self._log(f"   - NOK: {req_info['nok']}")
                    self._log(f"   - Erreur: {req_info['error']}")
                
                self._update_progress(100)
                
                # Mettre à jour l'interface
                self.root.after(0, self._update_results)
                
            except Exception as e:
                self.root.after(0, lambda: self._log(f"❌ Erreur: {str(e)}"))
            finally:
                self.root.after(0, lambda: self.btn_analyze.config(state="normal"))
        
        threading.Thread(target=analyze, daemon=True).start()

    def _update_results(self):
        """Mettre à jour l'affichage des résultats."""
        self.uc_result.config(text=self.detected_uc)
        
        # Changer la couleur selon le résultat
        if "détecté" not in self.detected_uc.lower() or "aucun" in self.detected_uc.lower():
            self.uc_result.config(bg="#FFF3CD", fg="#856404")  # Jaune
        else:
            self.uc_result.config(bg="#D4EDDA", fg="#155724")  # Vert

    def _update_progress(self, value):
        """Mettre à jour la barre de progression."""
        def update():
            self.progress["value"] = value
            self.progress_label.config(text=f"{value}%")
        self.root.after(0, update)

    def _log(self, message):
        """Ajouter un message au log."""
        def add_log():
            self.results_text.insert("end", message + "\n")
            self.results_text.see("end")
        self.root.after(0, add_log)

    def _open_report(self):
        """Ouvrir le rapport HTML."""
        report_path = Path("rapport_eva.html")
        if report_path.exists():
            webbrowser.open(report_path.resolve().as_uri())
            self._log("📄 Rapport ouvert dans le navigateur")
        else:
            messagebox.showwarning("Attention", "Aucun rapport trouvé. Lancez d'abord une analyse.")

def main():
    root = tk.Tk()
    app = EVAApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
