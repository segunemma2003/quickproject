import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from pathlib import Path
import threading
import webbrowser
import os
import sys
from typing import Optional
import datetime

# Add the Gmail directory to the path to import the existing modules
sys.path.append('Gmail')

# Import the existing backend modules
try:
    from eva_detecteur import (
        analyser_et_generer_rapport,
        verifier_presence_mapping_0p01s,
        CONFIG,
    )
except ImportError:
    # Fallback if modules not found
    def analyser_et_generer_rapport(*args, **kwargs):
        return {"Test": {"status": "detected", "required": 5, "present": 3, "missing": "signal1, signal2"}}
    
    def verifier_presence_mapping_0p01s(*args, **kwargs):
        import pandas as pd
        return pd.DataFrame({"Signal": ["Test1", "Test2"], "Status": ["OK", "NOK"]})
    
    CONFIG = {"myf": None}

# ====== Modern Color Palette ======
PRIMARY_BG = "#1a1a2e"        # Dark blue background
SECONDARY_BG = "#16213e"      # Slightly lighter blue
CARD_BG = "#0f3460"           # Card background
ACCENT_COLOR = "#e94560"      # Red accent
SUCCESS_COLOR = "#00d4aa"     # Green success
WARNING_COLOR = "#ffa726"     # Orange warning
TEXT_PRIMARY = "#ffffff"      # White text
TEXT_SECONDARY = "#b0b0b0"    # Gray text
BORDER_COLOR = "#2d3748"      # Border color

# ====== Fonts ======
FONT_H1 = ("Segoe UI", 24, "bold")
FONT_H2 = ("Segoe UI", 18, "bold")
FONT_H3 = ("Segoe UI", 14, "bold")
FONT_BODY = ("Segoe UI", 12)
FONT_SMALL = ("Segoe UI", 10)

# ====== Languages ======
LANG = {
    "fr": {
        "title": "EVA - Analyseur de Données Véhicule",
        "subtitle": "Interface d'analyse automatique des fichiers MDF",
        "import": "Importer un fichier MDF",
        "file_types": "Fichiers supportés: .mdf, .mf4, .dat",
        "choose": "Parcourir...",
        "no_file": "Aucun fichier sélectionné",
        "myf": "Version MyF",
        "auto": "Auto-détection",
        "sweet": "Version SWEET",
        "sweet400": "SWEET 400",
        "sweet500": "SWEET 500",
        "start": "Lancer l'analyse",
        "analyzing": "Analyse en cours...",
        "checking": "Vérification SWEET...",
        "success": "Analyse terminée avec succès",
        "file_err": "Erreur de fichier",
        "select_first": "Veuillez d'abord sélectionner un fichier.",
        "status_ready": "Prêt à analyser",
        "status_complete": "Analyse terminée",
        "options": "Options d'analyse",
        "results": "Résultats",
        "use_case": "Use Case détecté:",
        "progress": "Progression:",
        "language": "Langue",
        "file_selected": "Fichier sélectionné",
        "generate_report": "Générer le rapport",
        "open_report": "Ouvrir le rapport",
        "report_generated": "Rapport généré avec succès",
    },
    "en": {
        "title": "EVA - Vehicle Data Analyzer",
        "subtitle": "Automatic MDF file analysis interface",
        "import": "Import MDF file",
        "file_types": "Supported files: .mdf, .mf4, .dat",
        "choose": "Browse...",
        "no_file": "No file selected",
        "myf": "MyF version",
        "auto": "Auto-detect",
        "sweet": "SWEET version",
        "sweet400": "SWEET 400",
        "sweet500": "SWEET 500",
        "start": "Start analysis",
        "analyzing": "Analyzing...",
        "checking": "Checking SWEET...",
        "success": "Analysis completed successfully",
        "file_err": "File error",
        "select_first": "Please select a file first.",
        "status_ready": "Ready to analyze",
        "status_complete": "Analysis complete",
        "options": "Analysis options",
        "results": "Results",
        "use_case": "Detected Use Case:",
        "progress": "Progress:",
        "language": "Language",
        "file_selected": "File selected",
        "generate_report": "Generate report",
        "open_report": "Open report",
        "report_generated": "Report generated successfully",
    },
}

class ModernButton(tk.Button):
    """Custom modern button with hover effects"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(
            relief="flat",
            borderwidth=0,
            font=FONT_BODY,
            cursor="hand2"
        )
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, e):
        self.configure(bg=self._get_hover_color())
    
    def _on_leave(self, e):
        self.configure(bg=self._get_normal_color())
    
    def _get_normal_color(self):
        return self.cget("bg")
    
    def _get_hover_color(self):
        # Darken the current color for hover effect
        return ACCENT_COLOR

class EVAModernApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.lang_var = tk.StringVar(value="en")
        self.T = LANG[self.lang_var.get()]
        
        # Configure main window
        self.root.title(self.T["title"])
        self.root.geometry("1200x800")
        self.root.configure(bg=PRIMARY_BG)
        self.root.option_add("*Font", FONT_BODY)
        self.root.minsize(1000, 700)
        
        # Center the window
        self.center_window()
        
        # State variables
        self.selected_file: Optional[str] = None
        self.detected_uc: str = "Not detected"
        self.selected_myf = tk.StringVar(value=self.T["auto"])
        self.selected_sweet = tk.StringVar(value=self.T["sweet400"])
        self.status_text = tk.StringVar(value=self.T["status_ready"])
        self.analysis_results = {}
        
        # Build the interface
        self._init_styles()
        self._build_header()
        self._build_main_content()
        self._build_footer()
        
        # Apply dark theme
        self._apply_dark_theme()
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def _init_styles(self):
        """Initialize ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure("Modern.TFrame", background=PRIMARY_BG)
        style.configure("Card.TFrame", background=CARD_BG, relief="flat", borderwidth=0)
        style.configure("Header.TLabel", font=FONT_H1, foreground=TEXT_PRIMARY, background=PRIMARY_BG)
        style.configure("Subtitle.TLabel", font=FONT_H2, foreground=TEXT_SECONDARY, background=PRIMARY_BG)
        style.configure("Title.TLabel", font=FONT_H3, foreground=TEXT_PRIMARY, background=CARD_BG)
        style.configure("Body.TLabel", font=FONT_BODY, foreground=TEXT_PRIMARY, background=CARD_BG)
        style.configure("Muted.TLabel", font=FONT_SMALL, foreground=TEXT_SECONDARY, background=CARD_BG)
        
        # Progress bar style
        style.configure("Modern.Horizontal.TProgressbar",
                       troughcolor=SECONDARY_BG,
                       background=ACCENT_COLOR,
                       thickness=12,
                       borderwidth=0)
    
    def _apply_dark_theme(self):
        """Apply dark theme to all widgets"""
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.configure(bg=PRIMARY_BG)
    
    def _build_header(self):
        """Build the header section"""
        header = tk.Frame(self.root, bg=PRIMARY_BG, height=120, padx=30, pady=20)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        
        # Title and subtitle
        title_frame = tk.Frame(header, bg=PRIMARY_BG)
        title_frame.pack(expand=True, fill="both")
        
        self.lbl_title = tk.Label(title_frame, text=self.T["title"], 
                                 font=FONT_H1, fg=TEXT_PRIMARY, bg=PRIMARY_BG)
        self.lbl_title.pack(anchor="center")
        
        self.lbl_subtitle = tk.Label(title_frame, text=self.T["subtitle"], 
                                   font=FONT_H2, fg=TEXT_SECONDARY, bg=PRIMARY_BG)
        self.lbl_subtitle.pack(anchor="center", pady=(5, 0))
        
        # Language switcher
        lang_frame = tk.Frame(header, bg=PRIMARY_BG)
        lang_frame.pack(side="right", fill="y")
        
        for code, label in [("fr", "FR"), ("en", "EN")]:
            btn = ModernButton(lang_frame, text=label, 
                             bg=ACCENT_COLOR if self.lang_var.get() == code else SECONDARY_BG,
                             fg=TEXT_PRIMARY,
                             command=lambda c=code: self._set_language(c),
                             width=8, height=2)
            btn.pack(side="top", pady=2)
    
    def _build_main_content(self):
        """Build the main content area"""
        main_frame = tk.Frame(self.root, bg=PRIMARY_BG, padx=30, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Create scrollable canvas
        canvas = tk.Canvas(main_frame, bg=PRIMARY_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=PRIMARY_BG)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Build content sections
        self._build_file_section(scrollable_frame)
        self._build_options_section(scrollable_frame)
        self._build_analysis_section(scrollable_frame)
        self._build_results_section(scrollable_frame)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
    
    def _build_file_section(self, parent):
        """Build file import section"""
        card = tk.Frame(parent, bg=CARD_BG, padx=25, pady=20, relief="flat", bd=0)
        card.pack(fill="x", pady=(0, 20))
        
        # Title
        tk.Label(card, text=self.T["import"], font=FONT_H3, fg=TEXT_PRIMARY, bg=CARD_BG).pack(anchor="w", pady=(0, 10))
        tk.Label(card, text=self.T["file_types"], font=FONT_SMALL, fg=TEXT_SECONDARY, bg=CARD_BG).pack(anchor="w", pady=(0, 20))
        
        # File selection
        file_frame = tk.Frame(card, bg=CARD_BG)
        file_frame.pack(fill="x")
        
        self.btn_browse = ModernButton(file_frame, text=self.T["choose"], 
                                     bg=ACCENT_COLOR, fg=TEXT_PRIMARY,
                                     command=self._pick_file, width=15, height=2)
        self.btn_browse.pack(side="left", padx=(0, 15))
        
        self.file_label = tk.Label(file_frame, text=self.T["no_file"], 
                                 font=FONT_BODY, fg=TEXT_SECONDARY, bg=CARD_BG)
        self.file_label.pack(side="left", fill="x", expand=True)
    
    def _build_options_section(self, parent):
        """Build options section"""
        card = tk.Frame(parent, bg=CARD_BG, padx=25, pady=20, relief="flat", bd=0)
        card.pack(fill="x", pady=(0, 20))
        
        # Title
        tk.Label(card, text=self.T["options"], font=FONT_H3, fg=TEXT_PRIMARY, bg=CARD_BG).pack(anchor="w", pady=(0, 20))
        
        # Options grid
        options_frame = tk.Frame(card, bg=CARD_BG)
        options_frame.pack(fill="x")
        
        # MyF Version
        myf_frame = tk.Frame(options_frame, bg=CARD_BG)
        myf_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(myf_frame, text=self.T["myf"] + ":", font=FONT_BODY, fg=TEXT_PRIMARY, bg=CARD_BG).pack(side="left", padx=(0, 15))
        
        myf_options = [self.T["auto"], "MyF2", "MyF3", "MyF4.1", "MyF4.2"]
        self.myf_pills = self._build_pill_buttons(myf_frame, myf_options, self.selected_myf)
        self.myf_pills.pack(side="left", fill="x", expand=True)
        
        # SWEET Version
        sweet_frame = tk.Frame(options_frame, bg=CARD_BG)
        sweet_frame.pack(fill="x")
        
        tk.Label(sweet_frame, text=self.T["sweet"] + ":", font=FONT_BODY, fg=TEXT_PRIMARY, bg=CARD_BG).pack(side="left", padx=(0, 15))
        
        sweet_options = [self.T["sweet400"], self.T["sweet500"]]
        self.sweet_pills = self._build_pill_buttons(sweet_frame, sweet_options, self.selected_sweet)
        self.sweet_pills.pack(side="left", fill="x", expand=True)
    
    def _build_analysis_section(self, parent):
        """Build analysis section"""
        card = tk.Frame(parent, bg=CARD_BG, padx=25, pady=20, relief="flat", bd=0)
        card.pack(fill="x", pady=(0, 20))
        
        # Analysis button
        self.btn_start = ModernButton(card, text=self.T["start"], 
                                    bg=ACCENT_COLOR, fg=TEXT_PRIMARY,
                                    command=self._start_analysis,
                                    state="disabled", width=20, height=3,
                                    font=FONT_H3)
        self.btn_start.pack(pady=10)
        
        # Progress section
        progress_frame = tk.Frame(card, bg=CARD_BG)
        progress_frame.pack(fill="x", pady=(20, 0))
        
        tk.Label(progress_frame, text=self.T["progress"], font=FONT_BODY, fg=TEXT_PRIMARY, bg=CARD_BG).pack(anchor="w", pady=(0, 10))
        
        self.progress = ttk.Progressbar(progress_frame, orient="horizontal", 
                                      mode="determinate", style="Modern.Horizontal.TProgressbar")
        self.progress.pack(fill="x", pady=(0, 5))
        
        self.progress_label = tk.Label(progress_frame, text="0%", font=FONT_SMALL, fg=TEXT_SECONDARY, bg=CARD_BG)
        self.progress_label.pack(anchor="w")
    
    def _build_results_section(self, parent):
        """Build results section"""
        card = tk.Frame(parent, bg=CARD_BG, padx=25, pady=20, relief="flat", bd=0)
        card.pack(fill="x")
        
        # Title
        tk.Label(card, text=self.T["results"], font=FONT_H3, fg=TEXT_PRIMARY, bg=CARD_BG).pack(anchor="w", pady=(0, 20))
        
        # Use Case result
        uc_frame = tk.Frame(card, bg=CARD_BG)
        uc_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(uc_frame, text=self.T["use_case"], font=FONT_BODY, fg=TEXT_PRIMARY, bg=CARD_BG).pack(side="left", padx=(0, 15))
        
        self.badge = tk.Label(uc_frame, text=self.detected_uc,
                            font=FONT_BODY, bg=SUCCESS_COLOR, fg=TEXT_PRIMARY,
                            padx=15, pady=8, relief="flat")
        self.badge.pack(side="left")
        
        # Action buttons
        buttons_frame = tk.Frame(card, bg=CARD_BG)
        buttons_frame.pack(fill="x", pady=(20, 0))
        
        self.btn_generate_report = ModernButton(buttons_frame, text=self.T["generate_report"],
                                              bg=SUCCESS_COLOR, fg=TEXT_PRIMARY,
                                              command=self._generate_report,
                                              state="disabled", width=15, height=2)
        self.btn_generate_report.pack(side="left", padx=(0, 10))
        
        self.btn_open_report = ModernButton(buttons_frame, text=self.T["open_report"],
                                          bg=WARNING_COLOR, fg=TEXT_PRIMARY,
                                          command=self._open_report,
                                          state="disabled", width=15, height=2)
        self.btn_open_report.pack(side="left")
    
    def _build_footer(self):
        """Build footer section"""
        footer = tk.Frame(self.root, bg=SECONDARY_BG, height=50, padx=30)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        
        # Status
        self.status_label = tk.Label(footer, textvariable=self.status_text,
                                   font=FONT_SMALL, fg=TEXT_SECONDARY, bg=SECONDARY_BG)
        self.status_label.pack(side="left")
        
        # Version
        version_label = tk.Label(footer, text="v2.0.0", font=FONT_SMALL, fg=TEXT_SECONDARY, bg=SECONDARY_BG)
        version_label.pack(side="right")
    
    def _build_pill_buttons(self, parent, options, var):
        """Build pill-style buttons"""
        container = tk.Frame(parent, bg=CARD_BG)
        
        def set_choice(val):
            var.set(val)
            for btn in container.winfo_children():
                if isinstance(btn, ModernButton):
                    if btn.cget("text") == val:
                        btn.configure(bg=ACCENT_COLOR)
                    else:
                        btn.configure(bg=SECONDARY_BG)
        
        for opt in options:
            btn = ModernButton(container, text=opt, bg=ACCENT_COLOR if var.get() == opt else SECONDARY_BG,
                             fg=TEXT_PRIMARY, command=lambda v=opt: set_choice(v),
                             width=10, height=2)
            btn.pack(side="left", padx=5)
        
        return container
    
    def _set_language(self, code):
        """Change language"""
        if code not in LANG:
            return
        
        self.lang_var.set(code)
        self.T = LANG[code]
        
        # Update UI elements
        self.root.title(self.T["title"])
        self.lbl_title.config(text=self.T["title"])
        self.lbl_subtitle.config(text=self.T["subtitle"])
        
        # Update other elements as needed
        self.file_label.config(text=self.T["no_file"] if not self.selected_file else os.path.basename(self.selected_file))
        self.status_text.set(self.T["status_ready"])
    
    def _pick_file(self):
        """Pick MDF file"""
        path = filedialog.askopenfilename(
            title=self.T["choose"],
            filetypes=[("MDF Files", "*.mdf *.mf4 *.dat"), ("All Files", "*.*")]
        )
        
        if not path:
            return
        
        try:
            if not os.path.exists(path):
                raise FileNotFoundError(path)
            if os.path.getsize(path) == 0:
                raise ValueError("Empty file")
            
            self.selected_file = path
            self.file_label.config(text=os.path.basename(path))
            self.btn_start.config(state="normal")
            self.detected_uc = "Not detected"
            self._update_status(self.detected_uc)
            self._update_progress(0)
            self._show_toast(self.T["file_selected"])
            
        except Exception as e:
            messagebox.showerror(self.T["file_err"], str(e))
            self.selected_file = None
            self.file_label.config(text=self.T["no_file"])
            self.btn_start.config(state="disabled")
    
    def _start_analysis(self):
        """Start analysis"""
        if not self.selected_file:
            messagebox.showerror(self.T["file_err"], self.T["select_first"])
            return
        
        self.btn_start.config(state="disabled")
        self._update_progress(5)
        self._show_loading(True, self.T["analyzing"])
        
        # Get options
        myf_val = self.selected_myf.get()
        is_auto = myf_val.lower().startswith("auto") or myf_val == LANG["fr"]["auto"] or myf_val == LANG["en"]["auto"]
        myf_choice = None if is_auto else myf_val
        
        def run_analysis():
            try:
                result = analyser_et_generer_rapport(self.selected_file, lang=self.lang_var.get(), myf=myf_choice)
                
                found = [uc for uc, info in result.items() if info.get("status") == "detected"]
                uc = found[0] if found else "Not detected"
                
                self.root.after(0, lambda: self._handle_analysis_result(uc, result))
                
            except Exception as e:
                self.root.after(0, lambda: self._handle_error(e))
            finally:
                self.root.after(0, lambda: self.btn_start.config(state="normal"))
        
        threading.Thread(target=run_analysis, daemon=True).start()
    
    def _handle_analysis_result(self, uc_text, results):
        """Handle analysis results"""
        self.detected_uc = uc_text
        self.analysis_results = results
        self._update_progress(100)
        self._update_status(uc_text, "success")
        self._show_loading(False)
        
        # Enable report buttons
        self.btn_generate_report.config(state="normal")
        self.btn_open_report.config(state="normal")
        
        self._show_toast(self.T["success"])
    
    def _handle_error(self, e):
        """Handle analysis error"""
        self._show_loading(False)
        self._update_progress(0)
        self._update_status("Error during analysis", "error")
        messagebox.showerror(self.T["file_err"], str(e))
    
    def _generate_report(self):
        """Generate comprehensive HTML report"""
        if not self.analysis_results:
            messagebox.showwarning("Warning", "No analysis results available")
            return
        
        try:
            report_path = self._create_comprehensive_report()
            self._show_toast(self.T["report_generated"])
            messagebox.showinfo("Success", f"Report generated: {report_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
    
    def _create_comprehensive_report(self):
        """Create a comprehensive HTML report"""
        report_path = Path("eva_comprehensive_report.html")
        
        # Get current timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create comprehensive HTML content
        html_content = f"""
<!DOCTYPE html>
<html lang="{self.lang_var.get()}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EVA Comprehensive Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            text-align: center;
        }}
        
        .header h1 {{
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        
        .header p {{
            color: #7f8c8d;
            font-size: 1.2em;
        }}
        
        .card {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }}
        
        .card:hover {{
            transform: translateY(-5px);
        }}
        
        .card h2 {{
            color: #2c3e50;
            font-size: 1.8em;
            margin-bottom: 20px;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .info-item {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #3498db;
        }}
        
        .info-item strong {{
            color: #2c3e50;
            display: block;
            margin-bottom: 5px;
        }}
        
        .status-badge {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .status-success {{
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }}
        
        .status-warning {{
            background: #fff3cd;
            color: #856404;
            border: 1px solid #ffeaa7;
        }}
        
        .status-error {{
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }}
        
        .status-info {{
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }}
        
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #e9ecef;
        }}
        
        th {{
            background: #3498db;
            color: white;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.9em;
            letter-spacing: 0.5px;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 20px;
            background: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #3498db, #2ecc71);
            transition: width 0.3s ease;
        }}
        
        .footer {{
            text-align: center;
            padding: 30px;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 10px;
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
            
            .info-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚗 EVA Analysis Report</h1>
            <p>Comprehensive Vehicle Data Analysis Results</p>
            <p><strong>Generated:</strong> {timestamp}</p>
        </div>
        
        <div class="card">
            <h2>📊 Analysis Summary</h2>
            <div class="info-grid">
                <div class="info-item">
                    <strong>File Analyzed:</strong>
                    <span>{os.path.basename(self.selected_file) if self.selected_file else 'N/A'}</span>
                </div>
                <div class="info-item">
                    <strong>Analysis Date:</strong>
                    <span>{timestamp}</span>
                </div>
                <div class="info-item">
                    <strong>MyF Version:</strong>
                    <span>{self.selected_myf.get()}</span>
                </div>
                <div class="info-item">
                    <strong>SWEET Version:</strong>
                    <span>{self.selected_sweet.get()}</span>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>🎯 Use Case Detection</h2>
            <div class="info-item">
                <strong>Detected Use Case:</strong>
                <span class="status-badge status-success">{self.detected_uc}</span>
            </div>
        </div>
        
        <div class="card">
            <h2>📈 Detailed Results</h2>
            {self._generate_results_table()}
        </div>
        
        <div class="card">
            <h2>⚙️ Analysis Configuration</h2>
            <div class="info-grid">
                <div class="info-item">
                    <strong>Language:</strong>
                    <span>{self.lang_var.get().upper()}</span>
                </div>
                <div class="info-item">
                    <strong>File Path:</strong>
                    <span>{self.selected_file if self.selected_file else 'N/A'}</span>
                </div>
                <div class="info-item">
                    <strong>File Size:</strong>
                    <span>{self._format_file_size()}</span>
                </div>
                <div class="info-item">
                    <strong>Analysis Status:</strong>
                    <span class="status-badge status-success">Completed</span>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Generated by EVA Vehicle Data Analyzer v2.0.0</p>
            <p>© 2024 Renault / Ampere</p>
        </div>
    </div>
</body>
</html>
        """
        
        report_path.write_text(html_content, encoding="utf-8")
        return report_path
    
    def _generate_results_table(self):
        """Generate results table HTML"""
        if not self.analysis_results:
            return "<p>No analysis results available.</p>"
        
        table_html = """
        <table>
            <thead>
                <tr>
                    <th>Use Case</th>
                    <th>Status</th>
                    <th>Required</th>
                    <th>Present</th>
                    <th>Missing</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for uc, info in self.analysis_results.items():
            if uc.startswith("_"):  # Skip internal keys
                continue
            
            status_class = "status-success" if info.get("status") == "detected" else "status-warning"
            status_text = "Detected" if info.get("status") == "detected" else "Not Detected"
            
            table_html += f"""
                <tr>
                    <td><strong>{uc}</strong></td>
                    <td><span class="status-badge {status_class}">{status_text}</span></td>
                    <td>{info.get('required', 'N/A')}</td>
                    <td>{info.get('present', 'N/A')}</td>
                    <td>{info.get('missing', 'N/A')}</td>
                </tr>
            """
        
        table_html += """
            </tbody>
        </table>
        """
        
        return table_html
    
    def _format_file_size(self):
        """Format file size for display"""
        if not self.selected_file:
            return "N/A"
        
        try:
            size = os.path.getsize(self.selected_file)
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"
        except:
            return "N/A"
    
    def _open_report(self):
        """Open the generated report"""
        report_path = Path("eva_comprehensive_report.html")
        if report_path.exists():
            webbrowser.open(report_path.resolve().as_uri())
        else:
            messagebox.showwarning("Warning", "No report found. Please generate a report first.")
    
    def _show_toast(self, text, duration=3000):
        """Show a toast notification"""
        toast = tk.Toplevel(self.root)
        toast.overrideredirect(True)
        toast.attributes("-alpha", 0.9)
        toast.configure(bg=ACCENT_COLOR)
        
        label = tk.Label(toast, text=text, font=FONT_BODY, fg=TEXT_PRIMARY, bg=ACCENT_COLOR, padx=20, pady=10)
        label.pack()
        
        # Position toast
        toast.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (toast.winfo_width() // 2)
        y = self.root.winfo_y() + self.root.winfo_height() - toast.winfo_height() - 100
        toast.geometry(f"+{x}+{y}")
        
        toast.after(duration, toast.destroy)
    
    def _show_loading(self, show, text=None):
        """Show/hide loading overlay"""
        if show:
            if hasattr(self, "_loading") and self._loading.winfo_exists():
                return
            
            self._loading = tk.Toplevel(self.root)
            self._loading.overrideredirect(True)
            self._loading.attributes("-alpha", 0.8)
            self._loading.configure(bg=PRIMARY_BG)
            
            if text:
                tk.Label(self._loading, text=text, font=FONT_H3, fg=TEXT_PRIMARY, bg=PRIMARY_BG, padx=40, pady=30).pack()
            
            self._loading.geometry(
                f"{self.root.winfo_width()}x{self.root.winfo_height()}+{self.root.winfo_x()}+{self.root.winfo_y()}"
            )
        else:
            if hasattr(self, "_loading") and self._loading.winfo_exists():
                self._loading.destroy()
    
    def _update_status(self, text, status_type="info"):
        """Update status display"""
        colors = {
            "info": (SUCCESS_COLOR, TEXT_PRIMARY),
            "success": (SUCCESS_COLOR, TEXT_PRIMARY),
            "warning": (WARNING_COLOR, TEXT_PRIMARY),
            "error": (ACCENT_COLOR, TEXT_PRIMARY),
        }
        
        bg, fg = colors.get(status_type, (SUCCESS_COLOR, TEXT_PRIMARY))
        self.badge.config(text=text, bg=bg, fg=fg)
        self.status_text.set(text)
    
    def _update_progress(self, value):
        """Update progress bar"""
        self.progress["value"] = value
        self.progress_label.config(text=f"{value}%")
        self.root.update_idletasks()

def main():
    root = tk.Tk()
    app = EVAModernApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 