\# 📇 ContactIQ 2026 — Personal Relationship Intelligence System



> A feature-rich, AI-powered desktop contact manager built with Python \& Tkinter.  

> \*\*CodSoft Python Programming Internship — Task 5 (Upgraded)\*\*



\---



\## 📌 Table of Contents



\- \[Overview](#overview)

\- \[Features](#features)

\- \[Screenshots / UI Structure](#ui-structure)

\- \[Tech Stack](#tech-stack)

\- \[Project Structure](#project-structure)

\- \[Installation \& Setup](#installation--setup)

\- \[How to Run](#how-to-run)

\- \[Usage Guide](#usage-guide)

\- \[Data Storage](#data-storage)

\- \[Import \& Export](#import--export)

\- \[AI Features](#ai-features)

\- \[Keyboard \& UX Highlights](#keyboard--ux-highlights)

\- \[Future Improvements](#future-improvements)

\- \[Author](#author)

\- \[License](#license)



\---



\## Overview



\*\*ContactIQ 2026\*\* is a fully-featured, offline-first desktop contact manager built entirely in Python using the `tkinter` GUI library. It goes far beyond a simple address book — it tracks relationship health, logs interactions, visualizes your network, and provides AI-powered suggestions and smart search, all within a modern dark-navy themed UI.



This project was built as an \*\*upgraded version of Task 5\*\* for the CodSoft Python Programming Internship.



\---



\## Features



\### 👤 Smart Contact Profiles

\- Store \*\*multiple phone numbers and email addresses\*\* per contact

\- Fields for company, role/title, address, birthday, anniversary

\- LinkedIn and Twitter social handles

\- Rich notes section

\- Tag system with color-coded labels (e.g., `family`, `work`, `recruiter`, `doctor`)

\- Group assignment: \*\*Work\*\*, \*\*Family\*\*, \*\*Network\*\*

\- Emergency contact flag with 🚨 indicator



\### 🔍 AI-Powered Natural Language Search

\- Search by name, company, role, address, tags, notes, or phone/email

\- Special queries:

&#x20; - `"birthday"` → shows contacts with upcoming birthdays (next 30 days)

&#x20; - `"emergency"` → filters only emergency contacts

&#x20; - `"follow up"` → surfaces contacts with low health scores

&#x20; - Multi-word queries match across all contact fields



\### 🔁 Duplicate Detection

\- Automatically checks for conflicts on \*\*phone number\*\*, \*\*email\*\*, and \*\*name\*\* when adding or editing

\- Prompts the user before saving duplicates, with a clear warning dialog



\### ❤️ Relationship Health Score

\- Each contact has a \*\*score from 0–100\*\*

\- Score is color-coded: 🟢 Strong (80+), 🟡 Fair (55–79), 🔴 Weak (<55)

\- Score \*\*increases by 5 points\*\* every time you log an interaction (capped at 100)

\- Displayed as a mini progress bar in the detail panel



\### 📅 Interaction Timeline

\- Log interactions of types: \*\*Call\*\*, \*\*Email\*\*, \*\*WhatsApp Message\*\*, \*\*Meeting\*\*

\- Each entry stores: type, date, and optional note

\- Chronologically displayed with color-coded icons in the Timeline tab



\### 🎂 Birthday \& Follow-up Reminders

\- Auto-popup on launch if any contact has a birthday \*\*within the next 3 days\*\*

\- Dedicated \*\*Reminders panel\*\* showing:

&#x20; - All birthdays in the next 30 days

&#x20; - Contacts not touched in 30+ days with health score below 80



\### 🏷️ Smart Groups \& Tag Filtering

\- Filter contacts by group tabs: \*\*All / Work / Family / Network / ⭐ Emergency\*\*

\- Inline tag management — add tags to any contact from the detail view

\- Tags are color-themed by category



\### 📊 Contact Analytics Dashboard

\- Per-contact analytics tab showing:

&#x20; - Total interactions logged

&#x20; - Breakdown bar chart (calls vs emails vs messages vs meetings)

&#x20; - Health score display

&#x20; - Birthday countdown timer



\### 🕸️ Network Graph Visualization

\- Canvas-drawn network graph for each contact

\- Shows up to 5 related contacts connected by \*\*shared tags\*\*

\- Click on satellite nodes to navigate to that contact

\- Central node highlighted in indigo



\### 📤 Import \& Export

| Format | Import | Export |

|--------|--------|--------|

| CSV    | ✅     | ✅     |

| vCard (.vcf) | ✅ | ✅ |

| JSON   | ❌     | ✅     |



\### 🎨 Modern Dark UI

\- Dark navy color palette (`#0F1629` base)

\- Colored avatar initials auto-generated from name

\- Hover effects on all interactive elements

\- Color-coded buttons (indigo = primary, emerald = positive, rose = danger, amber = warning)

\- Scrollable sidebar list with active selection indicator bar



\---



\## UI Structure



```

┌─────────────────────────────────────────────────────────────────┐

│  🔵 ContactIQ 2026   \[🔍 AI Search Bar]   \[Import]\[Export]\[🔔]\[+ Add]  │

├──────────────────┬──────────────────────────────────────────────┤

│  All │Work│Family│  Contact Header (Avatar, Name, Role, Tags)   │

│  Network│Emergency  ├──────────────────────────────────────────┤

│ ─────────────── │  \[📋 Info] \[📅 Timeline] \[🕸 Network] \[📊 Analytics] │

│  Contact List   │                                              │

│  (scrollable)   │       Active Tab Content                     │

│                 │                                              │

│  \[name + role]  │                                              │

│  \[health pill]  │                                              │

└──────────────── ┴──────────────────────────────────────────────┘

```



\---



\## Tech Stack



| Component        | Technology             |

|------------------|------------------------|

| Language         | Python 3.8+            |

| GUI Framework    | `tkinter` + `ttk`      |

| Data Storage     | JSON (local flat file) |

| Canvas Drawing   | `tkinter.Canvas`       |

| Color Utilities  | `colorsys` (stdlib)    |

| Date Handling    | `datetime` (stdlib)    |

| CSV Import/Export| `csv` (stdlib)         |

| Email Launch     | `webbrowser` (stdlib)  |

| No external dependencies required |         |



\---



\## Project Structure



```

contact\_book/

│

├── contact\_book.py        # Basic contact book (original Task 5)

├── contacts.json          # Data file for basic version

│

├── contacts\_pro.json      # Data file for ContactIQ (auto-created on first run)

└── contacts\_pro.py        # ← ContactIQ 2026 main application (this file)

```



> `contacts\_pro.json` is created automatically when you run the app and save your first contact. You do not need to create it manually.



\---



\## Installation \& Setup



\### Prerequisites



\- \*\*Python 3.8 or higher\*\*

\- `tkinter` (comes pre-installed with Python on Windows and most Linux distros)



\### Check if tkinter is available



```bash

python -m tkinter

```



If a small window appears, you're good to go.



\### On Linux (if tkinter is missing)



```bash

sudo apt-get install python3-tk

```



\### Clone the Repository



```bash

git clone https://github.com/shekhawatnigam-design/CODSOFT.git

cd CODSOFT/contact\_book

```



\---



\## How to Run



```bash

python contacts\_pro.py

```



The application window will launch maximized automatically.



\---



\## Usage Guide



\### ➕ Adding a Contact

1\. Click the \*\*"＋ Add Contact"\*\* button in the top-right

2\. Fill in the form (Name and at least one Phone are required)

3\. Optionally assign tags, group, social links, and mark as emergency

4\. Click \*\*"✓ Save Contact"\*\*



\### 🔍 Searching Contacts

\- Type in the search bar at the top

\- Supports partial matches across name, tags, company, role, notes, phone, and email

\- Try `"birthday"`, `"emergency"`, or `"follow up"` for smart filters



\### ✏️ Editing a Contact

\- Click a contact in the sidebar to open their detail panel

\- Click the \*\*"✏ Edit"\*\* button in the header



\### 🗑️ Deleting a Contact

\- Open the contact's detail panel

\- Click \*\*"🗑 Delete"\*\* and confirm the dialog



\### 📅 Logging an Interaction

\- Open a contact → go to the \*\*Timeline\*\* tab

\- Click \*\*"＋ Log Interaction"\*\*

\- Choose type (Call / Email / Message / Meeting), date, and an optional note

\- Health score auto-increments by 5 on each log



\### 🏷️ Adding a Tag

\- Open a contact → \*\*Info\*\* tab → scroll to Tags section

\- Click \*\*"Add Tag"\*\* and type the tag name



\### 🔔 Viewing Reminders

\- Click the \*\*"🔔 Reminders"\*\* button in the top bar

\- See upcoming birthdays and follow-up suggestions



\---



\## Data Storage



All contacts are stored locally in `contacts\_pro.json` in the same directory as the script. No internet connection or external database is required.



\### Sample Contact JSON Structure



```json

{

&#x20; "Rahul Sharma": {

&#x20;   "phones": \["+91-9876543210"],

&#x20;   "emails": \["rahul@example.com"],

&#x20;   "company": "Infosys",

&#x20;   "role": "Software Engineer",

&#x20;   "address": "Noida, UP",

&#x20;   "birthday": "1999-03-15",

&#x20;   "anniversary": "",

&#x20;   "tags": \["work", "python", "college"],

&#x20;   "group": "Work",

&#x20;   "score": 75,

&#x20;   "notes": "Met at PyCon India 2024.",

&#x20;   "social": {

&#x20;     "linkedin": "linkedin.com/in/rahulsharma",

&#x20;     "twitter": "@rahul\_dev"

&#x20;   },

&#x20;   "emergency": false,

&#x20;   "interactions": \[

&#x20;     {

&#x20;       "type": "call",

&#x20;       "label": "Called",

&#x20;       "when": "2026-05-20",

&#x20;       "note": "Discussed project ideas"

&#x20;     }

&#x20;   ],

&#x20;   "created": "2026-01-10"

&#x20; }

}

```



\---



\## Import \& Export



\### CSV Import

Your CSV file should have the following column headers (case-insensitive):



```

name, phone, email, company, role, address, birthday, tags, group, notes

```



\### vCard Import

Standard `.vcf` files (vCard v3.0) are supported. Fields parsed: `FN`, `TEL`, `EMAIL`, `ORG`, `TITLE`, `BDAY`, `NOTE`.



\### Export Options

\- \*\*CSV\*\* — spreadsheet-friendly, opens in Excel/Google Sheets

\- \*\*vCard (.vcf)\*\* — import into phone or other contact apps

\- \*\*JSON\*\* — full data backup including interactions and scores



\---



\## AI Features



| Feature | How It Works |

|---------|-------------|

| Natural Language Search | Scans a text blob of all contact fields; detects keywords like "birthday", "emergency", "follow up" |

| Relationship Health Score | Starts at 50, increases with logged interactions, decreases with inactivity |

| AI Insight Card | Generates a contextual suggestion per contact based on score, inactivity days, and tags |

| Birthday Reminders | Calculates days until next birthday and triggers banners + popups |

| Duplicate Detection | Compares phone, email, and name on every save |



> Note: The AI features are rule-based and heuristic, not LLM-powered. They use Python logic to simulate intelligent suggestions.



\---



\## Keyboard \& UX Highlights



\- \*\*Mouse scroll\*\* works in the contact list and all scrollable dialogs

\- \*\*Hover effects\*\* on all buttons and contact rows

\- \*\*Active contact\*\* highlighted with an indigo left border

\- \*\*Birthday contacts\*\* show 🎂 icon in the list

\- \*\*Emergency contacts\*\* show 🚨 icon in the list

\- \*\*Auto-maximize\*\* on launch (Windows `zoomed`, Linux `-zoomed`)



\---



\## Future Improvements



\- \[ ] Cloud sync (Google Contacts / iCloud API integration)

\- \[ ] Dark/light theme toggle

\- \[ ] Real LLM-powered AI insights via Anthropic or OpenAI API

\- \[ ] Contact photo upload support

\- \[ ] WhatsApp / Telegram quick-launch buttons

\- \[ ] Android APK export via Kivy port

\- \[ ] Search history and pinned contacts

\- \[ ] Bulk import from phone backup files



\---



\## Author



\*\*Nigam Kumar\*\*  

CodSoft Python Programming Intern  

📧 shekhawatnigam@gmail.com  



\---



\## License



This project was created as part of the \*\*CodSoft Internship Program\*\*.  

Free to use for educational and personal purposes.



\---



> ⭐ If you found this project helpful, consider starring the repository!

