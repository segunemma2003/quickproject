import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from pathlib import Path
import threading
import webbrowser
import os
from typing import Optional

# ====== Backend (keep your existing module) ======
from eva_detecteur import (
    analyser_et_generer_rapport,
    verifier_presence_mapping_0p01s,
    CONFIG,
)

# ====== Logos (your absolute paths) ======
LOGO_RENAULT = Path(r"C:\Users\p131242\OneDrive - Alliance\EVA\icons\renault.png")
LOGO_AMPERE  = Path(r"C:\Users\p131242\OneDrive - Alliance\EVA\icons\AMPERE_logo.jpg")

# ====== Palette douce (sans bleu) ======
CREAM_BG = "#F7F5F2"       # fond principal crème
CARD_BG  = "#FFFFFF"       # cartes blanches
INK      = "#3E3E3E"       # texte principal
MUTED    = "#6E6E6E"       # texte atténué
PRIMARY  = "#8BBF9F"       # sauge (boutons/états actifs)
PRIMARY_HOVER = "#79A98C"   # sauge foncée
SOFT_SURFACE = "#EFEAE4"   # surface douce pour boutons pills
SOFT_TINT    = "#F3FBF6"   # léger vert pâle pour badges
ACCENT   = "#F2B3A3"       # pêche pour progressbar
SUCCESS  = "#5CB85C"
WARNING  = "#E6A23C"
ERROR    = "#E74C3C"

# ====== Fonts ======
FONT_H1 = ("Segoe UI", 20, "bold")
FONT_H2 = ("Segoe UI", 14, "bold")
FONT_BODY = ("Segoe UI", 11)
FONT_SMALL = ("Segoe UI", 10)

# ====== Langues ======
LANG = {
    "fr": {
        "title": "Interface EVA – Renault / Ampere",
        "import": "Importer un fichier de mesures",
        "file_types": "(.dat / .mdf / .mf4)",
        "choose": "Parcourir...",
        "no_file": "Aucun fichier sélectionné",
        "myf": "Version MyF",
        "auto": "Auto",
        "sweet": "Version SWEET",
        "sweet400": "SWEET 400",
        "sweet500": "SWEET 500",
        "start": "Lancer l'analyse",
        "detected": "Use Case détecté",
        "analyzing": "Analyse en cours...",
        "checking": "Vérification SWEET...",
        "success": "Analyse terminée",
        "file_err": "Erreur de fichier",
        "select_first": "Veuillez d'abord sélectionner un fichier.",
        "status_ready": "Prêt à analyser",
        "status_complete": "Analyse terminée",
        "options": "Options",
        "results": "Résultats",
        "use_case": "Use Case:",
        "progress": "Progression:",
        "language": "Langue",
        "file_selected": "Fichier sélectionné",
    },
    "en": {
        "title": "EVA Interface – Renault / Ampere",
        "import": "Import a measurement file",
        "file_types": "(.dat / .mdf / .mf4)",
        "choose": "Browse...",
        "no_file": "No file selected",
        "myf": "MyF version",
        "auto": "Auto",
        "sweet": "SWEET version",
        "sweet400": "SWEET 400",
        "sweet500": "SWEET 500",
        "start": "Run analysis",
        "detected": "Use Case detected",
        "analyzing": "Analyzing...",
        "checking": "Checking SWEET...",
        "success": "Analysis complete",
        "file_err": "File error",
        "select_first": "Please select a file first.",
        "status_ready": "Ready to analyze",
        "status_complete": "Analysis complete",
        "options": "Options",
        "results": "Results",
        "use_case": "Use Case:",
        "progress": "Progress:",
        "language": "Language",
        "file_selected": "File selected",
    },
}


class EVAApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        # Langue par défaut
        self.lang_var = tk.StringVar(value="fr")
        self.T = LANG[self.lang_var.get()]

        self.root.title(self.T["title"]) 
        self.root.geometry("1100x750")
        self.root.configure(bg=CREAM_BG)
        self.root.option_add("*Font", FONT_BODY)

        # Set minimum window size
        self.root.minsize(900, 650)

        # state
        self.selected_file: Optional[str] = None
        self.detected_uc: str = "Non détecté"
        self.selected_myf = tk.StringVar(value=self.T["auto"]) 
        self.selected_sweet = tk.StringVar(value=self.T["sweet400"]) 
        self.status_text = tk.StringVar(value=self.T["status_ready"]) 

        self._init_styles()
        self._build_header()
        self._build_body()
        self._build_footer()

    # ---------- styles ----------
    def _init_styles(self):
        s = ttk.Style()
        try:
            s.theme_use("clam")
        except Exception:
            pass

        # Base
        s.configure("TFrame", background=CREAM_BG)

        # Buttons — primaire
        s.configure(
            "Primary.TButton",
            font=("Segoe UI", 11, "bold"),
            padding=(20, 10),
            foreground="#FFFFFF",
            background=PRIMARY,
            borderwidth=0,
            focusthickness=0,
        )
        s.map(
            "Primary.TButton",
            background=[("active", PRIMARY_HOVER), ("disabled", SOFT_SURFACE)],
            foreground=[("disabled", MUTED)],
        )

        # Boutons pilules (options)
        s.configure(
            "Pill.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(12, 6),
            foreground=INK,
            background=SOFT_SURFACE,
            borderwidth=0,
        )
        s.map(
            "Pill.TButton",
            background=[("active", "#E8E2DA"), ("selected", PRIMARY)],
            foreground=[("active", INK), ("selected", "#FFFFFF")],
        )

        # Progressbar
        s.configure(
            "Horizontal.TProgressbar",
            thickness=12,
            background=ACCENT,
            troughcolor="#F8EDE9",
            bordercolor="#F8EDE9",
            lightcolor=ACCENT,
            darkcolor=ACCENT,
        )

        # Labels
        s.configure("Title.TLabel", font=FONT_H1, foreground=INK, background=CARD_BG)
        s.configure("Subtitle.TLabel", font=FONT_H2, foreground=INK, background=CARD_BG)
        s.configure("Muted.TLabel", font=FONT_SMALL, foreground=MUTED, background=CARD_BG)
        s.configure("Status.TLabel", font=FONT_SMALL, foreground=MUTED, background=CARD_BG)

        # Card style
        s.configure("Card.TFrame", background=CARD_BG, relief="flat", borderwidth=0)

    # ---------- header ----------
    def _build_header(self):
        header = tk.Frame(self.root, bg=CARD_BG, height=80, padx=20, pady=8)
        header.pack(fill="x", side="top")

        # Left logo
        left = tk.Frame(header, bg=CARD_BG)
        left.pack(side="left", fill="y")
        try:
            r_img = ImageTk.PhotoImage(Image.open(LOGO_RENAULT).resize((100, 50)))
            tk.Label(left, image=r_img, bg=CARD_BG).pack(side="left", padx=10)
            left.img = r_img
        except Exception:
            tk.Label(left, text="RENAULT", font=("Segoe UI", 14, "bold"), fg=INK, bg=CARD_BG).pack()

        # Center title
        center = tk.Frame(header, bg=CARD_BG)
        center.pack(side="left", fill="both", expand=True)
        self.lbl_header_title = ttk.Label(center, text=self.T["title"], style="Title.TLabel")
        self.lbl_header_title.pack(anchor="center")

        # Right logo
        right = tk.Frame(header, bg=CARD_BG)
        right.pack(side="right", fill="y")
        try:
            a_img = ImageTk.PhotoImage(Image.open(LOGO_AMPERE).resize((100, 50)))
            tk.Label(right, image=a_img, bg=CARD_BG).pack(side="right", padx=10)
            right.img = a_img
        except Exception:
            tk.Label(right, text="AMPERE", font=("Segoe UI", 14, "bold"), fg=INK, bg=CARD_BG).pack()

    # ---------- layout ----------
    def _build_body(self):
        # permet de reconstruire sur changement de langue
        self._body_frame = tk.Frame(self.root, bg=CREAM_BG, padx=30, pady=20)
        self._body_frame.pack(fill="both", expand=True)

        # File import card
        self._build_import_section(self._body_frame)

        # Options card
        self._build_options_section(self._body_frame)

        # Actions card
        self._build_actions_section(self._body_frame)

        # Results card
        self._build_results_section(self._body_frame)

    def _build_footer(self):
        footer = tk.Frame(self.root, bg=CARD_BG, height=40, padx=20)
        footer.pack(fill="x", side="bottom")

        status = ttk.Label(footer, textvariable=self.status_text, style="Status.TLabel")
        status.pack(side="left")

        version = ttk.Label(footer, text="v1.0.0", style="Status.TLabel")
        version.pack(side="right")

    def _build_import_section(self, parent):
        card = ttk.Frame(parent, style="Card.TFrame", padding=20)
        card.pack(fill="x", pady=(0, 15))

        self.lbl_import_title = ttk.Label(card, text=self.T["import"], style="Subtitle.TLabel")
        self.lbl_import_title.pack(anchor="w", pady=(0, 10))
        self.lbl_file_types = ttk.Label(card, text=self.T["file_types"], style="Muted.TLabel")
        self.lbl_file_types.pack(anchor="w", pady=(0, 15))

        # File selection area
        file_frame = tk.Frame(card, bg=CARD_BG)
        file_frame.pack(fill="x")

        self.btn_browse = ttk.Button(file_frame, text=self.T["choose"], style="Primary.TButton", command=self._pick_file)
        self.btn_browse.pack(side="left", padx=(0, 10))

        self.file_label = ttk.Label(file_frame, text=self.T["no_file"], style="Muted.TLabel")
        self.file_label.pack(side="left", fill="x", expand=True)

    def _build_options_section(self, parent):
        card = ttk.Frame(parent, style="Card.TFrame", padding=20)
        card.pack(fill="x", pady=(0, 15))

        self.lbl_options = ttk.Label(card, text=self.T["options"], style="Subtitle.TLabel")
        self.lbl_options.pack(anchor="w", pady=(0, 15))

        # Language switch
        lang_frame = tk.Frame(card, bg=CARD_BG)
        lang_frame.pack(fill="x", pady=(0, 15))
        tk.Label(lang_frame, text=self.T["language"] + ":", font=("Segoe UI", 11), fg=INK, bg=CARD_BG).pack(side="left", padx=(0, 15))
        self._build_language_switch(lang_frame).pack(side="left", fill="x", expand=True)

        # MyF Version
        myf_frame = tk.Frame(card, bg=CARD_BG)
        myf_frame.pack(fill="x", pady=(0, 15))

        self.lbl_myf_title = tk.Label(myf_frame, text=self.T["myf"] + ":", font=("Segoe UI", 11), fg=INK, bg=CARD_BG)
        self.lbl_myf_title.pack(side="left", padx=(0, 15))

        self.myf_var = self.selected_myf
        myf_options = [self.T["auto"], "MyF2", "MyF3", "MyF4.1", "MyF4.2"]
        self.myf_pills = self._build_pill_buttons(myf_frame, myf_options, self.myf_var)
        self.myf_pills.pack(side="left", fill="x", expand=True)

        # SWEET Version
        sweet_frame = tk.Frame(card, bg=CARD_BG)
        sweet_frame.pack(fill="x")

        self.lbl_sweet_title = tk.Label(sweet_frame, text=self.T["sweet"] + ":", font=("Segoe UI", 11), fg=INK, bg=CARD_BG)
        self.lbl_sweet_title.pack(side="left", padx=(0, 15))

        self.sweet_var = self.selected_sweet
        self.sweet_pills = self._build_pill_buttons(sweet_frame, [self.T["sweet400"], self.T["sweet500"]], self.sweet_var)
        self.sweet_pills.pack(side="left", fill="x", expand=True)

    def _build_actions_section(self, parent):
        card = ttk.Frame(parent, style="Card.TFrame", padding=20)
        card.pack(fill="x", pady=(0, 15))

        self.btn_start = ttk.Button(
            card,
            text=self.T["start"],
            style="Primary.TButton",
            command=self._start_analysis,
            state="disabled",
        )
        self.btn_start.pack()

    def _build_results_section(self, parent):
        card = ttk.Frame(parent, style="Card.TFrame", padding=20)
        card.pack(fill="x")

        self.lbl_results = ttk.Label(card, text=self.T["results"], style="Subtitle.TLabel")
        self.lbl_results.pack(anchor="w", pady=(0, 15))

        # Detection result
        result_frame = tk.Frame(card, bg=CARD_BG)
        result_frame.pack(fill="x", pady=(0, 15))

        self.lbl_uc_title = tk.Label(result_frame, text=self.T["use_case"], font=("Segoe UI", 11), fg=INK, bg=CARD_BG)
        self.lbl_uc_title.pack(side="left", padx=(0, 15))

        self.badge = tk.Label(
            result_frame,
            text=self.detected_uc,
            font=("Segoe UI", 10, "bold"),
            bg=SOFT_TINT,
            fg=INK,
            padx=15,
            pady=5,
        )
        self.badge.pack(side="left")

        # Progress bar
        pb_frame = tk.Frame(card, bg=CARD_BG)
        pb_frame.pack(fill="x")

        self.lbl_progress = tk.Label(pb_frame, text=self.T["progress"], font=("Segoe UI", 11), fg=INK, bg=CARD_BG)
        self.lbl_progress.pack(side="left", padx=(0, 15))

        self.progress = ttk.Progressbar(
            pb_frame,
            orient="horizontal",
            length=400,
            mode="determinate",
            style="Horizontal.TProgressbar",
        )
        self.progress.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.progress_label = ttk.Label(pb_frame, text="0%", style="Muted.TLabel")
        self.progress_label.pack(side="left")

    # ---------- widgets ----------
    def _build_language_switch(self, parent):
        container = tk.Frame(parent, bg=CARD_BG)

        def set_lang(code: str):
            if code not in LANG:
                return
            self.lang_var.set(code)
            self._set_language(code)

        for code, label in ("fr", "FR"), ("en", "EN"):
            btn = ttk.Button(container, text=label, style="Pill.TButton", command=lambda c=code: set_lang(c))
            btn.pack(side="left", padx=5)
            if self.lang_var.get() == code:
                btn.state(["selected"])
        return container

    def _build_pill_buttons(self, parent, options, var: tk.StringVar):
        container = tk.Frame(parent, bg=CARD_BG)

        def set_choice(val):
            var.set(val)
            for btn in container.winfo_children():
                if isinstance(btn, ttk.Button):
                    btn.state(["!pressed"])
                    if btn.cget("text") == val:
                        btn.state(["selected"])

            if var is self.myf_var:
                # map "Auto" key across languages
                is_auto = val.lower().startswith("auto") or val == LANG["fr"]["auto"] or val == LANG["en"]["auto"]
                CONFIG["myf"] = None if is_auto else val
                self._update_status(f"{self.detected_uc} | MyF={val}")

        for opt in options:
            btn = ttk.Button(container, text=opt, style="Pill.TButton", command=lambda v=opt: set_choice(v))
            btn.pack(side="left", padx=5)
            if var.get() == opt:
                btn.state(["selected"])

        return container

    # ---------- UX helpers ----------
    def _show_toast(self, text: str, ms: int = 1800):
        toast = tk.Toplevel(self.root)
        toast.overrideredirect(True)
        toast.attributes("-alpha", 0.95)

        frame = tk.Frame(toast, bg=INK, padx=2, pady=2)
        frame.pack()

        label = tk.Label(frame, text=text, font=FONT_SMALL, bg=CARD_BG, fg=INK, padx=15, pady=8)
        label.pack()

        # Position above footer
        toast.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (toast.winfo_width() // 2)
        y = self.root.winfo_y() + self.root.winfo_height() - toast.winfo_height() - 50
        toast.geometry(f"+{x}+{y}")

        toast.after(ms, toast.destroy)

    def _show_loading(self, show: bool, text: Optional[str] = None):
        if show:
            if hasattr(self, "_loading") and self._loading.winfo_exists():
                return

            self._loading = tk.Toplevel(self.root)
            self._loading.overrideredirect(True)
            self._loading.attributes("-alpha", 0.85)
            self._loading.configure(bg=INK)

            if text:
                tk.Label(self._loading, text=text, font=("Segoe UI", 14), fg="#FFFFFF", bg=INK, padx=30, pady=20).pack()

            self._loading.geometry(
                f"{self.root.winfo_width()}x{self.root.winfo_height()}+{self.root.winfo_x()}+{self.root.winfo_y()}"
            )
        else:
            if hasattr(self, "_loading") and self._loading.winfo_exists():
                self._loading.destroy()

    def _update_status(self, text: str, status_type: str = "info"):
        colors = {
            "info": (SOFT_TINT, INK),
            "success": (SUCCESS, "#FFFFFF"),
            "warning": (WARNING, "#FFFFFF"),
            "error": (ERROR, "#FFFFFF"),
        }

        bg, fg = colors.get(status_type, (SOFT_TINT, INK))
        self.badge.config(text=text, bg=bg, fg=fg)
        self.status_text.set(text)

    def _update_progress(self, value: int):
        self.progress["value"] = value
        self.progress_label.config(text=f"{value}%")
        self.root.update_idletasks()

    def _set_language(self, code: str):
        # Sauvegarder l'état actuel
        prev_selected_file = self.selected_file
        prev_detected_uc = self.detected_uc
        prev_progress = 0
        try:
            prev_progress = int(self.progress["value"]) if hasattr(self, "progress") else 0
        except Exception:
            prev_progress = 0
        prev_status = self.status_text.get()

        # Appliquer la nouvelle langue
        self.T = LANG.get(code, LANG["fr"])
        self.root.title(self.T["title"]) 
        if hasattr(self, "lbl_header_title"):
            self.lbl_header_title.config(text=self.T["title"]) 

        # Reconstruire le corps (plus simple pour tout mettre à jour)
        if hasattr(self, "_body_frame") and self._body_frame.winfo_exists():
            self._body_frame.destroy()
        self._build_body()

        # Restaurer l'état des widgets dépendants
        if prev_selected_file:
            self.file_label.config(text=os.path.basename(prev_selected_file))
            self.btn_start.config(state="normal")
        else:
            self.file_label.config(text=self.T["no_file"])
            self.btn_start.config(state="disabled")

        self.detected_uc = prev_detected_uc
        self._update_progress(int(prev_progress))

        # Mettre à jour le statut lisible
        if prev_status in (LANG['fr']["status_ready"], LANG['en']["status_ready"]):
            self.status_text.set(self.T["status_ready"])
        elif prev_status in (LANG['fr']["status_complete"], LANG['en']["status_complete"]):
            self.status_text.set(self.T["status_complete"])
        else:
            self.status_text.set(prev_status)

        # Rafraîchir le badge avec la langue actuelle
        self._update_status(self.detected_uc, "info")

    # ---------- events ----------
    def _pick_file(self):
        path = filedialog.askopenfilename(
            title=self.T["choose"],
            filetypes=[("Fichiers MDF", "*.dat *.mdf *.mf4"), ("Tous les fichiers", "*.*")],
        )

        if not path:
            return

        try:
            if not os.path.exists(path):
                raise FileNotFoundError(path)
            if os.path.getsize(path) == 0:
                raise ValueError("Fichier vide")

            self.selected_file = path
            self.file_label.config(text=os.path.basename(path))
            self.btn_start.config(state="normal")
            self.detected_uc = "Non détecté" if self.lang_var.get() == "fr" else "Not detected"
            self._update_status(self.detected_uc)
            self._update_progress(0)
            self._show_toast(self.T["file_selected"]) 

        except Exception as e:
            messagebox.showerror(self.T["file_err"], str(e))
            self.selected_file = None
            self.file_label.config(text=self.T["no_file"])
            self.btn_start.config(state="disabled")

    def _start_analysis(self):
        if not self.selected_file:
            messagebox.showerror(self.T["file_err"], self.T["select_first"])
            return

        self.btn_start.config(state="disabled")
        self._update_progress(5)
        self._show_loading(True, self.T["analyzing"]) 

        # "Auto" peut être FR/EN
        myf_val = self.selected_myf.get()
        is_auto = myf_val.lower().startswith("auto") or myf_val == LANG["fr"]["auto"] or myf_val == LANG["en"]["auto"]
        myf_choice = None if is_auto else myf_val

        def run_analysis():
            try:
                try:
                    result = analyser_et_generer_rapport(self.selected_file, lang=self.lang_var.get(), myf=myf_choice)
                except TypeError:
                    CONFIG["myf"] = myf_choice
                    result = analyser_et_generer_rapport(self.selected_file, lang=self.lang_var.get())

                found = [uc for uc, info in result.items() if info.get("status") == "detected"]
                uc = found[0] if found else ("Non détecté" if self.lang_var.get() == "fr" else "Not detected")

                self.root.after(0, lambda: self._handle_analysis_result(uc))

            except Exception as e:
                self.root.after(0, lambda: self._handle_error(e))
            finally:
                self.root.after(0, lambda: self.btn_start.config(state="normal"))

        threading.Thread(target=run_analysis, daemon=True).start()

    def _handle_analysis_result(self, uc_text: str):
        self.detected_uc = uc_text
        self._update_progress(50)
        self._update_status(uc_text, "info")

        # Start SWEET verification
        self._show_loading(True, self.T["checking"]) 

        sweet_mode = "sweet400" if "400" in self.selected_sweet.get() else "sweet500"
        myf_val = self.selected_myf.get()
        is_auto = myf_val.lower().startswith("auto") or myf_val == LANG["fr"]["auto"] or myf_val == LANG["en"]["auto"]
        myf_choice = None if is_auto else myf_val
        uc_id = None if self.detected_uc in ("Non détecté", "Not detected", "None") else self.detected_uc

        def run_sweet_verification():
            try:
                try:
                    df = verifier_presence_mapping_0p01s(
                        self.selected_file, mode=sweet_mode, uc_id=uc_id, myf=myf_choice
                    )
                except TypeError:
                    CONFIG["myf"] = myf_choice
                    df = verifier_presence_mapping_0p01s(self.selected_file, mode=sweet_mode, uc_id=uc_id)

                html = Path(f"verification_{sweet_mode}.html")
                html.write_text(df.to_html(index=False), encoding="utf-8")

                col = "Statut" if "Statut" in df.columns else ("Status" if "Status" in df.columns else None)
                ok = (df[col] == "OK").all() if col else False
                version = "400" if sweet_mode.endswith("400") else "500"
                label = f"SWEET {version} - {'OK' if ok else 'NOK'}"

                self.root.after(0, lambda: self._handle_sweet_result(html, label, ok))

            except Exception as e:
                self.root.after(0, lambda: self._handle_error(e))

        threading.Thread(target=run_sweet_verification, daemon=True).start()

    def _handle_sweet_result(self, html_path: Path, label: str, ok: bool):
        self._update_progress(100)
        self._update_status(label, "success" if ok else "warning")
        self._show_loading(False)

        try:
            webbrowser.open(html_path.resolve().as_uri())
        finally:
            self._show_toast(self.T["success"]) 

    def _handle_error(self, e: Exception):
        self._show_loading(False)
        self._update_progress(0)
        self._update_status("Erreur lors de l'analyse" if self.lang_var.get()=="fr" else "Error during analysis", "error")
        messagebox.showerror(self.T["file_err"], str(e))


def main():
    root = tk.Tk()
    app = EVAApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from pathlib import Path
import threading
import webbrowser
import os
from typing import Optional

# ====== Backend (keep your existing module) ======
from eva_detecteur import (
    analyser_et_generer_rapport,
    verifier_presence_mapping_0p01s,
    CONFIG,
)

# ====== Logos (your absolute paths) ======
LOGO_RENAULT = Path(r"C:\Users\p131242\OneDrive - Alliance\EVA\icons\renault.png")
LOGO_AMPERE  = Path(r"C:\Users\p131242\OneDrive - Alliance\EVA\icons\AMPERE_logo.jpg")

# ====== Palette douce (sans bleu) ======
CREAM_BG = "#F7F5F2"       # fond principal crème
CARD_BG  = "#FFFFFF"       # cartes blanches
INK      = "#3E3E3E"       # texte principal
MUTED    = "#6E6E6E"       # texte atténué
PRIMARY  = "#8BBF9F"       # sauge (boutons/états actifs)
PRIMARY_HOVER = "#79A98C"   # sauge foncée
SOFT_SURFACE = "#EFEAE4"   # surface douce pour boutons pills
SOFT_TINT    = "#F3FBF6"   # léger vert pâle pour badges
ACCENT   = "#F2B3A3"       # pêche pour progressbar
SUCCESS  = "#5CB85C"
WARNING  = "#E6A23C"
ERROR    = "#E74C3C"

# ====== Fonts ======
FONT_H1 = ("Segoe UI", 20, "bold")
FONT_H2 = ("Segoe UI", 14, "bold")
FONT_BODY = ("Segoe UI", 11)
FONT_SMALL = ("Segoe UI", 10)

# ====== Langues ======
LANG = {
    "fr": {
        "title": "Interface EVA – Renault / Ampere",
        "import": "Importer un fichier de mesures",
        "file_types": "(.dat / .mdf / .mf4)",
        "choose": "Parcourir...",
        "no_file": "Aucun fichier sélectionné",
        "myf": "Version MyF",
        "auto": "Auto",
        "sweet": "Version SWEET",
        "sweet400": "SWEET 400",
        "sweet500": "SWEET 500",
        "start": "Lancer l'analyse",
        "detected": "Use Case détecté",
        "analyzing": "Analyse en cours...",
        "checking": "Vérification SWEET...",
        "success": "Analyse terminée",
        "file_err": "Erreur de fichier",
        "select_first": "Veuillez d'abord sélectionner un fichier.",
        "status_ready": "Prêt à analyser",
        "status_complete": "Analyse terminée",
        "options": "Options",
        "results": "Résultats",
        "use_case": "Use Case:",
        "progress": "Progression:",
        "language": "Langue",
        "file_selected": "Fichier sélectionné",
    },
    "en": {
        "title": "EVA Interface – Renault / Ampere",
        "import": "Import a measurement file",
        "file_types": "(.dat / .mdf / .mf4)",
        "choose": "Browse...",
        "no_file": "No file selected",
        "myf": "MyF version",
        "auto": "Auto",
        "sweet": "SWEET version",
        "sweet400": "SWEET 400",
        "sweet500": "SWEET 500",
        "start": "Run analysis",
        "detected": "Use Case detected",
        "analyzing": "Analyzing...",
        "checking": "Checking SWEET...",
        "success": "Analysis complete",
        "file_err": "File error",
        "select_first": "Please select a file first.",
        "status_ready": "Ready to analyze",
        "status_complete": "Analysis complete",
        "options": "Options",
        "results": "Results",
        "use_case": "Use Case:",
        "progress": "Progress:",
        "language": "Language",
        "file_selected": "File selected",
    },
}


class EVAApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        # Langue par défaut
        self.lang_var = tk.StringVar(value="fr")
        self.T = LANG[self.lang_var.get()]

        self.root.title(self.T["title"]) 
        self.root.geometry("1100x750")
        self.root.configure(bg=CREAM_BG)
        self.root.option_add("*Font", FONT_BODY)

        # Set minimum window size
        self.root.minsize(900, 650)

        # state
        self.selected_file: Optional[str] = None
        self.detected_uc: str = "Non détecté"
        self.selected_myf = tk.StringVar(value=self.T["auto"]) 
        self.selected_sweet = tk.StringVar(value=self.T["sweet400"]) 
        self.status_text = tk.StringVar(value=self.T["status_ready"]) 

        self._init_styles()
        self._build_header()
        self._build_body()
        self._build_footer()

    # ---------- styles ----------
    def _init_styles(self):
        s = ttk.Style()
        try:
            s.theme_use("clam")
        except Exception:
            pass

        # Base
        s.configure("TFrame", background=CREAM_BG)

        # Buttons — primaire
        s.configure(
            "Primary.TButton",
            font=("Segoe UI", 11, "bold"),
            padding=(20, 10),
            foreground="#FFFFFF",
            background=PRIMARY,
            borderwidth=0,
            focusthickness=0,
        )
        s.map(
            "Primary.TButton",
            background=[("active", PRIMARY_HOVER), ("disabled", SOFT_SURFACE)],
            foreground=[("disabled", MUTED)],
        )

        # Boutons pilules (options)
        s.configure(
            "Pill.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(12, 6),
            foreground=INK,
            background=SOFT_SURFACE,
            borderwidth=0,
        )
        s.map(
            "Pill.TButton",
            background=[("active", "#E8E2DA"), ("selected", PRIMARY)],
            foreground=[("active", INK), ("selected", "#FFFFFF")],
        )

        # Progressbar
        s.configure(
            "Horizontal.TProgressbar",
            thickness=12,
            background=ACCENT,
            troughcolor="#F8EDE9",
            bordercolor="#F8EDE9",
            lightcolor=ACCENT,
            darkcolor=ACCENT,
        )

        # Labels
        s.configure("Title.TLabel", font=FONT_H1, foreground=INK, background=CARD_BG)
        s.configure("Subtitle.TLabel", font=FONT_H2, foreground=INK, background=CARD_BG)
        s.configure("Muted.TLabel", font=FONT_SMALL, foreground=MUTED, background=CARD_BG)
        s.configure("Status.TLabel", font=FONT_SMALL, foreground=MUTED, background=CARD_BG)

        # Card style
        s.configure("Card.TFrame", background=CARD_BG, relief="flat", borderwidth=0)

    # ---------- header ----------
    def _build_header(self):
        header = tk.Frame(self.root, bg=CARD_BG, height=80, padx=20, pady=8)
        header.pack(fill="x", side="top")

        # Left logo
        left = tk.Frame(header, bg=CARD_BG)
        left.pack(side="left", fill="y")
        try:
            r_img = ImageTk.PhotoImage(Image.open(LOGO_RENAULT).resize((100, 50)))
            tk.Label(left, image=r_img, bg=CARD_BG).pack(side="left", padx=10)
            left.img = r_img
        except Exception:
            tk.Label(left, text="RENAULT", font=("Segoe UI", 14, "bold"), fg=INK, bg=CARD_BG).pack()

        # Center title
        center = tk.Frame(header, bg=CARD_BG)
        center.pack(side="left", fill="both", expand=True)
        self.lbl_header_title = ttk.Label(center, text=self.T["title"], style="Title.TLabel")
        self.lbl_header_title.pack(anchor="center")

        # Right logo
        right = tk.Frame(header, bg=CARD_BG)
        right.pack(side="right", fill="y")
        try:
            a_img = ImageTk.PhotoImage(Image.open(LOGO_AMPERE).resize((100, 50)))
            tk.Label(right, image=a_img, bg=CARD_BG).pack(side="right", padx=10)
            right.img = a_img
        except Exception:
            tk.Label(right, text="AMPERE", font=("Segoe UI", 14, "bold"), fg=INK, bg=CARD_BG).pack()

    # ---------- layout ----------
    def _build_body(self):
        # permet de reconstruire sur changement de langue
        self._body_frame = tk.Frame(self.root, bg=CREAM_BG, padx=30, pady=20)
        self._body_frame.pack(fill="both", expand=True)

        # File import card
        self._build_import_section(self._body_frame)

        # Options card
        self._build_options_section(self._body_frame)

        # Actions card
        self._build_actions_section(self._body_frame)

        # Results card
        self._build_results_section(self._body_frame)

    def _build_footer(self):
        footer = tk.Frame(self.root, bg=CARD_BG, height=40, padx=20)
        footer.pack(fill="x", side="bottom")

        status = ttk.Label(footer, textvariable=self.status_text, style="Status.TLabel")
        status.pack(side="left")

        version = ttk.Label(footer, text="v1.0.0", style="Status.TLabel")
        version.pack(side="right")

    def _build_import_section(self, parent):
        card = ttk.Frame(parent, style="Card.TFrame", padding=20)
        card.pack(fill="x", pady=(0, 15))

        self.lbl_import_title = ttk.Label(card, text=self.T["import"], style="Subtitle.TLabel")
        self.lbl_import_title.pack(anchor="w", pady=(0, 10))
        self.lbl_file_types = ttk.Label(card, text=self.T["file_types"], style="Muted.TLabel")
        self.lbl_file_types.pack(anchor="w", pady=(0, 15))

        # File selection area
        file_frame = tk.Frame(card, bg=CARD_BG)
        file_frame.pack(fill="x")

        self.btn_browse = ttk.Button(file_frame, text=self.T["choose"], style="Primary.TButton", command=self._pick_file)
        self.btn_browse.pack(side="left", padx=(0, 10))

        self.file_label = ttk.Label(file_frame, text=self.T["no_file"], style="Muted.TLabel")
        self.file_label.pack(side="left", fill="x", expand=True)

    def _build_options_section(self, parent):
        card = ttk.Frame(parent, style="Card.TFrame", padding=20)
        card.pack(fill="x", pady=(0, 15))

        self.lbl_options = ttk.Label(card, text=self.T["options"], style="Subtitle.TLabel")
        self.lbl_options.pack(anchor="w", pady=(0, 15))

        # Language switch
        lang_frame = tk.Frame(card, bg=CARD_BG)
        lang_frame.pack(fill="x", pady=(0, 15))
        tk.Label(lang_frame, text=self.T["language"] + ":", font=("Segoe UI", 11), fg=INK, bg=CARD_BG).pack(side="left", padx=(0, 15))
        self._build_language_switch(lang_frame).pack(side="left", fill="x", expand=True)

        # MyF Version
        myf_frame = tk.Frame(card, bg=CARD_BG)
        myf_frame.pack(fill="x", pady=(0, 15))

        self.lbl_myf_title = tk.Label(myf_frame, text=self.T["myf"] + ":", font=("Segoe UI", 11), fg=INK, bg=CARD_BG)
        self.lbl_myf_title.pack(side="left", padx=(0, 15))

        self.myf_var = self.selected_myf
        myf_options = [self.T["auto"], "MyF2", "MyF3", "MyF4.1", "MyF4.2"]
        self.myf_pills = self._build_pill_buttons(myf_frame, myf_options, self.myf_var)
        self.myf_pills.pack(side="left", fill="x", expand=True)

        # SWEET Version
        sweet_frame = tk.Frame(card, bg=CARD_BG)
        sweet_frame.pack(fill="x")

        self.lbl_sweet_title = tk.Label(sweet_frame, text=self.T["sweet"] + ":", font=("Segoe UI", 11), fg=INK, bg=CARD_BG)
        self.lbl_sweet_title.pack(side="left", padx=(0, 15))

        self.sweet_var = self.selected_sweet
        self.sweet_pills = self._build_pill_buttons(sweet_frame, [self.T["sweet400"], self.T["sweet500"]], self.sweet_var)
        self.sweet_pills.pack(side="left", fill="x", expand=True)

    def _build_actions_section(self, parent):
        card = ttk.Frame(parent, style="Card.TFrame", padding=20)
        card.pack(fill="x", pady=(0, 15))

        self.btn_start = ttk.Button(
            card,
            text=self.T["start"],
            style="Primary.TButton",
            command=self._start_analysis,
            state="disabled",
        )
        self.btn_start.pack()

    def _build_results_section(self, parent):
        card = ttk.Frame(parent, style="Card.TFrame", padding=20)
        card.pack(fill="x")

        self.lbl_results = ttk.Label(card, text=self.T["results"], style="Subtitle.TLabel")
        self.lbl_results.pack(anchor="w", pady=(0, 15))

        # Detection result
        result_frame = tk.Frame(card, bg=CARD_BG)
        result_frame.pack(fill="x", pady=(0, 15))

        self.lbl_uc_title = tk.Label(result_frame, text=self.T["use_case"], font=("Segoe UI", 11), fg=INK, bg=CARD_BG)
        self.lbl_uc_title.pack(side="left", padx=(0, 15))

        self.badge = tk.Label(
            result_frame,
            text=self.detected_uc,
            font=("Segoe UI", 10, "bold"),
            bg=SOFT_TINT,
            fg=INK,
            padx=15,
            pady=5,
        )
        self.badge.pack(side="left")

        # Progress bar
        pb_frame = tk.Frame(card, bg=CARD_BG)
        pb_frame.pack(fill="x")

        self.lbl_progress = tk.Label(pb_frame, text=self.T["progress"], font=("Segoe UI", 11), fg=INK, bg=CARD_BG)
        self.lbl_progress.pack(side="left", padx=(0, 15))

        self.progress = ttk.Progressbar(
            pb_frame,
            orient="horizontal",
            length=400,
            mode="determinate",
            style="Horizontal.TProgressbar",
        )
        self.progress.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.progress_label = ttk.Label(pb_frame, text="0%", style="Muted.TLabel")
        self.progress_label.pack(side="left")

    # ---------- widgets ----------
    def _build_language_switch(self, parent):
        container = tk.Frame(parent, bg=CARD_BG)

        def set_lang(code: str):
            if code not in LANG:
                return
            self.lang_var.set(code)
            self._set_language(code)

        for code, label in ("fr", "FR"), ("en", "EN"):
            btn = ttk.Button(container, text=label, style="Pill.TButton", command=lambda c=code: set_lang(c))
            btn.pack(side="left", padx=5)
            if self.lang_var.get() == code:
                btn.state(["selected"])
        return container

    def _build_pill_buttons(self, parent, options, var: tk.StringVar):
        container = tk.Frame(parent, bg=CARD_BG)

        def set_choice(val):
            var.set(val)
            for btn in container.winfo_children():
                if isinstance(btn, ttk.Button):
                    btn.state(["!pressed"])
                    if btn.cget("text") == val:
                        btn.state(["selected"])

            if var is self.myf_var:
                # map "Auto" key across languages
                is_auto = val.lower().startswith("auto") or val == LANG["fr"]["auto"] or val == LANG["en"]["auto"]
                CONFIG["myf"] = None if is_auto else val
                self._update_status(f"{self.detected_uc} | MyF={val}")

        for opt in options:
            btn = ttk.Button(container, text=opt, style="Pill.TButton", command=lambda v=opt: set_choice(v))
            btn.pack(side="left", padx=5)
            if var.get() == opt:
                btn.state(["selected"])

        return container

    # ---------- UX helpers ----------
    def _show_toast(self, text: str, ms: int = 1800):
        toast = tk.Toplevel(self.root)
        toast.overrideredirect(True)
        toast.attributes("-alpha", 0.95)

        frame = tk.Frame(toast, bg=INK, padx=2, pady=2)
        frame.pack()

        label = tk.Label(frame, text=text, font=FONT_SMALL, bg=CARD_BG, fg=INK, padx=15, pady=8)
        label.pack()

        # Position above footer
        toast.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (toast.winfo_width() // 2)
        y = self.root.winfo_y() + self.root.winfo_height() - toast.winfo_height() - 50
        toast.geometry(f"+{x}+{y}")

        toast.after(ms, toast.destroy)

    def _show_loading(self, show: bool, text: Optional[str] = None):
        if show:
            if hasattr(self, "_loading") and self._loading.winfo_exists():
                return

            self._loading = tk.Toplevel(self.root)
            self._loading.overrideredirect(True)
            self._loading.attributes("-alpha", 0.85)
            self._loading.configure(bg=INK)

            if text:
                tk.Label(self._loading, text=text, font=("Segoe UI", 14), fg="#FFFFFF", bg=INK, padx=30, pady=20).pack()

            self._loading.geometry(
                f"{self.root.winfo_width()}x{self.root.winfo_height()}+{self.root.winfo_x()}+{self.root.winfo_y()}"
            )
        else:
            if hasattr(self, "_loading") and self._loading.winfo_exists():
                self._loading.destroy()

    def _update_status(self, text: str, status_type: str = "info"):
        colors = {
            "info": (SOFT_TINT, INK),
            "success": (SUCCESS, "#FFFFFF"),
            "warning": (WARNING, "#FFFFFF"),
            "error": (ERROR, "#FFFFFF"),
        }

        bg, fg = colors.get(status_type, (SOFT_TINT, INK))
        self.badge.config(text=text, bg=bg, fg=fg)
        self.status_text.set(text)

    def _update_progress(self, value: int):
        self.progress["value"] = value
        self.progress_label.config(text=f"{value}%")
        self.root.update_idletasks()

    def _set_language(self, code: str):
        # Sauvegarder l'état actuel
        prev_selected_file = self.selected_file
        prev_detected_uc = self.detected_uc
        prev_progress = 0
        try:
            prev_progress = int(self.progress["value"]) if hasattr(self, "progress") else 0
        except Exception:
            prev_progress = 0
        prev_status = self.status_text.get()

        # Appliquer la nouvelle langue
        self.T = LANG.get(code, LANG["fr"])
        self.root.title(self.T["title"]) 
        if hasattr(self, "lbl_header_title"):
            self.lbl_header_title.config(text=self.T["title"]) 

        # Reconstruire le corps (plus simple pour tout mettre à jour)
        if hasattr(self, "_body_frame") and self._body_frame.winfo_exists():
            self._body_frame.destroy()
        self._build_body()

        # Restaurer l'état des widgets dépendants
        if prev_selected_file:
            self.file_label.config(text=os.path.basename(prev_selected_file))
            self.btn_start.config(state="normal")
        else:
            self.file_label.config(text=self.T["no_file"])
            self.btn_start.config(state="disabled")

        self.detected_uc = prev_detected_uc
        self._update_progress(int(prev_progress))

        # Mettre à jour le statut lisible
        if prev_status in (LANG['fr']["status_ready"], LANG['en']["status_ready"]):
            self.status_text.set(self.T["status_ready"])
        elif prev_status in (LANG['fr']["status_complete"], LANG['en']["status_complete"]):
            self.status_text.set(self.T["status_complete"])
        else:
            self.status_text.set(prev_status)

        # Rafraîchir le badge avec la langue actuelle
        self._update_status(self.detected_uc, "info")

    # ---------- events ----------
    def _pick_file(self):
        path = filedialog.askopenfilename(
            title=self.T["choose"],
            filetypes=[("Fichiers MDF", "*.dat *.mdf *.mf4"), ("Tous les fichiers", "*.*")],
        )

        if not path:
            return

        try:
            if not os.path.exists(path):
                raise FileNotFoundError(path)
            if os.path.getsize(path) == 0:
                raise ValueError("Fichier vide")

            self.selected_file = path
            self.file_label.config(text=os.path.basename(path))
            self.btn_start.config(state="normal")
            self.detected_uc = "Non détecté" if self.lang_var.get() == "fr" else "Not detected"
            self._update_status(self.detected_uc)
            self._update_progress(0)
            self._show_toast(self.T["file_selected"]) 

        except Exception as e:
            messagebox.showerror(self.T["file_err"], str(e))
            self.selected_file = None
            self.file_label.config(text=self.T["no_file"])
            self.btn_start.config(state="disabled")

    def _start_analysis(self):
        if not self.selected_file:
            messagebox.showerror(self.T["file_err"], self.T["select_first"])
            return

        self.btn_start.config(state="disabled")
        self._update_progress(5)
        self._show_loading(True, self.T["analyzing"]) 

        # "Auto" peut être FR/EN
        myf_val = self.selected_myf.get()
        is_auto = myf_val.lower().startswith("auto") or myf_val == LANG["fr"]["auto"] or myf_val == LANG["en"]["auto"]
        myf_choice = None if is_auto else myf_val

        def run_analysis():
            try:
                try:
                    result = analyser_et_generer_rapport(self.selected_file, lang=self.lang_var.get(), myf=myf_choice)
                except TypeError:
                    CONFIG["myf"] = myf_choice
                    result = analyser_et_generer_rapport(self.selected_file, lang=self.lang_var.get())

                found = [uc for uc, info in result.items() if info.get("status") == "detected"]
                uc = found[0] if found else ("Non détecté" if self.lang_var.get() == "fr" else "Not detected")

                self.root.after(0, lambda: self._handle_analysis_result(uc))

            except Exception as e:
                self.root.after(0, lambda: self._handle_error(e))
            finally:
                self.root.after(0, lambda: self.btn_start.config(state="normal"))

        threading.Thread(target=run_analysis, daemon=True).start()

    def _handle_analysis_result(self, uc_text: str):
        self.detected_uc = uc_text
        self._update_progress(50)
        self._update_status(uc_text, "info")

        # Start SWEET verification
        self._show_loading(True, self.T["checking"]) 

        sweet_mode = "sweet400" if "400" in self.selected_sweet.get() else "sweet500"
        myf_val = self.selected_myf.get()
        is_auto = myf_val.lower().startswith("auto") or myf_val == LANG["fr"]["auto"] or myf_val == LANG["en"]["auto"]
        myf_choice = None if is_auto else myf_val
        uc_id = None if self.detected_uc in ("Non détecté", "Not detected", "None") else self.detected_uc

        def run_sweet_verification():
            try:
                try:
                    df = verifier_presence_mapping_0p01s(
                        self.selected_file, mode=sweet_mode, uc_id=uc_id, myf=myf_choice
                    )
                except TypeError:
                    CONFIG["myf"] = myf_choice
                    df = verifier_presence_mapping_0p01s(self.selected_file, mode=sweet_mode, uc_id=uc_id)

                html = Path(f"verification_{sweet_mode}.html")
                html.write_text(df.to_html(index=False), encoding="utf-8")

                col = "Statut" if "Statut" in df.columns else ("Status" if "Status" in df.columns else None)
                ok = (df[col] == "OK").all() if col else False
                version = "400" if sweet_mode.endswith("400") else "500"
                label = f"SWEET {version} - {'OK' if ok else 'NOK'}"

                self.root.after(0, lambda: self._handle_sweet_result(html, label, ok))

            except Exception as e:
                self.root.after(0, lambda: self._handle_error(e))

        threading.Thread(target=run_sweet_verification, daemon=True).start()

    def _handle_sweet_result(self, html_path: Path, label: str, ok: bool):
        self._update_progress(100)
        self._update_status(label, "success" if ok else "warning")
        self._show_loading(False)

        try:
            webbrowser.open(html_path.resolve().as_uri())
        finally:
            self._show_toast(self.T["success"]) 

    def _handle_error(self, e: Exception):
        self._show_loading(False)
        self._update_progress(0)
        self._update_status("Erreur lors de l'analyse" if self.lang_var.get()=="fr" else "Error during analysis", "error")
        messagebox.showerror(self.T["file_err"], str(e))


def main():
    root = tk.Tk()
    app = EVAApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
