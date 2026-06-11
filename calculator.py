# ============================================
#   CodSoft Internship - Task 2
#   Advanced Calculator - FULL VERSION
#   Made by: Nigam Kumar
#   Batch: JUNE BATCH C3
# ============================================

import tkinter as tk
from tkinter import ttk
import math
import urllib.request
import json
import datetime

THEMES = {
    "dark": {
        "BG": "#1a1a2e", "BG3": "#0f3460", "DISPLAY_BG": "#0d0d1a",
        "BTN_NUM": "#1e1e3a", "BTN_OP": "#0f3460", "BTN_EQ": "#e94560",
        "BTN_FN": "#162040", "BTN_CLR": "#3a0f1e", "BTN_MEM": "#0f2030",
        "TEXT_PRI": "#ffffff", "TEXT_SEC": "#a0aec0", "TEXT_HIST": "#718096",
        "TEXT_OP": "#63b3ed", "TEXT_EQ": "#ffffff", "TEXT_ERR": "#fc8181",
        "ACCENT": "#e94560",
        "HOVER_NUM": "#2a2a4a", "HOVER_OP": "#1a4a7a", "HOVER_FN": "#203050",
        "HOVER_CLR": "#5a1a2e", "HOVER_EQ": "#c73050",
    },
    "light": {
        "BG": "#f0f0f5", "BG3": "#c0c0e0", "DISPLAY_BG": "#ffffff",
        "BTN_NUM": "#e8e8f0", "BTN_OP": "#dde8ff", "BTN_EQ": "#e94560",
        "BTN_FN": "#dde8f5", "BTN_CLR": "#ffe0e0", "BTN_MEM": "#e0eef8",
        "TEXT_PRI": "#1a1a2e", "TEXT_SEC": "#4a5568", "TEXT_HIST": "#718096",
        "TEXT_OP": "#185fa5", "TEXT_EQ": "#ffffff", "TEXT_ERR": "#c53030",
        "ACCENT": "#e94560",
        "HOVER_NUM": "#d8d8e8", "HOVER_OP": "#c0d8ff", "HOVER_FN": "#c8dff0",
        "HOVER_CLR": "#ffcccc", "HOVER_EQ": "#c73050",
    }
}
T = THEMES["dark"]

UNITS = {
    "Length":      {"units": ["Meter","Kilometer","Centimeter","Millimeter","Mile","Yard","Foot","Inch"],       "to_base": [1,1000,0.01,0.001,1609.34,0.9144,0.3048,0.0254]},
    "Weight":      {"units": ["Kilogram","Gram","Milligram","Pound","Ounce","Tonne"],                           "to_base": [1,0.001,1e-6,0.453592,0.0283495,1000]},
    "Temperature": {"units": ["Celsius","Fahrenheit","Kelvin"],                                                 "to_base": None},
    "Speed":       {"units": ["km/h","mph","m/s","Knot"],                                                       "to_base": [1,1.60934,3.6,1.852]},
    "Area":        {"units": ["m²","km²","cm²","ft²","Acre","Hectare"],                                         "to_base": [1,1e6,0.0001,0.092903,4046.86,10000]},
    "Data":        {"units": ["Byte","Kilobyte","Megabyte","Gigabyte","Terabyte"],                              "to_base": [1,1024,1048576,1073741824,1099511627776]},
}

def convert_units(value, category, from_unit, to_unit):
    data = UNITS[category]
    fi, ti = data["units"].index(from_unit), data["units"].index(to_unit)
    if category == "Temperature":
        c = value if from_unit=="Celsius" else (value-32)*5/9 if from_unit=="Fahrenheit" else value-273.15
        return c if to_unit=="Celsius" else c*9/5+32 if to_unit=="Fahrenheit" else c+273.15
    return value * data["to_base"][fi] / data["to_base"][ti]

def factorial(n):
    if n < 0 or not float(n).is_integer(): raise ValueError("Factorial undefined")
    n = int(n)
    if n > 170: raise ValueError("Too large")
    r = 1
    for i in range(2, n+1): r *= i
    return r

def format_number(n):
    if isinstance(n, str): return n
    if not math.isfinite(n): return "∞" if n > 0 else "-∞"
    if abs(n) >= 1e12 or (abs(n) < 1e-7 and n != 0): return f"{n:.4e}"
    return f"{n:.10f}".rstrip("0").rstrip(".")

def evaluate_expression(expr_str):
    expr_str = expr_str.strip().replace("×","*").replace("÷","/").replace("−","-")
    expr_str = expr_str.replace("π", str(math.pi)).replace("e", str(math.e))
    for ch in expr_str:
        if ch not in set("0123456789+-*/.()^ "): raise ValueError(f"Invalid: {ch}")
    return eval(expr_str.replace("^","**"), {"__builtins__": {}}, {})


class ScrollableFrame(tk.Frame):
    def __init__(self, parent, bg, **kwargs):
        super().__init__(parent, bg=bg, **kwargs)
        self.canvas = tk.Canvas(self, bg=bg, bd=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg=bg)
        self.inner_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.inner.bind("<Configure>", self._on_inner_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_inner_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.inner_id, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")


class AdvancedCalculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Advanced Calculator — Nigam Kumar | CodSoft")
        self.resizable(True, True)
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        w  = min(420, sw - 40)
        h  = min(820, sh - 80)
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        self.minsize(360, 400)

        self.current      = "0"
        self.expression   = ""
        self.bracket_expr = ""
        self.operator     = None
        self.prev_value   = None
        self.just_calc    = False
        self.memory       = None
        self.history      = []
        self.angle_mode   = "DEG"
        self.mode         = "standard"
        self.theme_name   = "dark"
        self.last_result  = None

        self._build_ui()
        self._bind_keys()
        self.update_display()

    def toggle_theme(self):
        self.theme_name = "light" if self.theme_name == "dark" else "dark"
        global T
        T = THEMES[self.theme_name]
        self._rebuild_ui()

    def _rebuild_ui(self):
        for w in self.winfo_children(): w.destroy()
        self._build_ui()
        self._bind_keys()
        self.update_display()

    def _build_ui(self):
        self.configure(bg=T["BG"])

        top = tk.Frame(self, bg=T["BG"])
        top.pack(fill="x", padx=12, pady=(6,0))
        tk.Label(top, text="CALCULATOR", bg=T["BG"],
                 fg=T["ACCENT"], font=("Consolas",11,"bold")).pack(side="left")
        self.theme_btn = tk.Button(top,
            text="☀ Light" if self.theme_name=="dark" else "☾ Dark",
            bg=T["BTN_FN"], fg=T["TEXT_SEC"], font=("Consolas",9),
            bd=0, relief="flat", padx=8, pady=2, cursor="hand2",
            command=self.toggle_theme)
        self.theme_btn.pack(side="right", padx=2)
        tk.Label(top, text="Nigam Kumar · CodSoft", bg=T["BG"],
                 fg=T["TEXT_HIST"], font=("Consolas",9)).pack(side="right")

        tk.Frame(self, bg=T["ACCENT"], height=1).pack(fill="x", padx=12)

        tab_frame = tk.Frame(self, bg=T["BG"], pady=4)
        tab_frame.pack(fill="x", padx=12)
        self.tab_btns = {}
        for mode in ["Standard","Scientific","Converter","Extra"]:
            b = tk.Button(tab_frame, text=mode, font=("Consolas",9),
                          bg=T["BTN_FN"], fg=T["TEXT_SEC"], bd=0, relief="flat",
                          padx=8, pady=3, cursor="hand2",
                          command=lambda m=mode.lower(): self.set_mode(m))
            b.pack(side="left", padx=2)
            self.tab_btns[mode.lower()] = b
        self._highlight_tab(self.mode)

        self.scroll_area = ScrollableFrame(self, bg=T["BG"])
        self.scroll_area.pack(fill="both", expand=True, padx=12, pady=(4,8))
        self.main_frame = self.scroll_area.inner

        self._build_display()
        self._build_memory_bar()
        self._build_standard_buttons()
        self._build_scientific_panel()
        self._build_converter_panel()
        self._build_extra_panel()
        self._build_history_panel()

        self.sci_frame.pack_forget()
        self.conv_frame.pack_forget()
        self.extra_frame.pack_forget()
        self.set_mode(self.mode)

    def _build_display(self):
        disp = tk.Frame(self.main_frame, bg=T["DISPLAY_BG"],
                        highlightbackground=T["BG3"], highlightthickness=1)
        disp.pack(fill="x", pady=(0,6))

        self.lbl_history = tk.Label(disp, text="", bg=T["DISPLAY_BG"],
                                    fg=T["TEXT_HIST"], font=("Consolas",9),
                                    anchor="e", padx=10, pady=2)
        self.lbl_history.pack(fill="x", pady=(4,0))

        self.lbl_bracket = tk.Label(disp, text="", bg=T["DISPLAY_BG"],
                                    fg=T["ACCENT"], font=("Consolas",10),
                                    anchor="e", padx=10)
        self.lbl_bracket.pack(fill="x")

        self.lbl_expr = tk.Label(disp, text="", bg=T["DISPLAY_BG"],
                                 fg=T["TEXT_SEC"], font=("Consolas",11),
                                 anchor="e", padx=10)
        self.lbl_expr.pack(fill="x")

        self.lbl_result = tk.Label(disp, text="0", bg=T["DISPLAY_BG"],
                                   fg=T["TEXT_PRI"], font=("Consolas",28,"bold"),
                                   anchor="e", padx=10, pady=6)
        self.lbl_result.pack(fill="x")

        bot = tk.Frame(disp, bg=T["DISPLAY_BG"])
        bot.pack(fill="x", padx=10, pady=(0,4))
        self.lbl_mem_disp = tk.Label(bot, text="", bg=T["DISPLAY_BG"],
                                     fg=T["TEXT_OP"], font=("Consolas",9))
        self.lbl_mem_disp.pack(side="left")
        tk.Button(bot, text="⎘ Copy", bg=T["BTN_FN"], fg=T["TEXT_SEC"],
                  font=("Consolas",9), bd=0, relief="flat", padx=6, pady=1,
                  cursor="hand2", command=self.copy_result).pack(side="right", padx=(3,0))
        self.ang_btn = tk.Button(bot, text="DEG", bg=T["BTN_FN"], fg=T["TEXT_OP"],
                                 font=("Consolas",9), bd=0, relief="flat", padx=6, pady=1,
                                 cursor="hand2", command=self.toggle_angle)
        self.ang_btn.pack(side="right")

    def _build_memory_bar(self):
        f = tk.Frame(self.main_frame, bg=T["BG"])
        f.pack(fill="x", pady=(0,4))
        for lbl, cmd in zip(
            ["MC","MR","M+","M−","MS","ANS"],
            [self.mem_clear,self.mem_recall,self.mem_add,self.mem_sub,self.mem_store,self.use_ans]
        ):
            b = tk.Button(f, text=lbl, font=("Consolas",9), bg=T["BTN_MEM"],
                          fg=T["TEXT_SEC"], bd=0, relief="flat", padx=0, pady=4,
                          cursor="hand2", command=cmd, width=4)
            b.pack(side="left", padx=1)
            self._hover(b, T["BTN_MEM"], T["HOVER_FN"])

    def _make_btn(self, parent, text, command, bg=None, fg=None, font=None, pady=11, width=5, hover=None):
        bg    = bg    or T["BTN_NUM"]
        fg    = fg    or T["TEXT_PRI"]
        font  = font  or ("Consolas",13,"bold")
        hover = hover or T["HOVER_NUM"]
        b = tk.Button(parent, text=text, font=font, bg=bg, fg=fg,
                      bd=0, relief="flat", padx=0, pady=pady,
                      cursor="hand2", command=command, width=width)
        self._hover(b, bg, hover)
        return b

    def _hover(self, w, n, h):
        w.bind("<Enter>", lambda e: w.config(bg=h))
        w.bind("<Leave>", lambda e: w.config(bg=n))

    def _build_standard_buttons(self):
        self.std_frame = tk.Frame(self.main_frame, bg=T["BG"])
        self.std_frame.pack(fill="x")

        layout = [
            [("AC",self.clear_all,T["BTN_CLR"],T["TEXT_ERR"],T["HOVER_CLR"]),
             ("(", lambda:self.input_bracket("("),T["BTN_FN"],T["TEXT_OP"],T["HOVER_FN"]),
             (")", lambda:self.input_bracket(")"),T["BTN_FN"],T["TEXT_OP"],T["HOVER_FN"]),
             ("÷", lambda:self.input_op("/"),T["BTN_OP"],T["TEXT_OP"],T["HOVER_OP"])],
            [("7",lambda:self.input_num("7"),T["BTN_NUM"],T["TEXT_PRI"],T["HOVER_NUM"]),
             ("8",lambda:self.input_num("8"),T["BTN_NUM"],T["TEXT_PRI"],T["HOVER_NUM"]),
             ("9",lambda:self.input_num("9"),T["BTN_NUM"],T["TEXT_PRI"],T["HOVER_NUM"]),
             ("×",lambda:self.input_op("*"),T["BTN_OP"],T["TEXT_OP"],T["HOVER_OP"])],
            [("4",lambda:self.input_num("4"),T["BTN_NUM"],T["TEXT_PRI"],T["HOVER_NUM"]),
             ("5",lambda:self.input_num("5"),T["BTN_NUM"],T["TEXT_PRI"],T["HOVER_NUM"]),
             ("6",lambda:self.input_num("6"),T["BTN_NUM"],T["TEXT_PRI"],T["HOVER_NUM"]),
             ("−",lambda:self.input_op("-"),T["BTN_OP"],T["TEXT_OP"],T["HOVER_OP"])],
            [("1",lambda:self.input_num("1"),T["BTN_NUM"],T["TEXT_PRI"],T["HOVER_NUM"]),
             ("2",lambda:self.input_num("2"),T["BTN_NUM"],T["TEXT_PRI"],T["HOVER_NUM"]),
             ("3",lambda:self.input_num("3"),T["BTN_NUM"],T["TEXT_PRI"],T["HOVER_NUM"]),
             ("+",lambda:self.input_op("+"),T["BTN_OP"],T["TEXT_OP"],T["HOVER_OP"])],
        ]

        for row_data in layout:
            row = tk.Frame(self.std_frame, bg=T["BG"])
            row.pack(fill="x", pady=2)
            for text, cmd, bg, fg, hov in row_data:
                self._make_btn(row, text, cmd, bg=bg, fg=fg, hover=hov).pack(side="left", padx=2, expand=True, fill="x")

        bot = tk.Frame(self.std_frame, bg=T["BG"])
        bot.pack(fill="x", pady=2)
        z = tk.Button(bot, text="0", font=("Consolas",13,"bold"),
                      bg=T["BTN_NUM"], fg=T["TEXT_PRI"], bd=0,
                      relief="flat", pady=11, cursor="hand2",
                      command=lambda: self.input_num("0"))
        self._hover(z, T["BTN_NUM"], T["HOVER_NUM"])
        z.pack(side="left", padx=2, expand=True, fill="x")
        for text, cmd, bg, fg, hov in [
            (".", self.input_dot, T["BTN_NUM"], T["TEXT_PRI"], T["HOVER_NUM"]),
            ("C", self.backspace, T["BTN_CLR"], T["TEXT_ERR"], T["HOVER_CLR"]),
            ("=", self.calculate, T["BTN_EQ"],  T["TEXT_EQ"],  T["HOVER_EQ"]),
        ]:
            fnt = ("Consolas",16,"bold") if text=="=" else ("Consolas",13,"bold")
            self._make_btn(bot, text, cmd, bg=bg, fg=fg, font=fnt, hover=hov).pack(side="left", padx=2, expand=True, fill="x")

    def _build_scientific_panel(self):
        self.sci_frame = tk.Frame(self.main_frame, bg=T["BG"])
        rows = [
            [("sin",lambda:self.sci_func("sin")),("cos",lambda:self.sci_func("cos")),
             ("tan",lambda:self.sci_func("tan")),("log",lambda:self.sci_func("log")),
             ("ln", lambda:self.sci_func("ln"))],
            [("√x", lambda:self.sci_func("sqrt")),("x²",lambda:self.sci_func("sq")),
             ("x³", lambda:self.sci_func("cube")),("xʸ",lambda:self.input_op("^")),
             ("1/x",lambda:self.sci_func("inv"))],
            [("n!", lambda:self.sci_func("fact")),("|x|",lambda:self.sci_func("abs")),
             ("π",  lambda:self.input_const(math.pi)),("e",lambda:self.input_const(math.e)),
             ("C",  self.backspace)],
        ]
        for row_data in rows:
            row = tk.Frame(self.sci_frame, bg=T["BG"])
            row.pack(fill="x", pady=2)
            for text, cmd in row_data:
                if text == "C":
                    b = self._make_btn(row, text, cmd, bg=T["BTN_CLR"], fg=T["TEXT_ERR"],
                                       font=("Consolas",11), hover=T["HOVER_CLR"])
                else:
                    b = self._make_btn(row, text, cmd, bg=T["BTN_FN"], fg=T["TEXT_SEC"],
                                       font=("Consolas",11), hover=T["HOVER_FN"])
                b.pack(side="left", padx=2, expand=True, fill="x")

    def _build_converter_panel(self):
        self.conv_frame = tk.Frame(self.main_frame, bg=T["BG"])
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("C.TCombobox", fieldbackground=T["BTN_FN"], background=T["BTN_FN"],
                         foreground=T["TEXT_PRI"], selectbackground=T["BG3"],
                         selectforeground=T["TEXT_PRI"], arrowcolor=T["TEXT_SEC"])

        def lbl(txt):
            tk.Label(self.conv_frame, text=txt, bg=T["BG"], fg=T["TEXT_SEC"],
                     font=("Consolas",10)).pack(anchor="w", pady=(4,1))

        lbl("Category")
        self.conv_cat = ttk.Combobox(self.conv_frame, style="C.TCombobox",
                                     values=list(UNITS.keys()), state="readonly", font=("Consolas",11))
        self.conv_cat.current(0)
        self.conv_cat.pack(fill="x", pady=(0,4))
        self.conv_cat.bind("<<ComboboxSelected>>", self._update_conv_units)

        lbl("From")
        fr = tk.Frame(self.conv_frame, bg=T["BG"])
        fr.pack(fill="x", pady=(0,4))
        self.conv_input = tk.Entry(fr, font=("Consolas",12), bg=T["BTN_FN"],
                                   fg=T["TEXT_PRI"], insertbackground=T["TEXT_PRI"],
                                   relief="flat", bd=5, width=10)
        self.conv_input.insert(0,"1")
        self.conv_input.pack(side="left", padx=(0,4))
        self.conv_input.bind("<KeyRelease>", lambda e: self._do_convert())
        self.conv_from = ttk.Combobox(fr, style="C.TCombobox", state="readonly", font=("Consolas",11))
        self.conv_from.pack(side="left", fill="x", expand=True)
        self.conv_from.bind("<<ComboboxSelected>>", lambda e: self._do_convert())

        lbl("To")
        self.conv_to = ttk.Combobox(self.conv_frame, style="C.TCombobox",
                                    state="readonly", font=("Consolas",11))
        self.conv_to.pack(fill="x", pady=(0,8))
        self.conv_to.bind("<<ComboboxSelected>>", lambda e: self._do_convert())

        tk.Frame(self.conv_frame, bg=T["ACCENT"], height=1).pack(fill="x", pady=(0,4))
        self.conv_result_var = tk.StringVar(value="—")
        tk.Label(self.conv_frame, textvariable=self.conv_result_var,
                 bg=T["DISPLAY_BG"], fg=T["ACCENT"],
                 font=("Consolas",18,"bold"), anchor="e", padx=12, pady=8).pack(fill="x")
        self._update_conv_units()

    def _update_conv_units(self, event=None):
        u = UNITS[self.conv_cat.get()]["units"]
        self.conv_from.config(values=u); self.conv_from.current(0)
        self.conv_to.config(values=u);   self.conv_to.current(1 if len(u)>1 else 0)
        self._do_convert()

    def _do_convert(self):
        try:
            val = float(self.conv_input.get())
            res = convert_units(val, self.conv_cat.get(), self.conv_from.get(), self.conv_to.get())
            self.conv_result_var.set(f"{format_number(res)} {self.conv_to.get()}")
        except Exception:
            self.conv_result_var.set("Invalid input")

    def _build_extra_panel(self):
        self.extra_frame = tk.Frame(self.main_frame, bg=T["BG"])
        sub_bar = tk.Frame(self.extra_frame, bg=T["BG"])
        sub_bar.pack(fill="x", pady=(0,6))
        self.sub_btns = {}
        self.sub_frames = {}
        for name in ["Currency","BMI","Age","EMI","Percent"]:
            b = tk.Button(sub_bar, text=name, font=("Consolas",9),
                          bg=T["BTN_FN"], fg=T["TEXT_SEC"],
                          bd=0, relief="flat", padx=6, pady=3,
                          cursor="hand2", command=lambda n=name: self._show_sub(n))
            b.pack(side="left", padx=2)
            self.sub_btns[name] = b
        self.sub_container = tk.Frame(self.extra_frame, bg=T["BG"])
        self.sub_container.pack(fill="x")
        self._build_currency_frame()
        self._build_bmi_frame()
        self._build_age_frame()
        self._build_emi_frame()
        self._build_percent_frame()
        self._show_sub("Currency")

    def _show_sub(self, name):
        for n, b in self.sub_btns.items():
            b.config(bg=T["ACCENT"] if n==name else T["BTN_FN"],
                     fg=T["TEXT_EQ"] if n==name else T["TEXT_SEC"])
        for n, f in self.sub_frames.items():
            f.pack_forget()
        self.sub_frames[name].pack(fill="x")

    def _result_box(self, parent):
        tk.Frame(parent, bg=T["ACCENT"], height=1).pack(fill="x", pady=(8,4))
        v = tk.StringVar(value="—")
        tk.Label(parent, textvariable=v, bg=T["DISPLAY_BG"], fg=T["ACCENT"],
                 font=("Consolas",16,"bold"), anchor="e", padx=12, pady=8).pack(fill="x")
        return v

    def _entry_row(self, parent, label, default=""):
        tk.Label(parent, text=label, bg=T["BG"], fg=T["TEXT_SEC"],
                 font=("Consolas",10)).pack(anchor="w", pady=(4,1))
        e = tk.Entry(parent, font=("Consolas",12), bg=T["BTN_FN"],
                     fg=T["TEXT_PRI"], insertbackground=T["TEXT_PRI"], relief="flat", bd=5)
        e.insert(0, default)
        e.pack(fill="x")
        return e

    def _calc_btn(self, parent, text, cmd):
        b = tk.Button(parent, text=text, font=("Consolas",11,"bold"),
                      bg=T["BTN_EQ"], fg=T["TEXT_EQ"], bd=0,
                      relief="flat", pady=7, cursor="hand2", command=cmd)
        self._hover(b, T["BTN_EQ"], T["HOVER_EQ"])
        b.pack(fill="x", pady=(8,0))

    def _build_currency_frame(self):
        f = tk.Frame(self.sub_container, bg=T["BG"])
        self.sub_frames["Currency"] = f
        self.cur_amount = self._entry_row(f, "Amount", "1")
        currencies = ["USD","INR","EUR","GBP","JPY","AED","CAD","AUD","CNY","SGD"]
        tk.Label(f, text="From", bg=T["BG"], fg=T["TEXT_SEC"],
                 font=("Consolas",10)).pack(anchor="w", pady=(4,1))
        self.cur_from = ttk.Combobox(f, values=currencies, style="C.TCombobox",
                                     state="readonly", font=("Consolas",11))
        self.cur_from.current(0); self.cur_from.pack(fill="x")
        tk.Label(f, text="To", bg=T["BG"], fg=T["TEXT_SEC"],
                 font=("Consolas",10)).pack(anchor="w", pady=(4,1))
        self.cur_to = ttk.Combobox(f, values=currencies, style="C.TCombobox",
                                   state="readonly", font=("Consolas",11))
        self.cur_to.current(1); self.cur_to.pack(fill="x")
        self.cur_result = self._result_box(f)
        self._calc_btn(f, "Convert (Live Rate)", self._do_currency)

    def _do_currency(self):
        try:
            amount = float(self.cur_amount.get())
            frm, to = self.cur_from.get(), self.cur_to.get()
            data = json.loads(urllib.request.urlopen(
                f"https://api.exchangerate-api.com/v4/latest/{frm}", timeout=5).read())
            rate = data["rates"][to]
            self.cur_result.set(f"{amount*rate:.4f} {to}  (1 {frm} = {rate:.4f} {to})")
        except Exception:
            self.cur_result.set("No internet / API error")

    def _build_bmi_frame(self):
        f = tk.Frame(self.sub_container, bg=T["BG"])
        self.sub_frames["BMI"] = f
        self.bmi_weight = self._entry_row(f, "Weight (kg)", "70")
        self.bmi_height = self._entry_row(f, "Height (cm)", "170")
        self.bmi_result = self._result_box(f)
        self._calc_btn(f, "Calculate BMI", self._do_bmi)

    def _do_bmi(self):
        try:
            w = float(self.bmi_weight.get())
            h = float(self.bmi_height.get()) / 100
            bmi = w / (h*h)
            cat = "Underweight" if bmi<18.5 else "Normal weight" if bmi<25 else "Overweight" if bmi<30 else "Obese"
            self.bmi_result.set(f"{bmi:.2f}  ({cat})")
        except Exception:
            self.bmi_result.set("Invalid input")

    def _build_age_frame(self):
        f = tk.Frame(self.sub_container, bg=T["BG"])
        self.sub_frames["Age"] = f
        self.age_dob = self._entry_row(f, "Date of Birth (DD/MM/YYYY)", "01/01/2000")
        self.age_result = self._result_box(f)
        self._calc_btn(f, "Calculate Age", self._do_age)

    def _do_age(self):
        try:
            dob   = datetime.datetime.strptime(self.age_dob.get().strip(), "%d/%m/%Y")
            today = datetime.datetime.today()
            years = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            months = (today.month - dob.month) % 12
            days  = (today - dob.replace(year=today.year)).days % 30
            self.age_result.set(f"{years} yrs  {months} mo  {days} days")
        except Exception:
            self.age_result.set("Use DD/MM/YYYY format")

    def _build_emi_frame(self):
        f = tk.Frame(self.sub_container, bg=T["BG"])
        self.sub_frames["EMI"] = f
        self.emi_principal = self._entry_row(f, "Loan Amount (₹)", "500000")
        self.emi_rate      = self._entry_row(f, "Annual Interest Rate (%)", "8.5")
        self.emi_tenure    = self._entry_row(f, "Tenure (months)", "60")
        self.emi_result    = self._result_box(f)
        self._calc_btn(f, "Calculate EMI", self._do_emi)

    def _do_emi(self):
        try:
            P = float(self.emi_principal.get())
            r = float(self.emi_rate.get()) / 12 / 100
            n = int(self.emi_tenure.get())
            emi = P/n if r==0 else P*r*(1+r)**n/((1+r)**n-1)
            total = emi * n
            self.emi_result.set(f"EMI: ₹{emi:,.2f}\nTotal: ₹{total:,.2f}  Int: ₹{total-P:,.2f}")
        except Exception:
            self.emi_result.set("Invalid input")

    def _build_percent_frame(self):
        f = tk.Frame(self.sub_container, bg=T["BG"])
        self.sub_frames["Percent"] = f
        tk.Label(f, text="What is X% of Y?", bg=T["BG"], fg=T["ACCENT"],
                 font=("Consolas",10,"bold")).pack(anchor="w", pady=(0,2))
        self.pct_x = self._entry_row(f, "Percentage (X%)", "15")
        self.pct_y = self._entry_row(f, "Of Value (Y)", "200")
        self.pct_result = self._result_box(f)
        self._calc_btn(f, "Calculate", self._do_percent)
        tk.Label(f, text="X is what % of Y?", bg=T["BG"], fg=T["ACCENT"],
                 font=("Consolas",10,"bold")).pack(anchor="w", pady=(12,2))
        self.pct_a = self._entry_row(f, "Value X", "30")
        self.pct_b = self._entry_row(f, "Total Y", "200")
        self.pct_result2 = self._result_box(f)
        self._calc_btn(f, "Calculate %", self._do_percent2)

    def _do_percent(self):
        try:
            x,y = float(self.pct_x.get()), float(self.pct_y.get())
            self.pct_result.set(f"{x}% of {y} = {x*y/100:.4f}")
        except Exception:
            self.pct_result.set("Invalid input")

    def _do_percent2(self):
        try:
            a,b = float(self.pct_a.get()), float(self.pct_b.get())
            self.pct_result2.set(f"{a} is {a/b*100:.4f}% of {b}")
        except Exception:
            self.pct_result2.set("Invalid input")

    def _build_history_panel(self):
        self.hist_frame = tk.Frame(self.main_frame, bg=T["BG"])
        self.hist_frame.pack(fill="x", pady=(6,0))
        hdr = tk.Frame(self.hist_frame, bg=T["BG"])
        hdr.pack(fill="x")
        tk.Label(hdr, text="History", bg=T["BG"], fg=T["TEXT_SEC"],
                 font=("Consolas",10)).pack(side="left")
        tk.Button(hdr, text="Clear", bg=T["BG"], fg=T["TEXT_HIST"],
                  font=("Consolas",9), bd=0, relief="flat",
                  cursor="hand2", command=self.clear_history).pack(side="right")
        self.hist_box = tk.Text(self.hist_frame, bg=T["DISPLAY_BG"], fg=T["TEXT_SEC"],
                                font=("Consolas",10), height=4, bd=0, relief="flat",
                                state="disabled", padx=8, pady=4,
                                wrap="none", cursor="arrow")
        self.hist_box.pack(fill="x", pady=(2,0))
        self.hist_box.tag_config("ans",  foreground=T["ACCENT"])
        self.hist_box.tag_config("expr", foreground=T["TEXT_SEC"])

    def set_mode(self, mode):
        self.mode = mode
        self._highlight_tab(mode)
        self.std_frame.pack_forget()
        self.sci_frame.pack_forget()
        self.conv_frame.pack_forget()
        self.extra_frame.pack_forget()
        if mode == "standard":
            self.std_frame.pack(fill="x")
        elif mode == "scientific":
            self.sci_frame.pack(fill="x", pady=(0,4))
            self.std_frame.pack(fill="x")
        elif mode == "converter":
            self.conv_frame.pack(fill="x")
        elif mode == "extra":
            self.extra_frame.pack(fill="x")

    def _highlight_tab(self, active):
        for name, btn in self.tab_btns.items():
            btn.config(bg=T["ACCENT"] if name==active else T["BTN_FN"],
                       fg=T["TEXT_EQ"] if name==active else T["TEXT_SEC"])

    def update_display(self):
        try:
            disp = format_number(float(self.current)) if self.current not in ("Error","") else self.current
        except Exception:
            disp = self.current
        self.lbl_result.config(
            text=disp,
            fg=T["TEXT_ERR"] if self.current=="Error" else T["TEXT_PRI"],
            font=("Consolas",20,"bold") if len(self.current)>10 else ("Consolas",28,"bold")
        )
        if self.operator and not self.just_calc:
            sym = {"+":"+","-":"−","*":"×","/":"÷","^":"ˆ"}.get(self.operator,self.operator)
            live = f"{format_number(self.prev_value)} {sym} {self.current}"
        else:
            live = self.expression
        self.lbl_expr.config(text=live)
        self.lbl_bracket.config(text=self.bracket_expr or "")
        self.lbl_mem_disp.config(text=f"M={format_number(self.memory)}" if self.memory is not None else "")

    def _set_history_line(self, text):
        self.lbl_history.config(text=text)

    def copy_result(self):
        try:
            val = format_number(float(self.current)) if self.current not in ("Error","") else self.current
            self.clipboard_clear(); self.clipboard_append(val)
            self._set_history_line(f"Copied: {val}")
        except Exception: pass

    def input_num(self, n):
        if self.bracket_expr:
            self.bracket_expr += n
            self.current = n if self.just_calc else (self.current if self.current!="0" else "")+n
            self.just_calc = False
        elif self.just_calc:
            self.current = n; self.just_calc = False
        elif self.current == "0":
            self.current = n
        else:
            self.current += n
        self.update_display()

    def input_dot(self):
        if self.just_calc: self.current = "0."; self.just_calc = False
        elif "." not in self.current: self.current += "."
        if self.bracket_expr: self.bracket_expr += "."
        self.update_display()

    def input_bracket(self, b):
        if b == "(":
            if self.just_calc: self.bracket_expr = ""; self.just_calc = False
            self.bracket_expr += "("; self.current = "0"
        else:
            self.bracket_expr += self.current + ")"
        self.update_display()

    def input_op(self, op):
        if self.bracket_expr:
            self.bracket_expr += {"+":"+","-":"-","*":"*","/":"/","^":"^"}.get(op,op)
            self.just_calc = True
        else:
            if self.operator and not self.just_calc: self._do_simple_calc()
            self.prev_value = float(self.current); self.operator = op
            sym = {"+":"+","-":"−","*":"×","/":"÷","^":"ˆ"}.get(op,op)
            self.expression = f"{format_number(self.prev_value)} {sym}"; self.just_calc = True
        self.update_display()

    def input_const(self, val):
        self.current = str(val); self.just_calc = False; self.update_display()

    def backspace(self):
        if self.bracket_expr: self.bracket_expr = self.bracket_expr[:-1]
        elif not self.just_calc: self.current = self.current[:-1] if len(self.current)>1 else "0"
        self.update_display()

    def clear_all(self):
        self.current="0"; self.expression=""; self.bracket_expr=""
        self.operator=None; self.prev_value=None; self.just_calc=False
        self._set_history_line(""); self.update_display()

    def toggle_sign(self):
        try: self.current = str(-float(self.current)); self.update_display()
        except Exception: pass

    def percent(self):
        try: self.current = str(float(self.current)/100); self.update_display()
        except Exception: pass

    def toggle_angle(self):
        self.angle_mode = "RAD" if self.angle_mode=="DEG" else "DEG"
        self.ang_btn.config(text=self.angle_mode)

    def use_ans(self):
        if self.last_result is not None:
            self.current = str(self.last_result); self.just_calc = False; self.update_display()

    def _do_simple_calc(self):
        a,b,op = self.prev_value, float(self.current), self.operator
        if op=="+": return a+b
        if op=="-": return a-b
        if op=="*": return a*b
        if op=="/":
            if b==0: raise ZeroDivisionError
            return a/b
        if op=="^": return a**b
        return b

    def calculate(self):
        if self.bracket_expr:
            full = self.bracket_expr + ("" if self.just_calc else self.current)
            try:
                result = evaluate_expression(full)
                self._push_history(full+" =", result)
                self._set_history_line(full+" =")
                self.last_result = result
                res_str = str(round(result,10)).rstrip("0").rstrip(".")
                self.expression=full+" ="; self.current=res_str
                self.bracket_expr=""; self.operator=None; self.prev_value=None; self.just_calc=True
            except ZeroDivisionError:
                self.current="Error"; self._set_history_line("Cannot divide by zero")
            except Exception as ex:
                self.current="Error"; self._set_history_line(f"Error: {ex}")
            self.update_display(); return

        if not self.operator: return
        sym = {"+":"+","-":"−","*":"×","/":"÷","^":"ˆ"}.get(self.operator,self.operator)
        hist_expr = f"{format_number(self.prev_value)} {sym} {format_number(float(self.current))}"
        try:
            result = self._do_simple_calc()
            self._push_history(hist_expr+" =", result)
            self._set_history_line(hist_expr+" =")
            self.last_result = result
            res_str = str(round(result,10)).rstrip("0").rstrip(".")
            self.expression=hist_expr+" ="; self.current=res_str
            self.operator=None; self.prev_value=None; self.just_calc=True
        except ZeroDivisionError:
            self.current="Error"; self._set_history_line("Cannot divide by zero")
        except Exception:
            self.current="Error"
        self.update_display()

    def sci_func(self, fn):
        try:
            v = float(self.current)
            rad = math.radians(v) if self.angle_mode=="DEG" else v
            ops = {
                "sin":  lambda: math.sin(rad),
                "cos":  lambda: math.cos(rad),
                "tan":  lambda: math.tan(rad),
                "log":  lambda: math.log10(v) if v>0 else (_ for _ in ()).throw(ValueError("log(negative)")),
                "ln":   lambda: math.log(v)   if v>0 else (_ for _ in ()).throw(ValueError("ln(negative)")),
                "sqrt": lambda: math.sqrt(v)  if v>=0 else (_ for _ in ()).throw(ValueError("√(negative) — Not real")),
                "sq":   lambda: v*v, "cube": lambda: v*v*v,
                "inv":  lambda: 1/v if v!=0 else (_ for _ in ()).throw(ZeroDivisionError),
                "fact": lambda: factorial(v), "abs": lambda: abs(v),
            }
            result = ops[fn]()
            he = f"{fn}({format_number(v)})"
            self._push_history(he+" =", result)
            self._set_history_line(f"{he} =")
            self.last_result = result
            self.current = str(round(result,10)).rstrip("0").rstrip(".")
            self.just_calc = True; self.update_display()
        except ValueError as ve:
            self.current="Error"; self._set_history_line(str(ve)); self.update_display()
        except Exception:
            self.current="Error"; self.update_display()

    def mem_store(self):
        try: self.memory = float(self.current)
        except Exception: pass
        self.update_display()

    def mem_recall(self):
        if self.memory is not None: self.current=str(self.memory); self.update_display()

    def mem_clear(self):
        self.memory=None; self.update_display()

    def mem_add(self):
        try: self.memory=(self.memory or 0)+float(self.current)
        except Exception: pass
        self.update_display()

    def mem_sub(self):
        try: self.memory=(self.memory or 0)-float(self.current)
        except Exception: pass
        self.update_display()

    def _push_history(self, expr, result):
        self.history.insert(0,(expr,result))
        if len(self.history)>20: self.history.pop()
        self._render_history()

    def _render_history(self):
        self.hist_box.config(state="normal")
        self.hist_box.delete("1.0","end")
        for expr, result in self.history:
            self.hist_box.insert("end", f"  {expr} ", "expr")
            self.hist_box.insert("end", f"{format_number(result)}\n", "ans")
        self.hist_box.config(state="disabled")

    def clear_history(self):
        self.history=[]; self._render_history()

    def _bind_keys(self):
        for k in "0123456789":
            self.bind(k, lambda e, n=k: self.input_num(n))
        self.bind(".",           lambda e: self.input_dot())
        self.bind("+",           lambda e: self.input_op("+"))
        self.bind("-",           lambda e: self.input_op("-"))
        self.bind("*",           lambda e: self.input_op("*"))
        self.bind("/",           lambda e: self.input_op("/"))
        self.bind("(",           lambda e: self.input_bracket("("))
        self.bind(")",           lambda e: self.input_bracket(")"))
        self.bind("<Return>",    lambda e: self.calculate())
        self.bind("<BackSpace>", lambda e: self.backspace())
        self.bind("<Escape>",    lambda e: self.clear_all())


if __name__ == "__main__":
    app = AdvancedCalculator()
    app.mainloop()