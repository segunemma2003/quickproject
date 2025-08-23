import tkinter as tk
from tkinter import filedialog, ttk, messagebox

class ReportGeneratorUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("EVA Automatic Report Generator")
        self.geometry("600x400")
        self.configure(bg="#f5f6fa")

        # Language selection
        self.language_var = tk.StringVar(value="French")
        lang_frame = tk.LabelFrame(self, text="Language", bg="#f5f6fa")
        lang_frame.pack(padx=10, pady=5, fill="x")
        tk.Radiobutton(lang_frame, text="Français", variable=self.language_var, value="French", bg="#f5f6fa").pack(side="left", padx=10)
        tk.Radiobutton(lang_frame, text="English", variable=self.language_var, value="English", bg="#f5f6fa").pack(side="left", padx=10)

        # MDF file selection
        self.mdf_path = tk.StringVar()
        file_frame = tk.LabelFrame(self, text="MDF File", bg="#f5f6fa")
        file_frame.pack(padx=10, pady=5, fill="x")
        tk.Entry(file_frame, textvariable=self.mdf_path, width=50, state="readonly").pack(side="left", padx=5)
        tk.Button(file_frame, text="Browse", command=self.browse_mdf).pack(side="left", padx=5)

        # Sweet selection
        self.sweet_var = tk.StringVar(value="Sweet 400")
        sweet_frame = tk.LabelFrame(self, text="Sweet Version", bg="#f5f6fa")
        sweet_frame.pack(padx=10, pady=5, fill="x")
        ttk.Combobox(sweet_frame, textvariable=self.sweet_var, values=["Sweet 400", "Sweet 500"], state="readonly").pack(padx=10, pady=5)

        # My FX selection
        self.myfx_vars = [tk.BooleanVar() for _ in range(4)]
        myfx_frame = tk.LabelFrame(self, text="My FX", bg="#f5f6fa")
        myfx_frame.pack(padx=10, pady=5, fill="x")
        for i, var in enumerate(self.myfx_vars, start=2):
            tk.Checkbutton(myfx_frame, text=f"MyF{i}", variable=var, bg="#f5f6fa").pack(side="left", padx=10)

        # Analyze button
        tk.Button(self, text="Analyze", bg="#273c75", fg="white", font=("Arial", 12, "bold"), command=self.analyze).pack(pady=20)

        # Status label
        self.status_label = tk.Label(self, text="", bg="#f5f6fa", fg="#353b48", font=("Arial", 10))
        self.status_label.pack(pady=5)

    def browse_mdf(self):
        path = filedialog.askopenfilename(filetypes=[("MDF Files", "*.mf4 *.mdf"), ("All Files", "*.*")])
        if path:
            self.mdf_path.set(path)

    def analyze(self):
        if not self.mdf_path.get():
            messagebox.showwarning("Missing File", "Please select an MDF file.")
            return
        # Collect options
        language = self.language_var.get()
        sweet = self.sweet_var.get()
        myfx_selected = [f"MyF{i+2}" for i, v in enumerate(self.myfx_vars) if v.get()]
        # Call your backend logic here
        self.status_label.config(text="Generating report, please wait...")
        # TODO: Call your report generation function here
        # Example: generate_report(self.mdf_path.get(), sweet, myfx_selected, language)
        self.status_label.config(text="Report generated successfully!")

if __name__ == "__main__":
    app = ReportGeneratorUI()
    app.mainloop()