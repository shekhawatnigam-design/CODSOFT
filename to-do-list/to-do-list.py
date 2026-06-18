import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv
from datetime import datetime, timedelta

# =========================
# DATABASE SETUP
# =========================

conn = sqlite3.connect("tasks.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS tasks(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT,
    priority TEXT,
    due_date TEXT,
    status TEXT DEFAULT 'Pending',
    created_at TEXT,
    completed_at TEXT,
    tags TEXT,
    progress INTEGER DEFAULT 0,
    notes TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS activity_log(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT,
    task_title TEXT,
    timestamp TEXT
)
""")

conn.commit()

# =========================
# DATABASE MIGRATION
# (safely adds new columns to old databases)
# =========================

def _add_column_if_missing(col, col_def):
    cur.execute("PRAGMA table_info(tasks)")
    existing = [row[1] for row in cur.fetchall()]
    if col not in existing:
        cur.execute(f"ALTER TABLE tasks ADD COLUMN {col} {col_def}")
        conn.commit()

_add_column_if_missing("completed_at", "TEXT")
_add_column_if_missing("tags",         "TEXT")
_add_column_if_missing("progress",     "INTEGER DEFAULT 0")
_add_column_if_missing("notes",        "TEXT")

# =========================
# THEME
# =========================

T = {
    "BG":      "#1e1e2f",
    "CARD":    "#2c2c3c",
    "SIDEBAR": "#16162a",
    "ACCENT":  "#6c63ff",
    "ACCENT2": "#a78bfa",
    "SUCCESS": "#4CAF50",
    "DANGER":  "#f44336",
    "WARNING": "#ff9800",
    "TEXT":    "#ffffff",
    "SUBTEXT": "#a0a0b0",
    "BORDER":  "#3a3a5c",
    "HOVER":   "#38384a",
}

PRIORITY_COLORS = {"High": "#f44336", "Medium": "#ff9800", "Low": "#4CAF50"}

CATEGORY_ICONS = {
    "Study":    "[Study]",
    "Work":     "[Work]",
    "Personal": "[Home]",
    "Health":   "[Health]",
    "Shopping": "[Shop]",
    "Finance":  "[Finance]",
    "Other":    "[*]",
}

# =========================
# ROOT WINDOW
# =========================

root = tk.Tk()
root.title("Smart Task Manager Pro")
root.geometry("1400x820")
root.minsize(1100, 650)
root.configure(bg=T["BG"])

root.update_idletasks()
x = (root.winfo_screenwidth()  - 1400) // 2
y = (root.winfo_screenheight() - 820)  // 2
root.geometry(f"1400x820+{x}+{y}")

# =========================
# VARIABLES
# =========================

title_var           = tk.StringVar()
desc_var            = tk.StringVar()
category_var        = tk.StringVar(value="Study")
priority_var        = tk.StringVar(value="Medium")
due_var             = tk.StringVar(value=datetime.today().strftime("%Y-%m-%d"))
tags_var            = tk.StringVar()
progress_var        = tk.IntVar(value=0)
search_var          = tk.StringVar()
filter_status_var   = tk.StringVar(value="All")
filter_priority_var = tk.StringVar(value="All")
filter_category_var = tk.StringVar(value="All")
sort_by_var         = tk.StringVar(value="Due Date")

# =========================
# STYLE
# =========================

style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview",
    background=T["CARD"], foreground=T["TEXT"],
    fieldbackground=T["CARD"], rowheight=32, font=("Segoe UI", 9))
style.configure("Treeview.Heading",
    background=T["ACCENT"], foreground="white",
    font=("Segoe UI", 9, "bold"), relief="flat")
style.map("Treeview", background=[("selected", T["ACCENT"])])
style.configure("TCombobox",
    background=T["CARD"], foreground=T["TEXT"],
    fieldbackground=T["CARD"], font=("Segoe UI", 9))
style.configure("TScrollbar",
    background=T["CARD"], troughcolor=T["BG"], arrowcolor=T["SUBTEXT"])
style.configure("TProgressbar",
    background=T["ACCENT"], troughcolor=T["CARD"])

# =========================
# HELPER WIDGETS
# =========================

def make_button(parent, text, command, color=None, width=None, pady=6, padx=12):
    c = color or T["ACCENT"]
    btn = tk.Button(parent, text=text, command=command,
        bg=c, fg="white", relief="flat",
        font=("Segoe UI", 9, "bold"),
        padx=padx, pady=pady,
        activebackground=T["ACCENT2"], activeforeground="white",
        cursor="hand2", bd=0)
    if width:
        btn.config(width=width)
    btn.bind("<Enter>", lambda e: btn.config(bg=T["ACCENT2"]))
    btn.bind("<Leave>", lambda e: btn.config(bg=c))
    return btn

def make_entry(parent, textvariable, width=None):
    e = tk.Entry(parent, textvariable=textvariable,
        bg=T["CARD"], fg=T["TEXT"], insertbackground=T["TEXT"],
        relief="flat", font=("Segoe UI", 10),
        highlightthickness=1,
        highlightcolor=T["ACCENT"],
        highlightbackground=T["BORDER"])
    if width:
        e.config(width=width)
    return e

def create_scrollable_frame(parent):
    container = tk.Frame(parent, bg=T["BG"])
    container.pack(fill="both", expand=True)

    canvas = tk.Canvas(
        container,
        bg=T["BG"],
        highlightthickness=0
    )

    scrollbar = ttk.Scrollbar(
        container,
        orient="vertical",
        command=canvas.yview
    )

    scrollable_frame = tk.Frame(
        canvas,
        bg=T["BG"]
    )

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window(
        (0, 0),
        window=scrollable_frame,
        anchor="nw"
    )

    canvas.configure(
        yscrollcommand=scrollbar.set
    )

    canvas.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )

    def _on_mousewheel(event):
        canvas.yview_scroll(
            int(-1 * (event.delta / 120)),
            "units"
        )

    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    return scrollable_frame

# =========================
# UTILITY
# =========================

def log_activity(action, task_title):
    cur.execute(
        "INSERT INTO activity_log(action, task_title, timestamp) VALUES(?,?,?)",
        (action, task_title, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()

def days_until(due_date_str):
    try:
        return (datetime.strptime(due_date_str, "%Y-%m-%d") - datetime.today()).days
    except:
        return None

# =========================
# LAYOUT SKELETON
# =========================

# --- Top bar ---
top_bar = tk.Frame(root, bg=T["SIDEBAR"], height=55)
top_bar.pack(fill="x", side="top")
top_bar.pack_propagate(False)

tk.Label(top_bar, text="Smart Task Manager Pro",
    bg=T["SIDEBAR"], fg=T["TEXT"],
    font=("Segoe UI", 15, "bold")).pack(side="left", padx=20, pady=10)

clock_label = tk.Label(top_bar, text="",
    bg=T["SIDEBAR"], fg=T["ACCENT2"], font=("Segoe UI", 10))
clock_label.pack(side="right", padx=20)

def update_clock():
    clock_label.config(text=datetime.now().strftime("%H:%M:%S    %d %b %Y"))
    root.after(1000, update_clock)

update_clock()

# --- Body ---
body = tk.Frame(root, bg=T["BG"])
body.pack(fill="both", expand=True)

sidebar = tk.Frame(body, bg=T["SIDEBAR"], width=220)
sidebar.pack(fill="y", side="left")
sidebar.pack_propagate(False)

main_content = tk.Frame(body, bg=T["BG"])
main_content.pack(fill="both", expand=True, side="left")

# =========================
# SIDEBAR
# =========================

tk.Label(sidebar, text="DASHBOARD", bg=T["SIDEBAR"], fg=T["SUBTEXT"],
    font=("Segoe UI", 8, "bold")).pack(pady=(20,5), padx=15, anchor="w")

stat_total     = tk.StringVar(value="0")
stat_pending   = tk.StringVar(value="0")
stat_completed = tk.StringVar(value="0")
stat_overdue   = tk.StringVar(value="0")

def make_stat_card(parent, label, var):
    f = tk.Frame(parent, bg=T["CARD"], padx=12, pady=10)
    f.pack(fill="x", padx=12, pady=4)
    tk.Label(f, text=label, bg=T["CARD"], fg=T["SUBTEXT"],
        font=("Segoe UI", 8)).pack(anchor="w")
    tk.Label(f, textvariable=var, bg=T["CARD"], fg=T["ACCENT2"],
        font=("Segoe UI", 18, "bold")).pack(anchor="w")

make_stat_card(sidebar, "Total Tasks",  stat_total)
make_stat_card(sidebar, "Pending",      stat_pending)
make_stat_card(sidebar, "Completed",    stat_completed)
make_stat_card(sidebar, "Overdue",      stat_overdue)

tk.Label(sidebar, text="QUICK FILTER", bg=T["SIDEBAR"], fg=T["SUBTEXT"],
    font=("Segoe UI", 8, "bold")).pack(pady=(20,5), padx=15, anchor="w")

def sidebar_filter(status):
    filter_status_var.set(status)
    refresh_tasks()

for label, status in [
    ("All Tasks",   "All"),
    ("Pending",     "Pending"),
    ("Completed",   "Completed"),
    ("In Progress", "In Progress"),
    ("Overdue",     "Overdue"),
]:
    btn = tk.Button(sidebar, text=label,
        command=lambda s=status: sidebar_filter(s),
        bg=T["SIDEBAR"], fg=T["TEXT"], relief="flat",
        font=("Segoe UI", 9), anchor="w",
        padx=15, pady=6, cursor="hand2",
        activebackground=T["HOVER"])
    btn.pack(fill="x")
    btn.bind("<Enter>", lambda e, b=btn: b.config(bg=T["HOVER"]))
    btn.bind("<Leave>", lambda e, b=btn: b.config(bg=T["SIDEBAR"]))

tk.Label(sidebar, text="CATEGORIES", bg=T["SIDEBAR"], fg=T["SUBTEXT"],
    font=("Segoe UI", 8, "bold")).pack(pady=(20,5), padx=15, anchor="w")

for cat, icon in CATEGORY_ICONS.items():
    btn = tk.Button(sidebar, text=f"{icon} {cat}",
        command=lambda c=cat: [filter_category_var.set(c), refresh_tasks()],
        bg=T["SIDEBAR"], fg=T["TEXT"], relief="flat",
        font=("Segoe UI", 9), anchor="w",
        padx=15, pady=5, cursor="hand2",
        activebackground=T["HOVER"])
    btn.pack(fill="x")
    btn.bind("<Enter>", lambda e, b=btn: b.config(bg=T["HOVER"]))
    btn.bind("<Leave>", lambda e, b=btn: b.config(bg=T["SIDEBAR"]))

tk.Frame(sidebar, bg=T["BORDER"], height=1).pack(fill="x", padx=12, pady=15)

# Export / Import defined after functions below; use lambda to defer
make_button(sidebar, "Export CSV", lambda: export_csv(), width=22, pady=5).pack(pady=3, padx=12, fill="x")
make_button(sidebar, "Import CSV", lambda: import_csv(), color=T["CARD"], width=22, pady=5).pack(pady=3, padx=12, fill="x")

# =========================
# TOOLBAR & TREE
# =========================

toolbar = tk.Frame(main_content, bg=T["CARD"], pady=8)
toolbar.pack(fill="x")

search_frame = tk.Frame(toolbar, bg=T["CARD"])
search_frame.pack(side="left", padx=15)
tk.Label(search_frame, text="Search:", bg=T["CARD"], fg=T["SUBTEXT"],
    font=("Segoe UI", 9)).pack(side="left")
search_entry = make_entry(search_frame, search_var, width=25)
search_entry.pack(side="left", padx=5)
search_var.trace("w", lambda *a: refresh_tasks())

filter_frame = tk.Frame(toolbar, bg=T["CARD"])
filter_frame.pack(side="left", padx=10)

for label, var, values in [
    ("Status:",   filter_status_var,   ["All","Pending","In Progress","Completed","Overdue"]),
    ("Priority:", filter_priority_var, ["All","High","Medium","Low"]),
    ("Category:", filter_category_var, ["All"] + list(CATEGORY_ICONS.keys())),
    ("Sort:",     sort_by_var,         ["Due Date","Priority","Title","Created","Progress"]),
]:
    tk.Label(filter_frame, text=label, bg=T["CARD"], fg=T["SUBTEXT"],
        font=("Segoe UI", 8)).pack(side="left", padx=(8,2))
    cb = ttk.Combobox(filter_frame, textvariable=var, values=values,
        width=10, state="readonly")
    cb.pack(side="left")
    cb.bind("<<ComboboxSelected>>", lambda e: refresh_tasks())

# Action bar -- all commands via lambda so forward refs are fine
action_bar = tk.Frame(main_content, bg=T["BG"], pady=6)
action_bar.pack(fill="x", padx=15)

make_button(action_bar, "+ Add Task",   lambda: open_add_task_window()).pack(side="left", padx=3)
make_button(action_bar, "Edit",         lambda: edit_task_window(),    color="#5c5ccc").pack(side="left", padx=3)
make_button(action_bar, "Complete",     lambda: complete_task(),       color=T["SUCCESS"]).pack(side="left", padx=3)
make_button(action_bar, "In Progress",  lambda: set_in_progress(),     color=T["WARNING"]).pack(side="left", padx=3)
make_button(action_bar, "Delete",       lambda: delete_task(),         color=T["DANGER"]).pack(side="left", padx=3)
make_button(action_bar, "Stats",        lambda: show_statistics(),     color="#9c27b0").pack(side="left", padx=3)
make_button(action_bar, "Activity Log", lambda: show_activity_log(),   color="#607d8b").pack(side="left", padx=3)
make_button(action_bar, "Reminders",    lambda: show_reminders(),      color="#e91e63").pack(side="left", padx=3)
make_button(action_bar, "Bulk Actions", lambda: show_bulk_actions(),   color="#795548").pack(side="left", padx=3)
make_button(action_bar, "Refresh",      lambda: refresh_tasks(),       color=T["CARD"]).pack(side="right", padx=3)

# Overall progress bar
prog_frame = tk.Frame(main_content, bg=T["BG"])
prog_frame.pack(fill="x", padx=15, pady=(0,5))
overall_progress_label = tk.Label(prog_frame, text="Overall Completion: 0%",
    bg=T["BG"], fg=T["SUBTEXT"], font=("Segoe UI", 8))
overall_progress_label.pack(side="left")
overall_progress = ttk.Progressbar(prog_frame, length=300, mode="determinate")
overall_progress.pack(side="left", padx=10)

# Treeview
tree_frame = tk.Frame(main_content, bg=T["BG"])
tree_frame.pack(fill="both", expand=True, padx=15, pady=(0,10))

columns = ("ID","Title","Category","Priority","Due Date","Status","Progress","Tags")
tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="extended")

col_widths = {"ID":40,"Title":230,"Category":90,"Priority":70,
              "Due Date":100,"Status":90,"Progress":80,"Tags":150}
for col in columns:
    tree.heading(col, text=col, command=lambda c=col: sort_by_column(c))
    tree.column(col, width=col_widths.get(col, 80),
        anchor="w" if col in ("Title","Tags") else "center")

tree.tag_configure("high",        foreground="#f44336")
tree.tag_configure("medium",      foreground="#ff9800")
tree.tag_configure("low",         foreground="#4CAF50")
tree.tag_configure("completed",   foreground=T["SUBTEXT"])
tree.tag_configure("overdue",     background="#3d1a1a")
tree.tag_configure("today",       background="#2a2a1a")
tree.tag_configure("in_progress", foreground="#58a6ff")

vsb = ttk.Scrollbar(tree_frame, orient="vertical",   command=tree.yview)
hsb = ttk.Scrollbar(tree_frame, orient="horizontal",  command=tree.xview)
tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
tree.grid(row=0, column=0, sticky="nsew")
vsb.grid(row=0, column=1, sticky="ns")
hsb.grid(row=1, column=0, sticky="ew")
tree_frame.grid_rowconfigure(0, weight=1)
tree_frame.grid_columnconfigure(0, weight=1)

# Status bar
status_bar = tk.Frame(main_content, bg=T["SIDEBAR"], height=28)
status_bar.pack(fill="x", side="bottom")
status_bar.pack_propagate(False)
status_label = tk.Label(status_bar, text="Ready",
    bg=T["SIDEBAR"], fg=T["SUBTEXT"], font=("Segoe UI", 8))
status_label.pack(side="left", padx=10, pady=5)
selected_label = tk.Label(status_bar, text="No selection",
    bg=T["SIDEBAR"], fg=T["SUBTEXT"], font=("Segoe UI", 8))
selected_label.pack(side="right", padx=10, pady=5)

# =========================
# CORE FUNCTIONS
# =========================

def refresh_tasks():
    for row in tree.get_children():
        tree.delete(row)

    query  = "SELECT id,title,category,priority,due_date,status,progress,tags,description FROM tasks WHERE 1=1"
    params = []

    search = search_var.get().strip()
    if search:
        query += " AND (title LIKE ? OR description LIKE ? OR tags LIKE ?)"
        params += [f"%{search}%", f"%{search}%", f"%{search}%"]

    sf = filter_status_var.get()
    if sf == "Overdue":
        today = datetime.today().strftime("%Y-%m-%d")
        query += " AND due_date < ? AND status != 'Completed'"
        params.append(today)
    elif sf != "All":
        query += " AND status = ?"
        params.append(sf)

    pf = filter_priority_var.get()
    if pf != "All":
        query += " AND priority = ?"
        params.append(pf)

    cf = filter_category_var.get()
    if cf != "All":
        query += " AND category = ?"
        params.append(cf)

    sort_map = {
        "Due Date": "due_date ASC",
        "Priority": "CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END",
        "Title":    "title ASC",
        "Created":  "created_at DESC",
        "Progress": "progress DESC",
    }
    query += f" ORDER BY {sort_map.get(sort_by_var.get(), 'due_date ASC')}"

    cur.execute(query, params)
    rows = cur.fetchall()

    today_str = datetime.today().strftime("%Y-%m-%d")

    for row in rows:
        id_, title, cat, priority, due, status, progress, tags, _ = row
        icon      = CATEGORY_ICONS.get(cat, "[*]")
        prog_disp = f"{progress}%" if progress else "0%"
        due_disp  = due or "-"
        d         = days_until(due) if due else None

        if due and d is not None:
            if d < 0 and status != "Completed":
                due_disp = f"[!] {due} ({abs(d)}d ago)"
            elif d == 0 and status != "Completed":
                due_disp = "Due TODAY"
            elif d <= 2 and status != "Completed":
                due_disp = f"{due} ({d}d left)"

        tags_list = [t.strip().upper() for t in (tags or "").split(",") if t.strip()]
        tags_disp = "  ".join([f"[{t}]" for t in tags_list[:3]])

        item_tags = []
        if status == "Completed":
            item_tags.append("completed")
        elif d is not None and d < 0:
            item_tags.append("overdue")
        elif d == 0:
            item_tags.append("today")
        elif status == "In Progress":
            item_tags.append("in_progress")

        if status != "Completed":
            if priority == "High":     item_tags.append("high")
            elif priority == "Medium": item_tags.append("medium")
            elif priority == "Low":    item_tags.append("low")

        tree.insert("", "end",
            values=(id_, f"{icon} {title}", cat, priority, due_disp, status, prog_disp, tags_disp),
            tags=tuple(item_tags))

    # Update sidebar stats
    cur.execute("SELECT COUNT(*) FROM tasks")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM tasks WHERE status='Pending'")
    pending = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM tasks WHERE status='Completed'")
    completed = cur.fetchone()[0]
    cur.execute(f"SELECT COUNT(*) FROM tasks WHERE due_date < '{today_str}' AND status != 'Completed'")
    overdue = cur.fetchone()[0]

    stat_total.set(str(total))
    stat_pending.set(str(pending))
    stat_completed.set(str(completed))
    stat_overdue.set(str(overdue))

    pct = int((completed / total) * 100) if total > 0 else 0
    overall_progress["value"] = pct
    overall_progress_label.config(text=f"Overall Completion: {pct}%")
    status_label.config(
        text=f"Showing {len(rows)} task(s)  -  {total} total  -  {completed} completed  -  {overdue} overdue")


def get_selected_id():
    sel = tree.selection()
    if not sel:
        messagebox.showwarning("Warning", "Please select a task first.")
        return None
    return tree.item(sel[0])["values"][0]


def delete_task():
    sel = tree.selection()
    if not sel:
        messagebox.showwarning("Warning", "Please select a task first.")
        return
    ids = [tree.item(s)["values"][0] for s in sel]
    if not messagebox.askyesno("Confirm Delete",
            f"Delete {len(ids)} task(s)? This cannot be undone."):
        return
    for task_id in ids:
        cur.execute("SELECT title FROM tasks WHERE id=?", (task_id,))
        row = cur.fetchone()
        if row:
            log_activity("Deleted", row[0])
        cur.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    refresh_tasks()


def complete_task():
    task_id = get_selected_id()
    if task_id is None:
        return
    cur.execute("SELECT title FROM tasks WHERE id=?", (task_id,))
    row = cur.fetchone()
    cur.execute(
        "UPDATE tasks SET status='Completed', progress=100, completed_at=? WHERE id=?",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), task_id))
    conn.commit()
    log_activity("Completed", row[0] if row else "")
    refresh_tasks()


def set_in_progress():
    task_id = get_selected_id()
    if task_id is None:
        return
    cur.execute("UPDATE tasks SET status='In Progress' WHERE id=?", (task_id,))
    conn.commit()
    refresh_tasks()


def sort_by_column(col):
    col_map = {
        "ID": "id", "Title": "title", "Category": "category",
        "Priority": "priority", "Due Date": "due_date",
        "Status": "status", "Progress": "progress", "Tags": "tags",
    }
    sort_by_var.set(col_map.get(col, "due_date"))
    refresh_tasks()


def export_csv():
    file = filedialog.asksaveasfilename(
        defaultextension=".csv", filetypes=[("CSV","*.csv")])
    if not file:
        return
    cur.execute("SELECT * FROM tasks")
    rows = cur.fetchall()
    with open(file, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ID","Title","Description","Category","Priority",
                    "Due Date","Status","Created","Completed","Tags","Progress","Notes"])
        w.writerows(rows)
    messagebox.showinfo("Export", f"Tasks exported to:\n{file}")
    log_activity("Export CSV", f"{len(rows)} tasks")


def import_csv():
    file = filedialog.askopenfilename(filetypes=[("CSV","*.csv")])
    if not file:
        return
    try:
        with open(file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                cur.execute("""
                    INSERT INTO tasks(title,description,category,priority,
                        due_date,status,created_at,tags,progress,notes)
                    VALUES(?,?,?,?,?,?,?,?,?,?)
                """, (
                    row.get("Title",""),
                    row.get("Description",""),
                    row.get("Category","Other"),
                    row.get("Priority","Medium"),
                    row.get("Due Date",""),
                    row.get("Status","Pending"),
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    row.get("Tags",""),
                    int(row.get("Progress",0)),
                    row.get("Notes",""),
                ))
                count += 1
        conn.commit()
        refresh_tasks()
        messagebox.showinfo("Import", f"{count} tasks imported!")
        log_activity("Import CSV", f"{count} tasks")
    except Exception as e:
        messagebox.showerror("Import Error", str(e))


# =========================
# ADD TASK WINDOW
# =========================

def open_add_task_window():
    win = tk.Toplevel(root)
    win.title("Add Task")
    win.geometry("650x700")
    win.configure(bg=T["BG"])
    win.grab_set()

    win.update_idletasks()
    wx = root.winfo_x() + (root.winfo_width()  - 520) // 2
    wy = root.winfo_y() + (root.winfo_height() - 600) // 2
    win.geometry(f"520x600+{wx}+{wy}")

    header = tk.Frame(win, bg=T["ACCENT"], height=50)
    header.pack(fill="x")
    header.pack_propagate(False)
    tk.Label(header, text="+ Add New Task", bg=T["ACCENT"], fg="white",
        font=("Segoe UI", 13, "bold")).pack(pady=12)

    bf = create_scrollable_frame(win)

    lv_title = tk.StringVar()
    lv_desc  = tk.StringVar()
    lv_tags  = tk.StringVar()
    lv_due   = tk.StringVar(value=datetime.today().strftime("%Y-%m-%d"))
    lv_cat   = tk.StringVar(value="Study")
    lv_prio  = tk.StringVar(value="Medium")
    lv_prog  = tk.IntVar(value=0)

    for label, var in [("Task Title *", lv_title), ("Description", lv_desc),
                        ("Tags (comma separated)", lv_tags), ("Due Date (YYYY-MM-DD)", lv_due)]:
        tk.Label(bf, text=label, bg=T["BG"], fg=T["SUBTEXT"],
            font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(8,2))
        make_entry(bf, var).pack(fill="x", ipady=5)

    tk.Label(bf, text="Category", bg=T["BG"], fg=T["SUBTEXT"],
        font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(8,2))
    ttk.Combobox(bf, textvariable=lv_cat,
        values=list(CATEGORY_ICONS.keys()), state="readonly").pack(fill="x", ipady=3)

    tk.Label(bf, text="Priority", bg=T["BG"], fg=T["SUBTEXT"],
        font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(8,2))
    pf = tk.Frame(bf, bg=T["BG"])
    pf.pack(fill="x")
    for p, color in PRIORITY_COLORS.items():
        tk.Radiobutton(pf, text=p, variable=lv_prio, value=p,
            bg=T["BG"], fg=color, selectcolor=T["CARD"],
            activebackground=T["BG"],
            font=("Segoe UI", 10, "bold")).pack(side="left", padx=10)

    tk.Label(bf, text="Initial Progress (%)", bg=T["BG"], fg=T["SUBTEXT"],
        font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(8,2))
    pf2 = tk.Frame(bf, bg=T["BG"])
    pf2.pack(fill="x")
    tk.Scale(pf2, variable=lv_prog, from_=0, to=100, orient="horizontal",
        bg=T["BG"], fg=T["TEXT"], troughcolor=T["CARD"],
        highlightthickness=0, length=300, sliderrelief="flat").pack(side="left", fill="x", expand=True)
    tk.Label(pf2, textvariable=lv_prog, bg=T["BG"], fg=T["ACCENT2"],
        font=("Segoe UI", 10, "bold")).pack(side="left", padx=5)

    tk.Label(bf, text="Notes", bg=T["BG"], fg=T["SUBTEXT"],
        font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(8,2))
    notes_box = tk.Text(bf, height=3, bg=T["CARD"], fg=T["TEXT"],
        insertbackground=T["TEXT"], relief="flat", font=("Segoe UI", 9),
        highlightthickness=1, highlightcolor=T["ACCENT"],
        highlightbackground=T["BORDER"])
    notes_box.pack(fill="x")

    def save_task():
        t = lv_title.get().strip()
        if not t:
            messagebox.showerror("Error", "Task title is required!", parent=win)
            return
        cur.execute("""
            INSERT INTO tasks(title,description,category,priority,due_date,
                status,created_at,tags,progress,notes)
            VALUES(?,?,?,?,?,?,?,?,?,?)
        """, (t, lv_desc.get(), lv_cat.get(), lv_prio.get(), lv_due.get(),
              "Pending", datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
              lv_tags.get(), lv_prog.get(), notes_box.get("1.0","end-1c")))
        conn.commit()
        log_activity("Added", t)
        refresh_tasks()
        win.destroy()
        status_label.config(text=f"Task '{t}' added successfully!")

    btn_f = tk.Frame(win, bg=T["BG"], pady=10)
    btn_f.pack(fill="x", padx=25)
    make_button(btn_f, "Add Task", save_task, pady=10).pack(
        side="left", expand=True, fill="x", padx=(0,5))
    make_button(btn_f, "Cancel", win.destroy, color=T["DANGER"], pady=10).pack(
        side="left", expand=True, fill="x")


# =========================
# EDIT TASK WINDOW
# =========================

def edit_task_window():
    sel = tree.selection()
    if not sel:
        messagebox.showwarning("Warning", "Select a task to edit.")
        return

    task_id = tree.item(sel[0])["values"][0]
    cur.execute("SELECT * FROM tasks WHERE id=?", (task_id,))
    row = cur.fetchone()
    if not row:
        return

    id_, title, description, category, priority, due_date, \
        status, created_at, completed_at, tags, progress, notes = row

    win = tk.Toplevel(root)
    win.title("Edit Task")
    win.geometry("700x750")
    win.configure(bg=T["BG"])
    win.grab_set()

    win.update_idletasks()
    wx = root.winfo_x() + (root.winfo_width()  - 540) // 2
    wy = root.winfo_y() + (root.winfo_height() - 660) // 2
    win.geometry(f"540x660+{wx}+{wy}")

    header = tk.Frame(win, bg="#5c5ccc", height=50)
    header.pack(fill="x")
    header.pack_propagate(False)
    short = (title[:40] + "...") if len(title) > 40 else title
    tk.Label(header, text=f"Edit: {short}",
        bg="#5c5ccc", fg="white", font=("Segoe UI", 12, "bold")).pack(pady=12)

    bf = create_scrollable_frame(win)

    e_title  = tk.StringVar(value=title)
    e_desc   = tk.StringVar(value=description or "")
    e_cat    = tk.StringVar(value=category)
    e_prio   = tk.StringVar(value=priority)
    e_due    = tk.StringVar(value=due_date or "")
    e_tags   = tk.StringVar(value=tags or "")
    e_status = tk.StringVar(value=status)
    e_prog   = tk.IntVar(value=progress or 0)

    for label, var in [("Title *", e_title), ("Description", e_desc),
                        ("Tags", e_tags), ("Due Date (YYYY-MM-DD)", e_due)]:
        tk.Label(bf, text=label, bg=T["BG"], fg=T["SUBTEXT"],
            font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(6,1))
        make_entry(bf, var).pack(fill="x", ipady=4)

    tk.Label(bf, text="Category", bg=T["BG"], fg=T["SUBTEXT"],
        font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(6,1))
    ttk.Combobox(bf, textvariable=e_cat,
        values=list(CATEGORY_ICONS.keys()), state="readonly").pack(fill="x", ipady=3)

    tk.Label(bf, text="Priority", bg=T["BG"], fg=T["SUBTEXT"],
        font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(6,1))
    pf = tk.Frame(bf, bg=T["BG"])
    pf.pack(fill="x")
    for p, color in PRIORITY_COLORS.items():
        tk.Radiobutton(pf, text=p, variable=e_prio, value=p,
            bg=T["BG"], fg=color, selectcolor=T["CARD"],
            activebackground=T["BG"],
            font=("Segoe UI", 10, "bold")).pack(side="left", padx=10)

    tk.Label(bf, text="Status", bg=T["BG"], fg=T["SUBTEXT"],
        font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(6,1))
    ttk.Combobox(bf, textvariable=e_status,
        values=["Pending","In Progress","Completed"],
        state="readonly").pack(fill="x", ipady=3)

    tk.Label(bf, text="Progress (%)", bg=T["BG"], fg=T["SUBTEXT"],
        font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(6,1))
    pf2 = tk.Frame(bf, bg=T["BG"])
    pf2.pack(fill="x")
    tk.Scale(pf2, variable=e_prog, from_=0, to=100, orient="horizontal",
        bg=T["BG"], fg=T["TEXT"], troughcolor=T["CARD"],
        highlightthickness=0, length=300, sliderrelief="flat").pack(side="left", fill="x", expand=True)
    tk.Label(pf2, textvariable=e_prog, bg=T["BG"], fg=T["ACCENT2"],
        font=("Segoe UI", 10, "bold")).pack(side="left", padx=5)

    tk.Label(bf, text="Notes", bg=T["BG"], fg=T["SUBTEXT"],
        font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(6,1))
    notes_box = tk.Text(bf, height=3, bg=T["CARD"], fg=T["TEXT"],
        insertbackground=T["TEXT"], relief="flat", font=("Segoe UI", 9),
        highlightthickness=1, highlightcolor=T["ACCENT"],
        highlightbackground=T["BORDER"])
    notes_box.insert("1.0", notes or "")
    notes_box.pack(fill="x")

    if created_at:
        tk.Label(bf, text=f"Created: {created_at}",
            bg=T["BG"], fg=T["SUBTEXT"], font=("Segoe UI", 7)).pack(anchor="e", pady=(5,0))

    def save_changes():
        t = e_title.get().strip()
        if not t:
            messagebox.showerror("Error", "Title required!", parent=win)
            return
        new_notes = notes_box.get("1.0","end-1c")
        c_at      = completed_at
        if e_status.get() == "Completed" and status != "Completed":
            c_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("""
            UPDATE tasks SET title=?,description=?,category=?,priority=?,
                due_date=?,status=?,tags=?,progress=?,notes=?,completed_at=?
            WHERE id=?
        """, (t, e_desc.get(), e_cat.get(), e_prio.get(), e_due.get(),
              e_status.get(), e_tags.get(), e_prog.get(), new_notes, c_at, task_id))
        conn.commit()
        log_activity("Edited", t)
        refresh_tasks()
        win.destroy()
        status_label.config(text=f"Task '{t}' updated!")

    btn_f = tk.Frame(win, bg=T["BG"], pady=10)
    btn_f.pack(fill="x", padx=25)
    make_button(btn_f, "Save Changes", save_changes, pady=10).pack(
        side="left", expand=True, fill="x", padx=(0,5))
    make_button(btn_f, "Cancel", win.destroy, color=T["DANGER"], pady=10).pack(
        side="left", expand=True, fill="x")


# =========================
# STATISTICS WINDOW
# =========================

def show_statistics():
    win = tk.Toplevel(root)
    win.title("Task Statistics")
    win.geometry("700x560")
    win.configure(bg=T["BG"])
    win.grab_set()

    header = tk.Frame(win, bg="#9c27b0", height=50)
    header.pack(fill="x")
    header.pack_propagate(False)
    tk.Label(header, text="Task Statistics & Analytics",
        bg="#9c27b0", fg="white", font=("Segoe UI", 13, "bold")).pack(pady=12)

    body = tk.Frame(win, bg=T["BG"], padx=20, pady=15)
    body.pack(fill="both", expand=True)

    cur.execute("SELECT COUNT(*) FROM tasks");                                                       total     = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM tasks WHERE status='Completed'");                              completed = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM tasks WHERE status='Pending'");                                pending   = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM tasks WHERE status='In Progress'");                            in_prog   = cur.fetchone()[0]
    today = datetime.today().strftime("%Y-%m-%d")
    cur.execute(f"SELECT COUNT(*) FROM tasks WHERE due_date < '{today}' AND status != 'Completed'"); overdue   = cur.fetchone()[0]
    cur.execute("SELECT AVG(progress) FROM tasks");                                                  avg_prog  = cur.fetchone()[0] or 0

    cards = tk.Frame(body, bg=T["BG"])
    cards.pack(fill="x", pady=(0,15))
    for label, val, color in [
        ("Total",       total,     T["ACCENT"]),
        ("Completed",   completed, T["SUCCESS"]),
        ("Pending",     pending,   T["WARNING"]),
        ("In Progress", in_prog,   "#58a6ff"),
        ("Overdue",     overdue,   T["DANGER"]),
    ]:
        f = tk.Frame(cards, bg=T["CARD"], padx=10, pady=10)
        f.pack(side="left", expand=True, fill="both", padx=5)
        tk.Label(f, text=str(val), bg=T["CARD"], fg=color,
            font=("Segoe UI", 22, "bold")).pack()
        tk.Label(f, text=label, bg=T["CARD"], fg=T["SUBTEXT"],
            font=("Segoe UI", 9)).pack()

    tk.Label(body, text=f"Average Progress: {avg_prog:.1f}%",
        bg=T["BG"], fg=T["TEXT"], font=("Segoe UI", 10)).pack(anchor="w", pady=(5,3))
    ttk.Progressbar(body, length=640, mode="determinate", value=avg_prog).pack(fill="x")

    tk.Label(body, text="By Category", bg=T["BG"], fg=T["SUBTEXT"],
        font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(15,5))
    cur.execute("SELECT category, COUNT(*) FROM tasks GROUP BY category ORDER BY COUNT(*) DESC")
    for cat, count in cur.fetchall():
        rf = tk.Frame(body, bg=T["BG"])
        rf.pack(fill="x", pady=2)
        icon = CATEGORY_ICONS.get(cat, "[*]")
        tk.Label(rf, text=f"{icon} {cat}", bg=T["BG"], fg=T["TEXT"],
            font=("Segoe UI", 9), width=18, anchor="w").pack(side="left")
        pct = int((count / total) * 100) if total > 0 else 0
        ttk.Progressbar(rf, length=380, mode="determinate", value=pct).pack(side="left", padx=8)
        tk.Label(rf, text=f"{count} ({pct}%)", bg=T["BG"], fg=T["SUBTEXT"],
            font=("Segoe UI", 9)).pack(side="left")

    tk.Label(body, text="By Priority", bg=T["BG"], fg=T["SUBTEXT"],
        font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(15,5))
    cur.execute("SELECT priority, COUNT(*) FROM tasks GROUP BY priority")
    for p, count in cur.fetchall():
        rf = tk.Frame(body, bg=T["BG"])
        rf.pack(fill="x", pady=2)
        pcolor = PRIORITY_COLORS.get(p, T["TEXT"])
        tk.Label(rf, text=f"* {p}", bg=T["BG"], fg=pcolor,
            font=("Segoe UI", 9, "bold"), width=10, anchor="w").pack(side="left")
        pct = int((count / total) * 100) if total > 0 else 0
        ttk.Progressbar(rf, length=380, mode="determinate", value=pct).pack(side="left", padx=8)
        tk.Label(rf, text=f"{count} ({pct}%)", bg=T["BG"], fg=T["SUBTEXT"],
            font=("Segoe UI", 9)).pack(side="left")

    rate = int((completed / total) * 100) if total > 0 else 0
    tk.Label(body, text=f"Completion Rate: {rate}%",
        bg=T["BG"], fg=T["SUCCESS"] if rate >= 50 else T["WARNING"],
        font=("Segoe UI", 12, "bold")).pack(pady=15)


# =========================
# ACTIVITY LOG
# =========================

def show_activity_log():
    win = tk.Toplevel(root)
    win.title("Activity Log")
    win.geometry("600x450")
    win.configure(bg=T["BG"])

    header = tk.Frame(win, bg="#607d8b", height=45)
    header.pack(fill="x")
    header.pack_propagate(False)
    tk.Label(header, text="Activity Log",
        bg="#607d8b", fg="white", font=("Segoe UI", 12, "bold")).pack(pady=10)

    frame = tk.Frame(win, bg=T["BG"], padx=15, pady=10)
    frame.pack(fill="both", expand=True)

    log_cols = ("Timestamp", "Action", "Task")
    log_tree = ttk.Treeview(frame, columns=log_cols, show="headings")
    for col in log_cols:
        log_tree.heading(col, text=col)
        log_tree.column(col, width=180 if col == "Timestamp" else 200)

    log_sb = ttk.Scrollbar(frame, orient="vertical", command=log_tree.yview)
    log_tree.configure(yscrollcommand=log_sb.set)
    log_tree.pack(side="left", fill="both", expand=True)
    log_sb.pack(side="right", fill="y")

    cur.execute(
        "SELECT timestamp, action, task_title FROM activity_log ORDER BY id DESC LIMIT 100"
    )
    for row in cur.fetchall():
        log_tree.insert("", "end", values=row)

    def clear_log():
        if messagebox.askyesno(
            "Clear Log",
            "Clear all activity logs?",
            parent=win
        ):
            cur.execute("DELETE FROM activity_log")
            conn.commit()
            for item in log_tree.get_children():
                log_tree.delete(item)

    make_button(
        win,
        "Clear Log",
        clear_log,
        color=T["DANGER"]
    ).pack(pady=8)


# =========================
# REMINDERS WINDOW
# =========================

def show_reminders():
    win = tk.Toplevel(root)
    win.title("Upcoming Reminders")
    win.geometry("580x450")
    win.configure(bg=T["BG"])

    header = tk.Frame(win, bg="#e91e63", height=45)
    header.pack(fill="x")
    header.pack_propagate(False)
    tk.Label(header, text="Upcoming & Overdue Tasks",
        bg="#e91e63", fg="white", font=("Segoe UI", 12, "bold")).pack(pady=10)

    frame = tk.Frame(win, bg=T["BG"], padx=15, pady=10)
    frame.pack(fill="both", expand=True)

    in_3 = (datetime.today() + timedelta(days=3)).strftime("%Y-%m-%d")
    cur.execute("""
        SELECT title, priority, due_date, status FROM tasks
        WHERE status != 'Completed' AND due_date <= ?
        ORDER BY due_date ASC
    """, (in_3,))
    rows = cur.fetchall()

    if not rows:
        tk.Label(frame, text="No upcoming or overdue tasks in the next 3 days!",
            bg=T["BG"], fg=T["SUCCESS"], font=("Segoe UI", 11)).pack(pady=30)
    else:
        canvas = tk.Canvas(frame, bg=T["BG"], highlightthickness=0)
        sb2    = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=T["BG"])
        scroll_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=sb2.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb2.pack(side="right", fill="y")

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        for title, priority, due, status in rows:
            d     = days_until(due)
            color = T["DANGER"] if (d is not None and d < 0) else \
                    T["WARNING"] if d == 0 else T["TEXT"]
            card  = tk.Frame(scroll_frame, bg=T["CARD"], padx=12, pady=8)
            card.pack(fill="x", pady=4, padx=5)
            tk.Label(card, text=title, bg=T["CARD"], fg=T["TEXT"],
                font=("Segoe UI", 10, "bold")).pack(anchor="w")
            info = f"Due: {due}  -  Priority: {priority}  -  "
            if d is not None:
                if d < 0:    info += f"[!] {abs(d)} day(s) OVERDUE"
                elif d == 0: info += "Due TODAY"
                else:        info += f"{d} day(s) remaining"
            tk.Label(card, text=info, bg=T["CARD"], fg=color,
                font=("Segoe UI", 9)).pack(anchor="w")


# =========================
# BULK ACTIONS
# =========================

def show_bulk_actions():
    win = tk.Toplevel(root)
    win.title("Bulk Actions")
    win.geometry("420x330")
    win.configure(bg=T["BG"])

    header = tk.Frame(win, bg="#795548", height=45)
    header.pack(fill="x")
    header.pack_propagate(False)
    tk.Label(header, text="Bulk Actions", bg="#795548", fg="white",
        font=("Segoe UI", 12, "bold")).pack(pady=10)

    frame = tk.Frame(win, bg=T["BG"], padx=25, pady=20)
    frame.pack(fill="both", expand=True)

    tk.Label(frame, text="Actions apply to tasks matching current filters:",
        bg=T["BG"], fg=T["SUBTEXT"], font=("Segoe UI", 9)).pack(pady=(0,15))

    def bulk_complete():
        sf = filter_status_var.get()
        if not messagebox.askyesno("Bulk Complete",
                f"Mark all '{sf}' tasks as Completed?", parent=win):
            return
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if sf == "All":
            cur.execute("UPDATE tasks SET status='Completed',progress=100,completed_at=? WHERE status != 'Completed'", (ts,))
        else:
            cur.execute("UPDATE tasks SET status='Completed',progress=100,completed_at=? WHERE status=?", (ts, sf))
        conn.commit()
        log_activity("Bulk Complete", sf)
        refresh_tasks()
        win.destroy()

    def bulk_delete():
        sf = filter_status_var.get()
        if not messagebox.askyesno("Bulk Delete",
                f"DELETE all '{sf}' tasks? THIS CANNOT BE UNDONE!", parent=win):
            return
        if sf == "All":
            cur.execute("DELETE FROM tasks")
        else:
            cur.execute("DELETE FROM tasks WHERE status=?", (sf,))
        conn.commit()
        log_activity("Bulk Delete", sf)
        refresh_tasks()
        win.destroy()

    def bulk_priority():
        sub = tk.Toplevel(win)
        sub.title("Change Priority")
        sub.geometry("300x160")
        sub.configure(bg=T["BG"])
        np = tk.StringVar(value="Medium")
        tk.Label(sub, text="Set new priority for ALL tasks:",
            bg=T["BG"], fg=T["TEXT"], font=("Segoe UI", 10)).pack(pady=10)
        ttk.Combobox(sub, textvariable=np,
            values=["High","Medium","Low"], state="readonly").pack()
        def apply():
            cur.execute("UPDATE tasks SET priority=?", (np.get(),))
            conn.commit()
            refresh_tasks()
            sub.destroy()
            win.destroy()
        make_button(sub, "Apply to All", apply, pady=8).pack(pady=15)

    make_button(frame, "Mark All Filtered as Completed", bulk_complete,  color=T["SUCCESS"], pady=10).pack(fill="x", pady=5)
    make_button(frame, "Change Priority for All Tasks",  bulk_priority,  color=T["WARNING"], pady=10).pack(fill="x", pady=5)
    make_button(frame, "Delete All Filtered Tasks",      bulk_delete,    color=T["DANGER"],  pady=10).pack(fill="x", pady=5)

    tk.Label(frame, text="[!] These actions cannot be undone.",
        bg=T["BG"], fg=T["SUBTEXT"], font=("Segoe UI", 8)).pack(pady=8)


# =========================
# TASK DETAIL (double-click)
# =========================

def on_double_click(event):
    sel = tree.selection()
    if not sel:
        return
    task_id = tree.item(sel[0])["values"][0]
    cur.execute("SELECT * FROM tasks WHERE id=?", (task_id,))
    row = cur.fetchone()
    if not row:
        return

    id_, title, description, category, priority, due_date, \
        status, created_at, completed_at, tags, progress, notes = row

    win = tk.Toplevel(root)
    win.title("Task Detail")
    win.geometry("500x520")
    win.configure(bg=T["BG"])

    color = PRIORITY_COLORS.get(priority, T["ACCENT"])
    header = tk.Frame(win, bg=color, height=55)
    header.pack(fill="x")
    header.pack_propagate(False)
    icon = CATEGORY_ICONS.get(category, "[*]")
    tk.Label(header, text=f"{icon}  {title}",
        bg=color, fg="white", font=("Segoe UI", 13, "bold"),
        wraplength=450).pack(pady=14, padx=15, anchor="w")

    body = tk.Frame(win, bg=T["BG"], padx=20, pady=15)
    body.pack(fill="both", expand=True)

    def row_info(label, value, val_color=None):
        f = tk.Frame(body, bg=T["BG"])
        f.pack(fill="x", pady=4)
        tk.Label(f, text=label + ":", bg=T["BG"], fg=T["SUBTEXT"],
            font=("Segoe UI", 9, "bold"), width=14, anchor="w").pack(side="left")
        tk.Label(f, text=value or "-", bg=T["BG"],
            fg=val_color or T["TEXT"], font=("Segoe UI", 9),
            wraplength=330, justify="left").pack(side="left", padx=5)

    row_info("Category", f"{icon} {category}")
    row_info("Priority",  priority, PRIORITY_COLORS.get(priority))
    row_info("Status",    status,   T["SUCCESS"] if status == "Completed" else T["WARNING"])
    row_info("Due Date",  due_date)
    row_info("Tags",      tags)
    row_info("Created",   created_at)
    row_info("Completed", completed_at)

    for label, text in [("Description", description), ("Notes", notes)]:
        tk.Label(body, text=f"{label}:", bg=T["BG"], fg=T["SUBTEXT"],
            font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(10,3))
        box = tk.Text(body, height=3, bg=T["CARD"], fg=T["TEXT"],
            relief="flat", font=("Segoe UI", 9))
        box.insert("1.0", text or f"No {label.lower()}.")
        box.config(state="disabled")
        box.pack(fill="x")

    tk.Label(body, text=f"Progress: {progress or 0}%",
        bg=T["BG"], fg=T["TEXT"], font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(12,3))
    ttk.Progressbar(body, length=440, mode="determinate",
        value=progress or 0).pack(fill="x")

    btn_f = tk.Frame(win, bg=T["BG"], pady=10)
    btn_f.pack(fill="x", padx=20)
    make_button(btn_f, "Edit Task", lambda: [win.destroy(), edit_task_window()]).pack(side="left", padx=5)
    make_button(btn_f, "Complete",  lambda: [complete_task(), win.destroy()], color=T["SUCCESS"]).pack(side="left", padx=5)
    make_button(btn_f, "Close",     win.destroy, color=T["CARD"]).pack(side="right", padx=5)


tree.bind("<Double-1>", on_double_click)

def on_select(event):
    sel = tree.selection()
    selected_label.config(text=f"{len(sel)} task(s) selected")

tree.bind("<<TreeviewSelect>>", on_select)

def on_key(event):
    if event.keysym == "Delete":
        delete_task()
    elif event.keysym == "Return":
        on_double_click(event)
    elif event.state == 4 and event.keysym == "n":
        open_add_task_window()
    elif event.state == 4 and event.keysym == "f":
        search_entry.focus_set()
    elif event.state == 4 and event.keysym == "e":
        edit_task_window()

root.bind("<Key>", on_key)

# =========================
# INITIAL LOAD
# =========================

refresh_tasks()
root.after(60000, refresh_tasks)
status_label.config(
    text="Ready  -  Ctrl+N: New task   Ctrl+F: Search   Ctrl+E: Edit   Del: Delete   Double-click: Details")

root.mainloop()
conn.close()