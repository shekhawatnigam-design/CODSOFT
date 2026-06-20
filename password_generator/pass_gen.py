import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random
import string
import datetime



# Core password logic


AMBIGUOUS_CHARS = "lI1O0"

# Simple consonant/vowel pattern generator for pronounceable passwords
VOWELS = "aeiou"
CONSONANTS = "".join(c for c in string.ascii_lowercase if c not in VOWELS)


def generate_pronounceable(length):
    
    chars = []
    use_consonant = random.choice([True, False])
    while len(chars) < length:
        if use_consonant:
            chars.append(random.choice(CONSONANTS))
        else:
            chars.append(random.choice(VOWELS))
        use_consonant = not use_consonant

    # Capitalize a random letter and append a couple digits for strength
    idx = random.randrange(len(chars))
    chars[idx] = chars[idx].upper()
    word = "".join(chars)

    # Pad/trim with digits to hit exact length while keeping it readable
    if length > 4:
        digits = "".join(random.choice(string.digits) for _ in range(2))
        word = (word[: max(length - 2, 1)] + digits)[:length]
    return word[:length]


def generate_password(length, use_upper, use_lower, use_digits, use_symbols,
                       custom_symbols, exclude_ambiguous, exclude_chars,
                       pronounceable=False):
    """Generate a single random password based on selected options."""
    if pronounceable:
        pw = generate_pronounceable(length)
        if exclude_chars:
            # Regenerate if it contains excluded chars (best effort, capped tries)
            tries = 0
            while any(c in exclude_chars for c in pw) and tries < 20:
                pw = generate_pronounceable(length)
                tries += 1
        return pw

    char_pool = ""
    guaranteed_chars = []

    upper_set = string.ascii_uppercase
    lower_set = string.ascii_lowercase
    digit_set = string.digits
    symbol_set = custom_symbols if custom_symbols else "!@#$%^&*()_+-=[]{}|;:,.<>?"

    if exclude_ambiguous:
        upper_set = "".join(c for c in upper_set if c not in AMBIGUOUS_CHARS)
        lower_set = "".join(c for c in lower_set if c not in AMBIGUOUS_CHARS)
        digit_set = "".join(c for c in digit_set if c not in AMBIGUOUS_CHARS)

    if exclude_chars:
        upper_set = "".join(c for c in upper_set if c not in exclude_chars)
        lower_set = "".join(c for c in lower_set if c not in exclude_chars)
        digit_set = "".join(c for c in digit_set if c not in exclude_chars)
        symbol_set = "".join(c for c in symbol_set if c not in exclude_chars)

    if use_upper and upper_set:
        char_pool += upper_set
        guaranteed_chars.append(random.choice(upper_set))
    if use_lower and lower_set:
        char_pool += lower_set
        guaranteed_chars.append(random.choice(lower_set))
    if use_digits and digit_set:
        char_pool += digit_set
        guaranteed_chars.append(random.choice(digit_set))
    if use_symbols and symbol_set:
        char_pool += symbol_set
        guaranteed_chars.append(random.choice(symbol_set))

    if not char_pool:
        return None

    remaining_length = max(length - len(guaranteed_chars), 0)
    password_chars = guaranteed_chars + [
        random.choice(char_pool) for _ in range(remaining_length)
    ]

    random.shuffle(password_chars)
    return "".join(password_chars[:length])


def evaluate_strength(password, use_upper, use_lower, use_digits, use_symbols):
    """Return (label, color, score 0-100) describing password strength."""
    if not password:
        return "—", "#888888", 0

    variety_count = sum([use_upper, use_lower, use_digits, use_symbols]) or 1
    length = len(password)

    score = 0
    if length >= 8:
        score += 1
    if length >= 12:
        score += 1
    if length >= 16:
        score += 1
    if length >= 20:
        score += 1
    score += variety_count

    percent = min(int(score / 8 * 100), 100)

    if score <= 2:
        return "Weak", "#e74c3c", max(percent, 15)
    elif score <= 4:
        return "Medium", "#f39c12", percent
    elif score <= 6:
        return "Strong", "#2ecc71", percent
    else:
        return "Very Strong", "#27ae60", 100



# Theme palettes


THEMES = {
    "dark": {
        "bg": "#0a0e14",
        "card": "#11161f",
        "entry_bg": "#161d29",
        "text": "#e6edf3",
        "subtext": "#7d8a9c",
        "accent": "#00e5c7",
        "accent_hover": "#00c2a8",
        "track": "#1c2433",
        "border": "#1f2a3a",
        "danger": "#ff5566",
    },
    "light": {
        "bg": "#eef1f6",
        "card": "#ffffff",
        "entry_bg": "#eef2f8",
        "text": "#0d1b2a",
        "subtext": "#5c6b7a",
        "accent": "#00a896",
        "accent_hover": "#00897b",
        "track": "#dde4ee",
        "border": "#d8dee8",
        "danger": "#e5484d",
    },
}

MONO_FONT = "Consolas"

# GUI Application


class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🔐 Secure Password Generator")
        self.root.geometry("500x760")
        self.root.minsize(460, 680)

        self.theme_name = "dark"
        self.theme = THEMES[self.theme_name]

        self.generated_passwords = []
        self.history = []  # list of dicts: {password, timestamp}

        self.root.configure(bg=self.theme["bg"])
        self._build_ui()
        self._bind_shortcuts ()

    # UI construction
    
    def _build_ui(self):
        t = self.theme

        # ----- Header with theme toggle -----
        self.header = tk.Frame(self.root, bg=t["bg"])
        self.header.pack(fill="x", pady=(20, 5))

        title_row = tk.Frame(self.header, bg=t["bg"])
        title_row.pack(fill="x", padx=20)

        title_left = tk.Frame(title_row, bg=t["bg"])
        title_left.pack(side="left")

        self.status_dot = tk.Label(
            title_left, text="●", font=(MONO_FONT, 12),
            bg=t["bg"], fg=t["accent"]
        )
        self.status_dot.pack(side="left", padx=(0, 6))

        self.title_label = tk.Label(
            title_left, text="PASSWORD_GEN", font=(MONO_FONT, 18, "bold"),
            bg=t["bg"], fg=t["text"]
        )
        self.title_label.pack(side="left")

        self.title_suffix = tk.Label(
            title_left, text=" v2.0", font=(MONO_FONT, 10),
            bg=t["bg"], fg=t["accent"]
        )
        self.title_suffix.pack(side="left", anchor="s", pady=(0, 3))

        self.theme_btn = tk.Button(
            title_row, text="☀ LIGHT" if self.theme_name == "dark" else "● DARK",
            font=(MONO_FONT, 9, "bold"), bd=1, relief="flat", cursor="hand2",
            bg=t["card"], fg=t["accent"], activebackground=t["entry_bg"],
            activeforeground=t["accent"],
            highlightbackground=t["border"], highlightthickness=1,
            padx=10, pady=4,
            command=self._toggle_theme
        )
        self.theme_btn.pack(side="right")

        self.subtitle_label = tk.Label(
            self.header, text="$ generate --secure --random",
            font=(MONO_FONT, 10), bg=t["bg"], fg=t["subtext"]
        )
        self.subtitle_label.pack(padx=20, anchor="w", pady=(4, 0))

        # ----- Notebook (tabs) -----
        style = ttk.Style()
        style.theme_use("default")
        self._style_notebook(style)

        self.notebook = ttk.Notebook(self.root, style="Custom.TNotebook")
        self.notebook.pack(fill="both", expand=True, padx=15, pady=10)

        self.gen_tab = tk.Frame(self.notebook, bg=t["bg"])
        self.history_tab = tk.Frame(self.notebook, bg=t["bg"])

        self.notebook.add(self.gen_tab, text="  ⚡ Generator  ")
        self.notebook.add(self.history_tab, text="  🕘 History  ")

        self._build_generator_tab(self.gen_tab)
        self._build_history_tab(self.history_tab)

        # ----- Toast (floating notification) -----
        self.toast = tk.Label(
            self.root, text="", font=(MONO_FONT, 10, "bold"),
            bg=t["accent"], fg="#0a0e14", padx=14, pady=8
        )
        # placed dynamically via place(), hidden by default

    def _style_notebook(self, style):
        t = self.theme
        style.configure("Custom.TNotebook", background=t["bg"], borderwidth=0)
        style.configure(
            "Custom.TNotebook.Tab",
            background=t["card"], foreground=t["subtext"],
            padding=[14, 9], font=(MONO_FONT, 10, "bold"), borderwidth=0
        )
        style.map(
            "Custom.TNotebook.Tab",
            background=[("selected", t["accent"])],
            foreground=[("selected", "#0a0e14")],
        )
        style.configure("Custom.Vertical.TScrollbar", background=t["entry_bg"],
                         troughcolor=t["bg"], bordercolor=t["bg"],
                         arrowcolor=t["accent"])

    
    # Generator tab
    
    def _build_generator_tab(self, parent):
        t = self.theme

        card = tk.Frame(
            parent, bg=t["card"], highlightbackground=t["border"],
            highlightthickness=1, bd=0
        )
        card.pack(fill="both", expand=True, pady=(0, 5))
        self.gen_card = card

        # ----- Length (slider + manual entry) -----
        length_frame = tk.Frame(card, bg=t["card"])
        length_frame.pack(fill="x", padx=20, pady=(20, 5))

        tk.Label(
            length_frame, text="Password Length:",
            font=(MONO_FONT, 11, "bold"), bg=t["card"], fg=t["text"]
        ).pack(side="left")

        self.length_var = tk.IntVar(value=12)
        self.length_entry = tk.Entry(
            length_frame, textvariable=self.length_var, width=4,
            font=(MONO_FONT, 11, "bold"), bg=t["entry_bg"], fg=t["accent"],
            relief="flat", justify="center", insertbackground=t["text"]
        )
        self.length_entry.pack(side="right")
        self.length_entry.bind("<KeyRelease>", self._on_length_entry_change)

        self.length_slider = tk.Scale(
            card, from_=4, to=64, orient="horizontal",
            variable=self.length_var, bg=t["card"], fg=t["text"],
            troughcolor=t["track"], highlightthickness=0, bd=0,
            activebackground=t["accent"], font=(MONO_FONT, 9),
            showvalue=False, command=lambda e: self._on_settings_change()
        )
        self.length_slider.pack(fill="x", padx=20, pady=(0, 12))

        # ----- Mode toggle: Standard vs Pronounceable -----
        mode_frame = tk.Frame(card, bg=t["card"])
        mode_frame.pack(fill="x", padx=20, pady=(0, 10))

        tk.Label(
            mode_frame, text="Mode:", font=(MONO_FONT, 10, "bold"),
            bg=t["card"], fg=t["text"]
        ).pack(side="left")

        self.mode_var = tk.StringVar(value="standard")
        self.standard_radio = tk.Radiobutton(
            mode_frame, text="Standard (Random)", variable=self.mode_var,
            value="standard", font=(MONO_FONT, 9), bg=t["card"], fg=t["text"],
            selectcolor=t["entry_bg"], activebackground=t["card"],
            activeforeground=t["text"], command=self._on_mode_change
        )
        self.standard_radio.pack(side="left", padx=(10, 0))

        self.pronounceable_radio = tk.Radiobutton(
            mode_frame, text="Pronounceable", variable=self.mode_var,
            value="pronounceable", font=(MONO_FONT, 9), bg=t["card"], fg=t["text"],
            selectcolor=t["entry_bg"], activebackground=t["card"],
            activeforeground=t["text"], command=self._on_mode_change
        )
        self.pronounceable_radio.pack(side="left", padx=(10, 0))

        # ----- Character type checkboxes -----
        self.options_frame = tk.Frame(card, bg=t["card"])
        self.options_frame.pack(fill="x", padx=20, pady=(0, 5))

        self.use_upper = tk.BooleanVar(value=True)
        self.use_lower = tk.BooleanVar(value=True)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=True)
        self.exclude_ambiguous = tk.BooleanVar(value=False)

        self.checkbuttons = []
        checks = [
            ("Uppercase Letters (A-Z)", self.use_upper),
            ("Lowercase Letters (a-z)", self.use_lower),
            ("Numbers (0-9)", self.use_digits),
            ("Special Characters (!@#$%)", self.use_symbols),
        ]
        for text, var in checks:
            cb = tk.Checkbutton(
                self.options_frame, text=text, variable=var,
                font=(MONO_FONT, 10), bg=t["card"], fg=t["text"],
                selectcolor=t["entry_bg"], activebackground=t["card"],
                activeforeground=t["text"], anchor="w",
                command=self._on_settings_change
            )
            cb.pack(fill="x", pady=2)
            self.checkbuttons.append(cb)

        cb_ambiguous = tk.Checkbutton(
            self.options_frame, text="Exclude ambiguous characters (l, 1, I, O, 0)",
            variable=self.exclude_ambiguous, font=(MONO_FONT, 10),
            bg=t["card"], fg=t["text"], selectcolor=t["entry_bg"],
            activebackground=t["card"], activeforeground=t["text"],
            anchor="w", command=self._on_settings_change
        )
        cb_ambiguous.pack(fill="x", pady=2)
        self.checkbuttons.append(cb_ambiguous)

        # ----- Custom exclude characters -----
        exclude_frame = tk.Frame(card, bg=t["card"])
        exclude_frame.pack(fill="x", padx=20, pady=(8, 5))

        tk.Label(
            exclude_frame, text="Exclude specific characters:",
            font=(MONO_FONT, 9), bg=t["card"], fg=t["subtext"]
        ).pack(anchor="w")

        self.exclude_var = tk.StringVar(value="")
        self.exclude_entry = tk.Entry(
            exclude_frame, textvariable=self.exclude_var,
            font=("Consolas", 10), bg=t["entry_bg"], fg=t["text"],
            relief="flat", insertbackground=t["text"]
        )
        self.exclude_entry.pack(fill="x", ipady=4, pady=(2, 0))
        self.exclude_entry.bind("<KeyRelease>", lambda e: None)

        # ----- Number of passwords -----
        count_frame = tk.Frame(card, bg=t["card"])
        count_frame.pack(fill="x", padx=20, pady=(12, 5))

        tk.Label(
            count_frame, text="How many passwords?",
            font=(MONO_FONT, 10), bg=t["card"], fg=t["text"]
        ).pack(side="left")

        self.count_var = tk.IntVar(value=1)
        self.count_spin = tk.Spinbox(
            count_frame, from_=1, to=10, width=4,
            textvariable=self.count_var, font=(MONO_FONT, 10),
            bg=t["entry_bg"], fg=t["text"], justify="center", relief="flat"
        )
        self.count_spin.pack(side="right")

        # ----- Generate button -----
        self.generate_btn = tk.Button(
            card, text="⚡ GENERATE PASSWORD   (Ctrl+G)",
            font=(MONO_FONT, 11, "bold"), bg=t["accent"], fg="#0a0e14",
            activebackground=t["accent_hover"], activeforeground="#0a0e14",
            relief="flat", cursor="hand2", bd=0, command=self._on_generate
        )
        self.generate_btn.pack(fill="x", padx=20, pady=(12, 10), ipady=8)
        self.generate_btn.bind("<Enter>", lambda e: self.generate_btn.config(bg=t["accent_hover"]))
        self.generate_btn.bind("<Leave>", lambda e: self.generate_btn.config(bg=t["accent"]))

        # ----- Output box (terminal-style with inline copy button) -----
        self.output_label = tk.Label(
            card, text="OUTPUT://", font=(MONO_FONT, 10, "bold"),
            bg=t["card"], fg=t["accent"], anchor="w"
        )
        self.output_label.pack(fill="x", padx=20, pady=(0, 4))

        output_row = tk.Frame(
            card, bg=t["entry_bg"], highlightbackground=t["border"],
            highlightthickness=1
        )
        output_row.pack(fill="x", padx=20, pady=(0, 10))
        self.output_row = output_row

        self.output_box = tk.Text(
            output_row, height=5, font=(MONO_FONT, 12),
            bg=t["entry_bg"], fg=t["accent"], relief="flat",
            wrap="word", state="disabled", padx=12, pady=10,
            highlightthickness=0, bd=0
        )
        self.output_box.pack(side="left", fill="both", expand=True)

        self.copy_icon_btn = tk.Button(
            output_row, text="⧉", font=(MONO_FONT, 16, "bold"),
            bg=t["accent"], fg="#0a0e14",
            activebackground=t["accent_hover"], activeforeground="#0a0e14",
            relief="flat", cursor="hand2", bd=0, width=3,
            command=self._on_copy
        )
        self.copy_icon_btn.pack(side="right", fill="y")
        self.copy_icon_btn.bind("<Enter>", lambda e: self.copy_icon_btn.config(bg=t["accent_hover"]))
        self.copy_icon_btn.bind("<Leave>", lambda e: self.copy_icon_btn.config(bg=t["accent"]))

        # ----- Strength meter -----
        strength_label_row = tk.Frame(card, bg=t["card"])
        strength_label_row.pack(fill="x", padx=20)

        tk.Label(
            strength_label_row, text="STRENGTH:",
            font=(MONO_FONT, 10, "bold"), bg=t["card"], fg=t["subtext"]
        ).pack(side="left")

        self.strength_text = tk.Label(
            strength_label_row, text="—", font=(MONO_FONT, 10, "bold"),
            bg=t["card"], fg=t["subtext"]
        )
        self.strength_text.pack(side="left", padx=(6, 0))

        self.strength_canvas = tk.Canvas(
            card, height=8, bg=t["track"], highlightthickness=0
        )
        self.strength_canvas.pack(fill="x", padx=20, pady=(6, 14))
        self.strength_bar = None

        # ----- Action buttons row -----
        action_row = tk.Frame(card, bg=t["card"])
        action_row.pack(fill="x", padx=20, pady=(0, 20))

        self.copy_btn = tk.Button(
            action_row, text="⧉  COPY PASSWORD", font=(MONO_FONT, 10, "bold"),
            bg=t["accent"], fg="#0a0e14",
            activebackground=t["accent_hover"], activeforeground="#0a0e14",
            relief="flat", cursor="hand2", bd=0,
            command=self._on_copy
        )
        self.copy_btn.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 5))

        self.save_btn = tk.Button(
            action_row, text="💾 SAVE", font=(MONO_FONT, 10, "bold"),
            bg=t["entry_bg"], fg=t["text"],
            activebackground=t["track"], activeforeground=t["text"],
            relief="flat", cursor="hand2", bd=1,
            highlightbackground=t["border"], highlightthickness=1,
            command=self._on_save
        )
        self.save_btn.pack(side="left", fill="x", expand=True, ipady=8, padx=(5, 0))

        self.copy_btn.bind("<Enter>", lambda e: self.copy_btn.config(bg=t["accent_hover"]))
        self.copy_btn.bind("<Leave>", lambda e: self.copy_btn.config(bg=t["accent"]))
        self.save_btn.bind("<Enter>", lambda e: self.save_btn.config(bg=t["track"]))
        self.save_btn.bind("<Leave>", lambda e: self.save_btn.config(bg=t["entry_bg"]))

        # Footer
        self.footer_label = tk.Label(
            parent, text="CodSoft Internship Project • Built with Python & Tkinter",
            font=(MONO_FONT, 8), bg=t["bg"], fg=t["subtext"]
        )
        self.footer_label.pack(pady=(2, 6))

    
    # History tab
    
    def _build_history_tab(self, parent):
        t = self.theme

        info = tk.Label(
            parent, text="Click any password below to copy it again.",
            font=(MONO_FONT, 9), bg=t["bg"], fg=t["subtext"]
        )
        info.pack(anchor="w", padx=15, pady=(10, 5))
        self.history_info_label = info

        list_container = tk.Frame(parent, bg=t["card"])
        list_container.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        self.history_card = list_container

        canvas = tk.Canvas(list_container, bg=t["card"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=canvas.yview)
        self.history_inner = tk.Frame(canvas, bg=t["card"])

        self.history_inner.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.history_inner, anchor="nw", width=440)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=5)
        scrollbar.pack(side="right", fill="y")
        self.history_canvas = canvas

        clear_btn = tk.Button(
            parent, text="🗑️ Clear History", font=(MONO_FONT, 10, "bold"),
            bg=t["entry_bg"], fg=t["text"], activebackground=t["track"],
            activeforeground=t["text"], relief="flat", cursor="hand2",
            command=self._clear_history
        )
        clear_btn.pack(fill="x", padx=15, pady=(0, 15), ipady=6)
        self.clear_history_btn = clear_btn

        self._render_history()

    def _render_history(self):
        t = self.theme
        for widget in self.history_inner.winfo_children():
            widget.destroy()

        if not self.history:
            tk.Label(
                self.history_inner, text="No passwords generated yet.",
                font=(MONO_FONT, 10), bg=t["card"], fg=t["subtext"]
            ).pack(pady=20)
            return

        for entry in reversed(self.history):
            row = tk.Frame(self.history_inner, bg=t["entry_bg"])
            row.pack(fill="x", padx=8, pady=4)

            pw_label = tk.Label(
                row, text=entry["password"], font=("Consolas", 11),
                bg=t["entry_bg"], fg=t["accent"], anchor="w"
            )
            pw_label.pack(side="left", fill="x", expand=True, padx=10, pady=8)

            time_label = tk.Label(
                row, text=entry["timestamp"], font=(MONO_FONT, 8),
                bg=t["entry_bg"], fg=t["subtext"]
            )
            time_label.pack(side="right", padx=10)

            for widget in (row, pw_label, time_label):
                widget.bind(
                    "<Button-1>",
                    lambda e, pw=entry["password"]: self._copy_text(pw, "History password copied!")
                )
                widget.config(cursor="hand2")

    def _clear_history(self):
        if not self.history:
            return
        if messagebox.askyesno("Clear History", "Remove all saved password history?"):
            self.history.clear()
            self._render_history()

    
    # Theme toggle
    
    def _toggle_theme(self):
        self.theme_name = "light" if self.theme_name == "dark" else "dark"
        self.theme = THEMES[self.theme_name]

        # Rebuild UI in place with new theme colors
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.configure(bg=self.theme["bg"])
        self._build_ui()
        self._restore_state_after_theme_switch()

    def _restore_state_after_theme_switch(self):
        # Re-render password output & history with preserved data
        if self.generated_passwords:
            self.output_box.config(state="normal")
            self.output_box.delete("1.0", "end")
            self.output_box.insert("1.0", "\n".join(self.generated_passwords))
            self.output_box.config(state="disabled")
            self._update_strength(self.generated_passwords[-1])
        self._render_history()

    
    # Settings/event handlers
    
    def _on_mode_change(self):
        is_pronounceable = self.mode_var.get() == "pronounceable"
        state = "disabled" if is_pronounceable else "normal"
        for cb in self.checkbuttons:
            cb.config(state=state)
        self._on_settings_change()

    def _on_length_entry_change(self, event=None):
        value = self.length_entry.get()
        if value.isdigit():
            n = int(value)
            if 4 <= n <= 64:
                self.length_slider.set(n)

    def _on_settings_change(self):
        if self.generated_passwords:
            self._update_strength(self.generated_passwords[-1])

    def _on_generate(self):
        length = self.length_var.get()
        use_upper = self.use_upper.get()
        use_lower = self.use_lower.get()
        use_digits = self.use_digits.get()
        use_symbols = self.use_symbols.get()
        count = self.count_var.get()
        pronounceable = self.mode_var.get() == "pronounceable"
        exclude_chars = self.exclude_var.get()

        if not pronounceable and not any([use_upper, use_lower, use_digits, use_symbols]):
            messagebox.showwarning(
                "No Character Type Selected",
                "Please select at least one character type "
                "(uppercase, lowercase, numbers, or symbols)."
            )
            return

        if length < 4:
            messagebox.showwarning("Length Too Short", "Please choose a length of at least 4.")
            return

        self.generated_passwords = []
        for _ in range(count):
            pw = generate_password(
                length, use_upper, use_lower, use_digits, use_symbols,
                custom_symbols=None, exclude_ambiguous=self.exclude_ambiguous.get(),
                exclude_chars=exclude_chars, pronounceable=pronounceable
            )
            if pw:
                self.generated_passwords.append(pw)
                self.history.append({
                    "password": pw,
                    "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
                })

        self.history = self.history[-20:]  # keep last 20

        self.output_box.config(state="normal")
        self.output_box.delete("1.0", "end")
        self.output_box.insert("1.0", "\n".join(self.generated_passwords))
        self.output_box.config(state="disabled")

        if self.generated_passwords:
            self._update_strength(self.generated_passwords[-1])
            self._flash_output()

        self._render_history()

    def _flash_output(self):
        """Brief highlight flash on the output box to confirm generation."""
        original = self.output_box.cget("bg")
        flash_color = self.theme["accent"]
        self.output_box.config(bg=flash_color)
        self.root.after(120, lambda: self.output_box.config(bg=original))

    def _update_strength(self, password):
        label, color, percent = evaluate_strength(
            password, self.use_upper.get(), self.use_lower.get(),
            self.use_digits.get(), self.use_symbols.get()
        )
        self.strength_text.config(text=label, fg=color)
        self._animate_strength_bar(percent, color)

    def _animate_strength_bar(self, target_percent, color):
        self.strength_canvas.delete("all")
        width = self.strength_canvas.winfo_width() or 400
        height = 10
        self.strength_canvas.update_idletasks()
        width = self.strength_canvas.winfo_width() or 400

        bar = self.strength_canvas.create_rectangle(
            0, 0, 0, height, fill=color, width=0
        )

        def grow(current=0):
            target_width = int(width * target_percent / 100)
            step = max(1, target_width // 12)
            current = min(current + step, target_width)
            self.strength_canvas.coords(bar, 0, 0, current, height)
            if current < target_width:
                self.root.after(12, lambda: grow(current))

        grow()

    
    # Copy / Save / Toast
    
    def _on_copy(self):
        if not self.generated_passwords:
            self._show_toast("Generate a password first!", error=True)
            return
        text_to_copy = (
            self.generated_passwords[-1]
            if len(self.generated_passwords) == 1
            else "\n".join(self.generated_passwords)
        )
        self._copy_text(text_to_copy, "Copied to clipboard! ✅")

    def _copy_text(self, text, message):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()
        self._show_toast(message)

    def _on_save(self):
        if not self.generated_passwords:
            self._show_toast("Generate a password first!", error=True)
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")],
            initialfile="passwords.txt",
            title="Save Generated Passwords"
        )
        if not filepath:
            return
        try:
            with open(filepath, "w") as f:
                f.write("\n".join(self.generated_passwords))
            self._show_toast("Saved to file! 💾")
        except OSError as e:
            messagebox.showerror("Save Failed", str(e))

    def _show_toast(self, message, error=False):
        t = self.theme
        self.toast.config(
            text=message,
            bg=(t["danger"] if error else t["accent"]),
            fg=("#ffffff" if error else "#0a0e14")
        )
        self.toast.place(relx=0.5, rely=0.96, anchor="s")
        self.root.after(1800, lambda: self.toast.place_forget())


    # Keyboard shortcuts
   
    def _bind_shortcuts(self):
        self.root.bind("<Control-g>", lambda e: self._on_generate())
        self.root.bind("<Control-G>", lambda e: self._on_generate())
        self.root.bind("<Control-c>", lambda e: self._on_copy())
        self.root.bind("<Control-s>", lambda e: self._on_save())


# Entry point

def main():
    root = tk.Tk()
    app = PasswordGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()