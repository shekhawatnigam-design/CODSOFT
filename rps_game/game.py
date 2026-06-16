import tkinter as tk
from tkinter import font as tkfont
import random, math, time

BG      = "#0d0d1a"
BG2     = "#13132b"
CARD    = "#1a1a35"
CARD2   = "#22224a"
BORDER  = "#2e2e60"
ACCENT  = "#7c5cfc"
ACCENT2 = "#a78bfa"
GREEN   = "#4ade80"
GREEN2  = "#166534"
RED     = "#f87171"
RED2    = "#7f1d1d"
YELLOW  = "#fbbf24"
YELLOW2 = "#78350f"
WHITE   = "#f0f0ff"
GREY    = "#8888aa"
DIMGREY = "#44446a"

MODES = {
    "classic": {
        "moves": ["rock","paper","scissors"],
        "emojis": {"rock":"🪨","paper":"📄","scissors":"✂️"},
        "beats": {"rock":["scissors"],"scissors":["paper"],"paper":["rock"]},
        "rules": {"rock":{"scissors":"crushes"},"scissors":{"paper":"cuts"},"paper":{"rock":"covers"}}
    },
    "spock": {
        "moves": ["rock","paper","scissors","lizard","spock"],
        "emojis": {"rock":"🪨","paper":"📄","scissors":"✂️","lizard":"🦎","spock":"🖖"},
        "beats": {"rock":["scissors","lizard"],"paper":["rock","spock"],
                  "scissors":["paper","lizard"],"lizard":["spock","paper"],"spock":["scissors","rock"]},
        "rules": {
            "rock":{"scissors":"crushes","lizard":"crushes"},
            "paper":{"rock":"covers","spock":"disproves"},
            "scissors":{"paper":"cuts","lizard":"decapitates"},
            "lizard":{"spock":"poisons","paper":"eats"},
            "spock":{"scissors":"smashes","rock":"vaporizes"}
        }
    }
}

ACHIEVEMENTS = [
    ("first",    "⚔️ First Blood",   "Win your first round",        lambda s: s["wins"]>=1),
    ("streak3",  "🔥 On Fire",        "Win 3 rounds in a row",       lambda s: s["max_streak"]>=3),
    ("flawless", "💎 Flawless",       "Win match without losing",    lambda s: s["flawless"]),
    ("comeback", "🦅 Comeback Kid",   "Win after trailing 0-2",      lambda s: s["comeback"]),
    ("spockwin", "🖖 Spock Master",   "Win 3 times using Spock",     lambda s: s["spock_wins"]>=3),
    ("centurion","🛡️ Centurion",      "Play 20 total rounds",        lambda s: s["total"]>=20),
    ("perfect",  "🌟 Perfect Ten",    "Achieve 10-round win streak", lambda s: s["max_streak"]>=10),
    ("veteran",  "🎖️ Veteran",        "Play 50 total rounds",        lambda s: s["total"]>=50),
]


class Particle:
    def __init__(self, x, y, burst_type="win"):
        self.x, self.y = x, y
        angle = random.uniform(0, 2*math.pi)
        speed = random.uniform(2, 6)
        self.vx = math.cos(angle)*speed
        self.vy = math.sin(angle)*speed - random.uniform(1, 3)
        self.life = 1.0
        self.decay = random.uniform(0.02, 0.045)
        self.size = random.uniform(4, 9)
        palettes = {
            "win":  [ACCENT, ACCENT2, GREEN, YELLOW, "#ff6ef7", "#60efff"],
            "lose": [RED, "#ff4444", "#ff8888", YELLOW],
            "tie":  [YELLOW, ACCENT, WHITE, GREY],
        }
        self.color = random.choice(palettes.get(burst_type, palettes["win"]))

    def update(self):
        self.x += self.vx; self.vy += 0.18; self.y += self.vy
        self.life -= self.decay; self.size *= 0.96

    def alive(self): return self.life > 0.05 and self.size > 1


class Star:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.x = random.uniform(0, w)
        self.y = random.uniform(0, h)
        self.r = random.uniform(0.5, 2.0)
        self.speed = random.uniform(0.1, 0.5)
        self.phase = random.uniform(0, math.pi*2)
        self.twinkle_speed = random.uniform(0.01, 0.04)

    def update(self):
        self.phase += self.twinkle_speed
        self.y += self.speed
        if self.y > self.h:
            self.y = 0
            self.x = random.uniform(0, self.w)

    def alpha(self): return 0.3 + 0.7*abs(math.sin(self.phase))


class AnimBG(tk.Canvas):
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=BG, highlightthickness=0, **kw)
        self.W = self.H = 1
        self.t = 0
        self.stars, self.particles = [], []
        self.orbs = [
            {"rx":0.25,"ry":0.25,"r":160,"color":"#2a1080","sx":0.0008,"sy":0.0006,"px":0,"py":1},
            {"rx":0.75,"ry":0.55,"r":130,"color":"#0a2a70","sx":0.0012,"sy":0.0009,"px":2,"py":0},
            {"rx":0.50,"ry":0.85,"r":100,"color":"#4a0a60","sx":0.0010,"sy":0.0007,"px":4,"py":3},
        ]
        self.bind("<Configure>", self._resize)
        self._loop()

    def _resize(self, e):
        self.W, self.H = e.width, e.height
        self.stars = [Star(self.W, self.H) for _ in range(100)]

    def burst(self, x, y, burst_type="win", n=45):
        for _ in range(n):
            self.particles.append(Particle(x, y, burst_type))

    @staticmethod
    def _blend(fg, bg, a):
        def p(h): h=h.lstrip("#"); return int(h[:2],16),int(h[2:4],16),int(h[4:6],16)
        fr,fg_,fb = p(fg); br,bg_,bb = p(bg)
        return "#{:02x}{:02x}{:02x}".format(
            int(br+(fr-br)*a), int(bg_+(fg_-bg_)*a), int(bb+(fb-bb)*a))

    def _loop(self):
        self.t += 1
        if self.W > 1:
            self._draw()
        self.after(16, self._loop)

    def _draw(self):
        self.delete("bg")
        W, H, t = self.W, self.H, self.t
        # background
        self.create_rectangle(0,0,W,H, fill=BG, outline="", tags="bg")
        # orbs
        for o in self.orbs:
            o["px"] += o["sx"]; o["py"] += o["sy"]
            cx = W*o["rx"] + math.sin(o["px"])*50
            cy = H*o["ry"] + math.cos(o["py"])*35
            for s, a in [(1.0,1.0),(0.65,0.55),(0.35,0.25),(0.15,0.1)]:
                r = o["r"]*s
                c = self._blend(o["color"], BG, a)
                self.create_oval(cx-r,cy-r,cx+r,cy+r, fill=c, outline="", tags="bg")
        # grid
        sp = 44
        ox = int(t*0.5)%sp; oy = int(t*0.3)%sp
        gc = self._blend("#4040ff", BG, 0.07)
        for x in range(-sp, W+sp, sp):
            self.create_line(int(x+ox),0,int(x+ox),H, fill=gc, width=1, tags="bg")
        for y in range(-sp, H+sp, sp):
            self.create_line(0,int(y+oy),W,int(y+oy), fill=gc, width=1, tags="bg")
        # stars
        for s in self.stars:
            s.update()
            a = s.alpha()
            c = self._blend("#c0c0ff", BG, a*0.9)
            r = max(0.5, s.r)
            self.create_oval(s.x-r,s.y-r,s.x+r,s.y+r, fill=c, outline="", tags="bg")
        # particles
        alive = []
        for p in self.particles:
            p.update()
            if p.alive():
                c = self._blend(p.color, BG, p.life)
                r = max(1, p.size)
                self.create_oval(p.x-r,p.y-r,p.x+r,p.y+r, fill=c, outline="", tags="bg")
                alive.append(p)
        self.particles = alive


class Tooltip:
    def __init__(self, widget, text):
        self.widget, self.text = widget, text
        self.tip = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, e):
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        tk.Label(self.tip, text=self.text, bg=CARD2, fg=WHITE,
                 font=("Segoe UI",9), padx=8, pady=4,
                 relief="flat", bd=0,
                 highlightbackground=BORDER, highlightthickness=1).pack()

    def _hide(self, e):
        if self.tip:
            self.tip.destroy(); self.tip = None


class Toast(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=CARD2, highlightbackground=ACCENT, highlightthickness=1)
        self.lbl = tk.Label(self, text="", bg=CARD2, fg=WHITE,
                            font=("Segoe UI Emoji",11,"bold"), padx=16, pady=8)
        self.lbl.pack()
        self._job = None

    def show(self, msg, root, ms=2800):
        self.lbl.config(text=msg)
        self.place(relx=0.5, rely=0.05, anchor="n")
        self.lift()
        if self._job: root.after_cancel(self._job)
        self._job = root.after(ms, self.place_forget)


class PillGroup(tk.Frame):
    def __init__(self, parent, options, default, callback=None, **kw):
        super().__init__(parent, bg=BG, **kw)
        self.var = tk.StringVar(value=str(default))
        self.cb = callback
        self.btns = {}
        for val, lbl in options:
            b = tk.Label(self, text=lbl, bg=CARD2, fg=GREY,
                         font=("Segoe UI",10), padx=14, pady=6, cursor="hand2",
                         relief="flat", highlightbackground=BORDER, highlightthickness=1)
            b.pack(side="left", padx=3, pady=2)
            b.bind("<Button-1>", lambda e, v=val: self._pick(v))
            b.bind("<Enter>", lambda e, w=b: w.config(fg=WHITE) if self.var.get()!=str(val) else None)
            b.bind("<Leave>", lambda e, w=b, v=val: w.config(fg=GREY) if self.var.get()!=str(v) else None)
            self.btns[str(val)] = b
        self._pick(str(default), silent=True)

    def _pick(self, val, silent=False):
        self.var.set(val)
        for k, b in self.btns.items():
            if k == val:
                b.config(bg=ACCENT, fg=WHITE, highlightbackground=ACCENT2,
                         font=("Segoe UI",10,"bold"))
            else:
                b.config(bg=CARD2, fg=GREY, highlightbackground=BORDER,
                         font=("Segoe UI",10))
        if not silent and self.cb:
            self.cb(val)

    def get(self): return self.var.get()


class MoveBtn(tk.Frame):
    def __init__(self, parent, move, emoji, callback, size=90):
        super().__init__(parent, bg=CARD, highlightbackground=BORDER,
                         highlightthickness=2, cursor="hand2")
        self.move = move
        self.callback = callback
        self._locked = False
        self._selected = False

        self.lbl_e = tk.Label(self, text=emoji, bg=CARD,
                              font=("Segoe UI Emoji", max(20, size//3)))
        self.lbl_n = tk.Label(self, text=move.upper(), bg=CARD, fg=GREY,
                              font=("Segoe UI", max(8, size//11), "bold"))
        self.lbl_e.pack(pady=(8,2))
        self.lbl_n.pack(pady=(0,8))

        for w in (self, self.lbl_e, self.lbl_n):
            w.bind("<Enter>",    self._enter)
            w.bind("<Leave>",    self._leave)
            w.bind("<Button-1>", self._click)

    def _enter(self, e):
        if not self._locked and not self._selected:
            self.config(bg=CARD2, highlightbackground=ACCENT)
            self.lbl_e.config(bg=CARD2); self.lbl_n.config(bg=CARD2, fg=ACCENT2)

    def _leave(self, e):
        if not self._locked and not self._selected:
            self.config(bg=CARD, highlightbackground=BORDER)
            self.lbl_e.config(bg=CARD); self.lbl_n.config(bg=CARD, fg=GREY)

    def _click(self, e):
        if not self._locked:
            self.callback(self.move)

    def select(self):
        self._selected = True
        self.config(bg=CARD2, highlightbackground=ACCENT2, highlightthickness=3)
        self.lbl_e.config(bg=CARD2); self.lbl_n.config(bg=CARD2, fg=ACCENT2)

    def lock(self): self._locked = True
    def unlock(self):
        self._locked = False; self._selected = False
        self.config(bg=CARD, highlightbackground=BORDER, highlightthickness=2)
        self.lbl_e.config(bg=CARD); self.lbl_n.config(bg=CARD, fg=GREY)

    def resize(self, size):
        self.lbl_e.config(font=("Segoe UI Emoji", max(20, size//3)))
        self.lbl_n.config(font=("Segoe UI", max(8, size//11), "bold"))


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("⚔️  Rock · Paper · Scissors  DELUXE")
        self.geometry("560x820")
        self.minsize(420, 620)
        self.configure(bg=BG)
        self.resizable(True, True)

        # game state
        self.G = MODES["classic"]
        self.mode = "classic"; self.diff = "normal"; self.target = 5
        self.player_name = "Player"
        self.scores = {"p":0,"c":0,"t":0}
        self.round_num = 1
        self.history, self.streak = [], []
        self.cpu_hist = {}
        self.locked = False; self.auto_job = None
        self.unlocked = set()
        self.stats = self._fresh_stats()

        # animated background (fills whole window)
        self.bg = AnimBG(self)
        self.bg.place(x=0,y=0,relwidth=1,relheight=1)

        # toast
        self.toast = Toast(self)

        # main scrollable content over the background
        self._build_ui()
        self.bind("<Configure>", self._on_resize)
        self.show("setup")

   
    def _fresh_stats(self):
        return {"wins":0,"max_streak":0,"cur_streak":0,
                "flawless":False,"comeback":False,
                "spock_wins":0,"total":0,"_was02":False}

    def _on_resize(self, e):
        if e.widget is not self: return
        W = e.width
        # dynamically resize move buttons
        btn_size = max(70, min(120, (W - 80) // len(self.G["moves"])))
        for b in getattr(self, "_move_btns", {}).values():
            b.resize(btn_size)

    def show(self, name):
        for n, f in self._screens.items():
            f.place_forget()
        self._screens[name].place(x=0,y=0,relwidth=1,relheight=1)
        self._screens[name].lift()
        self.toast.lift()
        if name == "game":
            self._refresh_game_ui()


    def _build_ui(self):
        self._screens = {}
        self._screens["setup"]   = self._build_setup()
        self._screens["game"]    = self._build_game()
        self._screens["victory"] = self._build_victory()

  
    def _build_setup(self):
        root = tk.Frame(self, bg="")  # transparent-ish
        root.configure(bg=BG)

        # centered card
        outer = tk.Frame(root, bg=BG)
        outer.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9)

        tk.Label(outer, text="⚔️", bg=BG, font=("Segoe UI Emoji",52)).pack(pady=(0,4))
        tk.Label(outer, text="ROCK · PAPER · SCISSORS",
                 bg=BG, fg=WHITE, font=("Segoe UI",16,"bold")).pack()
        tk.Label(outer, text="D E L U X E   E D I T I O N",
                 bg=BG, fg=ACCENT, font=("Segoe UI",9,"bold")).pack()
        tk.Label(outer, text="Configure your match and step into the arena",
                 bg=BG, fg=GREY, font=("Segoe UI",10)).pack(pady=(4,16))

        self._sep(outer)

        # name
        self._section_lbl(outer, "👤  YOUR NAME")
        nf = tk.Frame(outer, bg=CARD2, highlightbackground=BORDER, highlightthickness=1)
        nf.pack(fill="x", pady=(0,10))
        self._name_var = tk.StringVar(value="Player")
        ne = tk.Entry(nf, textvariable=self._name_var, bg=CARD2, fg=WHITE,
                      font=("Segoe UI",13), insertbackground=WHITE, bd=0,
                      highlightthickness=0, disabledbackground=CARD2)
        ne.pack(fill="x", padx=12, pady=10)
        ne.bind("<FocusIn>",  lambda e: nf.config(highlightbackground=ACCENT))
        ne.bind("<FocusOut>", lambda e: nf.config(highlightbackground=BORDER))

        self._section_lbl(outer, "🎮  GAME MODE")
        self._mode_pills = PillGroup(outer,
            [("classic","🪨  Classic (3 moves)"), ("spock","🖖  Lizard-Spock (5 moves)")],
            "classic")
        self._mode_pills.pack(fill="x", pady=(0,10))

        self._section_lbl(outer, "🧠  DIFFICULTY")
        self._diff_pills = PillGroup(outer,
            [("easy","😊 Easy"), ("normal","⚔️ Normal"), ("hard","🤖 Hard AI")],
            "normal")
        self._diff_pills.pack(fill="x", pady=(0,10))

        self._section_lbl(outer, "🏆  MATCH LENGTH")
        self._tgt_pills = PillGroup(outer,
            [(3,"Best of 3"),(5,"Best of 5"),(7,"Best of 7"),(999,"∞ Endless")],
            5)
        self._tgt_pills.pack(fill="x", pady=(0,20))

        self._sep(outer)

        btn = tk.Label(outer, text="⚔️   START GAME", bg=ACCENT, fg=WHITE,
                       font=("Segoe UI",13,"bold"), pady=14, cursor="hand2",
                       highlightbackground=ACCENT2, highlightthickness=2)
        btn.pack(fill="x", pady=(14,4))
        btn.bind("<Button-1>", lambda e: self._start_game())
        btn.bind("<Enter>", lambda e: btn.config(bg=ACCENT2))
        btn.bind("<Leave>", lambda e: btn.config(bg=ACCENT))

        tk.Label(outer, text="No installation needed · 100% Python · tkinter",
                 bg=BG, fg=DIMGREY, font=("Segoe UI",8)).pack(pady=6)
        return root

   
    def _build_game(self):
        root = tk.Frame(self, bg=BG)

        # ── header bar
        hdr = tk.Frame(root, bg=BG2, highlightbackground=BORDER, highlightthickness=1)
        hdr.pack(fill="x")
        self._lbl_player = tk.Label(hdr, text="Player", bg=BG2, fg=WHITE,
                                    font=("Segoe UI",13,"bold"), padx=14, pady=10)
        self._lbl_player.pack(side="left")
        self._lbl_mode_tag = tk.Label(hdr, text="", bg=BG2, fg=DIMGREY,
                                      font=("Segoe UI",9))
        self._lbl_mode_tag.pack(side="left")

        for txt, tip, cmd in [
            ("⟳","Reset scores", self._reset_scores),
            ("📖","View rules",   self._show_rules),
            ("⚙","Settings",     lambda: self.show("setup")),
        ]:
            b = tk.Label(hdr, text=txt, bg=CARD2, fg=GREY,
                         font=("Segoe UI Emoji",13), padx=12, pady=8,
                         cursor="hand2", highlightbackground=BORDER, highlightthickness=1)
            b.pack(side="right", padx=4, pady=6)
            b.bind("<Button-1>", lambda e, c=cmd: c())
            b.bind("<Enter>", lambda e, w=b: w.config(bg=CARD, fg=WHITE))
            b.bind("<Leave>", lambda e, w=b: w.config(bg=CARD2, fg=GREY))
            Tooltip(b, tip)

        # ── scrollable area
        sc = tk.Canvas(root, bg=BG, highlightthickness=0)
        sb = tk.Scrollbar(root, orient="vertical", command=sc.yview, bg=BG,
                          troughcolor=BG2, activebackground=ACCENT)
        sc.configure(yscrollcommand=sb.set)
        sc.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        inner = tk.Frame(sc, bg=BG)
        win_id = sc.create_window((0,0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda e: sc.configure(scrollregion=sc.bbox("all")))
        sc.bind("<Configure>",    lambda e: sc.itemconfig(win_id, width=e.width))

        # mousewheel scroll
        def _scroll(e):
            sc.yview_scroll(int(-1*(e.delta/120)), "units")
        sc.bind_all("<MouseWheel>", _scroll)

        P = {"padx":18, "pady":4}

        # ── scoreboard
        sb_row = tk.Frame(inner, bg=BG)
        sb_row.pack(fill="x", padx=18, pady=(14,6))

        # player card
        pcard = tk.Frame(sb_row, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        pcard.pack(side="left", fill="x", expand=True, padx=(0,6), ipady=8)
        tk.Label(pcard, text="YOU", bg=CARD, fg=GREY, font=("Segoe UI",9,"bold")).pack(pady=(6,0))
        self._lbl_pscore = tk.Label(pcard, text="0", bg=CARD, fg=GREEN,
                                    font=("Segoe UI",32,"bold"))
        self._lbl_pscore.pack()
        self._lbl_pname2 = tk.Label(pcard, text="Player", bg=CARD, fg=DIMGREY,
                                    font=("Segoe UI",9))
        self._lbl_pname2.pack(pady=(0,6))

        # center
        mid = tk.Frame(sb_row, bg=BG)
        mid.pack(side="left", padx=8)
        tk.Label(mid, text="VS", bg=BG, fg=GREY, font=("Segoe UI",14,"bold")).pack()
        self._lbl_round = tk.Label(mid, text="Round 1", bg=BG, fg=DIMGREY,
                                   font=("Segoe UI",9))
        self._lbl_round.pack()

        # cpu card
        ccard = tk.Frame(sb_row, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        ccard.pack(side="left", fill="x", expand=True, padx=(6,0), ipady=8)
        tk.Label(ccard, text="CPU", bg=CARD, fg=GREY, font=("Segoe UI",9,"bold")).pack(pady=(6,0))
        self._lbl_cscore = tk.Label(ccard, text="0", bg=CARD, fg=RED,
                                    font=("Segoe UI",32,"bold"))
        self._lbl_cscore.pack()
        tk.Label(ccard, text="Computer", bg=CARD, fg=DIMGREY, font=("Segoe UI",9)).pack(pady=(0,6))

        # ── win-progress bar
        prog_frame = tk.Frame(inner, bg=BG)
        prog_frame.pack(fill="x", padx=18, pady=(0,6))
        self._prog_canvas = tk.Canvas(prog_frame, bg=CARD, height=6,
                                      highlightthickness=0)
        self._prog_canvas.pack(fill="x")
        self._prog_bar = self._prog_canvas.create_rectangle(0,0,0,6, fill=ACCENT, outline="")

        # ── arena
        arena = tk.Frame(inner, bg=CARD2, highlightbackground=BORDER, highlightthickness=1)
        arena.pack(fill="x", padx=18, pady=8)
        arena.columnconfigure(0, weight=1); arena.columnconfigure(2, weight=1)

        pf = tk.Frame(arena, bg=CARD2); pf.grid(row=0, column=0, sticky="nsew", padx=10, pady=16)
        self._lbl_p_tag  = tk.Label(pf, text="You",  bg=CARD2, fg=GREY,   font=("Segoe UI",10))
        self._lbl_p_hand = tk.Label(pf, text="🤔",   bg=CARD2, font=("Segoe UI Emoji",52))
        self._lbl_p_move = tk.Label(pf, text="",     bg=CARD2, fg=ACCENT2, font=("Segoe UI",10,"bold"))
        self._lbl_p_tag.pack(); self._lbl_p_hand.pack(); self._lbl_p_move.pack()

        cf = tk.Frame(arena, bg=CARD2); cf.grid(row=0, column=2, sticky="nsew", padx=10, pady=16)
        tk.Label(cf, text="CPU",  bg=CARD2, fg=GREY,   font=("Segoe UI",10)).pack()
        self._lbl_c_hand = tk.Label(cf, text="🤔",    bg=CARD2, font=("Segoe UI Emoji",52))
        self._lbl_c_move = tk.Label(cf, text="",      bg=CARD2, fg=ACCENT2, font=("Segoe UI",10,"bold"))
        self._lbl_c_hand.pack(); self._lbl_c_move.pack()

        mf = tk.Frame(arena, bg=CARD2); mf.grid(row=0, column=1, sticky="nsew")
        self._lbl_vs = tk.Label(mf, text="VS", bg=CARD2, fg=GREY,
                                font=("Segoe UI",16,"bold"))
        self._lbl_vs.pack(expand=True)

        # ── result banner
        self._result_frame = tk.Frame(inner, bg=CARD2,
                                      highlightbackground=BORDER, highlightthickness=1)
        self._result_frame.pack(fill="x", padx=18, pady=4)
        self._lbl_result = tk.Label(self._result_frame, text="👇  Choose your move below!",
                                    bg=CARD2, fg=GREY, font=("Segoe UI",12,"bold"),
                                    pady=12, wraplength=460, justify="center")
        self._lbl_result.pack()

        # ── moves label
        self._lbl_moves_head = tk.Label(inner, text="YOUR MOVE", bg=BG, fg=ACCENT2,
                                        font=("Segoe UI",9,"bold"))
        self._lbl_moves_head.pack(pady=(10,4))

        # ── moves container (rebuilt dynamically)
        self._moves_frame = tk.Frame(inner, bg=BG)
        self._moves_frame.pack(pady=(0,4))
        self._move_btns = {}

        # ── streak
        st_row = tk.Frame(inner, bg=BG)
        st_row.pack(pady=4)
        tk.Label(st_row, text="Streak:", bg=BG, fg=GREY, font=("Segoe UI",10)).pack(side="left")
        self._lbl_streak = tk.Label(st_row, text="○ ○ ○ ○ ○", bg=BG, fg=DIMGREY,
                                    font=("Segoe UI",14))
        self._lbl_streak.pack(side="left", padx=8)
        self._lbl_streak_tag = tk.Label(st_row, text="", bg=BG, fg=YELLOW,
                                        font=("Segoe UI",10,"bold"))
        self._lbl_streak_tag.pack(side="left")

        # ── action row
        ar = tk.Frame(inner, bg=BG)
        ar.pack(fill="x", padx=18, pady=8)
        self._auto_btn = self._action_btn(ar, "▶  Watch CPU",    self._toggle_auto, "left")
        self._action_btn(ar, "📖  Rules",        self._show_rules, "left")
        self._action_btn(ar, "🗂  History",       self._toggle_history, "right")
        self._action_btn(ar, "🏆  Achievements", self._toggle_achs, "right")

        self._sep2(inner)

        # ── history panel (collapsible)
        self._hist_visible = True
        self._hist_section = tk.Frame(inner, bg=BG)
        self._hist_section.pack(fill="x", padx=18, pady=(0,4))
        tk.Label(self._hist_section, text="🕐  MATCH HISTORY", bg=BG, fg=ACCENT2,
                 font=("Segoe UI",9,"bold")).pack(anchor="w", pady=(0,4))
        self._hist_frame = tk.Frame(self._hist_section, bg=BG)
        self._hist_frame.pack(fill="x")

        self._sep2(inner)

        # ── achievements panel (collapsible)
        self._ach_visible = True
        self._ach_section = tk.Frame(inner, bg=BG)
        self._ach_section.pack(fill="x", padx=18, pady=(0,20))
        tk.Label(self._ach_section, text="🏆  ACHIEVEMENTS", bg=BG, fg=ACCENT2,
                 font=("Segoe UI",9,"bold")).pack(anchor="w", pady=(0,4))
        self._ach_frame = tk.Frame(self._ach_section, bg=BG)
        self._ach_frame.pack(fill="x")

        return root


    def _build_victory(self):
        root = tk.Frame(self, bg=BG)
        inner = tk.Frame(root, bg=BG)
        inner.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.88)

        self._vic_icon  = tk.Label(inner, text="🏆", bg=BG, font=("Segoe UI Emoji",72))
        self._vic_icon.pack(pady=(0,8))
        self._vic_title = tk.Label(inner, text="You won!", bg=BG, fg=WHITE,
                                   font=("Segoe UI",22,"bold"))
        self._vic_title.pack()
        self._vic_sub   = tk.Label(inner, text="", bg=BG, fg=GREY, font=("Segoe UI",12))
        self._vic_sub.pack(pady=4)

        tk.Frame(inner, bg=BG, height=14).pack()

        stats_row = tk.Frame(inner, bg=BG)
        stats_row.pack(fill="x", pady=8)
        self._vic_labels = {}
        for key, label, color in [("p","YOUR WINS",GREEN),("t","TIES",YELLOW),("c","CPU WINS",RED)]:
            c = tk.Frame(stats_row, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
            c.pack(side="left", fill="x", expand=True, padx=5, ipady=10)
            tk.Label(c, text=label, bg=CARD, fg=GREY, font=("Segoe UI",9,"bold")).pack(pady=(8,0))
            v = tk.Label(c, text="0", bg=CARD, fg=color, font=("Segoe UI",28,"bold"))
            v.pack(pady=(0,8))
            self._vic_labels[key] = v

        tk.Frame(inner, bg=BG, height=20).pack()

        pa = tk.Label(inner, text="🎮   PLAY AGAIN", bg=ACCENT, fg=WHITE,
                      font=("Segoe UI",13,"bold"), pady=14, cursor="hand2",
                      highlightbackground=ACCENT2, highlightthickness=2)
        pa.pack(fill="x")
        pa.bind("<Button-1>", lambda e: self._play_again())
        pa.bind("<Enter>", lambda e: pa.config(bg=ACCENT2))
        pa.bind("<Leave>", lambda e: pa.config(bg=ACCENT))

        tk.Frame(inner, bg=BG, height=8).pack()
        ch = tk.Label(inner, text="⚙  Change settings", bg=BG, fg=GREY,
                      font=("Segoe UI",11), cursor="hand2")
        ch.pack()
        ch.bind("<Button-1>", lambda e: self.show("setup"))
        ch.bind("<Enter>", lambda e: ch.config(fg=WHITE))
        ch.bind("<Leave>", lambda e: ch.config(fg=GREY))

        return root

 
    def _sep(self, parent):
        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", pady=8)

    def _sep2(self, parent):
        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", padx=18, pady=6)

    def _section_lbl(self, parent, text):
        tk.Label(parent, text=text, bg=BG, fg=ACCENT2,
                 font=("Segoe UI",9,"bold")).pack(anchor="w", pady=(10,3))

    def _action_btn(self, parent, text, cmd, side):
        b = tk.Label(parent, text=text, bg=CARD2, fg=GREY,
                     font=("Segoe UI",10), pady=8, padx=10, cursor="hand2",
                     highlightbackground=BORDER, highlightthickness=1)
        b.pack(side=side, fill="x", expand=True, padx=3)
        b.bind("<Button-1>", lambda e: cmd())
        b.bind("<Enter>", lambda e: b.config(bg=CARD, fg=WHITE))
        b.bind("<Leave>", lambda e: b.config(bg=CARD2, fg=GREY))
        return b


    def _start_game(self):
        self.player_name = self._name_var.get().strip() or "Player"
        self.mode   = self._mode_pills.get()
        self.diff   = self._diff_pills.get()
        self.target = int(self._tgt_pills.get())
        self.G      = MODES[self.mode]
        self.scores = {"p":0,"c":0,"t":0}
        self.round_num = 1
        self.history = []; self.streak = []; self.cpu_hist = {}
        self.locked = False; self.stats = self._fresh_stats()
        if self.auto_job: self.after_cancel(self.auto_job); self.auto_job = None
        self._build_move_buttons()
        self.show("game")

    def _refresh_game_ui(self):
        self._lbl_player.config(text=self.player_name)
        self._lbl_pname2.config(text=self.player_name)
        self._lbl_p_tag.config(text=self.player_name)
        mode_str = "Classic" if self.mode=="classic" else "Lizard-Spock"
        tgt_str  = f"Best of {self.target}" if self.target<999 else "Endless"
        self._lbl_mode_tag.config(text=f"  {mode_str} · {self.diff.title()} · {tgt_str}")
        self._lbl_pscore.config(text=str(self.scores["p"]))
        self._lbl_cscore.config(text=str(self.scores["c"]))
        self._lbl_round.config(text=f"Round {self.round_num}")
        self._lbl_p_hand.config(text="🤔"); self._lbl_c_hand.config(text="🤔")
        self._lbl_p_move.config(text="");   self._lbl_c_move.config(text="")
        self._lbl_vs.config(text="VS", fg=GREY)
        self._lbl_result.config(text="👇  Choose your move below!", bg=CARD2, fg=GREY)
        self._result_frame.config(bg=CARD2, highlightbackground=BORDER)
        self._lbl_streak.config(text="○ ○ ○ ○ ○", fg=DIMGREY)
        self._lbl_streak_tag.config(text="")
        self._update_progress()
        self._render_hist(); self._render_achs()

    def _build_move_buttons(self):
        for w in self._moves_frame.winfo_children(): w.destroy()
        self._move_btns = {}
        W = self.winfo_width() or 560
        btn_size = max(70, min(120, (W-80)//len(self.G["moves"])))
        for move in self.G["moves"]:
            b = MoveBtn(self._moves_frame, move, self.G["emojis"][move],
                        self._play, btn_size)
            b.pack(side="left", padx=5, pady=4)
            Tooltip(b, f"Play {move.title()}")
            self._move_btns[move] = b

    def _get_cpu(self, user_move):
        mv = self.G["moves"]
        if self.diff == "easy":
            for k,v in self.G["beats"].items():
                if user_move in v: return k
        if self.diff == "hard" and self.cpu_hist:
            pred = max(self.cpu_hist, key=self.cpu_hist.get)
            for k,v in self.G["beats"].items():
                if pred in v: return k
        return random.choice(mv)

    def _get_result(self, u, c):
        if u==c: return "tie"
        return "win" if c in self.G["beats"][u] else "lose"

    def _play(self, user_move, is_cpu=False):
        if self.locked: return
        if self.auto_job and not is_cpu:
            self.after_cancel(self.auto_job); self.auto_job=None
            self._auto_btn.config(text="▶  Watch CPU")

        self.locked = True
        self.cpu_hist[user_move] = self.cpu_hist.get(user_move,0)+1
        cpu_move = random.choice(self.G["moves"]) if is_cpu else self._get_cpu(user_move)

        # lock & highlight buttons
        for m, b in self._move_btns.items():
            b.lock()
            if m == user_move: b.select()

        self._lbl_p_hand.config(text="✊"); self._lbl_c_hand.config(text="✊")
        self._lbl_p_move.config(text="");   self._lbl_c_move.config(text="")
        self._lbl_result.config(text="", bg=CARD2)
        self._result_frame.config(bg=CARD2)
        self._countdown(3, user_move, cpu_move)

    def _countdown(self, n, um, cm):
        count_colors = {3: YELLOW, 2: ACCENT2, 1: GREEN}
        if n > 0:
            self._lbl_vs.config(text=str(n), fg=count_colors.get(n, WHITE),
                                font=("Segoe UI",22,"bold"))
            self.after(500, lambda: self._countdown(n-1, um, cm))
        else:
            self._lbl_vs.config(text="VS", fg=GREY, font=("Segoe UI",16,"bold"))
            self._reveal(um, cm)

    def _reveal(self, um, cm):
        G = self.G
        result = self._get_result(um, cm)
        self.stats["total"] += 1
        self._lbl_p_hand.config(text=G["emojis"][um])
        self._lbl_c_hand.config(text=G["emojis"][cm])
        self._lbl_p_move.config(text=um.upper())
        self._lbl_c_move.config(text=cm.upper())

        s = self.scores; st = self.stats
        needed = math.ceil(self.target/2) if self.target<999 else 99999

        if result == "tie":
            s["t"] += 1; st["cur_streak"] = 0; self.streak.append("t")
            self._result_frame.config(bg=YELLOW2, highlightbackground=YELLOW)
            self._lbl_result.config(text="🤝  It's a tie! Great minds think alike.",
                                    bg=YELLOW2, fg=YELLOW)
            self._burst("tie")
        elif result == "win":
            s["p"] += 1; st["wins"] += 1; st["cur_streak"] += 1
            st["max_streak"] = max(st["max_streak"], st["cur_streak"])
            if um=="spock": st["spock_wins"] += 1
            if s["c"]==0 and s["p"]==needed: st["flawless"]=True
            if st.get("_was02") and s["p"]>s["c"]: st["comeback"]=True
            rule = G["rules"][um][cm]
            self._result_frame.config(bg=GREEN2, highlightbackground=GREEN)
            self._lbl_result.config(
                text=f"✅  You win!  {G['emojis'][um]} {um} {rule} {G['emojis'][cm]} {cm}",
                bg=GREEN2, fg=GREEN)
            self.streak.append("w")
            self._burst("win")
        else:
            s["c"] += 1; st["cur_streak"] = 0; self.streak.append("l")
            if s["c"]==2 and s["p"]==0: st["_was02"]=True
            rule = G["rules"][cm][um]
            self._result_frame.config(bg=RED2, highlightbackground=RED)
            self._lbl_result.config(
                text=f"❌  CPU wins!  {G['emojis'][cm]} {cm} {rule} {G['emojis'][um]} {um}",
                bg=RED2, fg=RED)
            self._burst("lose")

        self._lbl_pscore.config(text=str(s["p"]))
        self._lbl_cscore.config(text=str(s["c"]))
        self.round_num += 1
        self._lbl_round.config(text=f"Round {self.round_num}")
        if len(self.streak)>5: self.streak.pop(0)
        self.history.insert(0,{"rd":self.round_num-1,"you":um,"cpu":cm,
                                "result":result,"eu":G["emojis"][um],"ec":G["emojis"][cm]})
        self._update_streak(); self._update_progress()
        self._render_hist(); self._check_achs()

        if s["p"]>=needed or s["c"]>=needed:
            self.after(1100, lambda: self._show_victory(s["p"]>=needed))
        else:
            self.after(750, self._unlock_moves)

    def _burst(self, kind):
        try:
            x = self._lbl_p_hand.winfo_rootx()-self.bg.winfo_rootx()+30
            y = self._lbl_p_hand.winfo_rooty()-self.bg.winfo_rooty()+30
            self.bg.burst(x, y, kind, 40)
        except Exception: pass

    def _unlock_moves(self):
        for b in self._move_btns.values(): b.unlock()
        self.locked = False

    def _update_streak(self):
        s = self.streak[-5:]
        icons = {"w":"●","l":"●","t":"●"}
        color_map = {"w":GREEN,"l":RED,"t":YELLOW}
        dots = " ".join(icons.get(r,"○") for r in s) + " ○"*(5-len(s))
        clr = color_map.get(s[-1], DIMGREY) if s else DIMGREY
        self._lbl_streak.config(text=dots, fg=clr)
        run=0
        if self.streak:
            last=self.streak[-1]
            for r in reversed(self.streak):
                if r==last: run+=1
                else: break
        label = f"{run}✕ {'WINS!' if self.streak and self.streak[-1]=='w' else 'LOSSES!' if self.streak and self.streak[-1]=='l' else 'TIES!'}" if run>=3 else ""
        self._lbl_streak_tag.config(text=label)

    def _update_progress(self):
        needed = math.ceil(self.target/2) if self.target<999 else 1
        p = self.scores["p"]; c = self.scores["c"]
        try:
            W = self._prog_canvas.winfo_width() or 400
            mid = W//2
            # player bar (left→mid)
            pw = int(mid*(p/needed)) if needed else 0
            # cpu bar (mid→right)
            cw = int(mid*(c/needed)) if needed else 0
            self._prog_canvas.delete("all")
            self._prog_canvas.create_rectangle(0,0,W,6, fill=CARD, outline="")
            if pw: self._prog_canvas.create_rectangle(mid-pw,0,mid,6, fill=GREEN, outline="")
            if cw: self._prog_canvas.create_rectangle(mid,0,mid+cw,6, fill=RED, outline="")
            self._prog_canvas.create_rectangle(mid-1,0,mid+1,6, fill=WHITE, outline="")
        except Exception: pass

    def _render_hist(self):
        for w in self._hist_frame.winfo_children(): w.destroy()
        if not self.history:
            tk.Label(self._hist_frame, text="No rounds yet", bg=BG, fg=DIMGREY,
                     font=("Segoe UI",10)).pack()
            return
        for h in self.history[:10]:
            row = tk.Frame(self._hist_frame, bg=CARD,
                           highlightbackground=BORDER, highlightthickness=1)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=f"Rd {h['rd']}", bg=CARD, fg=DIMGREY,
                     font=("Segoe UI",9), width=5).pack(side="left", padx=8, pady=5)
            tk.Label(row, text=f"{h['eu']} {h['you']}", bg=CARD, fg=WHITE,
                     font=("Segoe UI Emoji",10)).pack(side="left", padx=4)
            tk.Label(row, text="vs", bg=CARD, fg=DIMGREY,
                     font=("Segoe UI",9)).pack(side="left")
            tk.Label(row, text=f"{h['ec']} {h['cpu']}", bg=CARD, fg=WHITE,
                     font=("Segoe UI Emoji",10)).pack(side="left", padx=4)
            t,c = {"win":("WIN",GREEN),"lose":("LOSE",RED),"tie":("TIE",YELLOW)}[h["result"]]
            tk.Label(row, text=t, bg=CARD, fg=c,
                     font=("Segoe UI",10,"bold"), width=5).pack(side="right", padx=8)

    def _render_achs(self):
        for w in self._ach_frame.winfo_children(): w.destroy()
        cols = 2
        frames = [tk.Frame(self._ach_frame, bg=BG) for _ in range((len(ACHIEVEMENTS)+1)//cols)]
        for f in frames: f.pack(fill="x", pady=2)
        for i,(aid,name,desc,_) in enumerate(ACHIEVEMENTS):
            unlocked = aid in self.unlocked
            row = frames[i//cols]
            card = tk.Frame(row, bg="#161635" if unlocked else CARD,
                            highlightbackground=ACCENT if unlocked else BORDER,
                            highlightthickness=1)
            card.pack(side="left", fill="x", expand=True, padx=3, ipady=4)
            icon, lbl = name.split(" ",1)
            tk.Label(card, text=icon, bg=card.cget("bg"),
                     font=("Segoe UI Emoji",16)).pack(anchor="w", padx=8, pady=(6,0))
            tk.Label(card, text=lbl, bg=card.cget("bg"),
                     fg=ACCENT2 if unlocked else GREY,
                     font=("Segoe UI",9,"bold")).pack(anchor="w", padx=8)
            tk.Label(card, text=desc, bg=card.cget("bg"), fg=DIMGREY,
                     font=("Segoe UI",8), wraplength=150).pack(anchor="w", padx=8, pady=(0,6))

    def _check_achs(self):
        for aid, name, desc, check in ACHIEVEMENTS:
            if aid not in self.unlocked and check(self.stats):
                self.unlocked.add(aid)
                self.toast.show(f"{name}  unlocked!", self)
                self._render_achs()

    def _toggle_auto(self):
        if self.auto_job:
            self.after_cancel(self.auto_job); self.auto_job=None
            self._auto_btn.config(text="▶  Watch CPU"); return
        self._auto_btn.config(text="⏹  Stop")
        def _tick():
            if not self.locked and self._move_btns:
                self._play(random.choice(list(self._move_btns.keys())), is_cpu=True)
            self.auto_job = self.after(1800, _tick)
        _tick()

    def _toggle_history(self):
        self._hist_visible = not self._hist_visible
        if self._hist_visible: self._hist_frame.pack(fill="x")
        else: self._hist_frame.pack_forget()

    def _toggle_achs(self):
        self._ach_visible = not self._ach_visible
        if self._ach_visible: self._ach_frame.pack(fill="x")
        else: self._ach_frame.pack_forget()

    def _show_rules(self):
        w = tk.Toplevel(self)
        w.title("📖 Game Rules")
        w.configure(bg=BG)
        w.geometry("420x460")
        w.resizable(True, True)
        tk.Label(w, text="📖  GAME RULES", bg=BG, fg=WHITE,
                 font=("Segoe UI",14,"bold")).pack(pady=14)
        tk.Frame(w, bg=BORDER, height=1).pack(fill="x", padx=20, pady=4)
        for m in self.G["moves"]:
            for beaten in self.G["beats"][m]:
                rule = self.G["rules"][m][beaten]
                row = tk.Frame(w, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
                row.pack(fill="x", padx=20, pady=3)
                tk.Label(row, text=self.G["emojis"][m], bg=CARD,
                         font=("Segoe UI Emoji",20)).pack(side="left", padx=12, pady=8)
                tk.Label(row, text=m.title(), bg=CARD, fg=WHITE,
                         font=("Segoe UI",11,"bold"), width=9).pack(side="left")
                tk.Label(row, text=rule, bg=CARD, fg=GREY,
                         font=("Segoe UI",10), width=14).pack(side="left")
                tk.Label(row, text=self.G["emojis"][beaten], bg=CARD,
                         font=("Segoe UI Emoji",20)).pack(side="left", padx=6)
                tk.Label(row, text=beaten.title(), bg=CARD, fg=WHITE,
                         font=("Segoe UI",11)).pack(side="left")

    def _reset_scores(self):
        if self.auto_job: self.after_cancel(self.auto_job); self.auto_job=None
        self.scores={"p":0,"c":0,"t":0}; self.round_num=1
        self.history=[]; self.streak=[]; self.cpu_hist={}
        self.locked=False; self.stats=self._fresh_stats()
        self._build_move_buttons()
        self._refresh_game_ui()
        self.toast.show("🔄  Scores reset!", self, 1500)

    def _show_victory(self, player_won):
        if self.auto_job: self.after_cancel(self.auto_job); self.auto_job=None
        self._vic_icon.config(text="🏆" if player_won else "😅")
        self._vic_title.config(text="You won the match!" if player_won else "CPU wins!",
                               fg=GREEN if player_won else RED)
        self._vic_sub.config(text="Brilliant — you dominated! 🎉" if player_won
                             else "Keep practicing, you'll get there! 💪")
        for k,v in self._vic_labels.items(): v.config(text=str(self.scores[k]))
        self.show("victory")

    def _play_again(self):
        self.scores={"p":0,"c":0,"t":0}; self.round_num=1
        self.history=[]; self.streak=[]; self.cpu_hist={}
        self.locked=False; self.stats=self._fresh_stats()
        if self.auto_job: self.after_cancel(self.auto_job); self.auto_job=None
        self._build_move_buttons()
        self.show("game")


if __name__ == "__main__":
    app = App()
    app.mainloop()