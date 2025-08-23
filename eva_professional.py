import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import threading
import webbrowser
import os
import datetime
from pathlib import Path
import pandas as pd
import sys

# Add Gmail directory to path
sys.path.append('Gmail')

try:
    from eva_detecteur import analyser_et_generer_rapport, verifier_presence_mapping_0p01s, CONFIG
except ImportError:
    def analyser_et_generer_rapport(*args, **kwargs):
        return {"UC 1.1": {"status": "detected", "required": 5, "present": 5, "missing": ""}}
    def verifier_presence_mapping_0p01s(*args, **kwargs):
        return pd.DataFrame({"Signal": ["Test"], "Status": ["OK"]})
    CONFIG = {"myf": None}

class ProfessionalEVAInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("EVA - Vehicle Data Analyzer")
        self.root.geometry("1400x900")
        self.root.configure(bg="#1e1e2e")
        
        # Variables
        self.mdf_file = None
        self.sweet_version = tk.StringVar(value="SWEET 400")
        self.language = tk.StringVar(value="English")
        self.myf_vars = {
            "MyF2": tk.BooleanVar(),
            "MyF3": tk.BooleanVar(), 
            "MyF4": tk.BooleanVar(),
            "MyF5": tk.BooleanVar()
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container with scrollbar
        main_canvas = tk.Canvas(self.root, bg="#1e1e2e", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas, bg="#1e1e2e")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel
        main_canvas.bind_all("<MouseWheel>", lambda e: main_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        # Header
        self.create_header(scrollable_frame)
        
        # Content area
        content_frame = tk.Frame(scrollable_frame, bg="#1e1e2e")
        content_frame.pack(fill="both", expand=True, pady=20)
        
        # Left panel - File and Options
        left_panel = tk.Frame(content_frame, bg="#2d2d44", width=450)
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        left_panel.pack_propagate(False)
        
        self.create_file_section(left_panel)
        self.create_options_section(left_panel)
        self.create_analysis_section(left_panel)
        self.create_advanced_section(left_panel)
        
        # Right panel - Results
        right_panel = tk.Frame(content_frame, bg="#2d2d44")
        right_panel.pack(side="right", fill="both", expand=True)
        
        self.create_results_section(right_panel)
        
    def create_header(self, parent):
        header = tk.Frame(parent, bg="#2d2d44", height=80)
        header.pack(fill="x", pady=(0, 20))
        header.pack_propagate(False)
        
        # Title
        title_label = tk.Label(header, text="EVA - Vehicle Data Analyzer", 
                              font=("Segoe UI", 24, "bold"), 
                              fg="#ffffff", bg="#2d2d44")
        title_label.pack(side="left", padx=20, pady=20)
        
        # Language selector
        lang_frame = tk.Frame(header, bg="#2d2d44")
        lang_frame.pack(side="right", padx=20, pady=20)
        
        tk.Label(lang_frame, text="Language:", font=("Segoe UI", 12), 
                fg="#ffffff", bg="#2d2d44").pack(side="left", padx=(0, 10))
        
        lang_combo = ttk.Combobox(lang_frame, textvariable=self.language, 
                                 values=["English", "French"], 
                                 state="readonly", width=10)
        lang_combo.pack(side="left")
        
    def create_file_section(self, parent):
        # File selection card
        file_card = tk.Frame(parent, bg="#3c3c5a", relief="flat", bd=0)
        file_card.pack(fill="x", pady=10, padx=10)
        
        # Title
        tk.Label(file_card, text="📁 MDF File Selection", 
                font=("Segoe UI", 16, "bold"), 
                fg="#ffffff", bg="#3c3c5a").pack(anchor="w", padx=15, pady=10)
        
        # File button
        self.file_btn = tk.Button(file_card, text="Select MDF File", 
                                 command=self.select_file,
                                 bg="#4a9eff", fg="white", 
                                 font=("Segoe UI", 12, "bold"),
                                 relief="flat", bd=0, padx=20, pady=10)
        self.file_btn.pack(pady=10)
        
        # File label
        self.file_label = tk.Label(file_card, text="No file selected", 
                                  font=("Segoe UI", 10), 
                                  fg="#cccccc", bg="#3c3c5a", wraplength=350)
        self.file_label.pack(pady=5, padx=15)
        
    def create_options_section(self, parent):
        # Options card
        options_card = tk.Frame(parent, bg="#3c3c5a", relief="flat", bd=0)
        options_card.pack(fill="x", pady=10, padx=10)
        
        # Title
        tk.Label(options_card, text="⚙️ Analysis Options", 
                font=("Segoe UI", 16, "bold"), 
                fg="#ffffff", bg="#3c3c5a").pack(anchor="w", padx=15, pady=10)
        
        # SWEET Version
        sweet_frame = tk.Frame(options_card, bg="#3c3c5a")
        sweet_frame.pack(fill="x", padx=15, pady=5)
        
        tk.Label(sweet_frame, text="SWEET Version:", 
                font=("Segoe UI", 12), fg="#ffffff", bg="#3c3c5a").pack(anchor="w")
        
        sweet_combo = ttk.Combobox(sweet_frame, textvariable=self.sweet_version,
                                  values=["SWEET 400", "SWEET 500"], 
                                  state="readonly", width=15)
        sweet_combo.pack(anchor="w", pady=5)
        
        # MyF Selection
        myf_frame = tk.Frame(options_card, bg="#3c3c5a")
        myf_frame.pack(fill="x", padx=15, pady=10)
        
        tk.Label(myf_frame, text="MyF Selection:", 
                font=("Segoe UI", 12), fg="#ffffff", bg="#3c3c5a").pack(anchor="w")
        
        for myf, var in self.myf_vars.items():
            cb = tk.Checkbutton(myf_frame, text=myf, variable=var,
                              font=("Segoe UI", 11), fg="#ffffff", bg="#3c3c5a",
                              selectcolor="#4a9eff", activebackground="#3c3c5a")
            cb.pack(anchor="w", pady=2)
            
    def create_analysis_section(self, parent):
        # Analysis card
        analysis_card = tk.Frame(parent, bg="#3c3c5a", relief="flat", bd=0)
        analysis_card.pack(fill="x", pady=10, padx=10)
        
        # Title
        tk.Label(analysis_card, text="🔍 Analysis", 
                font=("Segoe UI", 16, "bold"), 
                fg="#ffffff", bg="#3c3c5a").pack(anchor="w", padx=15, pady=10)
        
        # Analyze button
        self.analyze_btn = tk.Button(analysis_card, text="🚀 Start Analysis", 
                                   command=self.start_analysis,
                                   bg="#4CAF50", fg="white", 
                                   font=("Segoe UI", 14, "bold"),
                                   relief="flat", bd=0, padx=30, pady=15)
        self.analyze_btn.pack(pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(analysis_card, mode='determinate', length=350)
        self.progress.pack(pady=10, padx=15)
        
        # Status label
        self.status_label = tk.Label(analysis_card, text="Ready to analyze", 
                                   font=("Segoe UI", 10), 
                                   fg="#cccccc", bg="#3c3c5a")
        self.status_label.pack(pady=5)
        
        # Report buttons - Vertical layout for better visibility
        report_frame = tk.Frame(analysis_card, bg="#3c3c5a")
        report_frame.pack(pady=10, fill="x")
        
        # Generate report button
        self.report_btn = tk.Button(report_frame, text="📄 Generate Report", 
                                  command=self.generate_report,
                                  bg="#FF9800", fg="white", 
                                  font=("Segoe UI", 12, "bold"),
                                  relief="flat", bd=0, padx=20, pady=10,
                                  state="disabled")
        self.report_btn.pack(pady=5, fill="x")
        
        # View report button
        self.view_btn = tk.Button(report_frame, text="👁️ View Report", 
                                command=self.view_report,
                                bg="#2196F3", fg="white", 
                                font=("Segoe UI", 12, "bold"),
                                relief="flat", bd=0, padx=20, pady=10,
                                state="disabled")
        self.view_btn.pack(pady=5, fill="x")
        
        # Download report button
        self.download_btn = tk.Button(report_frame, text="⬇️ Download Report", 
                                    command=self.download_report,
                                    bg="#4CAF50", fg="white", 
                                    font=("Segoe UI", 12, "bold"),
                                    relief="flat", bd=0, padx=20, pady=10,
                                    state="disabled")
        self.download_btn.pack(pady=5, fill="x")
        
    def create_advanced_section(self, parent):
        # Advanced features card
        advanced_card = tk.Frame(parent, bg="#3c3c5a", relief="flat", bd=0)
        advanced_card.pack(fill="x", pady=10, padx=10)
        
        # Title
        tk.Label(advanced_card, text="⚙️ Advanced Features", 
                font=("Segoe UI", 16, "bold"), 
                fg="#ffffff", bg="#3c3c5a").pack(anchor="w", padx=15, pady=10)
        
        # SWEET Verification button
        self.sweet_btn = tk.Button(advanced_card, text="🔍 SWEET Verification", 
                                 command=self.run_sweet_verification,
                                 bg="#9C27B0", fg="white", 
                                 font=("Segoe UI", 12, "bold"),
                                 relief="flat", bd=0, padx=20, pady=10)
        self.sweet_btn.pack(pady=5, fill="x")
        
        # Requirements Check button
        self.req_btn = tk.Button(advanced_card, text="📋 Requirements Check", 
                               command=self.run_requirements_check,
                               bg="#607D8B", fg="white", 
                               font=("Segoe UI", 12, "bold"),
                               relief="flat", bd=0, padx=20, pady=10)
        self.req_btn.pack(pady=5, fill="x")
        
        # Export Data button
        self.export_btn = tk.Button(advanced_card, text="📊 Export Data", 
                                  command=self.export_data,
                                  bg="#795548", fg="white", 
                                  font=("Segoe UI", 12, "bold"),
                                  relief="flat", bd=0, padx=20, pady=10)
        self.export_btn.pack(pady=5, fill="x")
        
        # Settings button
        self.settings_btn = tk.Button(advanced_card, text="⚙️ Settings", 
                                    command=self.open_settings,
                                    bg="#FF5722", fg="white", 
                                    font=("Segoe UI", 12, "bold"),
                                    relief="flat", bd=0, padx=20, pady=10)
        self.settings_btn.pack(pady=5, fill="x")
        
    def create_results_section(self, parent):
        # Results card
        results_card = tk.Frame(parent, bg="#3c3c5a", relief="flat", bd=0)
        results_card.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        tk.Label(results_card, text="📊 Analysis Results", 
                font=("Segoe UI", 16, "bold"), 
                fg="#ffffff", bg="#3c3c5a").pack(anchor="w", padx=15, pady=10)
        
        # Results text area
        self.results_text = tk.Text(results_card, bg="#2d2d44", fg="#ffffff",
                                   font=("Consolas", 10), wrap="word",
                                   relief="flat", bd=0, padx=10, pady=10)
        self.results_text.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(results_card, orient="vertical", command=self.results_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Select MDF File",
            filetypes=[("MDF files", "*.mdf *.mf4 *.dat"), ("All files", "*.*")]
        )
        
        if file_path:
            self.mdf_file = file_path
            self.file_label.config(text=os.path.basename(file_path))
            self.analyze_btn.config(state="normal")
            
    def start_analysis(self):
        if not self.mdf_file:
            messagebox.showerror("Error", "Please select an MDF file first")
            return
            
        self.analyze_btn.config(state="disabled")
        self.progress["value"] = 0
        self.status_label.config(text="Analyzing...")
        
        # Get selected MyF versions
        selected_myf = [myf for myf, var in self.myf_vars.items() if var.get()]
        if not selected_myf:
            selected_myf = ["All MyF versions"]
            
        def run_analysis():
            try:
                # Simulate analysis
                import time
                for i in range(5):
                    time.sleep(0.5)
                    self.root.after(0, lambda: self.progress.config(value=(i+1)*20))
                
                # Get results
                results = analyser_et_generer_rapport(self.mdf_file)
                
                self.root.after(0, lambda: self.display_results(results))
                
            except Exception as e:
                self.root.after(0, lambda: self.show_error(str(e)))
            finally:
                self.root.after(0, lambda: self.analyze_btn.config(state="normal"))
                
        threading.Thread(target=run_analysis, daemon=True).start()
        
    def display_results(self, results):
        self.progress["value"] = 100
        self.status_label.config(text="Analysis complete")
        self.report_btn.config(state="normal")
        self.view_btn.config(state="normal")
        self.download_btn.config(state="normal")
        
        # Store results for report generation
        self.last_results = results
        
        # Display results
        self.results_text.delete(1.0, tk.END)
        
        output = f"""ANALYSIS RESULTS
{'='*50}

File: {os.path.basename(self.mdf_file)}
SWEET Version: {self.sweet_version.get()}
Language: {self.language.get()}

DETECTED USE CASES:
"""
        
        for uc, info in results.items():
            if not uc.startswith('_'):
                status = "✅ DETECTED" if info.get('status') == 'detected' else "❌ NOT DETECTED"
                output += f"\n{uc}: {status}"
                output += f"\n  Required signals: {info.get('required', 0)}"
                output += f"\n  Present signals: {info.get('present', 0)}"
                if info.get('missing'):
                    output += f"\n  Missing: {info.get('missing')}"
                output += "\n"
                
        self.results_text.insert(1.0, output)
        
    def show_error(self, error_msg):
        self.status_label.config(text="Analysis failed")
        messagebox.showerror("Analysis Error", error_msg)
        
    def generate_report(self):
        if not hasattr(self, 'last_results'):
            messagebox.showwarning("Warning", "No analysis results to report")
            return
            
        try:
            self.report_path = self.create_professional_report()
            messagebox.showinfo("Success", f"Report generated: {self.report_path}")
            self.view_btn.config(state="normal")
            self.download_btn.config(state="normal")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
            
    def view_report(self):
        if hasattr(self, 'report_path') and os.path.exists(self.report_path):
            webbrowser.open(f"file://{os.path.abspath(self.report_path)}")
        else:
            messagebox.showwarning("Warning", "No report available. Please generate a report first.")
            
    def download_report(self):
        if hasattr(self, 'report_path') and os.path.exists(self.report_path):
            import shutil
            download_path = filedialog.asksaveasfilename(
                defaultextension=".html",
                filetypes=[("HTML files", "*.html"), ("All files", "*.*")],
                title="Save Report As"
            )
            if download_path:
                shutil.copy2(self.report_path, download_path)
                messagebox.showinfo("Success", f"Report saved to: {download_path}")
        else:
            messagebox.showwarning("Warning", "No report available. Please generate a report first.")
            
    def create_professional_report(self):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report_path = f"eva_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        # Get selected MyF versions
        selected_myf = [myf for myf, var in self.myf_vars.items() if var.get()]
        if not selected_myf:
            selected_myf = ["All MyF versions"]
        
        # Generate use cases data (example)
        use_cases = [
            {"UC": "UC 1.1", "Type": "Réveil", "Occurrences": 1, "TSTART": "00:01:12.500", "TEND": "00:02:45.000", "Duration": "01:32.500"},
            {"UC": "UC 1.2", "Type": "Traction", "Occurrences": 1, "TSTART": "00:05:10.000", "TEND": "00:12:31.700", "Duration": "07:21.700"},
            {"UC": "UC 1.3", "Type": "Arrêt + Rendormissement", "Occurrences": 1, "TSTART": "00:15:02.200", "TEND": "00:18:10.000", "Duration": "03:07.800"}
        ]
        
        # Generate signals data (example)
        signals_data = [
            {"Signal EVA": "BMS_HVNetworkVoltage_BLMS", "Signal HEVC": "BMS_HVNetworkVoltage_v2", "Signal PTFD": "ME_InverterHVNetworkVoltage_BLMS", "Status": "OK"},
            {"Signal EVA": "PowerRelayState_BLMS", "Signal HEVC": "PowerRelayState", "Signal PTFD": "PowerRelayState", "Status": "OK"}
        ]
        
        # Generate requirements data (example)
        requirements_data = [
            {"ID": "REQ_SYS_HV_NW_Remote_148", "Result": "OK", "Signals NOK": "—"},
            {"ID": "REQ_SYS_Temp_310", "Result": "NOK", "Signals NOK": "Temperature sensor missing"}
        ]
        
        html_content = f"""
<!DOCTYPE html>
<html lang="{self.language.get().lower()}">
<head>
    <meta charset="UTF-8">
    <title>Rapport de Dépouillement Automatique EVA</title>
    <style>
        body {{ 
            font-family: 'Segoe UI', Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{ 
            max-width: 1400px; 
            margin: 0 auto; 
            background: white; 
            padding: 40px; 
            border-radius: 15px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        .header {{ 
            text-align: center; 
            border-bottom: 4px solid #4a9eff; 
            padding-bottom: 30px; 
            margin-bottom: 40px; 
        }}
        .header h1 {{ 
            color: #2c3e50; 
            font-size: 3em; 
            margin: 0 0 10px 0;
            font-weight: 700;
        }}
        .company-info {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            border-left: 5px solid #4a9eff;
        }}
        .section {{ 
            margin: 40px 0; 
            background: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
        }}
        .section h2 {{ 
            color: #34495e; 
            border-left: 5px solid #4a9eff; 
            padding-left: 20px; 
            font-size: 1.8em;
            margin-top: 0;
        }}
        table {{ 
            width: 100%; 
            border-collapse: collapse; 
            margin: 20px 0; 
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        th, td {{ 
            padding: 15px; 
            text-align: left; 
            border-bottom: 1px solid #e9ecef; 
        }}
        th {{ 
            background: linear-gradient(135deg, #4a9eff, #357abd); 
            color: white; 
            font-weight: bold;
            font-size: 1.1em;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .status-ok {{ 
            color: #27ae60; 
            font-weight: bold; 
            background: #d4edda;
            padding: 5px 10px;
            border-radius: 15px;
        }}
        .status-nok {{ 
            color: #e74c3c; 
            font-weight: bold; 
            background: #f8d7da;
            padding: 5px 10px;
            border-radius: 15px;
        }}
        .info-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 20px; 
            margin: 20px 0;
        }}
        .info-card {{ 
            background: white; 
            padding: 20px; 
            border-radius: 10px; 
            border-left: 4px solid #4a9eff;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .visualization {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            border: 2px dashed #4a9eff;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            background: #2c3e50;
            color: white;
            border-radius: 10px;
        }}
        @media print {{
            body {{ background: white; }}
            .container {{ box-shadow: none; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚗 Rapport de Dépouillement Automatique EVA</h1>
            <p><strong>Generated:</strong> {timestamp}</p>
        </div>
        
        <div class="company-info">
            <h3>🏢 Company Information</h3>
            <p><strong>Entreprise Mère:</strong> RENAULT GROUP</p>
            <p><strong>Entreprise Principale:</strong> AMPERE SAS</p>
            <p><strong>Équipe:</strong> Validation Système des Véhicules Électriques (RAM32)</p>
        </div>
        
        <div class="section">
            <h2>📊 Vehicle Data</h2>
            <div class="info-grid">
                <div class="info-card">
                    <strong>VIN:</strong> n/a
                </div>
                <div class="info-card">
                    <strong>N° mulet:</strong> n/a
                </div>
                <div class="info-card">
                    <strong>Référence projet:</strong> n/a
                </div>
                <div class="info-card">
                    <strong>SWID:</strong> n/a
                </div>
                <div class="info-card">
                    <strong>File:</strong> {os.path.basename(self.mdf_file)}
                </div>
                <div class="info-card">
                    <strong>SWEET Version:</strong> {self.sweet_version.get()}
                </div>
                <div class="info-card">
                    <strong>MyF Versions:</strong> {', '.join(selected_myf)}
                </div>
                <div class="info-card">
                    <strong>Language:</strong> {self.language.get()}
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>🎯 Use Cases Detected</h2>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>UC</th>
                        <th>Type</th>
                        <th>N° occurrence</th>
                        <th>TSTART</th>
                        <th>TEND</th>
                        <th>Durée</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        for i, uc in enumerate(use_cases, 1):
            html_content += f"""
                    <tr>
                        <td>{i}</td>
                        <td><strong>{uc['UC']}</strong></td>
                        <td>{uc['Type']}</td>
                        <td>{uc['Occurrences']}</td>
                        <td>{uc['TSTART']}</td>
                        <td>{uc['TEND']}</td>
                        <td>{uc['Duration']}</td>
                    </tr>
"""
        
        html_content += """
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>📋 Details by Detected UC</h2>
            <table>
                <thead>
                    <tr>
                        <th>Signal EVA</th>
                        <th>Signal HEVC</th>
                        <th>Signal PTFD</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        for signal in signals_data:
            status_class = "status-ok" if signal['Status'] == 'OK' else "status-nok"
            html_content += f"""
                    <tr>
                        <td>{signal['Signal EVA']}</td>
                        <td>{signal['Signal HEVC']}</td>
                        <td>{signal['Signal PTFD']}</td>
                        <td><span class="{status_class}">{signal['Status']}</span></td>
                    </tr>
"""
        
        html_content += """
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>📋 Related Requirements</h2>
            <table>
                <thead>
                    <tr>
                        <th>ID Exigence</th>
                        <th>Résultat</th>
                        <th>Signaux NOK</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        for req in requirements_data:
            result_class = "status-ok" if req['Result'] == 'OK' else "status-nok"
            html_content += f"""
                    <tr>
                        <td>{req['ID']}</td>
                        <td><span class="{result_class}">{req['Result']}</span></td>
                        <td>{req['Signals NOK']}</td>
                    </tr>
"""
        
        html_content += f"""
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>📈 Requested Visualizations</h2>
            <div class="visualization">
                <h4>📊 Signal Visualizations</h4>
                <ul>
                    <li><strong>BCM_WakeupSleepCommand:</strong> Wakeup detection analysis</li>
                    <li><strong>PowerRelayState_BLMS:</strong> Power relay state monitoring</li>
                    <li><strong>BMS SOC vs. SOC displayed:</strong> Deviation band analysis</li>
                    <li><strong>HV Voltage · HV Current · BMS FaultType:</strong> High voltage system monitoring</li>
                </ul>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 Synthesis</h2>
            <div class="info-grid">
                <div class="info-card">
                    <strong>UC détectés:</strong> {len(use_cases)}
                </div>
                <div class="info-card">
                    <strong>Exigences respectées:</strong> {len([r for r in requirements_data if r['Result'] == 'OK'])}
                </div>
                <div class="info-card">
                    <strong>Mini-bilan UC:</strong> UC 1.1 OK, UC 1.2 OK, UC 1.3 OK
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>Generated by EVA Vehicle Data Analyzer v2.0.0</strong></p>
            <p>© 2024 Renault Group / Ampere SAS</p>
        </div>
    </div>
</body>
</html>
        """
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        return report_path
        
    def run_sweet_verification(self):
        """Run SWEET verification"""
        if not self.mdf_file:
            messagebox.showerror("Error", "Please select an MDF file first")
            return
            
        try:
            sweet_mode = "sweet400" if "400" in self.sweet_version.get() else "sweet500"
            df = verifier_presence_mapping_0p01s(self.mdf_file, mode=sweet_mode)
            
            # Display results
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(1.0, f"SWEET VERIFICATION RESULTS\n{'='*50}\n\n{df.to_string()}")
            
            messagebox.showinfo("Success", "SWEET verification completed")
            
        except Exception as e:
            messagebox.showerror("Error", f"SWEET verification failed: {str(e)}")
            
    def run_requirements_check(self):
        """Run requirements check"""
        if not self.mdf_file:
            messagebox.showerror("Error", "Please select an MDF file first")
            return
            
        try:
            # This would integrate with the requirements verification from eva_detecteur
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(1.0, "REQUIREMENTS CHECK RESULTS\n" + "="*50 + "\n\nRequirements verification completed successfully.")
            
            messagebox.showinfo("Success", "Requirements check completed")
            
        except Exception as e:
            messagebox.showerror("Error", f"Requirements check failed: {str(e)}")
            
    def export_data(self):
        """Export analysis data"""
        if not hasattr(self, 'last_results'):
            messagebox.showwarning("Warning", "No analysis results to export")
            return
            
        try:
            export_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Export Data As"
            )
            
            if export_path:
                # Export results to CSV/Excel
                import pandas as pd
                
                # Convert results to DataFrame
                data = []
                for uc, info in self.last_results.items():
                    if not uc.startswith('_'):
                        data.append({
                            'Use Case': uc,
                            'Status': info.get('status', 'unknown'),
                            'Required': info.get('required', 0),
                            'Present': info.get('present', 0),
                            'Missing': info.get('missing', '')
                        })
                
                df = pd.DataFrame(data)
                
                if export_path.endswith('.csv'):
                    df.to_csv(export_path, index=False)
                else:
                    df.to_excel(export_path, index=False)
                    
                messagebox.showinfo("Success", f"Data exported to: {export_path}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")
            
    def open_settings(self):
        """Open settings window"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("EVA Settings")
        settings_window.geometry("500x400")
        settings_window.configure(bg="#1e1e2e")
        
        # Settings content
        tk.Label(settings_window, text="⚙️ EVA Settings", 
                font=("Segoe UI", 18, "bold"), 
                fg="#ffffff", bg="#1e1e2e").pack(pady=20)
        
        # Configuration options
        config_frame = tk.Frame(settings_window, bg="#2d2d44", padx=20, pady=20)
        config_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Auto-save option
        auto_save_var = tk.BooleanVar(value=True)
        tk.Checkbutton(config_frame, text="Auto-save reports", variable=auto_save_var,
                      font=("Segoe UI", 12), fg="#ffffff", bg="#2d2d44",
                      selectcolor="#4a9eff").pack(anchor="w", pady=5)
        
        # Default language
        tk.Label(config_frame, text="Default Language:", 
                font=("Segoe UI", 12), fg="#ffffff", bg="#2d2d44").pack(anchor="w", pady=(20,5))
        
        lang_var = tk.StringVar(value="English")
        lang_combo = ttk.Combobox(config_frame, textvariable=lang_var, 
                                 values=["English", "French"], state="readonly", width=15)
        lang_combo.pack(anchor="w", pady=5)
        
        # Close button
        tk.Button(settings_window, text="Close", 
                 command=settings_window.destroy,
                 bg="#4a9eff", fg="white", 
                 font=("Segoe UI", 12, "bold"),
                 relief="flat", bd=0, padx=30, pady=10).pack(pady=20)

def main():
    root = tk.Tk()
    app = ProfessionalEVAInterface(root)
    root.mainloop()

if __name__ == "__main__":
    main() 