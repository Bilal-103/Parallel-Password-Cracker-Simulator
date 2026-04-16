import os
import random
import subprocess
import threading
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText


APP_TITLE = "Password Cracker Simulator - Cinematic Console"
DEFAULT_CHARSET = "abcdefghijklmnopqrstuvwxyz0123456789"
MATRIX_GLYPHS = "01ABCDEF@$#%&*"


THEME = {
    "base": "#010905",
    "base_alt": "#02120b",
    "grid": "#0a2d1f",
    "grid_soft": "#072016",
    "panel": "#02160f",
    "panel_alt": "#032117",
    "panel_deep": "#000f09",
    "line": "#0f5f3d",
    "text": "#d6ffe8",
    "muted": "#6fa78d",
    "accent": "#39ff9b",
    "accent_soft": "#22a96b",
    "warning": "#ffcb6b",
    "danger": "#ff5f73",
    "console": "#00110a",
    "console_text": "#b8ffd8",
}


class PasswordSimulatorGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1220x790")
        self.root.minsize(1020, 700)

        self.target_var = tk.StringVar()
        self.wordlist_var = tk.StringVar()
        self.max_len_var = tk.StringVar(value="5")
        self.charset_var = tk.StringVar(value=DEFAULT_CHARSET)
        self.limit_var = tk.StringVar(value="200000")
        self.proposal_var = tk.BooleanVar(value=True)
        self.mode_var = tk.StringVar(value="Run all")

        self.status_var = tk.StringVar(value="System idle | awaiting operator")
        self.clock_var = tk.StringVar(value="00:00:00")
        self.uplink_var = tk.StringVar(value="--")
        self.thermal_var = tk.StringVar(value="--")
        self.trace_var = tk.StringVar(value="STANDBY")

        self.run_button: tk.Button | None = None
        self.output_box: ScrolledText | None = None
        self.status_label: tk.Label | None = None
        self.signal_canvas: tk.Canvas | None = None
        self.bg_canvas: tk.Canvas | None = None

        self.is_running = False
        self.matrix_streams: list[dict[str, float]] = []

        self.build_ui()

    def build_ui(self) -> None:
        self.root.configure(bg=THEME["base"])
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self._configure_ttk_styles()

        self.bg_canvas = tk.Canvas(
            self.root,
            bg=THEME["base"],
            highlightthickness=0,
            bd=0,
        )
        self.bg_canvas.grid(row=0, column=0, sticky="nsew")
        self.bg_canvas.bind("<Configure>", self._on_canvas_resize)

        shell = tk.Frame(self.root, bg=THEME["base"], padx=24, pady=22)
        shell.grid(row=0, column=0, sticky="nsew")
        shell.columnconfigure(0, weight=2, minsize=360)
        shell.columnconfigure(1, weight=3, minsize=520)
        shell.rowconfigure(1, weight=1)

        header_card = tk.Frame(
            shell,
            bg=THEME["panel"],
            highlightthickness=1,
            highlightbackground=THEME["line"],
            padx=16,
            pady=12,
        )
        header_card.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        self._build_header(header_card)

        form_card = tk.Frame(
            shell,
            bg=THEME["panel_alt"],
            highlightthickness=1,
            highlightbackground=THEME["line"],
        )
        form_card.grid(row=1, column=0, sticky="nsew", padx=(0, 10))

        output_card = tk.Frame(
            shell,
            bg=THEME["panel"],
            highlightthickness=1,
            highlightbackground=THEME["line"],
        )
        output_card.grid(row=1, column=1, sticky="nsew", padx=(10, 0))

        self._build_form(form_card)
        self._build_output(output_card)

        status_strip = tk.Frame(
            shell,
            bg=THEME["panel"],
            highlightthickness=1,
            highlightbackground=THEME["line"],
        )
        status_strip.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(14, 0))

        indicator = tk.Canvas(
            status_strip,
            width=14,
            height=14,
            bg=THEME["panel"],
            highlightthickness=0,
            bd=0,
        )
        indicator.pack(side="left", padx=(14, 8), pady=10)
        indicator.create_oval(2, 2, 12, 12, fill=THEME["accent"], outline="")

        self.status_label = tk.Label(
            status_strip,
            textvariable=self.status_var,
            bg=THEME["panel"],
            fg=THEME["accent"],
            font=("Consolas", 10, "bold"),
            padx=4,
            pady=10,
            anchor="w",
        )
        self.status_label.pack(side="left", fill="x", expand=True)

        self._emit_boot_sequence()
        self._update_hud()
        self._animate_ambience()

    def _configure_ttk_styles(self) -> None:
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")

        style.configure(
            "Cinematic.TCombobox",
            foreground=THEME["text"],
            fieldbackground=THEME["panel_deep"],
            background=THEME["panel_deep"],
            font=("Consolas", 10),
        )
        style.map(
            "Cinematic.TCombobox",
            fieldbackground=[("readonly", THEME["panel_deep"])],
            foreground=[("readonly", THEME["text"])],
            selectbackground=[("readonly", THEME["panel_deep"])],
            selectforeground=[("readonly", THEME["text"])],
        )

        self.root.option_add("*TCombobox*Listbox*Background", THEME["panel_deep"])
        self.root.option_add("*TCombobox*Listbox*Foreground", THEME["text"])
        self.root.option_add("*TCombobox*Listbox*selectBackground", THEME["accent_soft"])
        self.root.option_add("*TCombobox*Listbox*selectForeground", "#00110a")

    def _build_header(self, parent: tk.Frame) -> None:
        parent.columnconfigure(0, weight=1)

        tk.Label(
            parent,
            text="PARALLEL PASSWORD CRACKER :: CINEMATIC COMMAND INTERFACE",
            bg=THEME["panel"],
            fg=THEME["accent"],
            font=("Bahnschrift SemiBold", 21),
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        tk.Label(
            parent,
            text="AUTHORIZED SIMULATION NODE | CPU + OPENMP + MPI + CUDA",
            bg=THEME["panel"],
            fg=THEME["muted"],
            font=("Consolas", 10),
            anchor="w",
            pady=6,
        ).grid(row=1, column=0, sticky="w")

        tk.Label(
            parent,
            textvariable=self.clock_var,
            bg=THEME["panel"],
            fg=THEME["text"],
            font=("Consolas", 14, "bold"),
            anchor="e",
        ).grid(row=0, column=1, rowspan=2, sticky="e", padx=(10, 0))

    def _build_form(self, parent: tk.Frame) -> None:
        parent.columnconfigure(1, weight=1)

        tk.Label(
            parent,
            text="OPERATOR CONTROLS",
            bg=THEME["panel_alt"],
            fg=THEME["text"],
            font=("Bahnschrift", 15, "bold"),
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
            text="SCAN",
            command=self.pick_wordlist,
            bg=THEME["accent_soft"],
            fg="#00110a",
            activebackground=THEME["accent"],
            activeforeground="#00110a",
            relief="flat",
            font=("Consolas", 10, "bold"),
            padx=12,
            pady=7,
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
            selectcolor=THEME["panel_deep"],
            font=("Consolas", 10),
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
            style="Cinematic.TCombobox",
            values=["Run all", "Sequential only", "OpenMP only", "MPI only", "CUDA only"],
            font=("Consolas", 10),
        )
        mode_combo.grid(row=row, column=1, columnspan=2, sticky="ew", padx=(4, 12), pady=6)

        row += 1
        action_wrap = tk.Frame(parent, bg=THEME["panel_alt"])
        action_wrap.grid(row=row, column=1, columnspan=2, sticky="ew", padx=(4, 12), pady=(14, 16))
        action_wrap.columnconfigure(0, weight=1)
        action_wrap.columnconfigure(1, weight=1)

        self.run_button = tk.Button(
            action_wrap,
            text="INITIATE RUN",
            command=self.run_simulation,
            bg=THEME["accent"],
            fg="#00110a",
            activebackground="#83ffc3",
            activeforeground="#00110a",
            relief="flat",
            font=("Consolas", 11, "bold"),
            padx=10,
            pady=8,
            cursor="hand2",
        )
        self.run_button.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        clear_btn = tk.Button(
            action_wrap,
            text="PURGE LOG",
            command=self.clear_output,
            bg="#214938",
            fg=THEME["text"],
            activebackground="#2e6a51",
            activeforeground=THEME["text"],
            relief="flat",
            font=("Consolas", 10, "bold"),
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
        parent.rowconfigure(2, weight=1)

        tk.Label(
            parent,
            text="LIVE CONSOLE FEED",
            bg=THEME["panel"],
            fg=THEME["text"],
            font=("Bahnschrift", 15, "bold"),
            padx=14,
            pady=12,
        ).grid(row=0, column=0, sticky="w")

        hud = tk.Frame(
            parent,
            bg=THEME["panel"],
            padx=12,
            pady=2,
        )
        hud.grid(row=1, column=0, sticky="ew")
        hud.columnconfigure(0, weight=1)
        hud.columnconfigure(1, weight=1)
        hud.columnconfigure(2, weight=1)
        hud.columnconfigure(3, weight=1)

        self._build_hud_chip(hud, "UPLINK", self.uplink_var, 0)
        self._build_hud_chip(hud, "CORE TEMP", self.thermal_var, 1)
        self._build_hud_chip(hud, "TRACE BUS", self.trace_var, 2)

        signal_wrap = tk.Frame(
            hud,
            bg=THEME["panel_deep"],
            highlightthickness=1,
            highlightbackground=THEME["line"],
            padx=6,
            pady=4,
        )
        signal_wrap.grid(row=0, column=3, sticky="ew", padx=(6, 0), pady=6)

        tk.Label(
            signal_wrap,
            text="SIGNAL",
            bg=THEME["panel_deep"],
            fg=THEME["muted"],
            font=("Consolas", 8, "bold"),
        ).pack(anchor="w")

        self.signal_canvas = tk.Canvas(
            signal_wrap,
            height=34,
            bg=THEME["panel_deep"],
            highlightthickness=0,
            bd=0,
        )
        self.signal_canvas.pack(fill="x", expand=True)

        self.output_box = ScrolledText(
            parent,
            wrap="word",
            font=("Consolas", 10),
            bg=THEME["console"],
            fg=THEME["console_text"],
            insertbackground=THEME["accent"],
            selectbackground="#1f5f44",
            relief="flat",
            padx=12,
            pady=10,
            borderwidth=0,
        )
        self.output_box.grid(row=2, column=0, sticky="nsew", padx=12, pady=(6, 12))
        self.output_box.configure(state="disabled")

    def _build_hud_chip(self, parent: tk.Frame, title: str, variable: tk.StringVar, column: int) -> None:
        chip = tk.Frame(
            parent,
            bg=THEME["panel_deep"],
            highlightthickness=1,
            highlightbackground=THEME["line"],
            padx=8,
            pady=6,
        )
        chip.grid(row=0, column=column, sticky="ew", padx=(0 if column == 0 else 6, 0), pady=6)

        tk.Label(
            chip,
            text=title,
            bg=THEME["panel_deep"],
            fg=THEME["muted"],
            font=("Consolas", 8, "bold"),
            anchor="w",
        ).pack(anchor="w")

        tk.Label(
            chip,
            textvariable=variable,
            bg=THEME["panel_deep"],
            fg=THEME["accent"],
            font=("Consolas", 11, "bold"),
            anchor="w",
            pady=2,
        ).pack(anchor="w")

    def _label(self, parent: tk.Frame, text: str, row: int) -> None:
        tk.Label(
            parent,
            text=text,
            bg=THEME["panel_alt"],
            fg=THEME["muted"],
            font=("Consolas", 10, "bold"),
            padx=12,
        ).grid(row=row, column=0, sticky="w", pady=6)

    def _entry(self, parent: tk.Frame, variable: tk.StringVar, row: int) -> tk.Entry:
        entry = tk.Entry(
            parent,
            textvariable=variable,
            bg=THEME["panel_deep"],
            fg=THEME["text"],
            insertbackground=THEME["accent"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=THEME["line"],
            highlightcolor=THEME["accent"],
            font=("Consolas", 10),
        )
        entry.grid(row=row, column=1, columnspan=2, sticky="ew", padx=(4, 12), pady=6, ipady=6)
        return entry

    def _on_canvas_resize(self, event: tk.Event) -> None:
        self._draw_background(event.width, event.height)

        target_streams = max(16, event.width // 65)
        if len(self.matrix_streams) != target_streams:
            self._build_matrix_streams(event.width, event.height, target_streams)

    def _draw_background(self, width: int, height: int) -> None:
        if self.bg_canvas is None:
            return

        canvas = self.bg_canvas
        canvas.delete("bg")

        split = int(height * 0.4)
        canvas.create_rectangle(0, 0, width, split, fill=THEME["base_alt"], outline="", tags="bg")
        canvas.create_rectangle(0, split, width, height, fill=THEME["base"], outline="", tags="bg")

        for x in range(0, width, 48):
            shade = THEME["grid"] if x % 192 == 0 else THEME["grid_soft"]
            canvas.create_line(x, 0, x, height, fill=shade, width=1, tags="bg")

        for y in range(0, height, 48):
            shade = THEME["grid"] if y % 192 == 0 else THEME["grid_soft"]
            canvas.create_line(0, y, width, y, fill=shade, width=1, tags="bg")

        margin = 12
        canvas.create_rectangle(
            margin,
            margin,
            max(margin + 2, width - margin),
            max(margin + 2, height - margin),
            outline=THEME["grid"],
            width=2,
            tags="bg",
        )

    def _build_matrix_streams(self, width: int, height: int, count: int) -> None:
        safe_width = max(width, 320)
        safe_height = max(height, 300)
        self.matrix_streams = []

        for _ in range(count):
            self.matrix_streams.append(
                {
                    "x": float(random.randint(20, safe_width - 20)),
                    "y": random.uniform(-safe_height, 0),
                    "speed": random.uniform(2.4, 7.2),
                    "length": float(random.randint(8, 16)),
                }
            )

    def _animate_ambience(self) -> None:
        if self.bg_canvas is None:
            return

        canvas = self.bg_canvas
        width = max(canvas.winfo_width(), 320)
        height = max(canvas.winfo_height(), 280)

        if not self.matrix_streams:
            self._build_matrix_streams(width, height, max(16, width // 65))

        canvas.delete("matrix")

        for stream in self.matrix_streams:
            stream["y"] += stream["speed"]
            x = stream["x"]
            y = stream["y"]
            length = int(stream["length"])

            if y - (length * 16) > height:
                stream["y"] = random.uniform(-250, -24)
                stream["x"] = float(random.randint(20, max(20, width - 20)))

            for idx in range(length):
                draw_y = y - (idx * 16)
                if draw_y < -18 or draw_y > height + 18:
                    continue

                if idx == 0:
                    tone = "#d9ffe8"
                elif idx < 4:
                    tone = THEME["accent"]
                else:
                    tone = "#1a7249"

                canvas.create_text(
                    x,
                    draw_y,
                    text=random.choice(MATRIX_GLYPHS),
                    fill=tone,
                    font=("Consolas", 11, "bold"),
                    tags="matrix",
                )

        try:
            self.root.after(90, self._animate_ambience)
        except tk.TclError:
            return

    def _update_hud(self) -> None:
        self.clock_var.set(datetime.now().strftime("%H:%M:%S"))

        if self.is_running:
            self.uplink_var.set(f"{random.randint(93, 99)}%")
            self.thermal_var.set(f"{random.randint(62, 78)} C")
            self.trace_var.set("TRACE ACTIVE")
        else:
            self.uplink_var.set(f"{random.randint(75, 92)}%")
            self.thermal_var.set(f"{random.randint(47, 61)} C")
            self.trace_var.set("TRACE STANDBY")

        self._draw_signal_bars()

        try:
            self.root.after(700, self._update_hud)
        except tk.TclError:
            return

    def _draw_signal_bars(self) -> None:
        if self.signal_canvas is None:
            return

        canvas = self.signal_canvas
        canvas.delete("bars")

        width = max(canvas.winfo_width(), 120)
        height = max(canvas.winfo_height(), 26)
        bars = 15
        bar_width = max(4, (width - 16) // bars)

        for idx in range(bars):
            strength = random.randint(6, max(10, height - 3))
            x0 = 8 + (idx * bar_width)
            x1 = x0 + max(2, bar_width - 2)
            y0 = height - strength
            y1 = height - 2
            color = THEME["accent"] if strength > int(height * 0.65) else THEME["accent_soft"]
            canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="", tags="bars")

    def _set_status(self, message: str, color: str) -> None:
        self.status_var.set(message)
        if self.status_label is not None:
            self.status_label.configure(fg=color)

    def _emit_boot_sequence(self) -> None:
        self.append_output("[BOOT] Visual shell online.\n")
        self.append_output("[BOOT] Link established with parallel compute modules.\n")
        self.append_output("[INFO] Input attack parameters and launch with INITIATE RUN.\n\n")

    def pick_wordlist(self) -> None:
        selected = filedialog.askopenfilename(
            title="Select wordlist file",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        )
        if selected:
            self.wordlist_var.set(selected)

    def clear_output(self) -> None:
        if self.output_box is None:
            return

        self.output_box.configure(state="normal")
        self.output_box.delete("1.0", "end")
        self.output_box.configure(state="disabled")

    def append_output(self, text: str) -> None:
        if self.output_box is None:
            return

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

        if self.run_button is not None:
            self.run_button.configure(state="disabled", text="EXECUTING...")

        self.is_running = True
        self._set_status("Live run in progress | attack matrix engaged", THEME["warning"])
        self.clear_output()

        self.append_output("[CMD] Operator command accepted.\n")
        self.append_output(f"[CFG] Target: {self.target_var.get().strip()}\n")
        self.append_output(f"[CFG] Mode: {self.mode_var.get()}\n")
        self.append_output(f"[CFG] Candidate mode: {'Proposal' if self.proposal_var.get() else 'Smart'}\n")
        self.append_output("[EXEC] Spawning simulator process...\n\n")

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
                self.append_output(f"\n\n[EXIT] Process finished with exit code: {completed.returncode}\n")

                self.is_running = False
                if completed.returncode == 0:
                    self._set_status("Run complete | node returned to standby", THEME["accent"])
                else:
                    self._set_status("Run completed with errors | inspect console output", THEME["danger"])

                if self.run_button is not None:
                    self.run_button.configure(state="normal", text="INITIATE RUN")

            self.root.after(0, finish)
        except Exception as exc:  # pragma: no cover - defensive UI path
            def fail() -> None:
                self.append_output(f"Execution failed: {exc}\n")
                self.is_running = False
                self._set_status("Execution failure detected", THEME["danger"])
                if self.run_button is not None:
                    self.run_button.configure(state="normal", text="INITIATE RUN")

            self.root.after(0, fail)


def main() -> None:
    root = tk.Tk()
    PasswordSimulatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()