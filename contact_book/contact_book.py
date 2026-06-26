"""
ContactIQ 2026 - Personal Relationship Intelligence System
CodSoft Python Programming Internship - Task 5 (Upgraded)

Features:
  - Smart contact profiles (multi-phone, email, social, company, tags, notes)
  - AI-powered natural language search
  - Duplicate detection (phone + email)
  - Relationship health score
  - Interaction timeline / logging
  - Birthday & follow-up reminders
  - Smart groups & dynamic tag filtering
  - Contact analytics dashboard
  - Import (CSV / vCard) & Export (CSV / vCard / JSON)
  - Emergency contacts panel
  - Network graph visualization (canvas)
  - Modern dark-navy themed UI with coloured buttons
"""

import json
import os
import csv
import math
import tkinter as tk
from tkinter import messagebox, ttk, filedialog, simpledialog
from datetime import datetime, date
import colorsys
import random

# ── Constants 

CONTACTS_FILE = "contacts_pro.json"
APP_TITLE     = "ContactIQ 2026"
WIN_W, WIN_H  = 1100, 680

# Palette
C_NAVY      = "#0F1629"
C_NAVY2     = "#1A2340"
C_NAVY3     = "#243058"
C_INDIGO    = "#6366F1"
C_INDIGO_D  = "#4F46E5"
C_EMERALD   = "#10B981"
C_AMBER     = "#F59E0B"
C_ROSE      = "#F43F5E"
C_SKY       = "#0EA5E9"
C_WHITE     = "#F8FAFC"
C_MUTED     = "#94A3B8"
C_BORDER    = "#2A3555"
C_SURFACE   = "#141E35"
C_SURFACE2  = "#1C2940"

AVATAR_COLORS = [
    ("#6366F1","#C7D2FE"), ("#10B981","#A7F3D0"), ("#F59E0B","#FDE68A"),
    ("#F43F5E","#FECDD3"), ("#0EA5E9","#BAE6FD"), ("#8B5CF6","#DDD6FE"),
    ("#EC4899","#FBCFE8"), ("#14B8A6","#99F6E4"),
]

TAG_COLORS = {
    "family":   C_EMERALD,  "friend":   C_SKY,      "work":     C_INDIGO,
    "recruiter":C_AMBER,    "hr":       C_AMBER,     "client":   C_ROSE,
    "doctor":   C_EMERALD,  "college":  C_SKY,       "cyber":    C_INDIGO,
    "python":   C_INDIGO,   "network":  C_ROSE,      "mentor":   C_EMERALD,
}

# ── Persistence 

def load_contacts():
    if os.path.exists(CONTACTS_FILE):
        with open(CONTACTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_contacts(contacts):
    with open(CONTACTS_FILE, "w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=2, ensure_ascii=False)

# ── Utilities 


def avatar_colors(name):
    idx = (ord(name[0]) + len(name)) % len(AVATAR_COLORS)
    return AVATAR_COLORS[idx]

def initials(name):
    parts = name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return name[:2].upper()

def days_until_birthday(bday_str):
    if not bday_str:
        return None
    try:
        bday = date.fromisoformat(bday_str)
        today = date.today()
        next_bday = bday.replace(year=today.year)
        if next_bday < today:
            next_bday = next_bday.replace(year=today.year + 1)
        return (next_bday - today).days
    except Exception:
        return None

def birthday_soon(bday_str, days=7):
    d = days_until_birthday(bday_str)
    return d is not None and 0 <= d <= days

def score_color(score):
    if score >= 80:
        return C_EMERALD
    if score >= 55:
        return C_AMBER
    return C_ROSE

def score_label(score):
    if score >= 80:
        return "Strong"
    if score >= 55:
        return "Fair"
    return "Weak"

def ai_search(query, contacts):
    q = query.lower().strip()
    if not q:
        return list(contacts.keys())
    results = []
    for name, info in contacts.items():
        blob = " ".join([
            name,
            info.get("company", ""),
            info.get("role", ""),
            info.get("address", ""),
            " ".join(info.get("tags", [])),
            info.get("notes", ""),
            info.get("group", ""),
            " ".join(info.get("phones", [])),
            " ".join(info.get("emails", [])),
        ]).lower()

        # Natural language hints
        if "birthday" in q or "bday" in q:
            if birthday_soon(info.get("birthday", ""), days=30):
                results.append(name)
            continue
        if "emergency" in q:
            if info.get("emergency"):
                results.append(name)
            continue
        if "follow" in q and "up" in q:
            if info.get("score", 100) < 70:
                results.append(name)
            continue

        if any(word in blob for word in q.split()):
            results.append(name)
    return results

def detect_duplicates(contacts, name, phone, email):
    dups = []
    for cname, info in contacts.items():
        if cname == name:
            continue
        if phone and phone in info.get("phones", []):
            dups.append((cname, "same phone"))
        if email and email in info.get("emails", []):
            dups.append((cname, "same email"))
        if cname.lower() == name.lower():
            dups.append((cname, "same name"))
    return dups

def ai_suggestion(name, info):
    score = info.get("score", 50)
    tags  = [t.lower() for t in info.get("tags", [])]
    last  = info.get("interactions", [{}])[-1].get("when", "") if info.get("interactions") else ""
    days_inactive = 0
    if last:
        try:
            days_inactive = (date.today() - date.fromisoformat(last)).days
        except Exception:
            pass

    if score >= 85:
        return f"Excellent relationship with {name.split()[0]}. Keep momentum with a casual check-in."
    if days_inactive > 90:
        return f"You haven't connected with {name.split()[0]} in {days_inactive} days. A quick message could rekindle this bond."
    if days_inactive > 30:
        return f"It's been a month since last contact. Consider sending {name.split()[0]} a relevant article or update."
    if "recruiter" in tags or "hr" in tags:
        return f"{name.split()[0]} is a recruiter at {info.get('company','your target company')}. Share your latest achievements or portfolio."
    if "doctor" in tags or "emergency" in tags:
        return f"Keep {name.split()[0]}'s contact updated and accessible. Mark as emergency if needed."
    return f"Regular touchpoints with {name.split()[0]} will improve relationship health over time."

# ── Styled Widgets 

def styled_btn(parent, text, cmd, color=C_INDIGO, fg=C_WHITE, icon="", width=None, font_size=11):
    kwargs = dict(
        text=f"{icon} {text}".strip() if icon else text,
        command=cmd,
        bg=color, fg=fg,
        activebackground=C_NAVY3, activeforeground=C_WHITE,
        relief="flat", bd=0,
        font=("Segoe UI", font_size, "bold"),
        cursor="hand2",
        padx=12, pady=6,
    )
    if width:
        kwargs["width"] = width
    btn = tk.Button(parent, **kwargs)
    # Hover effect
    btn.bind("<Enter>", lambda e, b=btn, c=color: b.config(bg=_lighten(c, 0.15)))
    btn.bind("<Leave>", lambda e, b=btn, c=color: b.config(bg=c))
    return btn

def _lighten(hex_color, factor=0.2):
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i+2], 16)/255 for i in (0,2,4))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    l = min(1.0, l + factor)
    r2, g2, b2 = colorsys.hls_to_rgb(h, l, s)
    return "#{:02x}{:02x}{:02x}".format(int(r2*255), int(g2*255), int(b2*255))

def label_frame(parent, title, **kwargs):
    frame = tk.Frame(parent, bg=C_SURFACE2, **kwargs)
    tk.Label(frame, text=title, bg=C_SURFACE2, fg=C_MUTED,
             font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=10, pady=(8,2))
    sep = tk.Frame(frame, bg=C_BORDER, height=1)
    sep.pack(fill="x", padx=10)
    return frame

def scrollable_frame(parent, bg=C_SURFACE):
    canvas = tk.Canvas(parent, bg=bg, highlightthickness=0)
    vsb = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    inner = tk.Frame(canvas, bg=bg)
    inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0,0), window=inner, anchor="nw")
    canvas.configure(yscrollcommand=vsb.set)
    canvas.pack(side="left", fill="both", expand=True)
    vsb.pack(side="right", fill="y")
    # mousewheel
    canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
    return canvas, inner

def draw_avatar(canvas_widget, cx, cy, r, name, bg, fg):
    canvas_widget.create_oval(cx-r, cy-r, cx+r, cy+r, fill=bg, outline="", tags="avatar")
    canvas_widget.create_text(cx, cy, text=initials(name), fill=fg,
                              font=("Segoe UI", max(8, r//2), "bold"), tags="avatar")

# ── Main Application 

class ContactIQApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(f"{WIN_W}x{WIN_H}")
        self.root.resizable(True, True)
        self.root.configure(bg=C_NAVY)

        self.contacts = load_contacts()
        self.active_name = None
        self.active_group = "All"
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *_: self.refresh_list())

        self._apply_ttk_style()
        self._build_ui()
        self.refresh_list()
        self._check_reminders()

    # ── TTK Style 

    def _apply_ttk_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
            background=C_SURFACE, foreground=C_WHITE,
            fieldbackground=C_SURFACE, rowheight=44,
            font=("Segoe UI", 11), borderwidth=0)
        style.configure("Treeview.Heading",
            background=C_NAVY2, foreground=C_MUTED,
            font=("Segoe UI", 10, "bold"), relief="flat", borderwidth=0)
        style.map("Treeview",
            background=[("selected", C_INDIGO)],
            foreground=[("selected", C_WHITE)])
        style.configure("Vertical.TScrollbar",
            background=C_NAVY2, troughcolor=C_NAVY, arrowcolor=C_MUTED,
            borderwidth=0, width=8)

    # ── UI Build 

    def _build_ui(self):
        # Top bar
        self._build_topbar()

        # Body: sidebar + detail
        body = tk.Frame(self.root, bg=C_NAVY)
        body.pack(fill="both", expand=True)

        self._build_sidebar(body)
        self._build_detail(body)

    def _build_topbar(self):
        bar = tk.Frame(self.root, bg=C_NAVY2, height=54)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        # Brand
        brand_frame = tk.Frame(bar, bg=C_NAVY2)
        brand_frame.pack(side="left", padx=16)
        dot = tk.Canvas(brand_frame, width=10, height=10, bg=C_NAVY2,
                        highlightthickness=0)
        dot.pack(side="left", pady=2)
        dot.create_oval(1, 1, 9, 9, fill=C_INDIGO, outline="")
        tk.Label(brand_frame, text=" ContactIQ 2026", bg=C_NAVY2,
                 fg=C_WHITE, font=("Segoe UI", 14, "bold")).pack(side="left")

        # Right actions
        right = tk.Frame(bar, bg=C_NAVY2)
        right.pack(side="right", padx=12, pady=8)
        styled_btn(right, "Reminders", self._show_reminders,
                   color=C_AMBER, icon="🔔").pack(side="right", padx=4)
        styled_btn(right, "Export", self._export_menu,
                   color=C_NAVY3, icon="⬆").pack(side="right", padx=4)
        styled_btn(right, "Import", self._import_menu,
                   color=C_NAVY3, icon="⬇").pack(side="right", padx=4)
        styled_btn(right, "Add Contact", self._open_add,
                   color=C_INDIGO, icon="＋").pack(side="right", padx=4)

        # Search
        center = tk.Frame(bar, bg=C_NAVY2)
        center.pack(side="left", fill="x", expand=True, padx=8)
        tk.Label(center, text="🔍", bg=C_NAVY2, fg=C_MUTED,
                 font=("Segoe UI", 12)).pack(side="left")
        search_entry = tk.Entry(center, textvariable=self.search_var,
                                bg=C_SURFACE, fg=C_WHITE, insertbackground=C_WHITE,
                                relief="flat", font=("Segoe UI", 12), bd=0)
        search_entry.pack(side="left", fill="x", expand=True, ipady=6, padx=6)
        search_entry.insert(0, "")
        search_entry.bind("<FocusIn>",  lambda e: search_entry.config(bg=C_SURFACE2))
        search_entry.bind("<FocusOut>", lambda e: search_entry.config(bg=C_SURFACE))
        tk.Label(center, text='AI Search: try "recruiters Delhi" or "birthday"',
                 bg=C_NAVY2, fg=C_MUTED, font=("Segoe UI", 9)).pack(side="left", padx=4)

    def _build_sidebar(self, parent):
        self.sidebar = tk.Frame(parent, bg=C_NAVY, width=270)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Group tabs
        tab_frame = tk.Frame(self.sidebar, bg=C_NAVY2)
        tab_frame.pack(fill="x")
        self.group_btns = {}
        for grp in ["All", "Work", "Family", "Network", "⭐ Emergency"]:
            key = grp.replace("⭐ ", "")
            b = tk.Button(tab_frame, text=grp, bg=C_NAVY2 if grp!="All" else C_INDIGO,
                          fg=C_WHITE if grp=="All" else C_MUTED,
                          relief="flat", bd=0, cursor="hand2",
                          font=("Segoe UI", 10),
                          command=lambda g=key: self._switch_group(g))
            b.pack(side="left", padx=2, pady=6, ipadx=6, ipady=4)
            self.group_btns[key] = b

        sep = tk.Frame(self.sidebar, bg=C_BORDER, height=1)
        sep.pack(fill="x")

        # Stats bar
        self.stats_label = tk.Label(self.sidebar, text="", bg=C_NAVY,
                                    fg=C_MUTED, font=("Segoe UI", 9))
        self.stats_label.pack(anchor="w", padx=12, pady=(6,2))

        # Contact list (canvas-based for custom rendering)
        list_outer = tk.Frame(self.sidebar, bg=C_NAVY)
        list_outer.pack(fill="both", expand=True)

        self.list_canvas = tk.Canvas(list_outer, bg=C_NAVY,
                                     highlightthickness=0)
        vsb = ttk.Scrollbar(list_outer, orient="vertical",
                            command=self.list_canvas.yview)
        self.list_canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.list_canvas.pack(fill="both", expand=True)

        self.list_inner = tk.Frame(self.list_canvas, bg=C_NAVY)
        self._list_win = self.list_canvas.create_window(
            (0,0), window=self.list_inner, anchor="nw")
        self.list_inner.bind("<Configure>", self._on_list_configure)
        self.list_canvas.bind("<Configure>",
            lambda e: self.list_canvas.itemconfig(self._list_win, width=e.width))
        self.list_canvas.bind("<MouseWheel>",
            lambda e: self.list_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    def _on_list_configure(self, event=None):
        self.list_canvas.configure(scrollregion=self.list_canvas.bbox("all"))

    def _build_detail(self, parent):
        self.detail_frame = tk.Frame(parent, bg=C_SURFACE)
        self.detail_frame.pack(side="left", fill="both", expand=True)

        self.empty_label = tk.Label(
            self.detail_frame,
            text="👤  Select a contact to view details\nor add a new one with the button above",
            bg=C_SURFACE, fg=C_MUTED,
            font=("Segoe UI", 14), justify="center")
        self.empty_label.place(relx=0.5, rely=0.5, anchor="center")

        self.detail_inner = tk.Frame(self.detail_frame, bg=C_SURFACE)

    # ── Refresh / Render 

    def refresh_list(self):
        query = self.search_var.get().strip()
        filtered = ai_search(query, self.contacts)

        # Group filter
        if self.active_group not in ("All", "Emergency"):
            filtered = [n for n in filtered
                        if self.contacts[n].get("group","") == self.active_group]
        elif self.active_group == "Emergency":
            filtered = [n for n in filtered if self.contacts[n].get("emergency")]

        filtered.sort()

        self.stats_label.config(
            text=f"{len(filtered)} of {len(self.contacts)} contacts"
            + (f"  ·  search: '{query}'" if query else ""))

        # Clear
        for w in self.list_inner.winfo_children():
            w.destroy()

        if not filtered:
            tk.Label(self.list_inner, text="No contacts found",
                     bg=C_NAVY, fg=C_MUTED,
                     font=("Segoe UI", 11)).pack(pady=20)
            return

        for name in filtered:
            self._render_contact_row(name, self.contacts[name])

    def _render_contact_row(self, name, info):
        is_active = (name == self.active_name)
        row_bg = C_SURFACE2 if is_active else C_NAVY
        hover_bg = C_SURFACE2

        row = tk.Frame(self.list_inner, bg=row_bg, cursor="hand2")
        row.pack(fill="x", padx=6, pady=2)

        # Avatar canvas
        av_bg, av_fg = avatar_colors(name)
        av_canvas = tk.Canvas(row, width=40, height=40, bg=row_bg,
                              highlightthickness=0)
        av_canvas.pack(side="left", padx=(10,8), pady=8)
        av_canvas.create_oval(2, 2, 38, 38, fill=av_bg, outline="")
        av_canvas.create_text(20, 20, text=initials(name),
                              fill=av_fg, font=("Segoe UI", 12, "bold"))

        # Info
        info_frame = tk.Frame(row, bg=row_bg)
        info_frame.pack(side="left", fill="both", expand=True, pady=8)

        # Birthday icon
        bday_icon = " 🎂" if birthday_soon(info.get("birthday","")) else ""
        em_icon = " 🚨" if info.get("emergency") else ""

        tk.Label(info_frame, text=name + bday_icon + em_icon,
                 bg=row_bg, fg=C_WHITE,
                 font=("Segoe UI", 11, "bold"),
                 anchor="w").pack(fill="x")
        sub = info.get("role","") or info.get("company","")
        if info.get("company") and info.get("role"):
            sub = f"{info['role']} · {info['company']}"
        tk.Label(info_frame, text=sub, bg=row_bg, fg=C_MUTED,
                 font=("Segoe UI", 9), anchor="w").pack(fill="x")

        # Score pill
        sc = info.get("score", 50)
        pill_bg = score_color(sc)
        pill = tk.Label(row, text=str(sc), bg=pill_bg, fg=C_WHITE,
                        font=("Segoe UI", 9, "bold"), padx=8, pady=2)
        pill.pack(side="right", padx=10)

        # Click / hover bindings
        def on_click(n=name):
            self.active_name = n
            self.refresh_list()
            self._render_detail(n)

        def on_enter(e, r=row, ib=info_frame, ac=av_canvas):
            r.config(bg=hover_bg)
            ib.config(bg=hover_bg)
            for w in ib.winfo_children():
                w.config(bg=hover_bg)
            ac.config(bg=hover_bg)

        def on_leave(e, r=row, rb=row_bg, ib=info_frame, ac=av_canvas):
            r.config(bg=rb)
            ib.config(bg=rb)
            for w in ib.winfo_children():
                w.config(bg=rb)
            ac.config(bg=rb)

        for widget in [row, info_frame, av_canvas, pill] + info_frame.winfo_children():
            widget.bind("<Button-1>", lambda e, n=name: on_click(n))
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)

        # Active indicator bar
        if is_active:
            bar = tk.Frame(row, bg=C_INDIGO, width=3)
            bar.pack(side="left", fill="y", before=av_canvas)

    # ── Detail Panel 

    def _render_detail(self, name):
        self.empty_label.place_forget()
        self.detail_inner.destroy()
        self.detail_inner = tk.Frame(self.detail_frame, bg=C_SURFACE)
        self.detail_inner.pack(fill="both", expand=True)

        info = self.contacts[name]

        # ── Header ──
        header = tk.Frame(self.detail_inner, bg=C_NAVY2)
        header.pack(fill="x", padx=0)

        # Avatar
        av_bg, av_fg = avatar_colors(name)
        av_canvas = tk.Canvas(header, width=70, height=70, bg=C_NAVY2,
                              highlightthickness=0)
        av_canvas.pack(side="left", padx=20, pady=16)
        av_canvas.create_oval(3, 3, 67, 67, fill=av_bg, outline="")
        av_canvas.create_text(35, 35, text=initials(name),
                              fill=av_fg, font=("Segoe UI", 22, "bold"))

        # Name + role
        name_frame = tk.Frame(header, bg=C_NAVY2)
        name_frame.pack(side="left", pady=12, fill="both", expand=True)

        tk.Label(name_frame, text=name, bg=C_NAVY2, fg=C_WHITE,
                 font=("Segoe UI", 18, "bold"), anchor="w").pack(fill="x")
        role_str = ""
        if info.get("role") and info.get("company"):
            role_str = f"{info['role']}  ·  {info['company']}"
        elif info.get("role"):
            role_str = info["role"]
        tk.Label(name_frame, text=role_str, bg=C_NAVY2, fg=C_MUTED,
                 font=("Segoe UI", 11), anchor="w").pack(fill="x")

        # Tags
        tag_row = tk.Frame(name_frame, bg=C_NAVY2)
        tag_row.pack(fill="x", pady=(6,0))
        for tag in info.get("tags", [])[:6]:
            tc = TAG_COLORS.get(tag.lower(), C_INDIGO)
            tk.Label(tag_row, text=tag, bg=_lighten(C_NAVY2, 0.05),
                     fg=tc, font=("Segoe UI", 9),
                     padx=8, pady=2, relief="flat",
                     bd=1).pack(side="left", padx=3)

        # Action buttons
        btn_frame = tk.Frame(header, bg=C_NAVY2)
        btn_frame.pack(side="right", padx=16, pady=12)

        phones = info.get("phones", [])
        if phones:
            styled_btn(btn_frame, "Call", lambda n=name: self._call(n),
                       color=C_EMERALD, icon="📞").pack(pady=2)
        emails = info.get("emails", [])
        if emails:
            styled_btn(btn_frame, "Email", lambda n=name: self._email(n),
                       color=C_SKY, icon="✉").pack(pady=2)
        styled_btn(btn_frame, "Edit", lambda n=name: self._open_edit(n),
                   color=C_INDIGO, icon="✏").pack(pady=2)
        styled_btn(btn_frame, "Delete", lambda n=name: self._delete_contact(n),
                   color=C_ROSE, icon="🗑").pack(pady=2)

        # Reminders banners
        self._render_banners(name, info)

        # ── Tab bar ──
        self.active_tab = tk.StringVar(value="info")
        tab_bar = tk.Frame(self.detail_inner, bg=C_NAVY2)
        tab_bar.pack(fill="x")
        self._tab_buttons = {}
        for tab_key, tab_label in [
            ("info","📋  Info"), ("timeline","📅  Timeline"),
            ("network","🕸  Network"), ("analytics","📊  Analytics")
        ]:
            b = tk.Button(tab_bar, text=tab_label,
                          bg=C_INDIGO if tab_key=="info" else C_NAVY2,
                          fg=C_WHITE, relief="flat", bd=0, cursor="hand2",
                          font=("Segoe UI", 10, "bold"),
                          padx=14, pady=8,
                          command=lambda k=tab_key: self._switch_tab(k, name))
            b.pack(side="left")
            self._tab_buttons[tab_key] = b

        # Tab content area
        self.tab_content = tk.Frame(self.detail_inner, bg=C_SURFACE)
        self.tab_content.pack(fill="both", expand=True)

        self._render_tab("info", name)

    def _render_banners(self, name, info):
        bdays = days_until_birthday(info.get("birthday",""))
        if bdays is not None and 0 <= bdays <= 7:
            banner = tk.Frame(self.detail_inner, bg="#1E3A2F", pady=6)
            banner.pack(fill="x", padx=8, pady=(4,0))
            tk.Label(banner,
                     text=f"🎂  Birthday in {bdays} day{'s' if bdays!=1 else ''}! "
                          f"Consider sending a message.",
                     bg="#1E3A2F", fg=C_EMERALD,
                     font=("Segoe UI", 10)).pack(side="left", padx=12)

        score = info.get("score", 100)
        interactions = info.get("interactions", [])
        if interactions:
            last_when = interactions[-1].get("when","")
            try:
                days_ago = (date.today() - date.fromisoformat(last_when)).days
            except Exception:
                days_ago = 0
            if score < 75 and days_ago > 30:
                banner2 = tk.Frame(self.detail_inner, bg="#2D1F4E", pady=6)
                banner2.pack(fill="x", padx=8, pady=(4,0))
                tk.Label(banner2,
                         text=f"✨  AI Suggestion: No contact for {days_ago} days. "
                              f"A quick message could improve relationship health.",
                         bg="#2D1F4E", fg="#A78BFA",
                         font=("Segoe UI", 10)).pack(side="left", padx=12)

    def _switch_tab(self, key, name):
        for k, b in self._tab_buttons.items():
            b.config(bg=C_INDIGO if k==key else C_NAVY2)
        self._render_tab(key, name)

    def _render_tab(self, tab, name):
        for w in self.tab_content.winfo_children():
            w.destroy()

        info = self.contacts[name]

        if tab == "info":
            self._render_info_tab(name, info)
        elif tab == "timeline":
            self._render_timeline_tab(name, info)
        elif tab == "network":
            self._render_network_tab(name, info)
        elif tab == "analytics":
            self._render_analytics_tab(name, info)

    # ── Info Tab 

    def _render_info_tab(self, name, info):
        canvas, inner = scrollable_frame(self.tab_content, bg=C_SURFACE)

        row1 = tk.Frame(inner, bg=C_SURFACE)
        row1.pack(fill="x", padx=12, pady=(12,6))

        # Contact details card
        card1 = label_frame(row1, "CONTACT DETAILS")
        card1.pack(side="left", fill="both", expand=True, padx=(0,6))

        fields = [
            ("📞 Phones",    "\n".join(info.get("phones",[]))),
            ("✉  Emails",    "\n".join(info.get("emails",[]))),
            ("📍 Address",   info.get("address","")),
            ("🎂 Birthday",  info.get("birthday","")),
            ("💍 Anniversary",info.get("anniversary","")),
        ]
        for lbl, val in fields:
            if not val:
                continue
            r = tk.Frame(card1, bg=C_SURFACE2)
            r.pack(fill="x", padx=10, pady=2)
            tk.Label(r, text=lbl, bg=C_SURFACE2, fg=C_MUTED,
                     font=("Segoe UI", 9), width=14, anchor="w").pack(side="left")
            tk.Label(r, text=val, bg=C_SURFACE2, fg=C_WHITE,
                     font=("Segoe UI", 10), anchor="w", wraplength=180,
                     justify="left").pack(side="left", padx=6)
        tk.Frame(card1, height=8, bg=C_SURFACE2).pack()

        # Professional card
        card2 = label_frame(row1, "PROFESSIONAL")
        card2.pack(side="left", fill="both", expand=True, padx=(6,0))

        score = info.get("score", 50)
        sc_color = score_color(score)

        pro_fields = [
            ("🏢 Company",  info.get("company","")),
            ("💼 Role",     info.get("role","")),
            ("👥 Group",    info.get("group","")),
            ("🔗 LinkedIn", info.get("social",{}).get("linkedin","")),
            ("🐦 Twitter",  info.get("social",{}).get("twitter","")),
        ]
        for lbl, val in pro_fields:
            if not val:
                continue
            r = tk.Frame(card2, bg=C_SURFACE2)
            r.pack(fill="x", padx=10, pady=2)
            tk.Label(r, text=lbl, bg=C_SURFACE2, fg=C_MUTED,
                     font=("Segoe UI", 9), width=12, anchor="w").pack(side="left")
            tk.Label(r, text=val, bg=C_SURFACE2, fg=C_WHITE,
                     font=("Segoe UI", 10), anchor="w").pack(side="left", padx=6)

        # Health score bar
        health_row = tk.Frame(card2, bg=C_SURFACE2)
        health_row.pack(fill="x", padx=10, pady=(8,4))
        tk.Label(health_row, text="❤ Health Score", bg=C_SURFACE2,
                 fg=C_MUTED, font=("Segoe UI", 9)).pack(anchor="w")
        bar_bg = tk.Frame(health_row, bg=C_NAVY, height=8)
        bar_bg.pack(fill="x", pady=4)
        bar_fg = tk.Frame(bar_bg, bg=sc_color, height=8,
                          width=max(4, int(score * 2)))
        bar_fg.pack(side="left")
        tk.Label(health_row, text=f"{score}/100 — {score_label(score)}",
                 bg=C_SURFACE2, fg=sc_color,
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")
        tk.Frame(card2, height=8, bg=C_SURFACE2).pack()

        # Notes card
        card3 = label_frame(inner, "NOTES")
        card3.pack(fill="x", padx=12, pady=6)
        notes = info.get("notes","") or "No notes yet."
        tk.Label(card3, text=notes, bg=C_SURFACE2, fg=C_WHITE,
                 font=("Segoe UI", 10), anchor="w", justify="left",
                 wraplength=600, padx=10, pady=8).pack(fill="x")

        # AI Suggestion
        card4 = label_frame(inner, "✨ AI INSIGHT")
        card4.pack(fill="x", padx=12, pady=6)
        suggestion = ai_suggestion(name, info)
        ai_frame = tk.Frame(card4, bg="#1F1560", padx=12, pady=8)
        ai_frame.pack(fill="x", padx=10, pady=6)
        tk.Label(ai_frame, text="🤖 " + suggestion, bg="#1F1560",
                 fg="#A78BFA", font=("Segoe UI", 10),
                 wraplength=580, justify="left", anchor="w").pack(fill="x")

        # Tags management
        card5 = label_frame(inner, "TAGS")
        card5.pack(fill="x", padx=12, pady=6)
        tags_row = tk.Frame(card5, bg=C_SURFACE2)
        tags_row.pack(fill="x", padx=10, pady=6)
        for tag in info.get("tags", []):
            tc = TAG_COLORS.get(tag.lower(), C_INDIGO)
            tk.Label(tags_row, text=tag, bg=C_NAVY3, fg=tc,
                     font=("Segoe UI", 10), padx=10, pady=3).pack(side="left", padx=3, pady=2)
        styled_btn(tags_row, "Add Tag", lambda n=name: self._add_tag(n),
                   color=C_NAVY3, font_size=9).pack(side="left", padx=6)
        tk.Frame(card5, height=6, bg=C_SURFACE2).pack()

    # ── Timeline Tab 

    def _render_timeline_tab(self, name, info):
        canvas, inner = scrollable_frame(self.tab_content, bg=C_SURFACE)

        card = label_frame(inner, "INTERACTION TIMELINE")
        card.pack(fill="x", padx=12, pady=12)

        interactions = info.get("interactions", [])
        if not interactions:
            tk.Label(card, text="No interactions logged yet.",
                     bg=C_SURFACE2, fg=C_MUTED,
                     font=("Segoe UI", 11), pady=12).pack()
        else:
            for ix in interactions:
                itype = ix.get("type","msg")
                icon = {"call":"📞","email":"✉","msg":"💬","meeting":"🤝"}.get(itype,"📌")
                ic = {"call":C_EMERALD,"email":C_INDIGO,"msg":C_AMBER,"meeting":C_SKY}.get(itype,C_MUTED)

                row = tk.Frame(card, bg=C_SURFACE2)
                row.pack(fill="x", padx=10, pady=3)

                tk.Label(row, text=icon, bg=C_SURFACE2,
                         font=("Segoe UI", 13)).pack(side="left", padx=8, pady=6)

                mid = tk.Frame(row, bg=C_SURFACE2)
                mid.pack(side="left", fill="both", expand=True, pady=6)
                tk.Label(mid, text=ix.get("label","Interaction"),
                         bg=C_SURFACE2, fg=ic,
                         font=("Segoe UI", 10, "bold"), anchor="w").pack(fill="x")
                if ix.get("note"):
                    tk.Label(mid, text=ix["note"], bg=C_SURFACE2,
                             fg=C_MUTED, font=("Segoe UI", 9),
                             anchor="w").pack(fill="x")

                tk.Label(row, text=ix.get("when",""), bg=C_SURFACE2,
                         fg=C_MUTED, font=("Segoe UI", 9),
                         padx=10).pack(side="right")

        # Log interaction button
        btn_row = tk.Frame(card, bg=C_SURFACE2)
        btn_row.pack(fill="x", padx=10, pady=(6,10))
        styled_btn(btn_row, "Log Interaction", lambda n=name: self._log_interaction(n),
                   color=C_INDIGO, icon="＋").pack(side="left")

    # ── Network Tab 

    def _render_network_tab(self, name, info):
        outer = tk.Frame(self.tab_content, bg=C_SURFACE)
        outer.pack(fill="both", expand=True, padx=12, pady=12)

        tk.Label(outer, text="🕸  Network Graph", bg=C_SURFACE, fg=C_MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")

        net_canvas = tk.Canvas(outer, bg=C_NAVY2, height=260,
                               highlightthickness=1,
                               highlightbackground=C_BORDER)
        net_canvas.pack(fill="x", pady=6)

        # Draw after layout
        outer.after(50, lambda: self._draw_network(net_canvas, name, info))

        # Related contacts
        tk.Label(outer, text="RELATED CONTACTS", bg=C_SURFACE, fg=C_MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(8,4))

        tags = set(t.lower() for t in info.get("tags",[]))
        related = [(n, c) for n, c in self.contacts.items()
                   if n != name and set(t.lower() for t in c.get("tags",[])) & tags]

        if not related:
            tk.Label(outer, text="No related contacts found by shared tags.",
                     bg=C_SURFACE, fg=C_MUTED, font=("Segoe UI", 10)).pack()
        else:
            for rname, rinfo in related[:5]:
                row = tk.Frame(outer, bg=C_SURFACE2, cursor="hand2")
                row.pack(fill="x", pady=2)
                av_bg, av_fg = avatar_colors(rname)
                av = tk.Canvas(row, width=32, height=32, bg=C_SURFACE2,
                               highlightthickness=0)
                av.pack(side="left", padx=8, pady=6)
                av.create_oval(2,2,30,30, fill=av_bg, outline="")
                av.create_text(16,16, text=initials(rname),
                               fill=av_fg, font=("Segoe UI", 9,"bold"))
                shared = tags & set(t.lower() for t in rinfo.get("tags",[]))
                mid = tk.Frame(row, bg=C_SURFACE2)
                mid.pack(side="left", fill="both", expand=True, pady=6)
                tk.Label(mid, text=rname, bg=C_SURFACE2, fg=C_WHITE,
                         font=("Segoe UI", 10,"bold"), anchor="w").pack(fill="x")
                tk.Label(mid, text="Shared: " + ", ".join(shared),
                         bg=C_SURFACE2, fg=C_MUTED,
                         font=("Segoe UI", 9), anchor="w").pack(fill="x")
                row.bind("<Button-1>", lambda e, rn=rname: (
                    setattr(self,"active_name",rn),
                    self.refresh_list(),
                    self._render_detail(rn)))

    def _draw_network(self, canvas, name, info):
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        if w < 10:
            canvas.after(100, lambda: self._draw_network(canvas, name, info))
            return
        canvas.delete("all")

        tags = set(t.lower() for t in info.get("tags",[]))
        related = [(n, c) for n, c in self.contacts.items()
                   if n != name and set(t.lower() for t in c.get("tags",[])) & tags][:5]

        cx, cy = w//2, h//2

        # Draw edges
        for i, (rname, _) in enumerate(related):
            angle = (i / max(len(related),1)) * 2 * math.pi - math.pi/2
            rx = cx + int(math.cos(angle) * min(w,h) * 0.35)
            ry = cy + int(math.sin(angle) * min(w,h) * 0.3)
            canvas.create_line(cx, cy, rx, ry, fill=C_BORDER, width=1.5)

        # Draw satellite nodes
        for i, (rname, _) in enumerate(related):
            angle = (i / max(len(related),1)) * 2 * math.pi - math.pi/2
            rx = cx + int(math.cos(angle) * min(w,h) * 0.35)
            ry = cy + int(math.sin(angle) * min(w,h) * 0.3)
            av_bg, av_fg = avatar_colors(rname)
            draw_avatar(canvas, rx, ry, 20, rname, av_bg, av_fg)
            canvas.create_text(rx, ry+28, text=rname.split()[0],
                                fill=C_MUTED, font=("Segoe UI", 8))

        # Center node
        av_bg, av_fg = avatar_colors(name)
        canvas.create_oval(cx-32, cy-32, cx+32, cy+32,
                           fill=C_INDIGO, outline=C_WHITE, width=2)
        canvas.create_text(cx, cy, text=initials(name),
                           fill=C_WHITE, font=("Segoe UI", 16, "bold"))
        canvas.create_text(cx, cy+44, text=name.split()[0],
                           fill=C_WHITE, font=("Segoe UI", 9, "bold"))

    # ── Analytics Tab 

    def _render_analytics_tab(self, name, info):
        canvas, inner = scrollable_frame(self.tab_content, bg=C_SURFACE)

        interactions = info.get("interactions", [])
        score = info.get("score", 50)
        tags = info.get("tags", [])

        # Stats grid
        stats = [
            ("Total Interactions", str(len(interactions)), C_INDIGO),
            ("Health Score",       f"{score}/100",          score_color(score)),
            ("Tags",               str(len(tags)),           C_SKY),
            ("Last Contact",       interactions[-1].get("when","—") if interactions else "—", C_MUTED),
        ]
        stats_row = tk.Frame(inner, bg=C_SURFACE)
        stats_row.pack(fill="x", padx=12, pady=(12,6))
        for label, val, color in stats:
            card = tk.Frame(stats_row, bg=C_SURFACE2, padx=16, pady=12)
            card.pack(side="left", fill="both", expand=True, padx=4)
            tk.Label(card, text=val, bg=C_SURFACE2, fg=color,
                     font=("Segoe UI", 18, "bold")).pack()
            tk.Label(card, text=label, bg=C_SURFACE2, fg=C_MUTED,
                     font=("Segoe UI", 9)).pack()

        # Breakdown bar chart (tkinter canvas)
        card_chart = label_frame(inner, "INTERACTION BREAKDOWN")
        card_chart.pack(fill="x", padx=12, pady=6)

        chart_canvas = tk.Canvas(card_chart, bg=C_SURFACE2, height=150,
                                 highlightthickness=0)
        chart_canvas.pack(fill="x", padx=10, pady=8)

        type_counts = {}
        for ix in interactions:
            t = ix.get("type","other")
            type_counts[t] = type_counts.get(t,0) + 1

        if type_counts:
            max_count = max(type_counts.values())
            bar_w = 60
            gap = 20
            start_x = 30
            bar_colors = {"call":C_EMERALD,"email":C_INDIGO,"msg":C_AMBER,"meeting":C_SKY}
            labels = {"call":"Calls","email":"Emails","msg":"Messages","meeting":"Meetings"}
            chart_height = 110

            for i, (itype, count) in enumerate(type_counts.items()):
                x = start_x + i * (bar_w + gap)
                bh = int((count / max_count) * chart_height)
                color = bar_colors.get(itype, C_MUTED)
                chart_canvas.create_rectangle(
                    x, chart_height - bh + 10,
                    x + bar_w, chart_height + 10,
                    fill=color, outline="")
                chart_canvas.create_text(
                    x + bar_w//2, chart_height - bh,
                    text=str(count), fill=color,
                    font=("Segoe UI", 10, "bold"), anchor="s")
                chart_canvas.create_text(
                    x + bar_w//2, chart_height + 22,
                    text=labels.get(itype, itype),
                    fill=C_MUTED, font=("Segoe UI", 9))
        else:
            chart_canvas.create_text(200, 75, text="No interaction data yet",
                                     fill=C_MUTED, font=("Segoe UI", 11))

        # Days until birthday
        bdays = days_until_birthday(info.get("birthday",""))
        if bdays is not None:
            card_bd = label_frame(inner, "BIRTHDAY COUNTDOWN")
            card_bd.pack(fill="x", padx=12, pady=6)
            bd_row = tk.Frame(card_bd, bg=C_SURFACE2)
            bd_row.pack(fill="x", padx=10, pady=8)
            tk.Label(bd_row, text=f"🎂  {bdays} days until birthday",
                     bg=C_SURFACE2, fg=C_AMBER if bdays<=30 else C_WHITE,
                     font=("Segoe UI", 13)).pack(side="left")

        tk.Frame(inner, height=20, bg=C_SURFACE).pack()

    # ── Add / Edit Contact 

    def _open_add(self):
        self._open_form("Add Contact", {})

    def _open_edit(self, name):
        self._open_form("Edit Contact", self.contacts[name], old_name=name)

    def _open_form(self, title, info, old_name=None):
        dlg = tk.Toplevel(self.root)
        dlg.title(title)
        dlg.geometry("520x680")
        dlg.configure(bg=C_NAVY)
        dlg.resizable(False, True)
        dlg.grab_set()

        tk.Label(dlg, text=title, bg=C_NAVY, fg=C_WHITE,
                 font=("Segoe UI", 14, "bold")).pack(pady=(16,6), padx=20, anchor="w")

        canvas_dlg = tk.Canvas(dlg, bg=C_NAVY, highlightthickness=0)
        vsb_dlg = ttk.Scrollbar(dlg, orient="vertical", command=canvas_dlg.yview)
        canvas_dlg.configure(yscrollcommand=vsb_dlg.set)
        vsb_dlg.pack(side="right", fill="y")
        canvas_dlg.pack(fill="both", expand=True)
        inner_dlg = tk.Frame(canvas_dlg, bg=C_NAVY)
        inner_dlg.bind("<Configure>", lambda e: canvas_dlg.configure(
            scrollregion=canvas_dlg.bbox("all")))
        canvas_dlg.create_window((0,0), window=inner_dlg, anchor="nw")
        canvas_dlg.bind("<MouseWheel>",
            lambda e: canvas_dlg.yview_scroll(int(-1*(e.delta/120)), "units"))

        def field(parent, lbl, default="", width=40):
            tk.Label(parent, text=lbl, bg=C_NAVY, fg=C_MUTED,
                     font=("Segoe UI", 9)).pack(anchor="w", padx=20, pady=(6,1))
            var = tk.StringVar(value=default)
            e = tk.Entry(parent, textvariable=var, width=width,
                         bg=C_SURFACE2, fg=C_WHITE, insertbackground=C_WHITE,
                         relief="flat", font=("Segoe UI", 11), bd=4)
            e.pack(fill="x", padx=20, ipady=4)
            return var

        f_name   = field(inner_dlg, "Full Name *",  old_name or "")
        f_phone  = field(inner_dlg, "Phone *",      ", ".join(info.get("phones",[])))
        f_email  = field(inner_dlg, "Email(s)",     ", ".join(info.get("emails",[])))
        f_company= field(inner_dlg, "Company",      info.get("company",""))
        f_role   = field(inner_dlg, "Role / Title", info.get("role",""))
        f_address= field(inner_dlg, "Address",      info.get("address",""))
        f_bday   = field(inner_dlg, "Birthday (YYYY-MM-DD)", info.get("birthday",""))
        f_anniv  = field(inner_dlg, "Anniversary (YYYY-MM-DD)", info.get("anniversary",""))
        f_tags   = field(inner_dlg, "Tags (comma separated)",
                         ", ".join(info.get("tags",[])))
        f_linkedin=field(inner_dlg, "LinkedIn",
                         info.get("social",{}).get("linkedin",""))
        f_twitter= field(inner_dlg, "Twitter",
                         info.get("social",{}).get("twitter",""))

        # Group select
        tk.Label(inner_dlg, text="Group", bg=C_NAVY, fg=C_MUTED,
                 font=("Segoe UI", 9)).pack(anchor="w", padx=20, pady=(6,1))
        grp_var = tk.StringVar(value=info.get("group","Work"))
        grp_cb = ttk.Combobox(inner_dlg, textvariable=grp_var,
                              values=["Work","Family","Network"],
                              state="readonly", font=("Segoe UI",11))
        grp_cb.pack(fill="x", padx=20)

        # Notes
        tk.Label(inner_dlg, text="Notes", bg=C_NAVY, fg=C_MUTED,
                 font=("Segoe UI", 9)).pack(anchor="w", padx=20, pady=(6,1))
        notes_text = tk.Text(inner_dlg, height=4, bg=C_SURFACE2, fg=C_WHITE,
                             insertbackground=C_WHITE, relief="flat",
                             font=("Segoe UI", 11), bd=4)
        notes_text.pack(fill="x", padx=20)
        notes_text.insert("1.0", info.get("notes",""))

        # Emergency toggle
        em_var = tk.BooleanVar(value=info.get("emergency", False))
        tk.Checkbutton(inner_dlg, text="⭐ Mark as Emergency Contact",
                       variable=em_var, bg=C_NAVY, fg=C_AMBER,
                       selectcolor=C_NAVY, activebackground=C_NAVY,
                       font=("Segoe UI", 10), cursor="hand2").pack(
                           anchor="w", padx=20, pady=8)

        def save():
            name = f_name.get().strip()
            phones = [p.strip() for p in f_phone.get().split(",") if p.strip()]
            emails = [e.strip() for e in f_email.get().split(",") if e.strip()]

            if not name or not phones:
                messagebox.showerror("Error", "Name and at least one phone are required.", parent=dlg)
                return

            # Duplicate detection
            dups = detect_duplicates(self.contacts, name, phones[0] if phones else "",
                                     emails[0] if emails else "")
            dups = [(n,r) for n,r in dups if n != old_name]
            if dups:
                dup_msg = "\n".join(f"  • {n} ({r})" for n,r in dups)
                if not messagebox.askyesno("Duplicate Detected",
                    f"Possible duplicate(s) found:\n{dup_msg}\n\nSave anyway?", parent=dlg):
                    return

            if old_name and old_name != name and old_name in self.contacts:
                del self.contacts[old_name]

            self.contacts[name] = {
                "phones":   phones,
                "emails":   emails,
                "company":  f_company.get().strip(),
                "role":     f_role.get().strip(),
                "address":  f_address.get().strip(),
                "birthday": f_bday.get().strip(),
                "anniversary": f_anniv.get().strip(),
                "tags":     [t.strip() for t in f_tags.get().split(",") if t.strip()],
                "group":    grp_var.get(),
                "score":    info.get("score", 50),
                "notes":    notes_text.get("1.0","end").strip(),
                "social":   {"linkedin": f_linkedin.get().strip(),
                             "twitter":  f_twitter.get().strip()},
                "emergency":em_var.get(),
                "interactions": info.get("interactions",[]),
                "created":  info.get("created", str(date.today())),
            }
            save_contacts(self.contacts)
            dlg.destroy()
            self.active_name = name
            self.refresh_list()
            self._render_detail(name)

        btn_row = tk.Frame(inner_dlg, bg=C_NAVY)
        btn_row.pack(fill="x", padx=20, pady=12)
        styled_btn(btn_row, "Save Contact", save, color=C_INDIGO, icon="✓").pack(side="left")
        styled_btn(btn_row, "Cancel", dlg.destroy, color=C_ROSE).pack(side="left", padx=8)

        tk.Frame(inner_dlg, height=20, bg=C_NAVY).pack()

    # ── Actions 

    def _delete_contact(self, name):
        if not messagebox.askyesno("Delete Contact",
            f"Permanently delete '{name}'?\nThis cannot be undone."):
            return
        del self.contacts[name]
        save_contacts(self.contacts)
        self.active_name = None
        self.refresh_list()
        self.detail_inner.destroy()
        self.empty_label.place(relx=0.5, rely=0.5, anchor="center")

    def _call(self, name):
        phones = self.contacts[name].get("phones",[])
        if not phones:
            return
        messagebox.showinfo("Call",
            f"Calling {name}:\n{phones[0]}\n\n"
            "(In a full implementation this would open your system dialer.)")

    def _email(self, name):
        emails = self.contacts[name].get("emails",[])
        if not emails:
            return
        import webbrowser
        webbrowser.open(f"mailto:{emails[0]}")

    def _add_tag(self, name):
        tag = simpledialog.askstring("Add Tag", "Enter new tag:", parent=self.root)
        if tag and tag.strip():
            self.contacts[name]["tags"].append(tag.strip())
            save_contacts(self.contacts)
            self._render_detail(name)

    def _log_interaction(self, name):
        dlg = tk.Toplevel(self.root)
        dlg.title("Log Interaction")
        dlg.geometry("380x280")
        dlg.configure(bg=C_NAVY)
        dlg.grab_set()

        tk.Label(dlg, text="Log Interaction", bg=C_NAVY, fg=C_WHITE,
                 font=("Segoe UI", 13, "bold")).pack(pady=14, padx=20, anchor="w")

        tk.Label(dlg, text="Type", bg=C_NAVY, fg=C_MUTED,
                 font=("Segoe UI", 9)).pack(anchor="w", padx=20)
        type_var = tk.StringVar(value="call")
        type_cb = ttk.Combobox(dlg, textvariable=type_var,
                               values=["call","email","msg","meeting"],
                               state="readonly", font=("Segoe UI",11))
        type_cb.pack(fill="x", padx=20, pady=4)

        tk.Label(dlg, text="Date (YYYY-MM-DD)", bg=C_NAVY, fg=C_MUTED,
                 font=("Segoe UI", 9)).pack(anchor="w", padx=20)
        date_var = tk.StringVar(value=str(date.today()))
        tk.Entry(dlg, textvariable=date_var, bg=C_SURFACE2, fg=C_WHITE,
                 insertbackground=C_WHITE, relief="flat",
                 font=("Segoe UI",11), bd=4).pack(fill="x", padx=20, ipady=4)

        tk.Label(dlg, text="Note", bg=C_NAVY, fg=C_MUTED,
                 font=("Segoe UI", 9)).pack(anchor="w", padx=20, pady=(8,0))
        note_var = tk.StringVar()
        tk.Entry(dlg, textvariable=note_var, bg=C_SURFACE2, fg=C_WHITE,
                 insertbackground=C_WHITE, relief="flat",
                 font=("Segoe UI",11), bd=4).pack(fill="x", padx=20, ipady=4)

        def save():
            itype = type_var.get()
            labels = {"call":"Called","email":"Email","msg":"WhatsApp","meeting":"Meeting"}
            self.contacts[name]["interactions"].insert(0, {
                "type":  itype,
                "label": labels.get(itype, itype.title()),
                "when":  date_var.get().strip(),
                "note":  note_var.get().strip(),
            })
            # Boost score
            sc = self.contacts[name].get("score", 50)
            self.contacts[name]["score"] = min(100, sc + 5)
            save_contacts(self.contacts)
            dlg.destroy()
            self._render_detail(name)

        btn_row = tk.Frame(dlg, bg=C_NAVY)
        btn_row.pack(pady=12, padx=20, anchor="w")
        styled_btn(btn_row, "Save", save, color=C_EMERALD).pack(side="left")
        styled_btn(btn_row, "Cancel", dlg.destroy, color=C_ROSE).pack(side="left", padx=8)

    # ── Group Switching 

    def _switch_group(self, group):
        self.active_group = group
        for k, b in self.group_btns.items():
            b.config(bg=C_INDIGO if k==group else C_NAVY2,
                     fg=C_WHITE if k==group else C_MUTED)
        self.refresh_list()

    # ── Reminders 

    def _check_reminders(self):
        bday_contacts = [(n, days_until_birthday(info.get("birthday","")))
                         for n, info in self.contacts.items()
                         if birthday_soon(info.get("birthday",""), days=3)]
        if bday_contacts:
            msg = "\n".join(f"🎂 {n} — in {d} day(s)" for n,d in bday_contacts)
            messagebox.showinfo("Birthday Reminders", f"Upcoming birthdays:\n\n{msg}")

    def _show_reminders(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Reminders & Suggestions")
        dlg.geometry("460x500")
        dlg.configure(bg=C_NAVY)

        tk.Label(dlg, text="🔔 Reminders & AI Suggestions", bg=C_NAVY,
                 fg=C_WHITE, font=("Segoe UI", 13, "bold")).pack(pady=14, padx=16, anchor="w")

        canvas_r, inner_r = scrollable_frame(dlg, bg=C_NAVY)

        # Birthdays
        tk.Label(inner_r, text="🎂  UPCOMING BIRTHDAYS (next 30 days)",
                 bg=C_NAVY, fg=C_MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=12, pady=(0,4))

        found_bday = False
        for name, info in self.contacts.items():
            d = days_until_birthday(info.get("birthday",""))
            if d is not None and 0 <= d <= 30:
                found_bday = True
                row = tk.Frame(inner_r, bg=C_SURFACE2, cursor="hand2")
                row.pack(fill="x", padx=12, pady=2)
                tk.Label(row, text=f"  {name}", bg=C_SURFACE2, fg=C_WHITE,
                         font=("Segoe UI", 11)).pack(side="left", pady=8)
                tk.Label(row, text=f"in {d} day(s)", bg=C_SURFACE2,
                         fg=C_AMBER, font=("Segoe UI", 10)).pack(side="right", padx=12)

        if not found_bday:
            tk.Label(inner_r, text="No birthdays in the next 30 days.",
                     bg=C_NAVY, fg=C_MUTED, font=("Segoe UI", 10)).pack(padx=16, pady=4)

        # Follow-up suggestions
        tk.Label(inner_r, text="✨  FOLLOW-UP SUGGESTIONS",
                 bg=C_NAVY, fg=C_MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=12, pady=(14,4))

        found_fu = False
        for name, info in self.contacts.items():
            ixs = info.get("interactions",[])
            if not ixs:
                continue
            try:
                days_ago = (date.today() - date.fromisoformat(ixs[-1].get("when",""))).days
            except Exception:
                continue
            if days_ago > 30 and info.get("score",100) < 80:
                found_fu = True
                row = tk.Frame(inner_r, bg=C_SURFACE2)
                row.pack(fill="x", padx=12, pady=2)
                tk.Label(row, text=f"  {name}", bg=C_SURFACE2, fg=C_WHITE,
                         font=("Segoe UI", 11)).pack(side="left", pady=8)
                tk.Label(row, text=f"{days_ago}d ago", bg=C_SURFACE2,
                         fg=C_ROSE, font=("Segoe UI", 10)).pack(side="right", padx=12)

        if not found_fu:
            tk.Label(inner_r, text="All contacts recently touched. Great networking!",
                     bg=C_NAVY, fg=C_EMERALD, font=("Segoe UI", 10)).pack(padx=16, pady=4)

        styled_btn(dlg, "Close", dlg.destroy, color=C_NAVY3).pack(pady=12)

    # ── Import / Export 

    def _import_menu(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Import Contacts")
        dlg.geometry("360x200")
        dlg.configure(bg=C_NAVY)
        dlg.grab_set()

        tk.Label(dlg, text="Import Contacts", bg=C_NAVY, fg=C_WHITE,
                 font=("Segoe UI", 13, "bold")).pack(pady=14, padx=16, anchor="w")

        btn_frame = tk.Frame(dlg, bg=C_NAVY)
        btn_frame.pack(padx=16, pady=4)
        styled_btn(btn_frame, "Import CSV", lambda: (dlg.destroy(), self._import_csv()),
                   color=C_EMERALD, icon="📄").pack(fill="x", pady=4)
        styled_btn(btn_frame, "Import vCard (.vcf)", lambda: (dlg.destroy(), self._import_vcf()),
                   color=C_SKY, icon="📇").pack(fill="x", pady=4)
        styled_btn(btn_frame, "Cancel", dlg.destroy, color=C_NAVY3).pack(fill="x", pady=4)

    def _import_csv(self):
        path = filedialog.askopenfilename(
            title="Import CSV", filetypes=[("CSV Files","*.csv"),("All","*.*")])
        if not path:
            return
        try:
            imported = 0
            with open(path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    name = row.get("name","").strip() or row.get("Name","").strip()
                    phone = row.get("phone","").strip() or row.get("Phone","").strip()
                    if not name:
                        continue
                    self.contacts[name] = {
                        "phones":   [phone] if phone else [],
                        "emails":   [row.get("email","").strip()],
                        "company":  row.get("company","").strip(),
                        "role":     row.get("role","").strip(),
                        "address":  row.get("address","").strip(),
                        "birthday": row.get("birthday","").strip(),
                        "anniversary": "",
                        "tags":     [t.strip() for t in row.get("tags","").split(",") if t.strip()],
                        "group":    row.get("group","Network").strip(),
                        "score":    50,
                        "notes":    row.get("notes","").strip(),
                        "social":   {"linkedin":"","twitter":""},
                        "emergency":False,
                        "interactions":[],
                        "created":  str(date.today()),
                    }
                    imported += 1
            save_contacts(self.contacts)
            self.refresh_list()
            messagebox.showinfo("Import Complete", f"Imported {imported} contact(s).")
        except Exception as ex:
            messagebox.showerror("Import Error", str(ex))

    def _import_vcf(self):
        path = filedialog.askopenfilename(
            title="Import vCard", filetypes=[("vCard","*.vcf"),("All","*.*")])
        if not path:
            return
        try:
            imported = 0
            with open(path, encoding="utf-8", errors="ignore") as f:
                content = f.read()
            cards = content.split("BEGIN:VCARD")
            for card in cards:
                if not card.strip():
                    continue
                name = phone = email = ""
                for line in card.splitlines():
                    if line.startswith("FN:"):
                        name = line[3:].strip()
                    elif line.startswith("TEL") and ":" in line:
                        phone = line.split(":",1)[1].strip()
                    elif line.startswith("EMAIL") and ":" in line:
                        email = line.split(":",1)[1].strip()
                if not name:
                    continue
                self.contacts[name] = {
                    "phones": [phone] if phone else [],
                    "emails": [email] if email else [],
                    "company":"","role":"","address":"","birthday":"",
                    "anniversary":"","tags":[],"group":"Network",
                    "score":50,"notes":"","social":{"linkedin":"","twitter":""},
                    "emergency":False,"interactions":[],"created":str(date.today()),
                }
                imported += 1
            save_contacts(self.contacts)
            self.refresh_list()
            messagebox.showinfo("Import Complete", f"Imported {imported} vCard(s).")
        except Exception as ex:
            messagebox.showerror("Import Error", str(ex))

    def _export_menu(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Export Contacts")
        dlg.geometry("360x220")
        dlg.configure(bg=C_NAVY)
        dlg.grab_set()

        tk.Label(dlg, text="Export Contacts", bg=C_NAVY, fg=C_WHITE,
                 font=("Segoe UI", 13, "bold")).pack(pady=14, padx=16, anchor="w")

        btn_frame = tk.Frame(dlg, bg=C_NAVY)
        btn_frame.pack(padx=16, pady=4)
        styled_btn(btn_frame, "Export as CSV", lambda: (dlg.destroy(), self._export_csv()),
                   color=C_EMERALD, icon="📄").pack(fill="x", pady=4)
        styled_btn(btn_frame, "Export as vCard (.vcf)",
                   lambda: (dlg.destroy(), self._export_vcf()),
                   color=C_SKY, icon="📇").pack(fill="x", pady=4)
        styled_btn(btn_frame, "Export as JSON",
                   lambda: (dlg.destroy(), self._export_json()),
                   color=C_AMBER, icon="{}").pack(fill="x", pady=4)
        styled_btn(btn_frame, "Cancel", dlg.destroy, color=C_NAVY3).pack(fill="x", pady=4)

    def _export_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV","*.csv")],
            initialfile="contacts_export.csv")
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["name","phone","email","company","role","address",
                             "birthday","tags","group","score","notes"])
            for name, info in self.contacts.items():
                writer.writerow([
                    name,
                    "; ".join(info.get("phones",[])),
                    "; ".join(info.get("emails",[])),
                    info.get("company",""),
                    info.get("role",""),
                    info.get("address",""),
                    info.get("birthday",""),
                    ", ".join(info.get("tags",[])),
                    info.get("group",""),
                    info.get("score",""),
                    info.get("notes",""),
                ])
        messagebox.showinfo("Export Complete", f"Exported to:\n{path}")

    def _export_vcf(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".vcf",
            filetypes=[("vCard","*.vcf")],
            initialfile="contacts_export.vcf")
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            for name, info in self.contacts.items():
                f.write("BEGIN:VCARD\nVERSION:3.0\n")
                f.write(f"FN:{name}\n")
                for phone in info.get("phones",[]):
                    f.write(f"TEL;TYPE=CELL:{phone}\n")
                for email in info.get("emails",[]):
                    f.write(f"EMAIL:{email}\n")
                if info.get("company"):
                    f.write(f"ORG:{info['company']}\n")
                if info.get("role"):
                    f.write(f"TITLE:{info['role']}\n")
                if info.get("birthday"):
                    f.write(f"BDAY:{info['birthday'].replace('-','')}\n")
                if info.get("notes"):
                    f.write(f"NOTE:{info['notes']}\n")
                f.write("END:VCARD\n\n")
        messagebox.showinfo("Export Complete", f"Exported to:\n{path}")

    def _export_json(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON","*.json")],
            initialfile="contacts_export.json")
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.contacts, f, indent=2, ensure_ascii=False)
        messagebox.showinfo("Export Complete", f"Exported to:\n{path}")


# ── Entry Point 

def main():
    root = tk.Tk()
    root.minsize(800, 500)
    try:
        root.state("zoomed")          # Windows maximise
    except Exception:
        try:
            root.attributes("-zoomed", True)   # Linux
        except Exception:
            pass
    app = ContactIQApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()