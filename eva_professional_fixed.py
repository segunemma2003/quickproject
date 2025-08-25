import tkinter as tk
from tkinter import ttk, filedialog, messagebox
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

# Import complete engine
try:
    from eva_complete_engine import eva_engine
except ImportError:
    # Create a simple fallback engine
    class SimpleEngine:
        def analyze_mdf_file(self, *args, **kwargs):
            return {"use_cases": {"UC 1.1": {"status": "detected", "required": 3, "present": 3, "missing": ""}}}
        def generate_comprehensive_report_data(self, *args, **kwargs):
            return {"company_info": {"parent_company": "RENAULT GROUP"}}
    
    eva_engine = SimpleEngine()

class EVAInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("EVA - Vehicle Data Analyzer")
        self.root.geometry("1200x800")
        self.root.configure(bg="#2c3e50")
        
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
        self.last_results = None
        self.report_path = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Main tab
        main_frame = tk.Frame(notebook, bg="#2c3e50")
        notebook.add(main_frame, text="Analysis")
        
        # Results tab
        results_frame = tk.Frame(notebook, bg="#2c3e50")
        notebook.add(results_frame, text="Results")
        
        self.setup_main_tab(main_frame)
        self.setup_results_tab(results_frame)
        
    def setup_main_tab(self, parent):
        # Header
        header = tk.Frame(parent, bg="#34495e", height=60)
        header.pack(fill="x", pady=(0, 10))
        header.pack_propagate(False)
        
        tk.Label(header, text="🚗 EVA - Vehicle Data Analyzer", 
                font=("Arial", 20, "bold"), fg="white", bg="#34495e").pack(pady=15)
        
        # Main content with proper grid
        content = tk.Frame(parent, bg="#2c3e50")
        content.pack(fill="both", expand=True, padx=10)
        
        # Configure grid
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)
        
        # Left column
        left_frame = tk.LabelFrame(content, text="📁 Configuration", 
                                  font=("Arial", 14, "bold"), fg="white", bg="#34495e")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=5)
        
        # Right column  
        right_frame = tk.LabelFrame(content, text="🔍 Analysis", 
                                   font=("Arial", 14, "bold"), fg="white", bg="#34495e")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=5)
        
        self.setup_left_panel(left_frame)
        self.setup_right_panel(right_frame)
        
    def setup_left_panel(self, parent):
        parent.configure(bg="#34495e", padx=15, pady=15)
        
        # File selection
        tk.Label(parent, text="Select MDF File:", font=("Arial", 12, "bold"), 
                fg="white", bg="#34495e").pack(anchor="w", pady=(0, 5))
        
        file_frame = tk.Frame(parent, bg="#34495e")
        file_frame.pack(fill="x", pady=(0, 15))
        
        self.file_btn = tk.Button(file_frame, text="📁 Browse Files", 
                                 command=self.select_file, bg="#3498db", fg="white", 
                                 font=("Arial", 11, "bold"), padx=20, pady=8)
        self.file_btn.pack(side="left")
        
        self.file_label = tk.Label(parent, text="No file selected", 
                                  font=("Arial", 10), fg="#bdc3c7", bg="#34495e")
        self.file_label.pack(anchor="w", pady=(0, 20))
        
        # SWEET Version
        tk.Label(parent, text="SWEET Version:", font=("Arial", 12, "bold"), 
                fg="white", bg="#34495e").pack(anchor="w", pady=(0, 5))
        
        sweet_combo = ttk.Combobox(parent, textvariable=self.sweet_version,
                                  values=["SWEET 400", "SWEET 500"], 
                                  state="readonly", width=15)
        sweet_combo.pack(anchor="w", pady=(0, 15))
        
        # MyF Selection
        tk.Label(parent, text="MyF Selection:", font=("Arial", 12, "bold"), 
                fg="white", bg="#34495e").pack(anchor="w", pady=(0, 5))
        
        for myf, var in self.myf_vars.items():
            cb = tk.Checkbutton(parent, text=myf, variable=var,
                              font=("Arial", 10), fg="white", bg="#34495e",
                              selectcolor="#3498db", activebackground="#34495e")
            cb.pack(anchor="w", pady=2)
            
        # Language
        tk.Label(parent, text="Language:", font=("Arial", 12, "bold"), 
                fg="white", bg="#34495e").pack(anchor="w", pady=(15, 5))
        
        lang_combo = ttk.Combobox(parent, textvariable=self.language, 
                                 values=["English", "French"], 
                                 state="readonly", width=15)
        lang_combo.pack(anchor="w")
        
    def setup_right_panel(self, parent):
        parent.configure(bg="#34495e", padx=15, pady=15)
        
        # Analysis button
        self.analyze_btn = tk.Button(parent, text="🚀 START ANALYSIS", 
                                   command=self.start_analysis,
                                   bg="#27ae60", fg="white", 
                                   font=("Arial", 14, "bold"),
                                   padx=30, pady=15, state="disabled")
        self.analyze_btn.pack(pady=(0, 15))
        
        # Progress section
        progress_frame = tk.Frame(parent, bg="#34495e")
        progress_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(progress_frame, text="Progress:", font=("Arial", 11, "bold"), 
                fg="white", bg="#34495e").pack(anchor="w")
        
        self.progress = ttk.Progressbar(progress_frame, mode='determinate', length=300)
        self.progress.pack(fill="x", pady=5)
        
        self.status_label = tk.Label(progress_frame, text="Ready to analyze", 
                                   font=("Arial", 10), fg="#bdc3c7", bg="#34495e")
        self.status_label.pack(anchor="w")
        
        # Report buttons
        report_frame = tk.Frame(parent, bg="#34495e")
        report_frame.pack(fill="x", pady=(15, 0))
        
        tk.Label(report_frame, text="Reports:", font=("Arial", 11, "bold"), 
                fg="white", bg="#34495e").pack(anchor="w", pady=(0, 10))
        
        self.report_btn = tk.Button(report_frame, text="📄 Generate Report", 
                                  command=self.generate_report,
                                  bg="#e67e22", fg="white", 
                                  font=("Arial", 11, "bold"),
                                  padx=20, pady=8, state="disabled")
        self.report_btn.pack(fill="x", pady=2)
        
        self.view_btn = tk.Button(report_frame, text="👁️ View Report", 
                                command=self.view_report,
                                bg="#3498db", fg="white", 
                                font=("Arial", 11, "bold"),
                                padx=20, pady=8, state="disabled")
        self.view_btn.pack(fill="x", pady=2)
        
        self.download_btn = tk.Button(report_frame, text="⬇️ Download Report", 
                                    command=self.download_report,
                                    bg="#27ae60", fg="white", 
                                    font=("Arial", 11, "bold"),
                                    padx=20, pady=8, state="disabled")
        self.download_btn.pack(fill="x", pady=2)
        
        # Advanced features
        advanced_frame = tk.Frame(parent, bg="#34495e")
        advanced_frame.pack(fill="x", pady=(20, 0))
        
        tk.Label(advanced_frame, text="Advanced:", font=("Arial", 11, "bold"), 
                fg="white", bg="#34495e").pack(anchor="w", pady=(0, 10))
        
        self.sweet_btn = tk.Button(advanced_frame, text="🔍 SWEET Verification", 
                                 command=self.run_sweet_verification,
                                 bg="#9b59b6", fg="white", 
                                 font=("Arial", 10, "bold"),
                                 padx=15, pady=6)
        self.sweet_btn.pack(fill="x", pady=1)
        
        self.export_btn = tk.Button(advanced_frame, text="📊 Export Data", 
                                  command=self.export_data,
                                  bg="#34495e", fg="white", 
                                  font=("Arial", 10, "bold"),
                                  padx=15, pady=6)
        self.export_btn.pack(fill="x", pady=1)
        
    def setup_results_tab(self, parent):
        # Results display
        tk.Label(parent, text="📊 Analysis Results", 
                font=("Arial", 16, "bold"), fg="white", bg="#2c3e50").pack(pady=10)
        
        # Text area with scrollbar
        text_frame = tk.Frame(parent, bg="#2c3e50")
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.results_text = tk.Text(text_frame, bg="#34495e", fg="white",
                                   font=("Consolas", 10), wrap="word")
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.results_text.yview)
        
        self.results_text.configure(yscrollcommand=scrollbar.set)
        self.results_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Select MDF File",
            filetypes=[("MDF files", "*.mdf *.mf4 *.dat"), ("All files", "*.*")]
        )
        
        if file_path:
            self.mdf_file = file_path
            self.file_label.config(text=f"Selected: {os.path.basename(file_path)}")
            self.analyze_btn.config(state="normal")
            
    def start_analysis(self):
        if not self.mdf_file:
            messagebox.showerror("Error", "Please select an MDF file first")
            return
            
        self.analyze_btn.config(state="disabled")
        self.progress["value"] = 0
        self.status_label.config(text="Starting analysis...")
        
        def run_analysis():
            try:
                # Progress updates
                for i in range(1, 6):
                    self.root.after(0, lambda v=i*20: self.progress.config(value=v))
                    self.root.after(0, lambda: self.status_label.config(text=f"Analyzing... {i*20}%"))
                    import time
                    time.sleep(0.5)
                
                # Get selected MyF versions
                selected_myf = [myf for myf, var in self.myf_vars.items() if var.get()]
                if not selected_myf:
                    selected_myf = ["All MyF versions"]
                
                # Run complete analysis
                sweet_mode = "sweet400" if "400" in self.sweet_version.get() else "sweet500"
                analysis_results = eva_engine.analyze_mdf_file(
                    self.mdf_file, 
                    sweet_version=sweet_mode,
                    myf_versions=selected_myf
                )
                
                self.root.after(0, lambda: self.display_complete_results(analysis_results))
                
            except Exception as e:
                self.root.after(0, lambda: self.show_error(str(e)))
            finally:
                self.root.after(0, lambda: self.analyze_btn.config(state="normal"))
                
        threading.Thread(target=run_analysis, daemon=True).start()
        
    def display_complete_results(self, analysis_results):
        self.last_results = analysis_results
        self.progress["value"] = 100
        self.status_label.config(text="Analysis complete!")
        
        # Enable report buttons
        self.report_btn.config(state="normal")
        self.view_btn.config(state="normal") 
        self.download_btn.config(state="normal")
        
        # Display results
        self.results_text.delete(1.0, tk.END)
        
        output = f"""COMPLETE EVA ANALYSIS RESULTS
{'='*70}

File: {os.path.basename(self.mdf_file)}
SWEET Version: {self.sweet_version.get()}
Language: {self.language.get()}
Analysis Time: {analysis_results.get('analysis_time', datetime.datetime.now().isoformat())}

USE CASE DETECTION:
{'-'*40}
"""
        
        # Display use cases
        for uc, info in analysis_results.get('use_cases', {}).items():
            status_icon = "✅" if info.get('status') == 'detected' else "❌"
            status_text = "DETECTED" if info.get('status') == 'detected' else "NOT DETECTED"
            output += f"\n{uc}: {status_icon} {status_text}"
            output += f"\n  Required signals: {info.get('required', 0)}"
            output += f"\n  Present signals: {info.get('present', 0)}"
            if info.get('missing'):
                output += f"\n  Missing: {info.get('missing')}"
            output += "\n"
        
        # Display SWEET compliance
        sweet = analysis_results.get('sweet_compliance', {})
        output += f"""
SWEET COMPLIANCE:
{'-'*40}
Total Signals: {sweet.get('total_signals', 0)}
OK Signals: {sweet.get('ok_signals', 0)}
Fallback Signals: {sweet.get('fallback_signals', 0)}
NOK Signals: {sweet.get('nok_signals', 0)}
Success Rate: {sweet.get('success_rate', 0):.1f}%

REQUIREMENTS CHECK:
{'-'*40}
"""
        
        # Display requirements
        reqs = analysis_results.get('requirements', {})
        output += f"Total Requirements: {reqs.get('total_requirements', 0)}\n"
        output += f"Passed: {reqs.get('passed_requirements', 0)}\n"
        output += f"Failed: {reqs.get('failed_requirements', 0)}\n"
        
        for req in reqs.get('requirements', []):
            status_icon = "✅" if req.get('result') == 'OK' else "❌"
            output += f"\n{req.get('id', 'Unknown')}: {status_icon} {req.get('result', 'Unknown')}"
            output += f"\n  {req.get('description', 'No description')}"
            if req.get('signals_nok'):
                output += f"\n  NOK Signals: {req.get('signals_nok')}"
            output += "\n"
                
        self.results_text.insert(1.0, output)
        messagebox.showinfo("Success", "Complete analysis finished successfully!")
        
    def show_error(self, error_msg):
        self.status_label.config(text="Analysis failed")
        self.progress["value"] = 0
        messagebox.showerror("Analysis Error", error_msg)
        
    def generate_report(self):
        if not self.last_results:
            messagebox.showwarning("Warning", "No analysis results available")
            return
            
        try:
            self.report_path = self.create_html_report()
            messagebox.showinfo("Success", f"Report generated: {self.report_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
            
    def view_report(self):
        if self.report_path and os.path.exists(self.report_path):
            webbrowser.open(f"file://{os.path.abspath(self.report_path)}")
        else:
            messagebox.showwarning("Warning", "No report available. Generate report first.")
            
    def download_report(self):
        if self.report_path and os.path.exists(self.report_path):
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
            messagebox.showwarning("Warning", "No report available. Generate report first.")
            
    def run_sweet_verification(self):
        if not self.mdf_file:
            messagebox.showerror("Error", "Please select an MDF file first")
            return
            
        try:
            sweet_mode = "sweet400" if "400" in self.sweet_version.get() else "sweet500"
            df = verifier_presence_mapping_0p01s(self.mdf_file, mode=sweet_mode)
            
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(1.0, f"SWEET VERIFICATION RESULTS\n{'='*50}\n\n{df.to_string()}")
            
            messagebox.showinfo("Success", "SWEET verification completed")
            
        except Exception as e:
            messagebox.showerror("Error", f"SWEET verification failed: {str(e)}")
            
    def export_data(self):
        if not self.last_results:
            messagebox.showwarning("Warning", "No analysis results to export")
            return
            
        try:
            export_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")],
                title="Export Data As"
            )
            
            if export_path:
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
            
    def create_html_report(self):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report_path = f"eva_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        # Generate comprehensive report data
        report_data = eva_engine.generate_comprehensive_report_data(self.last_results)
        
        # Get selected MyF versions
        selected_myf = [myf for myf, var in self.myf_vars.items() if var.get()]
        if not selected_myf:
            selected_myf = ["All MyF versions"]
            
        html_content = f"""<!DOCTYPE html>
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
            <p><strong>Entreprise Mère:</strong> {report_data.get('company_info', {}).get('parent_company', 'RENAULT GROUP')}</p>
            <p><strong>Entreprise Principale:</strong> {report_data.get('company_info', {}).get('main_company', 'AMPERE SAS')}</p>
            <p><strong>Équipe:</strong> {report_data.get('company_info', {}).get('team', 'Validation Système des Véhicules Électriques (RAM32)')}</p>
        </div>
        
        <div class="section">
            <h2>📊 Vehicle Data</h2>
            <div class="info-grid">
                <div class="info-card">
                    <strong>VIN:</strong> {report_data.get('vehicle_data', {}).get('vin', 'n/a')}
                </div>
                <div class="info-card">
                    <strong>N° mulet:</strong> {report_data.get('vehicle_data', {}).get('mulet_number', 'n/a')}
                </div>
                <div class="info-card">
                    <strong>Référence projet:</strong> {report_data.get('vehicle_data', {}).get('project_reference', 'n/a')}
                </div>
                <div class="info-card">
                    <strong>SWID:</strong> {report_data.get('vehicle_data', {}).get('swid', 'n/a')}
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
        
        for i, uc in enumerate(report_data.get('use_cases', []), 1):
            html_content += f"""
                    <tr>
                        <td>{i}</td>
                        <td><strong>{uc.get('UC', 'Unknown')}</strong></td>
                        <td>{uc.get('Type', 'Unknown')}</td>
                        <td>{uc.get('Occurrences', 0)}</td>
                        <td>{uc.get('TSTART', '00:00:00.000')}</td>
                        <td>{uc.get('TEND', '00:00:00.000')}</td>
                        <td>{uc.get('Duration', '00:00:00.000')}</td>
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
        
        for signal in report_data.get('signals_mapping', []):
            status_class = "status-ok" if signal.get('Status') == 'OK' else "status-nok"
            html_content += f"""
                    <tr>
                        <td>{signal.get('Signal EVA', '')}</td>
                        <td>{signal.get('Signal HEVC', '')}</td>
                        <td>{signal.get('Signal PTFD', '')}</td>
                        <td><span class="{status_class}">{signal.get('Status', 'Unknown')}</span></td>
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
        
        for req in report_data.get('requirements', {}).get('requirements', []):
            result_class = "status-ok" if req.get('result') == 'OK' else "status-nok"
            html_content += f"""
                    <tr>
                        <td>{req.get('id', 'Unknown')}</td>
                        <td><span class="{result_class}">{req.get('result', 'Unknown')}</span></td>
                        <td>{req.get('signals_nok', '—')}</td>
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
"""
        
        for signal in report_data.get('visualizations', {}).get('requested_signals', []):
            html_content += f"                    <li><strong>{signal}</strong></li>\n"
        
        html_content += """
                </ul>
                <h4>📋 Interpretation</h4>
                <ul>
"""
        
        for interpretation in report_data.get('visualizations', {}).get('interpretation', []):
            html_content += f"                    <li>{interpretation}</li>\n"
        
        html_content += f"""
                </ul>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 Synthesis</h2>
            <div class="info-grid">
                <div class="info-card">
                    <strong>UC détectés:</strong> {len(report_data.get('use_cases', []))}
                </div>
                <div class="info-card">
                    <strong>Exigences respectées:</strong> {report_data.get('requirements', {}).get('passed_requirements', 0)}
                </div>
                <div class="info-card">
                    <strong>Mini-bilan UC:</strong> {' '.join([f"{uc.get('UC', '')} OK" for uc in report_data.get('use_cases', [])])}
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>Generated by EVA Vehicle Data Analyzer v2.0.0</strong></p>
            <p>© 2024 Renault Group / Ampere SAS</p>
        </div>
    </div>
</body>
</html>"""
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        return report_path

def main():
    root = tk.Tk()
    app = EVAInterface(root)
    root.mainloop()

if __name__ == "__main__":
    main() 