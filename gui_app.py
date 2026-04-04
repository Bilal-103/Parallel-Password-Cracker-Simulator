import os
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText


APP_TITLE = "Password Cracker Simulator - GUI"
DEFAULT_CHARSET = "abcdefghijklmnopqrstuvwxyz0123456789"


THEME = {
    "bg_top": "#10151f",
    "bg_bottom": "#05070b",
    "panel": "#121824",
    "panel_alt": "#1a2232",
    "border": "#2f3c56",
    "text": "#e9eef9",
    "muted": "#9fb0cf",
    "accent": "#42d6ff",
    "accent_soft": "#2a4e66",
    "danger": "#f36f7f",
    "output_bg": "#0b1018",
}


class PasswordSimulatorGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1120x760")
        self.root.minsize(980, 680)

        self.target_var = tk.StringVar()
        self.wordlist_var = tk.StringVar()
        self.max_len_var = tk.StringVar(value="5")
        self.charset_var = tk.StringVar(value=DEFAULT_CHARSET)
        self.limit_var = tk.StringVar(value="200000")
        self.proposal_var = tk.BooleanVar(value=True)
        self.mode_var = tk.StringVar(value="Run all")
        self.status_var = tk.StringVar(value="Ready")

        self.run_button = None
        self.output_box = None
        self.build_ui()

    def build_ui(self) -> None:
        self.root.configure(bg=THEME["bg_bottom"])
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        shell = tk.Frame(self.root, bg=THEME["bg_bottom"], padx=22, pady=20)
        shell.grid(row=0, column=0, sticky="nsew")

        header_card = tk.Frame(shell, bg=THEME["panel"], bd=0, highlightthickness=1, highlightbackground=THEME["border"])
        header_card.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 14))

        title = tk.Label(
            header_card,
            text="PARALLEL PASSWORD CRACKER SIMULATOR",
            bg=THEME["panel"],
            fg=THEME["text"],
            font=("Bahnschrift SemiBold", 22),
            padx=20,
            pady=14,
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            header_card,
            text="Window GUI of parallel password cracker",
            bg=THEME["panel"],
            fg=THEME["muted"],
            font=("Segoe UI", 11),
            padx=20,
            pady=14,
        )
        subtitle.pack(anchor="w")

        shell.columnconfigure(0, weight=2)
        shell.columnconfigure(1, weight=3)
        shell.rowconfigure(1, weight=1)

        form_card = tk.Frame(shell, bg=THEME["panel_alt"], bd=0, highlightthickness=1, highlightbackground=THEME["border"])
        form_card.grid(row=1, column=0, sticky="nsew", padx=(0, 10))

        output_card = tk.Frame(shell, bg=THEME["panel"], bd=0, highlightthickness=1, highlightbackground=THEME["border"])
        output_card.grid(row=1, column=1, sticky="nsew", padx=(10, 0))

        self._build_form(form_card)
        self._build_output(output_card)

        status_strip = tk.Frame(shell, bg=THEME["panel"], bd=0, highlightthickness=1, highlightbackground=THEME["border"])
        status_strip.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(14, 0))
        tk.Label(
            status_strip,
            textvariable=self.status_var,
            bg=THEME["panel"],
            fg=THEME["accent"],
            font=("Consolas", 10, "bold"),
            padx=14,
            pady=10,
        ).pack(anchor="w")

    def _build_form(self, parent: tk.Frame) -> None:
        parent.columnconfigure(1, weight=1)

        tk.Label(
            parent,
            text="Simulation Controls",
            bg=THEME["panel_alt"],
            fg=THEME["text"],
            font=("Bahnschrift", 16, "bold"),
            padx=14,
            pady=14,
        ).grid(row=0, column=0, columnspan=3, sticky="w")

        row = 1
        self._label(parent, "Target password", row)
        self._entry(parent, self.target_var, row)

        row += 1
        self._label(parent, "Wordlist path", row)
        wordlist_entry = self._entry(parent, self.wordlist_var, row)
        wordlist_entry.grid_configure(columnspan=1)
        browse_btn = tk.Button(
            parent,
            text="Browse",
            command=self.pick_wordlist,
            bg=THEME["accent_soft"],
            fg=THEME["text"],
            activebackground=THEME["accent"],
            activeforeground="#03131c",
            relief="flat",
            padx=10,
            pady=6,
            cursor="hand2",
        )
        browse_btn.grid(row=row, column=2, sticky="ew", padx=(8, 12), pady=6)

        row += 1
        self._label(parent, "Maximum password length", row)
        self._entry(parent, self.max_len_var, row)

        row += 1
        self._label(parent, "Character set", row)
        self._entry(parent, self.charset_var, row)

        row += 1
        self._label(parent, "Brute-force candidate limit", row)
        self._entry(parent, self.limit_var, row)

        row += 1
        proposal = tk.Checkbutton(
            parent,
            text="Proposal mode (pure brute-force candidate space)",
            variable=self.proposal_var,
            bg=THEME["panel_alt"],
            fg=THEME["muted"],
            activebackground=THEME["panel_alt"],
            activeforeground=THEME["text"],
            selectcolor=THEME["output_bg"],
            padx=8,
            pady=8,
            highlightthickness=0,
        )
        proposal.grid(row=row, column=1, columnspan=2, sticky="w", padx=(4, 12), pady=(8, 2))

        row += 1
        self._label(parent, "Execution mode", row)
        mode_combo = ttk.Combobox(
            parent,
            textvariable=self.mode_var,
            state="readonly",
            values=["Run all", "Sequential only", "OpenMP only", "MPI only", "CUDA only"],
            font=("Segoe UI", 10),
        )
        mode_combo.grid(row=row, column=1, columnspan=2, sticky="ew", padx=(4, 12), pady=6)

        row += 1
        action_wrap = tk.Frame(parent, bg=THEME["panel_alt"])
        action_wrap.grid(row=row, column=1, columnspan=2, sticky="ew", padx=(4, 12), pady=(14, 16))
        action_wrap.columnconfigure(0, weight=1)
        action_wrap.columnconfigure(1, weight=1)

        self.run_button = tk.Button(
            action_wrap,
            text="Run Simulation",
            command=self.run_simulation,
            bg=THEME["accent"],
            fg="#03131c",
            activebackground="#75e7ff",
            activeforeground="#03131c",
            relief="flat",
            font=("Segoe UI", 11, "bold"),
            padx=10,
            pady=8,
            cursor="hand2",
        )
        self.run_button.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        clear_btn = tk.Button(
            action_wrap,
            text="Clear Output",
            command=self.clear_output,
            bg="#29344a",
            fg=THEME["text"],
            activebackground="#3d4d6f",
            activeforeground=THEME["text"],
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=10,
            pady=8,
            cursor="hand2",
        )
        clear_btn.grid(row=0, column=1, sticky="ew", padx=(6, 0))

        for idx in range(row + 1):
            parent.rowconfigure(idx, weight=0)
        parent.rowconfigure(row + 1, weight=1)

    def _build_output(self, parent: tk.Frame) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)

        tk.Label(
            parent,
            text="Console Feed",
            bg=THEME["panel"],
            fg=THEME["text"],
            font=("Bahnschrift", 16, "bold"),
            padx=14,
            pady=14,
        ).grid(row=0, column=0, sticky="w")

        self.output_box = ScrolledText(
            parent,
            wrap="word",
            font=("Consolas", 10),
            bg=THEME["output_bg"],
            fg=THEME["text"],
            insertbackground=THEME["accent"],
            selectbackground="#33526b",
            relief="flat",
            padx=12,
            pady=10,
        )
        self.output_box.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.output_box.insert("end", "Boot sequence complete. Configure options and launch simulation.\n")
        self.output_box.configure(state="disabled")

    def _label(self, parent: tk.Frame, text: str, row: int) -> None:
        tk.Label(
            parent,
            text=text,
            bg=THEME["panel_alt"],
            fg=THEME["muted"],
            font=("Segoe UI", 10, "bold"),
            padx=12,
        ).grid(row=row, column=0, sticky="w", pady=6)

    def _entry(self, parent: tk.Frame, variable: tk.StringVar, row: int) -> tk.Entry:
        entry = tk.Entry(
            parent,
            textvariable=variable,
            bg="#0f1724",
            fg=THEME["text"],
            insertbackground=THEME["accent"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=THEME["border"],
            highlightcolor=THEME["accent"],
            font=("Segoe UI", 10),
        )
        entry.grid(row=row, column=1, columnspan=2, sticky="ew", padx=(4, 12), pady=6, ipady=6)
        return entry

    def pick_wordlist(self) -> None:
        selected = filedialog.askopenfilename(
            title="Select wordlist file",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        )
        if selected:
            self.wordlist_var.set(selected)

    def clear_output(self) -> None:
        self.output_box.configure(state="normal")
        self.output_box.delete("1.0", "end")
        self.output_box.configure(state="disabled")

    def append_output(self, text: str) -> None:
        self.output_box.configure(state="normal")
        self.output_box.insert("end", text)
        self.output_box.see("end")
        self.output_box.configure(state="disabled")

    def validate_inputs(self) -> bool:
        if not self.target_var.get().strip():
            messagebox.showerror("Validation Error", "Target password cannot be empty.")
            return False

        try:
            max_len = int(self.max_len_var.get().strip())
            if max_len < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Validation Error", "Maximum password length must be an integer >= 1.")
            return False

        if not self.charset_var.get():
            messagebox.showerror("Validation Error", "Character set cannot be empty.")
            return False

        try:
            limit = int(self.limit_var.get().strip())
            if limit < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Validation Error", "Brute-force candidate limit must be an integer >= 1.")
            return False

        wordlist = self.wordlist_var.get().strip()
        if wordlist and not os.path.exists(wordlist):
            messagebox.showerror("Validation Error", "Wordlist file path does not exist.")
            return False

        return True

    def run_simulation(self) -> None:
        if not self.validate_inputs():
            return

        exe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "password_sim.exe")
        if not os.path.exists(exe_path):
            messagebox.showerror(
                "Executable Not Found",
                "password_sim.exe not found in project folder. Build it first.\n\n"
                "Build command:\n"
                "C:\\msys64\\ucrt64\\bin\\g++.exe -std=c++17 -O2 main.cpp simulation.cpp utils.cpp parallel_openmp.cpp parallel_mpi.cpp gpu_kernel.cpp -o password_sim.exe",
            )
            return

        self.run_button.configure(state="disabled")
        self.status_var.set("Running simulation...")
        self.clear_output()

        thread = threading.Thread(target=self._execute_program, args=(exe_path,), daemon=True)
        thread.start()

    def _execute_program(self, exe_path: str) -> None:
        mode_map = {
            "Run all": "1",
            "Sequential only": "2",
            "OpenMP only": "3",
            "MPI only": "4",
            "CUDA only": "5",
        }

        proposal_choice = "y" if self.proposal_var.get() else "n"
        inputs = [
            self.target_var.get().strip(),
            self.wordlist_var.get().strip(),
            self.max_len_var.get().strip(),
            self.charset_var.get(),
            self.limit_var.get().strip(),
            proposal_choice,
            mode_map.get(self.mode_var.get(), "1"),
        ]
        input_blob = "\n".join(inputs) + "\n"

        try:
            completed = subprocess.run(
                [exe_path],
                input=input_blob,
                text=True,
                capture_output=True,
                cwd=os.path.dirname(exe_path),
                check=False,
            )

            output = completed.stdout
            if completed.stderr:
                output += "\n[stderr]\n" + completed.stderr

            def finish() -> None:
                self.append_output(output if output else "No output received.\n")
                self.append_output(f"\n\nProcess finished with exit code: {completed.returncode}\n")
                self.status_var.set("Completed")
                self.run_button.configure(state="normal")

            self.root.after(0, finish)
        except Exception as exc:  # pragma: no cover - defensive UI path
            def fail() -> None:
                self.append_output(f"Execution failed: {exc}\n")
                self.status_var.set("Failed")
                self.run_button.configure(state="normal")

            self.root.after(0, fail)


def main() -> None:
    root = tk.Tk()

    style = ttk.Style()
    if "vista" in style.theme_names():
        style.theme_use("vista")

    PasswordSimulatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
