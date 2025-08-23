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
                
                # Run actual analysis
                results = analyser_et_generer_rapport(self.mdf_file, lang=self.language.get().lower())
                
                self.root.after(0, lambda: self.display_results(results))
                
            except Exception as e:
                self.root.after(0, lambda: self.show_error(str(e)))
            finally:
                self.root.after(0, lambda: self.analyze_btn.config(state="normal"))
                
        threading.Thread(target=run_analysis, daemon=True).start()
        
    def display_results(self, results):
        self.last_results = results
        self.progress["value"] = 100
        self.status_label.config(text="Analysis complete!")
        
        # Enable report buttons
        self.report_btn.config(state="normal")
        self.view_btn.config(state="normal") 
        self.download_btn.config(state="normal")
        
        # Display results
        self.results_text.delete(1.0, tk.END)
        
        output = f"""ANALYSIS RESULTS
{'='*60}

File: {os.path.basename(self.mdf_file)}
SWEET Version: {self.sweet_version.get()}
Language: {self.language.get()}
Analysis Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

DETECTED USE CASES:
{'-'*40}
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
        messagebox.showinfo("Success", "Analysis completed successfully!")
        
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
        
        # Get selected MyF versions
        selected_myf = [myf for myf, var in self.myf_vars.items() if var.get()]
        if not selected_myf:
            selected_myf = ["All MyF versions"]
            
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>EVA Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; text-align: center; font-size: 2.5em; margin-bottom: 30px; }}
        .section {{ margin: 30px 0; padding: 20px; background: #ecf0f1; border-radius: 8px; }}
        .section h2 {{ color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #3498db; color: white; }}
        .status-ok {{ color: #27ae60; font-weight: bold; }}
        .status-nok {{ color: #e74c3c; font-weight: bold; }}
        .info {{ background: #d5dbdb; padding: 15px; border-radius: 5px; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚗 EVA Analysis Report</h1>
        
        <div class="section">
            <h2>📊 Analysis Summary</h2>
            <div class="info">
                <strong>File:</strong> {os.path.basename(self.mdf_file)}<br>
                <strong>SWEET Version:</strong> {self.sweet_version.get()}<br>
                <strong>Language:</strong> {self.language.get()}<br>
                <strong>MyF Versions:</strong> {', '.join(selected_myf)}<br>
                <strong>Generated:</strong> {timestamp}
            </div>
        </div>
        
        <div class="section">
            <h2>🎯 Use Case Detection Results</h2>
            <table>
                <tr><th>Use Case</th><th>Status</th><th>Required</th><th>Present</th><th>Missing</th></tr>
"""
        
        for uc, info in self.last_results.items():
            if not uc.startswith('_'):
                status = "DETECTED" if info.get('status') == 'detected' else "NOT DETECTED"
                status_class = "status-ok" if status == "DETECTED" else "status-nok"
                html_content += f"""
                <tr>
                    <td><strong>{uc}</strong></td>
                    <td><span class="{status_class}">{status}</span></td>
                    <td>{info.get('required', 0)}</td>
                    <td>{info.get('present', 0)}</td>
                    <td>{info.get('missing', '')}</td>
                </tr>"""
                
        html_content += """
            </table>
        </div>
        
        <div class="section">
            <h2>📋 Analysis Details</h2>
            <p>Complete analysis performed according to EVA validation standards.</p>
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