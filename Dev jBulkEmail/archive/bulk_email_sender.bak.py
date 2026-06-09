"""
Gmail Bulk Email Sender - Desktop Application
------------------------------------------------------------------
PROJECT ARCHITECTURE:
- Main GUI: bulk_email_sender.py (Orchestrator)
- Auth Specialist: google_Authenticate.py (Verification Logic)
- Data Storage: login.txt, templates/, config.json
- Reporting: send_logs.txt, smtp_debug.log
------------------------------------------------------------------
"""

import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, font, simpledialog, colorchooser
import smtplib
import csv
import json
import os
import threading
import time
import itertools
import subprocess
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders
from datetime import datetime
from pathlib import Path
import ctypes
from ctypes import wintypes
import re
import base64
import io
import webbrowser
import sys

# --- PORTABILITY LAYER: Add core to path ---
BASE_DIR = Path(__file__).parent
CORE_DIR = BASE_DIR / "core"
sys.path.append(str(CORE_DIR))

# Now import our modules
from email_check import EmailChecker
from RichContentManager import RichContentManager, RichTextEditor, LinkPreviewFetcher, RichToolTip, ToolTip

# Import HTML rendering capability
try:
    from tkinterweb import HtmlFrame
    HTML_SUPPORT = True
except ImportError:
    HTML_SUPPORT = False
    print("Warning: tkinterweb not installed. Rich text rendering disabled.")

try:
    from bs4 import BeautifulSoup   # Gap 70: Move to top-level for perf/consistency
except ImportError:
    print("Warning: beautifulsoup4 not installed. HTML parsing disabled.")


# Popular SMTP Provider Settings
SMTP_PROVIDERS = {
    "Gmail":   {"host": "smtp.gmail.com",      "port": 587, "url": "https://myaccount.google.com/apppasswords"},
    "Outlook": {"host": "smtp.office365.com",  "port": 587, "url": "https://account.microsoft.com/security"},
    "Yahoo":   {"host": "smtp.mail.yahoo.com", "port": 587, "url": "https://login.yahoo.com/account/security"},
    "Zoho":    {"host": "smtp.zoho.com",        "port": 465, "url": "https://accounts.zoho.com/u/h#setting/clientapps"},
    "iCloud":  {"host": "smtp.mail.me.com",    "port": 587, "url": "https://appleid.apple.com/account/manage"},
}

# Gap 34: explicit domain → provider map so Outlook/iCloud etc. resolve correctly
_DOMAIN_TO_PROVIDER = {
    'gmail.com': 'Gmail',     'googlemail.com': 'Gmail',
    'outlook.com': 'Outlook', 'hotmail.com': 'Outlook',
    'live.com': 'Outlook',    'msn.com': 'Outlook',
    'yahoo.com': 'Yahoo',     'ymail.com': 'Yahoo',
    'zoho.com': 'Zoho',
    'icloud.com': 'iCloud',   'me.com': 'iCloud', 'mac.com': 'iCloud',
}


class RoundedButton(tk.Canvas):
    """Custom button with rounded corners"""
    def __init__(self, parent, text="", command=None, bg="#00E5FF", fg="#000000", 
                 hover_bg="#00B8D4", active_bg="#00838F", width=100, height=30, 
                 corner_radius=15, font=('Segoe UI', 8, 'bold'), **kwargs):
        try:
            parent_bg = parent.cget('bg')
        except:
            parent_bg = '#0B132B' # Fallback to theme background
            
        super().__init__(parent, width=width, height=height, bg=parent_bg, 
                        highlightthickness=0, **kwargs)
        
        self.command = command
        self.bg = bg
        self.fg = fg
        self.hover_bg = hover_bg
        self.active_bg = active_bg
        self.corner_radius = corner_radius
        self.text = text
        self.font = font
        self.is_hovered = False
        self.is_pressed = False
        
        # Draw button
        self.draw_button()
        
        # Bind events
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)
        
    # Draw rounded rectangle
    def _draw_rounded_rect(self, canvas, w, h, r, color):
        canvas.create_arc(0, 0, 2*r, 2*r, start=90, extent=90, fill=color, outline=color)
        canvas.create_arc(w-2*r, 0, w, 2*r, start=0, extent=90, fill=color, outline=color)
        canvas.create_arc(0, h-2*r, 2*r, h, start=180, extent=90, fill=color, outline=color)
        canvas.create_arc(w-2*r, h-2*r, w, h, start=270, extent=90, fill=color, outline=color)
        canvas.create_rectangle(r, 0, w-r, h, fill=color, outline=color)
        canvas.create_rectangle(0, r, w, h-r, fill=color, outline=color)

    def draw_button(self):
        self.delete("all")
        color = self.active_bg if self.is_pressed else (self.hover_bg if self.is_hovered else self.bg)
        w, h = self.winfo_reqwidth(), self.winfo_reqheight()
        self._draw_rounded_rect(self, w, h, self.corner_radius, color)
        self.create_text(w/2, h/2, text=self.text, fill=self.fg, font=self.font)
        
    def on_enter(self, event):
        self.is_hovered = True
        self.draw_button()
        self.config(cursor="hand2")
        
    def on_leave(self, event):
        self.is_hovered = False
        self.is_pressed = False
        self.draw_button()
        
    def on_press(self, event):
        self.is_pressed = True
        self.draw_button()
        
    def on_release(self, event):
        self.is_pressed = False
        self.draw_button()
        if self.command and self.is_hovered:
            self.command()

class BulkEmailSender:
    def __init__(self, root):
        self.root = root
        
        # --- WATERFALL LAYER 1: Core Tactical Directories ---
        self.base_dir = Path(__file__).parent
        self.dirs = {
            'assets':  self.base_dir / "assets",
            'config':  self.base_dir / "config",
            'logs':    self.base_dir / "logs",
            'exports': self.base_dir / "exports",
            'core':    self.base_dir / "core"
        }
        for d in self.dirs.values(): d.mkdir(exist_ok=True)

        self._init_paths()
        self._init_variables()
        
        # Gap: Dynamic Instance Discovery
        self._discover_checkpoints()
        
        # --- WATERFALL LAYER 3: Data Load & Theme Sync ---
        self.load_themes()
        self.load_config()
        self.load_accounts()

        # --- WATERFALL LAYER 4: UI Hierarchy Initialization ---
        self.root.title("jBulkEmailSender - Tactical Operations")
        self.root.geometry("1100x800")
        self.root.resizable(True, True)
        self.root.configure(bg='#0B132B')
        self.setup_ui()
        
        # --- WATERFALL LAYER 5: Cold Boot Reconstruction ---
        # Restore state if this was a tactical refresh
        self.load_reload_state()
        
        # Phase 12.9: Automated Mission Briefing
        if getattr(self, 'show_help_on_start', True):
            self.root.after(1500, self._show_help_mission)

    def _init_paths(self):
        """Encapsulated path mapping for portability."""
        self.config_file   = self.dirs['config']  / "config.json"
        self.master_log_file = self.dirs['logs']    / "send_logs.txt"
        self.log_file      = self.master_log_file
        self.login_file    = self.dirs['config']  / "login.txt"
        self.progress_file = self.dirs['config']  / "send_progress.json"
        self._checkpoints_dir = self.dirs['config'] / "checkpoints"
        self._checkpoints_dir.mkdir(exist_ok=True)
        self.templates_dir = self.dirs['exports'] / "templates"
        self._failed_dir   = self.dirs['exports'] / "failed"
        self.templates_dir.mkdir(exist_ok=True)
        self._failed_dir.mkdir(exist_ok=True)

    def _init_variables(self):
        """Initialize all operation-critical variables."""
        self.recipients = []
        self.accounts = {}
        self.is_sending = False
        self.send_thread = None
        self.current_smtp_host = "smtp.gmail.com"
        self.current_smtp_port = 587
        self.attachments = []
        self._snap = {}
        self._account_cycle = iter([])
        self.themes = {}
        self.current_theme_name = "Neural Void (Future)"
        self._last_failed_csv = None
        self._recipients_bak = None
        self._launch_cmd_bak = None
        self.config = {}
        self._active_checkpoints = []
        self._pending_resume_idx = 0
        self.show_help_on_start = True
        
    def _setup_styles(self):
        """Hierarchy level 2: Define mission aesthetics and 3D palette."""
        style = ttk.Style()
        style.theme_use('clam')
        
        self.colors = {
            'bg': '#808080',       # 50% Grey Mission Control
            'panel': '#4D4D4D',    # Darker Grey for Cards
            'aqua': '#00E5FF',     # Electric Aqua
            'glow': '#00B8D4',     # Deep Aqua
            'text': '#FFD700',     # Gold Command
            'white': '#FFFFFF',
            'border': '#94D2BD'
        }
        
        self.root.configure(bg=self.colors['bg'])
        style.configure('TFrame', background=self.colors['bg'])
        style.configure('TLabel', background=self.colors['bg'], foreground=self.colors['white'], font=('Segoe UI', 9))
        style.configure('TLabelFrame', background=self.colors['panel'], foreground=self.colors['aqua'], 
                        font=('Segoe UI', 9, 'bold'), borderwidth=4, relief='groove')
        style.configure('TLabelFrame.Label', background=self.colors['panel'], foreground=self.colors['aqua'])
        style.configure('TButton', font=('Segoe UI', 8, 'bold'), borderwidth=2, relief='raised', padding=(8, 4), cursor='hand2')
        style.configure('Accent.TButton', background=self.colors['aqua'], foreground='#000000', borderwidth=2, relief='raised')
        style.map('Accent.TButton', background=[('active', self.colors['glow']), ('pressed', '#00838F')], relief=[('pressed', 'sunken'), ('active', 'raised')])
        style.configure('Gold.TButton', background=self.colors['text'], foreground='#000000', padding=(8, 4), borderwidth=2, relief='raised')
        style.map('Gold.TButton', background=[('active', '#FFC107'), ('pressed', '#FF9800')], relief=[('pressed', 'sunken'), ('active', 'raised')])
        style.configure('TEntry', fieldbackground='#D3D3D3', foreground='#000000', insertcolor='#000000', borderwidth=2, relief='solid')
        style.configure('TSpinbox', fieldbackground='#D3D3D3', foreground='#000000', borderwidth=2, relief='solid')
        style.configure('TCombobox', fieldbackground='#D3D3D3', foreground='#000000', borderwidth=2, relief='solid')

    def _setup_main_containers(self):
        """Hierarchy level 2: Define the Fixed-width Tactical Sidebar (Reduced by 50%)."""
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Phase 13.5: Strictly Fixed Sidebar (180px FIX)
        self.main_frame.columnconfigure(0, weight=0, minsize=180) # Fixed Sidebar
        self.main_frame.columnconfigure(1, weight=1) # Fluid Main View
        self.main_frame.rowconfigure(1, weight=1)
    def setup_ui(self):
        """Hierarchy level 1: Orchestrate the mission-control dashboard."""
        self._setup_styles()
        self._setup_main_containers()
        self._setup_hud()
        self._setup_sidebar()
        self._setup_composition_area()
        self._setup_rich_editor()
        
        # Check if a previous interrupted session exists
        self._check_resume_available()
        # Apply initial mission theme
        self.root.after(100, lambda: self.apply_theme(self.current_theme_name))

    def _setup_hud(self):
        """Hierarchy level 3: Create the top Mission Status bar."""
        hud_frame = tk.Frame(self.main_frame, bg=self.colors['panel'], height=60, name="hud_frame")
        hud_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        hud_frame.grid_propagate(False)
        
        try:
            from tkinter import font as tkfont
            title_font = ('Orbitron', 20, 'bold') if 'Orbitron' in tkfont.families() else ('Segoe UI', 18, 'bold')
        except:
            title_font = ('Segoe UI', 18, 'bold')

        # Phase 13.6: Tactical Logo Integration
        logo_p = self.dirs['assets'] / "mission_icon.png"
        if logo_p.exists():
            try:
                from PIL import Image, ImageTk
                img = Image.open(logo_p).resize((40, 40), Image.Resampling.LANCZOS)
                self.hud_logo = ImageTk.PhotoImage(img) # Save reference
                tk.Label(hud_frame, image=self.hud_logo, bg=self.colors['panel']).pack(side="left", padx=(20, 5))
            except: pass
            
        tk.Label(hud_frame, text="🚀 jBulkEmailSender", bg=self.colors['panel'], fg=self.colors['text'], 
                 name="hud_title", font=title_font).pack(side="left", padx=5)
        
        self.hud_status_var = tk.StringVar(value="IDLE")
        tk.Label(hud_frame, textvariable=self.hud_status_var, bg=self.colors['panel'], fg=self.colors['aqua'], 
                 name="hud_status", font=('Segoe UI', 12, 'bold')).pack(side="left", expand=True)

        version_label = tk.Label(hud_frame, text="MISSION CONTROL • v6.1-MISSION", bg=self.colors['panel'], 
                                 fg=self.colors['aqua'], name="hud_version", font=('Segoe UI', 8, 'bold'))
        version_label.pack(side="right", padx=20)
        
        # Tooltip with Mission Objectives (RichToolTip from RichContentManager)
        purpose_lines = [
            ("TACTICAL EVALUATION: v6.0-PORTABLE", self.colors['aqua'], ("Segoe UI", 10, "bold")),
            ("-" * 55, "#444444", ("Segoe UI", 8)),
            ("PORTABILITY: Zero-Python executable build ready.", "#FFFFFF", ("Segoe UI", 9)),
            ("AESTHETICS: Watermark branding + Floating shadow enabled.", "#FFFFFF", ("Segoe UI", 9)),
            ("SAFETY: Waterfall uninitialized state protection.", self.colors['text'], ("Segoe UI", 9, "bold")),
            ("IO: Close-one-step-back file management.", self.colors['text'], ("Segoe UI", 9, "bold")),
            ("RECOVERY: Multi-checkpoint mission state logic.", self.colors['glow'], ("Segoe UI", 9, "bold"))
        ]
        RichToolTip(version_label, purpose_lines)

    def _setup_sidebar(self):
        """Hierarchy level 3: Create the left command and monitor sidebar (STRICTLY 180px)."""
        left_panel = ttk.Frame(self.main_frame)
        left_panel.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.E, tk.W), padx=(0, 5))
        left_panel.grid_propagate(False)
        left_panel.config(width=180)
        left_panel.columnconfigure(0, weight=1)
        
        # 1. Security (Multiple Accounts)
        sec_frame = ttk.LabelFrame(left_panel, text="🔑 Security", padding="5")
        sec_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        sec_frame.columnconfigure(1, weight=1)
        
        ttk.Label(sec_frame, text="ID:").grid(row=0, column=0, sticky="w")
        self.account_email_var = tk.StringVar()
        self.account_email_combo = ttk.Combobox(sec_frame, textvariable=self.account_email_var)
        self.account_email_combo.grid(row=0, column=1, pady=2, sticky="ew")
        self.account_email_combo.bind("<<ComboboxSelected>>", self.on_account_selected)
        
        ttk.Label(sec_frame, text="PW:").grid(row=1, column=0, sticky="w")
        self.password_var = tk.StringVar()
        pw_f = ttk.Frame(sec_frame)
        pw_f.grid(row=1, column=1, pady=2, sticky="ew")
        pw_f.columnconfigure(0, weight=1)
        self.password_entry = ttk.Entry(pw_f, textvariable=self.password_var, show="*")
        self.password_entry.grid(row=0, column=0, sticky="ew")
        self.pw_toggle_btn = ttk.Button(pw_f, text="👁", width=3, command=lambda: self.toggle_password(self.password_entry, self.pw_toggle_btn))
        self.pw_toggle_btn.grid(row=0, column=1, padx=(2,0))
        
        btn_f = ttk.Frame(sec_frame)
        btn_f.grid(row=2, column=0, columnspan=2, pady=5, sticky="ew")
        btn_f.columnconfigure((0,1), weight=1)
        ttk.Button(btn_f, text="🟢 SAVE", command=self.save_account, style='Accent.TButton').grid(row=0, column=0, padx=1, sticky="ew")
        ttk.Button(btn_f, text="🧪 TEST", command=self.test_login, style='Accent.TButton').grid(row=0, column=1, padx=1, sticky="ew")

        # 2. Templates & Options
        opt_frame = ttk.LabelFrame(left_panel, text="⚙️ Config", padding="5")
        opt_frame.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        opt_frame.columnconfigure(1, weight=1)
        opt_frame.columnconfigure(2, weight=1)
        
        ttk.Label(opt_frame, text="Delay(s):").grid(row=0, column=0, sticky="w")
        self.delay_var = tk.DoubleVar(value=self.config.get('delay', 1.0))
        ttk.Spinbox(opt_frame, from_=0, to=60, increment=0.5, textvariable=self.delay_var, width=5).grid(row=0, column=1, sticky="ew")
        
        ttk.Label(opt_frame, text="Batch:").grid(row=1, column=0, sticky="w")
        self.batch_size_var = tk.IntVar(value=self.config.get('batch_size', 50))
        ttk.Spinbox(opt_frame, from_=1, to=500, textvariable=self.batch_size_var, width=5).grid(row=1, column=1, sticky="ew")
        
        self.personalize_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(opt_frame, text="Personalize", variable=self.personalize_var).grid(row=2, column=0, sticky="w")
        self.html_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(opt_frame, text="HTML Mode", variable=self.html_var).grid(row=2, column=1, sticky="w")
        
        # Gap: Code Refresh Button (Dynamic Sync)
        self.refresh_btn = ttk.Button(opt_frame, text="🔄 REFRESH", command=self.restart_application, style='Accent.TButton', width=10)
        self.refresh_btn.grid(row=2, column=2, padx=(5, 0), sticky="ew")
        ToolTip(self.refresh_btn, "Reload application to apply code changes immediately.")
        
        ttk.Label(opt_frame, text="ℹ️ Batch Safety Activated", font=('Segoe UI', 7, 'italic'), foreground='#00B8D4').grid(row=3, column=0, columnspan=3, sticky="w")

        # 3. Actions & Status
        mon_frame = ttk.LabelFrame(left_panel, text="📊 Monitor", padding="5")
        mon_frame.grid(row=2, column=0, sticky="ew", pady=(0, 5))
        mon_frame.columnconfigure((0,1), weight=1)
        
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(mon_frame, textvariable=self.status_var, font=('Segoe UI', 8, 'bold')).grid(row=0, column=0, columnspan=2, sticky="w")
        self.progress_bar = ttk.Progressbar(mon_frame, mode='determinate')
        self.progress_bar.grid(row=1, column=0, columnspan=2, sticky="ew", pady=2)
        
        # Grid of controls
        bt = [("📂 T-LOAD", self.load_template, 2, 0), ("💾 T-SAVE", self.save_template, 2, 1),
              ("🛑 HALT", self.stop_sending, 3, 0), ("▶️ RESUME", self.resume_sending, 3, 1),
              ("📤 RETRY", self.retry_failed, 4, 0), ("🔍 PREVIEW", self.preview_email, 4, 1),
              ("📋 LOGS", self.view_logs, 5, 0), ("📁 FAILED", self.view_failed_folder, 5, 1),
              ("❓ HELP", self._show_help_mission, 6, 0)]
        for text, cmd, r, c in bt:
            btn = ttk.Button(mon_frame, text=text, command=cmd, style='Accent.TButton' if "RETRY" not in text else 'Gold.TButton')
            btn.grid(row=r, column=c, pady=1, padx=1, sticky="ew")
            if "HALT" in text: self.stop_btn = btn
            if "RESUME" in text: self.resume_btn = btn
            if "RETRY" in text: self.retry_btn = btn

        # 4. Activity Log
        l_frame = ttk.LabelFrame(left_panel, text="📜 Activity Log", padding="5")
        l_frame.grid(row=3, column=0, sticky="nsew")
        l_frame.columnconfigure(0, weight=1); l_frame.rowconfigure(0, weight=1); left_panel.rowconfigure(3, weight=1)
        self.log_text = scrolledtext.ScrolledText(l_frame, wrap=tk.WORD, font=('Consolas', 8), width=20, height=8, bg='#D3D3D3', bd=0)
        self.log_text.grid(row=0, column=0, sticky="nsew")
        ttk.Button(l_frame, text="🗑️ PURGE", command=lambda: self.log_text.delete('1.0', tk.END), style='Accent.TButton').grid(row=1, column=0, pady=5, sticky="ew")

    def _setup_composition_area(self):
        """Hierarchy level 3: Create the main email composition and launch deck."""
        right_panel = ttk.Frame(self.main_frame, padding="3")
        right_panel.grid(row=1, column=1, sticky="nsew")
        right_panel.columnconfigure(0, weight=10); right_panel.rowconfigure(2, weight=1)
        
        # 1. Transmission Control Strip
        tx_f = ttk.LabelFrame(right_panel, text="📡 Transmission Control", padding="3")
        tx_f.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 3))
        tx_f.columnconfigure((1,3,6), weight=1)
        
        ttk.Label(tx_f, text="From:").grid(row=0, column=0, padx=2)
        self.from_email_combo = ttk.Combobox(tx_f)
        self.from_email_combo.grid(row=0, column=1, sticky="ew")
        self.update_account_combobox()
        
        ttk.Label(tx_f, text="To:").grid(row=0, column=2, padx=2)
        self.recipient_file_var = tk.StringVar(value="No file")
        ttk.Label(tx_f, textvariable=self.recipient_file_var, font=('Segoe UI', 8, 'italic')).grid(row=0, column=3, sticky="ew")
        ttk.Button(tx_f, text="📎 LOAD", command=self.load_recipients, style='Accent.TButton').grid(row=0, column=4, padx=2)
        
        self.cc_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(tx_f, text="CC", variable=self.cc_var, command=self.on_cc_toggle).grid(row=0, column=5, padx=5)
        self.cc_info_var = tk.StringVar(value="[Disabled]")
        self.cc_info_label = ttk.Label(tx_f, textvariable=self.cc_info_var, font=('Segoe UI', 8, 'italic'))
        self.cc_info_label.grid(row=0, column=6, sticky="ew")
        ttk.Button(tx_f, text="📑 LIST", command=self.show_participant_list, style='Accent.TButton').grid(row=0, column=7, padx=2)
        
        self.attach_status_var = tk.StringVar(value="📎 0 files")

        # 2. Subject & Launch Row
        sub_f = ttk.LabelFrame(right_panel, text="📌 Subject", padding="3")
        sub_f.grid(row=1, column=0, sticky="ew", pady=(0, 3))
        sub_f.columnconfigure(0, weight=1)
        self.subject_var = tk.StringVar()
        ttk.Entry(sub_f, textvariable=self.subject_var, font=('Segoe UI', 11)).pack(fill="x", expand=True)
        
        l_cont = tk.Frame(right_panel, bg='#FF0000', width=118, bd=0)
        l_cont.grid(row=1, column=1, sticky="nsew", padx=(3, 0), pady=(0, 3))
        l_cont.grid_propagate(False)
        l_inner = tk.Frame(l_cont, bg=self.colors['bg'], bd=0)
        l_inner.pack(fill="both", expand=True, padx=4, pady=4)
        
        self.send_btn = RoundedButton(l_inner, text="🚀 LAUNCH", command=self.start_sending, bg=self.colors['text'], 
                                      fg='#000000', width=110, height=50, corner_radius=12)
        self.send_btn.pack(fill="both", expand=True)

    def _setup_rich_editor(self):
        """Hierarchy level 3: Initialize the high-performance Rich Text engine."""
        # Identification of right panel for parent reference
        right_panel = [c for c in self.main_frame.winfo_children() if isinstance(c, ttk.Frame) and not str(c).endswith('frame')][-1]
        
        body_frame = ttk.LabelFrame(right_panel, text="✉️ Email Body (HTML Enabled)", padding="3")
        body_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(0, 3))
        body_frame.columnconfigure(0, weight=1); body_frame.rowconfigure(1, weight=1)
        
        self.body_text = scrolledtext.ScrolledText(body_frame, wrap=tk.WORD, font=('Segoe UI', 11), bg='#FFFFFF', 
                                                 fg='#000000', insertbackground='#000000', padx=10, pady=10, bd=2, relief='solid')
        self.body_text.grid(row=1, column=0, sticky="nsew")
        
        self.body_html_content = ""
        self.rich_editor = RichTextEditor(self.root, self.body_text, lambda: self.html_var.set(True), 
                                        lambda msg: self.log_message(msg), attach_callback=self.attach_files, 
                                        attach_mgr_callback=self.show_attachment_manager, 
                                        attach_status_var=self.attach_status_var, theme_callback=self.apply_theme)
        
        self.rich_editor.create_toolbar(body_frame).grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 5))
        self.html_var.set(True)
        
    def get_body_content(self):
        """Get email body content (returns HTML if available, otherwise plain text)"""
        # If HTML mode is active, generate HTML from the current view
        if self.html_var.get():
            html = self.rich_editor.generate_html()
            return html
            
        # Return stored HTML if available (fallback)
        if self.body_html_content:
            return self.body_html_content
        
        # Otherwise return plain text from widget (stripped of global whitespace)
        if self.body_text:
            content = self.body_text.get('1.0', tk.END).strip()
            return content
        return ""


    
    def set_body_content(self, content):
        """Set email body content (stores HTML and displays formatted version)"""
        try:
            # Store the HTML content
            self.body_html_content = content
            
            # Convert HTML to formatted text with tags (Gap 70: BeautifulSoup now top-level)
            soup = BeautifulSoup(content, 'html.parser')
            
            # Clear the text widget
            if self.body_text:
                self.body_text.delete('1.0', tk.END)
                
                # Configure additional color tags
                self.body_text.tag_config("h1", font=('Segoe UI', 16, 'bold'), foreground='#000000')
                self.body_text.tag_config("h2", font=('Segoe UI', 14, 'bold'), foreground='#333333')
                self.body_text.tag_config("h3", font=('Segoe UI', 12, 'bold'), foreground='#555555')
                self.body_text.tag_config("code", font=('Consolas', 10), background='#F0F0F0')
                self.body_text.tag_config("indent1", lmargin1=20, lmargin2=20)
                self.body_text.tag_config("indent2", lmargin1=40, lmargin2=40)
                self.body_text.tag_config("bullet", lmargin1=20, lmargin2=40)
                
                # Process HTML and insert with formatting
                self._insert_html_formatted(soup.body if soup.body else soup, indent_level=0)
                
        except Exception as e:
            print(f"Error setting body content: {e}")
            import traceback
            traceback.print_exc()
            # Fallback: just insert as plain text
            if self.body_text:
                self.body_text.delete('1.0', tk.END)
                self.body_text.insert('1.0', content)
    
    def _insert_html_formatted(self, element, indent_level=0):
        """Recursively insert HTML elements with formatting while avoiding extra spaces"""
        if not element:
            return
            
        for child in element.children:
            if isinstance(child, str):
                # Text content - avoid adding extra spaces if it's just a newline or whitespace
                text = child.replace('\r', '')
                if not text.strip() and '\n' not in text:
                    continue
                
                # Apply indentation only for real text
                if indent_level > 0 and text.strip():
                    text = "    " * indent_level + text.lstrip()
                
                start_pos = self.body_text.index(tk.END)
                self.body_text.insert(tk.END, text)
                end_pos = self.body_text.index(tk.END)
                
                # Re-apply colorization for symbols
                for symbol, tag_name, color in [('✅', 'green_check', '#00AA00'), ('❌', 'red_x', '#FF0000')]:
                    if symbol in text:
                        self.body_text.tag_config(tag_name, foreground=color)
                        idx = start_pos
                        while True:
                            idx = self.body_text.search(symbol, idx, end_pos)
                            if not idx: break
                            self.body_text.tag_add(tag_name, idx, f"{idx}+1c")
                            idx = f"{idx}+1c"
            else:
                tag_name = child.name.lower() if hasattr(child, 'name') else ''
                
                if tag_name == 'br':
                    self.body_text.insert(tk.END, '\n')
                elif tag_name == 'p':
                    # Only add one newline before/after to avoid double-gap
                    self._insert_html_formatted(child, indent_level)
                    if not self.body_text.get("end-2c", "end-1c") == '\n':
                        self.body_text.insert(tk.END, '\n')
                elif tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    start_pos = self.body_text.index(tk.END)
                    self._insert_html_formatted(child, indent_level)
                    end_pos = self.body_text.index(tk.END)
                    self.body_text.tag_add(tag_name, start_pos, end_pos)
                    self.body_text.insert(tk.END, '\n')
                elif tag_name in ['b', 'strong']:
                    start_pos = self.body_text.index(tk.END)
                    self._insert_html_formatted(child, indent_level)
                    self.body_text.tag_add('bold', start_pos, self.body_text.index(tk.END))
                elif tag_name in ['i', 'em']:
                    start_pos = self.body_text.index(tk.END)
                    self._insert_html_formatted(child, indent_level)
                    self.body_text.tag_add('italic', start_pos, self.body_text.index(tk.END))
                elif tag_name == 'a':
                    start_pos = self.body_text.index(tk.END)
                    self._insert_html_formatted(child, indent_level)
                    end_pos = self.body_text.index(tk.END)
                    self.body_text.tag_add('link', start_pos, end_pos)
                    
                elif tag_name == 'span':
                    # Check for color style
                    style = child.get('style', '')
                    color = None
                    
                    # Try to extract color from style attribute
                    color_match = re.search(r'color:\s*([^;]+)', style, re.IGNORECASE)
                    if color_match:
                        color = color_match.group(1).strip()
                    
                    # Also check for direct color attribute
                    if not color and child.get('color'):
                        color = child.get('color')
                    
                    start_pos = self.body_text.index(tk.END)
                    self._insert_html_formatted(child, indent_level)
                    end_pos = self.body_text.index(tk.END)
                    
                    if color:
                        # Normalize color value
                        color = color.replace(' ', '')
                        # Create dynamic color tag
                        tag_name = f"color_{color.replace('#', '').replace('(', '').replace(')', '').replace(',', '_')}"
                        try:
                            self.body_text.tag_config(tag_name, foreground=color)
                            self.body_text.tag_add(tag_name, start_pos, end_pos)
                        except:
                            pass  # Invalid color, skip
                
                elif tag_name == 'font':
                    # Handle <font> tag with color attribute
                    color = child.get('color', '')
                    
                    start_pos = self.body_text.index(tk.END)
                    self._insert_html_formatted(child, indent_level)
                    end_pos = self.body_text.index(tk.END)
                    
                    if color:
                        tag_name = f"color_{color.replace('#', '')}"
                        try:
                            self.body_text.tag_config(tag_name, foreground=color)
                            self.body_text.tag_add(tag_name, start_pos, end_pos)
                        except:
                            pass
                        
                elif tag_name == 'ul':
                    self.body_text.insert(tk.END, '\n')
                    for li in child.find_all('li', recursive=False):
                        self.body_text.insert(tk.END, "    " * indent_level + "• ")
                        self._insert_html_formatted(li, indent_level + 1)
                        self.body_text.insert(tk.END, '\n')
                    self.body_text.insert(tk.END, '\n')
                    
                elif tag_name == 'ol':
                    self.body_text.insert(tk.END, '\n')
                    for idx, li in enumerate(child.find_all('li', recursive=False), 1):
                        self.body_text.insert(tk.END, "    " * indent_level + f"{idx}. ")
                        self._insert_html_formatted(li, indent_level + 1)
                        self.body_text.insert(tk.END, '\n')
                    self.body_text.insert(tk.END, '\n')
                    
                elif tag_name == 'code' or tag_name == 'pre':
                    start_pos = self.body_text.index(tk.END)
                    self._insert_html_formatted(child, indent_level)
                    end_pos = self.body_text.index(tk.END)
                    self.body_text.tag_add('code', start_pos, end_pos)
                    
                elif tag_name == 'div':
                    self._insert_html_formatted(child, indent_level)
                    self.body_text.insert(tk.END, '\n')
                    
                else:
                    # Default: just process children
                    self._insert_html_formatted(child, indent_level)
    
    def _load_html_safe(self, html_content):
        """Deprecated - no longer using HtmlFrame"""
        pass
    
    def smart_paste(self):
        """Paste rich HTML content from clipboard"""
        try:
            html_content = RichContentManager.get_html_from_clipboard()
            if html_content:
                self.set_body_content(html_content)
                self.log_message("✅ Pasted rich content with formatting!")
                messagebox.showinfo("Success", "Rich content pasted successfully!\n\nFormatting, colors, and images have been preserved.")
            else:
                self.log_message("⚠️ No rich content in clipboard")
                messagebox.showinfo("Paste Info", 
                    "No formatted content found in clipboard.\n\n" +
                    "To paste rich text:\n" +
                    "1. Copy from Word, Google Docs, or a web page\n" +
                    "2. Click 'Paste Rich Text' button\n\n" +
                    "Or simply type/paste directly in the email body!")
        except Exception as e:
            self.log_message(f"❌ Paste error: {str(e)}")
            messagebox.showerror("Paste Error", 
                f"Could not paste content:\n\n{str(e)}\n\n" +
                "Try pasting directly into the email body with Ctrl+V")
    
    def open_rich_editor(self):
        """Open rich content editor (deprecated - using inline HTML editor now)"""
        messagebox.showinfo("Rich Editor", 
            "The email body now supports rich text directly!\n\n" +
            "Just paste formatted content from:\n" +
            "• Microsoft Word\n" +
            "• Google Docs\n" +
            "• Outlook\n" +
            "• Any web page\n\n" +
            "All formatting, colors, images, and links will be preserved!")
        
    def load_themes(self):
        """Load themes from themes.json"""
        themes_file = self.dirs['assets'] / "themes.json"
        if themes_file.exists():
            try:
                with open(themes_file, 'r') as f:
                    self.themes = json.load(f)
            except Exception as e:
                print(f"Error loading themes: {e}")
                self.themes = {}

    @staticmethod
    def _calibrate_box_bg(hex_color, factor=1.4):
        """Optimized color calibration protocol (40% adjustment)."""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3: hex_color = ''.join([c*2 for c in hex_color])
        rgb = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
        return "#%02x%02x%02x" % tuple(min(255, int(c * factor)) for c in rgb)

    def _recursive_ui_sync(self, w, theme):
        """Deep hierarchy theme synchronization protocol."""
        try:
            if isinstance(w, tk.Toplevel): w.configure(bg=theme['bg'])
            if isinstance(w, tk.Frame) and not isinstance(w, ttk.Frame):
                w.configure(bg=theme['panel'] if 'hud' in str(w).lower() else theme['bg'])
            elif isinstance(w, tk.Label) and not isinstance(w, ttk.Label):
                w.configure(bg=theme['panel'] if 'hud' in str(w).lower() else theme['bg'], 
                            fg=theme['text_highlight'] if 'hud' in str(w).lower() else theme['text_main'])
            elif isinstance(w, tk.Canvas) and not isinstance(w, RoundedButton):
                w.configure(bg=theme['entry_bg'])
            elif isinstance(w, (tk.Text, scrolledtext.ScrolledText)):
                is_log = 'log' in str(w).lower()
                w.configure(bg=theme['entry_bg'] if is_log else theme['scrolled_text_bg'], 
                            fg=theme['entry_fg'] if is_log else theme['scrolled_text_fg'])
            elif isinstance(w, RoundedButton):
                w.bg, w.fg = theme['btn_bg'], theme['btn_fg']
                w.hover_bg, w.active_bg = theme['btn_hover'], theme['btn_active']
                try: 
                    p_bg = w.master.cget('bg')
                    w.configure(bg=p_bg)
                except: 
                    w.configure(bg=theme['bg'])
                w.draw_button()
        except: pass
        for child in w.winfo_children():
            self._recursive_ui_sync(child, theme)

    def apply_theme(self, theme_name):
        """Apply the selected theme to the entire UI"""
        if theme_name not in self.themes:
            return
            
        self.current_theme_name = theme_name
        theme = self.themes[theme_name]
        
        style = ttk.Style()

        box_bg = self._calibrate_box_bg(theme['bg'], 1.4)
        
        # Configure Colors
        style.configure('TFrame', background=theme['bg'])
        style.configure('TLabel', background=theme['bg'], foreground=theme['text_main'])
        
        # Ultra Bold Headers (Double Size) & Button-Colored Borders
        header_font = ('Segoe UI', 16, 'bold') # Doubled from standard 8-9pt
        
        style.configure('TLabelFrame', background=box_bg, 
                        foreground=theme['text_highlight'], 
                        borderwidth=3, relief='solid',
                        font=header_font)
        style.configure('TLabelFrame.Label', background=box_bg, 
                        foreground=theme['text_highlight'],
                        font=header_font)

        # Force border color using highlightthickness/background tricks if standard bordercolor fails
        # for ttk widgets in certain themes, we ensure the border stands out
        style.configure('TLabelFrame', bordercolor=theme['btn_bg'], lightcolor=theme['btn_bg'], darkcolor=theme['btn_bg'])
        
        style.configure('TButton', background=theme['btn_bg'], foreground=theme['btn_fg'], relief=theme['relief'])
        style.configure('Accent.TButton', background=theme['aqua'], foreground='#000000')
        style.map('Accent.TButton', 
                  background=[('active', theme['glow']), ('pressed', theme['shadow'])])
        
        style.configure('Gold.TButton', background=theme['text_highlight'], foreground='#000000')
        
        # Entry/Inputs
        style.configure('TEntry', fieldbackground=theme['entry_bg'], foreground=theme['entry_fg'])
        style.configure('TSpinbox', fieldbackground=theme['entry_bg'], foreground=theme['entry_fg'])
        style.configure('TCombobox', fieldbackground=theme['entry_bg'], foreground=theme['entry_fg'])

        # Treeview (Participant List)
        style.configure("Treeview", 
                        background=theme['scrolled_text_bg'], 
                        foreground=theme['scrolled_text_fg'], 
                        fieldbackground=theme['scrolled_text_bg'],
                        font=('Segoe UI', 9))
        style.configure("Treeview.Heading", 
                        background=theme['panel'], 
                        foreground=theme['text_highlight'], 
                        font=('Segoe UI', 9, 'bold'))
        style.map("Treeview", background=[('selected', theme['aqua'])], foreground=[('selected', '#000000')])
        
        # Update ToolTip and RichToolTip Globals in RichContentManager
        from RichContentManager import ToolTip, RichToolTip
        ToolTip.theme_bg = theme['panel']
        ToolTip.theme_fg = theme['aqua']
        RichToolTip.theme_bg = theme['bg']
        RichToolTip.theme_fg = theme['text_main']
        
        # Main root and HUD
        self.root.configure(bg=theme['bg'])
        
        self._recursive_ui_sync(self.root, theme)
        
        # Also scan self.root explicitly for any other windows if needed
        # (Though winfo_children should find them if they use self.root as master)
        
        # Save current theme back to config
        self.config['current_theme'] = theme_name
        self.save_config()

    def save_reload_state(self):
        """Capture all ephemeral UI state for a hot-reload."""
        try:
            state = {
                'subject': self.subject_var.get(),
                'body': self.get_body_content(),
                'sender': self.from_email_combo.get(),
                'recipient_file': self.recipient_file_var.get(),
                'recipients': self.recipients,
                'delay': self.delay_var.get(),
                'batch_size': self.batch_size_var.get(),
                'personalize': self.personalize_var.get(),
                'html_mode': self.html_var.get(),
                'cc_mode': self.cc_var.get(),
                'attachments': self.attachments
            }
            state_file = self.dirs['config'] / "reload_state.json"
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)
            self.log_message("💾 Tactical State Snapshotted for Refresh.")
        except Exception as e:
            print(f"Reload state save failed: {e}")

    def load_reload_state(self):
        """Restore UI state from a previous session if available."""
        state_file = self.dirs['config'] / "reload_state.json"
        if not state_file.exists():
            return
            
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            # Restore variables
            if 'subject' in state: self.subject_var.set(state['subject'])
            if 'sender' in state: self.from_email_combo.set(state['sender'])
            if 'recipient_file' in state: self.recipient_file_var.set(state['recipient_file'])
            if 'recipients' in state: 
                self.recipients = state['recipients']
                self.log_message(f"📂 Restored {len(self.recipients)} recipients from session.")
            
            if 'delay' in state: self.delay_var.set(state['delay'])
            if 'batch_size' in state: self.batch_size_var.set(state['batch_size'])
            if 'personalize' in state: self.personalize_var.set(state['personalize'])
            if 'html_mode' in state: self.html_var.set(state['html_mode'])
            if 'cc_mode' in state: self.cc_var.set(state['cc_mode'])
            if 'attachments' in state: 
                self.attachments = state['attachments']
                self.update_attachment_list() # Call relevant UI updates
            
            # Restore body content
            if 'body' in state:
                if state.get('html_mode'):
                    self.set_body_content(state['body'])
                else:
                    self.body_text.delete('1.0', tk.END)
                    self.body_text.insert('1.0', state['body'])
            
            # Update UI elements that depend on these vars
            self._update_all_ui_bindings()
            self.log_message("⚡ Tactical State Restored from Refresh.")
            
            # Clean up after successful load
            state_file.unlink()
        except Exception as e:
            self.log_message(f"⚠️ Reload state restoration failed: {e}")

    def _update_all_ui_bindings(self):
        """Force UI updates for variables that don't auto-update correctly."""
        try:
            self.update_account_combobox()
            self.on_cc_toggle()
            # Any other manual UI synch needed
        except: pass

    def load_config(self):
        """Load saved configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
                self.current_theme_name = self.config.get('current_theme', self.current_theme_name)
                self.show_help_on_start = self.config.get('show_help_on_start', self.show_help_on_start)
        else:
            self.config = {}
    
    def save_config(self):
        """Save general settings without overwriting critical mission state."""
        self.config.update({
            'delay':      self.delay_var.get(),
            'batch_size': self.batch_size_var.get(),
            'current_theme': getattr(self, 'current_theme_name', 'Neural Void (Future)'),
            'show_help_on_start': getattr(self, 'show_help_on_start', True)
        })
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
            
    def load_accounts(self):
        """Load accounts from login.txt"""
        self.accounts = {}
        if self.login_file.exists():
            with open(self.login_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if ':' in line:
                        parts = line.strip().split(':', 1)
                        if len(parts) == 2:
                            self.accounts[parts[0]] = parts[1]
        
    def open_app_pass_link(self):
        """Open the Google App Passwords page"""
        import webbrowser
        webbrowser.open("https://myaccount.google.com/apppasswords")
        self.log_message("🌐 Opened Google App Passwords page in browser")

    def test_login(self):
        """Open a new window to select provider and test connection"""
        email = self.account_email_var.get().strip()
        password = self.password_var.get().strip()
        
        if not email or not password:
            messagebox.showwarning("Incomplete", "Please enter both Email and Password first.")
            return

        test_win = tk.Toplevel(self.root)
        test_win.title("SMTP Provider Setup & Test")
        
        # Set size
        win_width = 480
        win_height = 700
        
        # Get screen dimensions
        screen_width = test_win.winfo_screenwidth()
        screen_height = test_win.winfo_screenheight()
        
        # Position: Start from 20% from left (after sidebar), center vertically
        x_position = int(screen_width * 0.20)  # 20% from left (sidebar area)
        y_position = (screen_height - win_height) // 2  # Vertically centered
        
        test_win.geometry(f"{win_width}x{win_height}+{x_position}+{y_position}")
        test_win.resizable(False, False)
        test_win.grab_set() # Modal

        main_v = ttk.Frame(test_win, padding="20")
        main_v.pack(fill="both", expand=True)

        # Show current account being tested
        account_info_frame = ttk.Frame(main_v)
        account_info_frame.pack(fill="x", pady=(0, 15))
        ttk.Label(account_info_frame, text="Authenticating Account:", font=('Segoe UI', 9)).pack()
        ttk.Label(account_info_frame, text=email, font=('Segoe UI', 11, 'bold'), foreground="#3498db").pack()

        ttk.Label(main_v, text="Step 1: Select your Email Provider", font=('Segoe UI', 10, 'bold')).pack(pady=(0, 10))

        # Provider Grid
        grid_f = ttk.Frame(main_v)
        grid_f.pack(fill="x", pady=5)
        
        selected_provider = tk.StringVar(value="Gmail")
        params_info = tk.StringVar(value="Host: smtp.gmail.com | Port: 587")
        
        def pick_provider(name):
            selected_provider.set(name)
            config = SMTP_PROVIDERS[name]
            self.current_smtp_host = config['host']
            self.current_smtp_port = config['port']
            params_info.set(f"Host: {config['host']} | Port: {config['port']}")
            self.log_message(f"📍 Selected {name} SMTP profile")

        # Create provider buttons
        for i, (name, cfg) in enumerate(SMTP_PROVIDERS.items()):
            row, col = divmod(i, 2)
            ttk.Button(grid_f, text=name, command=lambda n=name: pick_provider(n)).grid(row=row, column=col, sticky="ew", padx=2, pady=2)
        grid_f.columnconfigure(0, weight=1); grid_f.columnconfigure(1, weight=1)

        ttk.Separator(main_v, orient='horizontal').pack(fill='x', pady=15)

        # Step 2: Settings & Gen Key
        ttk.Label(main_v, text="Step 2: Configuration & Key", font=('Segoe UI', 10, 'bold')).pack(pady=(0, 5))
        ttk.Label(main_v, textvariable=params_info, font=('Consolas', 9)).pack()

        def open_gen_link():
            import webbrowser
            provider = selected_provider.get()
            
            # AccountChooser is far more effective at overriding the browser's default user
            if provider == "Gmail" and "@" in email:
                url = f"https://accounts.google.com/AccountChooser?Email={email}&continue=https://myaccount.google.com/apppasswords"
            elif provider == "Outlook" and "@" in email:
                url = f"https://account.live.com/proofs/Manage?login_hint={email}"
            else:
                url = SMTP_PROVIDERS[provider]['url']
                
            webbrowser.open(url)
            self.log_message(f"🌐 Opened {provider} login for {email} (Account Override)")

        ttk.Button(main_v, text="🚀 Get App Password / Key", command=open_gen_link).pack(pady=10, fill="x")

        ttk.Separator(main_v, orient='horizontal').pack(fill='x', pady=10)

        # Step 3: Save & Authenticate
        ttk.Label(main_v, text="Step 3: Save & Verify", font=('Segoe UI', 10, 'bold')).pack(pady=(0, 10))
        
        # Live Key Input
        key_input_frame = ttk.Frame(main_v)
        key_input_frame.pack(fill="x", pady=5)
        ttk.Label(key_input_frame, text="Paste New Key:", font=('Segoe UI', 9)).pack(side="left")
        
        popup_pass_var = tk.StringVar(value=password)
        pw_popup_frame = ttk.Frame(key_input_frame)
        pw_popup_frame.pack(side="left", fill="x", expand=True, padx=5)
        pw_popup_frame.columnconfigure(0, weight=1)
        
        popup_pass_entry = ttk.Entry(pw_popup_frame, textvariable=popup_pass_var, show="*")
        popup_pass_entry.grid(row=0, column=0, sticky="ew")
        
        toggle_popup_btn = ttk.Button(pw_popup_frame, text="👁", width=3)
        toggle_popup_btn.grid(row=0, column=1, padx=(2,0))
        toggle_popup_btn.config(command=lambda: self.toggle_password(popup_pass_entry, toggle_popup_btn))

        def save_from_popup():
            new_pw = popup_pass_var.get().strip()
            if not new_pw:
                messagebox.showwarning("Empty", "Please paste the key first.")
                return
            self.password_var.set(new_pw)
            self.save_account() # Uses self.account_email_var and self.password_var
            self.log_message(f"💾 Saved updated key for {email} via popup")
            messagebox.showinfo("Saved", "App Password saved to your profile!")

        ttk.Button(main_v, text="💾 Save Key to Profile", command=save_from_popup).pack(fill="x", pady=5)

        ttk.Separator(main_v, orient='horizontal').pack(fill='x', pady=10)

        test_status = tk.StringVar(value="Status: Not Tested")
        ttk.Label(main_v, textvariable=test_status, font=('Segoe UI', 9, 'italic')).pack()

        def run_actual_test():
            test_status.set("⏳ Running Technical Check...")
            provider = selected_provider.get()
            current_pw = popup_pass_var.get().strip()
            
            def thread_test():
                import subprocess
                import json
                import sys 
                try:
                    # Get absolute, normalized path with forward slashes
                    script_path = (self.dirs['core'] / "google_Authenticate.py").resolve()
                    script_path_str = script_path.as_posix()
                    
                    # Verify file exists
                    if not script_path.exists():
                        error_msg = f"System file missing: {script_path.name}\nExpected at: {script_path_str}"
                        test_status.set("❌ FILE MISSING")
                        self.log_message(f"❌ {error_msg}")
                        messagebox.showerror("Error", error_msg)
                        return

                    python_exe = sys.executable
                    # Use double quotes for arguments to handle shell special characters
                    cmd = [python_exe, script_path_str, f"{provider}", f"{email}", f"{current_pw}"]
                    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    stdout, stderr = process.communicate()
                    
                    if stdout:
                        result = json.loads(stdout)
                        if result.get("success"):
                            test_status.set("✅ SUCCESS!")
                            self.log_message(f"✅ SMTP Authenticated: {email} ({provider})")
                            messagebox.showinfo("Success", result.get("message"))
                        else:
                            test_status.set("❌ FAILED")
                            self.log_message(f"❌ SMTP Error: {result.get('message')}")
                            messagebox.showerror("Authentication Failed", result.get("message"))
                    else:
                        test_status.set("❌ ERROR")
                        self.log_message(f"❌ System Error: {stderr}")
                        messagebox.showerror("System Error", f"Check script failed: {stderr}")
                except Exception as e:
                    test_status.set("❌ ERROR")
                    self.log_message(f"❌ Technical Exception: {str(e)}")
                    messagebox.showerror("Technical Error", str(e))
            
            threading.Thread(target=thread_test, daemon=True).start()

        def open_debug_log_file():
            log_p = self.dirs['logs'] / "smtp_debug.log"
            if log_p.exists():
                os.startfile(log_p)
            else:
                messagebox.showinfo("No Log", "Debug log is currently empty.")

        # Main Action Buttons
        ttk.Separator(main_v, orient='horizontal').pack(fill='x', pady=5)
        
        self.auth_test_btn = ttk.Button(main_v, text="🧪 Authenticate & Test SMTP", 
                                       command=run_actual_test, padding="10")
        self.auth_test_btn.pack(pady=10, fill="x")
        
        footer_btn_frame = ttk.Frame(main_v)
        footer_btn_frame.pack(fill="x", pady=(10, 0))
        ttk.Button(footer_btn_frame, text="📋 View Technical Log", command=open_debug_log_file, width=20).pack(side="left", padx=5)
        ttk.Button(footer_btn_frame, text="Close", command=test_win.destroy, width=15).pack(side="right", padx=5)

    def on_account_selected(self, event=None):
        """Auto-fill password when an account is selected from the dropdown"""
        selected_email = self.account_email_var.get()
        if selected_email in self.accounts:
            self.password_var.set(self.accounts[selected_email])
            self.log_message(f"📑 Loaded saved credentials for {selected_email}")

    def save_account(self):
        """Add and save a new account to login.txt"""
        email = self.account_email_var.get().strip()
        password = self.password_var.get().strip()
        
        if not email or not password:
            messagebox.showwarning("Warning", "Please enter both Email and Password!")
            return
            
        self.accounts[email] = password
        
        with open(self.login_file, 'w', encoding='utf-8') as f:
            for em, pw in self.accounts.items():
                f.write(f"{em}:{pw}\n")
        
        self.update_account_combobox()
        messagebox.showinfo("Success", f"Account {email} saved successfully!")
        self.account_email_var.set("")
        self.password_var.set("")

    def update_account_combobox(self):
        """Update both account dropdowns (Security and Sender)"""
        emails = list(self.accounts.keys())
        # Update Security dropdown
        self.account_email_combo['values'] = emails
        # Update Sender dropdown
        self.from_email_combo['values'] = emails
        
        if emails:
            # Update Sender selection if empty
            if not self.from_email_combo.get():
                self.from_email_combo.set(emails[0])
            # Update Security selection if empty
            if not self.account_email_combo.get():
                self.account_email_combo.set(emails[0])
                self.on_account_selected()
        else:
            self.from_email_combo.set("")
            self.account_email_combo.set("")

    def show_app_password_help(self):
        """Show help for Gmail App Password"""
        help_text = """Gmail App Password Setup:

1. Go to Google Account settings
2. Enable 2-Step Verification
3. Go to Security > App passwords
4. Generate a new app password for 'Mail'
5. Copy and paste it here

Note: Use App Password, NOT your regular Gmail password!

Link: https://myaccount.google.com/apppasswords"""
        messagebox.showinfo("App Password Help", help_text)
    
    def load_recipients(self):
        """Load recipients from CSV or TXT file with validation"""
        filename = filedialog.askopenfilename(
            title="Select Recipients File",
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        self.current_filename = filename
        
        try:
            self.recipients = []
            
            if filename.lower().endswith('.csv'):
                # ---------------------------------------------------------
                # NEW LOGIC FOR CSV VALIDATION AND CORRECTION
                # ---------------------------------------------------------
                corrections, valid_rows, error = EmailChecker.process_csv_file(filename, include_cc=self.cc_var.get())
                
                if error:
                    messagebox.showerror("Error", f"Failed to process CSV: {error}")
                    return
                
                # Show corrections popup if any
                if corrections:
                    self.show_corrections_popup(corrections)
                
                # Load valid rows for sending
                self.recipients = valid_rows
                
            else:
                # Text file - one email per line (fallback)
                with open(filename, 'r', encoding='utf-8') as f:
                    for i, line in enumerate(f):
                        email = line.strip()
                        if email and '@' in email:
                            self.recipients.append({
                                'email': email, 
                                'name': email.split('@')[0],
                                'row_idx': -1 # Not applicable/supported for TXT
                            })
            
            count = len(self.recipients)
            self.recipient_file_var.set(f"{count} recipients loaded from {Path(filename).name}")
            self.log_message(f"✅ Loaded {count} recipients")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load recipients: {str(e)}")

    def show_corrections_popup(self, corrections):
        """Display correct emails popup"""
        popup = tk.Toplevel(self.root)
        popup.title("Email Corrections Report")
        popup.geometry("700x500")
        
        ttk.Label(popup, text=f"⚠️ Corrected {len(corrections)} email addresses!", 
                 font=('Segoe UI', 12, 'bold'), foreground="#FF6600").pack(pady=10)
        
        ttk.Label(popup, text="Original emails moved to Column D. Validated emails updated in Column A.",
                 font=('Segoe UI', 9)).pack(pady=(0, 10))
        
        # Create Treeview
        frame = ttk.Frame(popup)
        frame.pack(fill='both', expand=True, padx=10)
        
        tree = ttk.Treeview(frame, columns=('row', 'old', 'new'), show='headings', height=15)
        tree.heading('row', text='Row')
        tree.heading('old', text='Original (Invalid)')
        tree.heading('new', text='Corrected (Valid)')
        
        tree.column('row', width=50, anchor='center')
        tree.column('old', width=300)
        tree.column('new', width=300)
        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Insert data (limit to first 100 if too many?)
        # Requirement says "batch of 20", treeview scrolls natively so batching isn't strictly needed for display unless massive.
        # I'll show all because user requested "show corrected emails".
        for item in corrections:
            tree.insert('', tk.END, values=(item['row'], item['old'], item['new']))
            
        ttk.Button(popup, text="OK", command=popup.destroy).pack(pady=10)
    
    def save_template(self):
        """Save current email as template and open directory"""
        template_name = tk.simpledialog.askstring("Save Template", "Enter template name:")
        if not template_name:
            return
        
        # Determine the content to save: Use get_body_content to get HTML if needed
        # We strip the body content to ensure no extra trailing spaces/newlines
        content = self.get_body_content().strip()
        
        template = {
            'subject': self.subject_var.get().strip(),
            'body': content,
            'html': self.html_var.get()
        }
        
        template_file = self.templates_dir / f"{template_name}.json"
        try:
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2)
            
            self.log_message(f"💾 Template '{template_name}' saved to: {template_file}")
            
            # Open the path location in explorer as requested by user
            if self.templates_dir.exists():
                os.startfile(self.templates_dir) if sys.platform == 'win32' else webbrowser.open(self.templates_dir.as_uri())
            
            messagebox.showinfo("Success", f"Template '{template_name}' saved!")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save template: {e}")
    
    def load_template(self):
        """Open the template location and prompt for file selection"""
        # 1. Open the path location in explorer as requested
        if self.templates_dir.exists():
            os.startfile(self.templates_dir) if sys.platform == 'win32' else webbrowser.open(self.templates_dir.as_uri())
            self.log_message(f"📂 Opened template directory: {self.templates_dir}")

        # 2. Use a proper file dialog to load the template
        filename = filedialog.askopenfilename(
            initialdir=self.templates_dir,
            title="Select Template to Load",
            filetypes=[("JSON Templates", "*.json"), ("All Files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                template = json.load(f)
            
            self.subject_var.set(template.get('subject', ''))
            
            # Use set_body_content if it's HTML, otherwise just insert
            body = template.get('body', '')
            if template.get('html'):
                self.html_var.set(True)
                self.set_body_content(body)
            else:
                self.html_var.set(False)
                self.body_text.delete('1.0', tk.END)
                self.body_text.insert('1.0', body)
            
            self.log_message(f"✅ Loaded template from {Path(filename).name}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load template: {e}")
    

    def show_participant_list(self):
        """Display participants in a scrollable list with pagination of 10"""
        if not self.recipients:
            messagebox.showwarning("No Data", "No participants loaded yet!")
            return

        list_win = tk.Toplevel(self.root)
        list_win.title("Participant List")
        
        # Set size
        win_width = 500
        win_height = 600
        
        # Get screen dimensions
        screen_width = list_win.winfo_screenwidth()
        screen_height = list_win.winfo_screenheight()
        
        # Calculate position for top-right corner (with 10px margin)
        x_position = screen_width - win_width - 10
        y_position = 10
        
        list_win.geometry(f"{win_width}x{win_height}+{x_position}+{y_position}")
        list_win.resizable(False, False)

        # Apply current theme background
        theme = self.themes.get(self.current_theme_name, {})
        list_win.configure(bg=theme.get('bg', '#808080'))

        container = ttk.Frame(list_win, padding="15")
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="📜 Loaded Participants", font=('Segoe UI', 12, 'bold')).pack(pady=(0, 10))

        # Main List Area with Scrollbar
        list_frame = ttk.Frame(container)
        list_frame.pack(fill="both", expand=True)

        # Create Treeview for clean grid look
        is_cc_enabled = self.cc_var.get()
        if is_cc_enabled:
            columns = ('index', 'email', 'cc', 'name')
            tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
            
            tree.heading('index', text='#')
            tree.heading('email', text='To Recipients')
            tree.heading('cc', text='CC Recipients')
            tree.heading('name', text='Name')
            
            tree.column('index', width=40, anchor='center')
            tree.column('email', width=180)
            tree.column('cc', width=180)
            tree.column('name', width=100)
        else:
            columns = ('index', 'email', 'name')
            tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
            
            tree.heading('index', text='#')
            tree.heading('email', text='Email Address')
            tree.heading('name', text='Name')
            
            tree.column('index', width=40, anchor='center')
            tree.column('email', width=250)
            tree.column('name', width=210)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Pagination Logic
        self.current_page = 0
        batch_size = 20
        total_pages = (len(self.recipients) + batch_size - 1) // batch_size

        page_label = ttk.Label(container, text=f"Page 1 of {total_pages}", font=('Segoe UI', 9))

        def update_list():
            # Clear current view
            for item in tree.get_children():
                tree.delete(item)
            
            # Load batch
            start = self.current_page * batch_size
            end = min(start + batch_size, len(self.recipients))
            
            for idx in range(start, end):
                r = self.recipients[idx]
                if is_cc_enabled:
                    tree.insert('', tk.END, values=(idx + 1, r['email'], r.get('cc_emails', ''), r['name']))
                else:
                    tree.insert('', tk.END, values=(idx + 1, r['email'], r['name']))
            
            page_label.config(text=f"Batch {self.current_page + 1} of {total_pages} (Items {start+1}-{end} of {len(self.recipients)})")

        nav_frame = ttk.Frame(container)
        nav_frame.pack(fill="x", pady=10)

        def prev_page():
            if self.current_page > 0:
                self.current_page -= 1
                update_list()

        def next_page():
            if (self.current_page + 1) * batch_size < len(self.recipients):
                self.current_page += 1
                update_list()

        # Ensure nav buttons are prominent
        ttk.Button(nav_frame, text="⬅️ Prev 20", command=prev_page, style='Accent.TButton').pack(side="left", expand=True, padx=5)
        page_label.pack(side="left", expand=True)
        ttk.Button(nav_frame, text="Next 20 ➡️", command=next_page, style='Accent.TButton').pack(side="left", expand=True, padx=5)

        update_list()
        ttk.Button(container, text="Close", command=list_win.destroy).pack(pady=(5, 0))

    def preview_email(self):
        
        # Use first recipient for preview
        recipient = self.recipients[0]
        subject = self.subject_var.get()
        body = self.body_text.get('1.0', tk.END)
        
        if self.personalize_var.get():
            name = recipient.get('name', 'Customer')
            email_addr = recipient.get('email', '')
            
            # Case-insensitive replacement using regex
            subject = re.sub(r'\{name\}', name, subject, flags=re.IGNORECASE)
            subject = re.sub(r'\{email\}', email_addr, subject, flags=re.IGNORECASE)
            body = re.sub(r'\{name\}', name, body, flags=re.IGNORECASE)
            body = re.sub(r'\{email\}', email_addr, body, flags=re.IGNORECASE)
        
        preview_text = f"""To: {recipient['email']}
Cc: {recipient.get('cc_emails', 'N/A') if self.cc_var.get() else 'DISABLED'}
From: {self.account_email_var.get()}
Subject: {subject}

---
Preview shows first recipient. Personalization: {'ON' if self.personalize_var.get() else 'OFF'}
Total recipients: {len(self.recipients)}
"""
        
        # Create preview window
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Email Preview - Tactical Assessment")
        preview_window.geometry("800x600")  # Larger for rich view
        
        # Gap 69/74/77: Rich HTML Preview using tkinterweb (if supported)
        if HTML_SUPPORT:
            try:
                # Top metadata header
                theme = self.themes.get(self.current_theme_name, {})
                header_bg = theme.get('panel', '#2D2D2D')
                header_fg = theme.get('aqua', '#00E5FF')
                
                header = tk.Text(preview_window, height=6, bg=header_bg, fg=header_fg, font=('Consolas', 10), bd=0)
                header.pack(fill="x")
                header.insert('1.0', preview_text)
                header.config(state='disabled')
                
                # Scrollable HTML area
                html_preview = HtmlFrame(preview_window, messages_enabled=False)
                html_preview.pack(fill="both", expand=True)
                html_preview.load_html(body)
            except Exception as e:
                self.log_message(f"⚠️ Rich preview failed, falling back to text: {e}")
                HTML_SUPPORT_PREVIEW = False # Use local flag to avoid killing global support
            else:
                HTML_SUPPORT_PREVIEW = True
        else:
            HTML_SUPPORT_PREVIEW = False
        
        # Fallback to plain text if HTML failed or not supported
        if not HTML_SUPPORT_PREVIEW:
            text = scrolledtext.ScrolledText(preview_window, wrap=tk.WORD, font=('Consolas', 10))
            text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            text.insert('1.0', preview_text + "\n\nBODY:\n" + body)
            text.config(state='disabled')
    
    def start_sending(self):
        """Start sending emails — validates, snapshots UI state, then launches thread."""
        if self.is_sending: return
        
        # Check for pending resume
        start_idx = getattr(self, '_pending_resume_idx', 0)
        if start_idx > 0:
            if not messagebox.askyesno("Confirm Launch", 
                                       f"System is primed for RESUME.\n\n"
                                       f"Start sending from the recovery point (Email #{start_idx + 1})?\n"
                                       f"Click 'No' to start a fresh mission from the beginning (Row 1)."):
                start_idx = 0
        
        # Reset pending index after read
        self._pending_resume_idx = 0
        
        sender_email = self.from_email_combo.get().strip()
        if not sender_email:
            messagebox.showerror("Error", "Please select or enter a sender email!")
            return

        # Case-insensitive account lookup (Gap 25 fix)
        matched_email = next((k for k in self.accounts if k.lower() == sender_email.lower()), None)
        if not matched_email:
            messagebox.showerror("Error", f"Credentials for {sender_email} not found! Please save them first.")
            return

        if not self.recipients:
            messagebox.showerror("Error", "Please load recipients!")
            return

        if not self.subject_var.get().strip() or not self.body_text.get('1.0', tk.END).strip():
            messagebox.showwarning("Missing Content", "Subject and Email Body cannot be empty!")
            return

        # Gap 14/Choice Logic: Warn about overwriting if progress exists
        if self.progress_file.exists():
            if not messagebox.askyesno("New Mission", 
                                       "An interrupted mission is already pending.\n\n"
                                       "Starting a NEW mission will discard previous progress. Proceed?"):
                return

        if not messagebox.askyesno("Confirm", f"Send {len(self.recipients)} emails?\n\nThis action cannot be undone."):
            return

        self.log_text.delete('1.0', tk.END)
        self._build_account_cycle(matched_email)
        
        if start_idx == 0:
            # Assign a unique checkpoint file for this mission to avoid overlapping instances
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_subject = "".join([c for c in self.subject_var.get()[:15] if c.isalnum()])
            self.progress_file = self._checkpoints_dir / f"Mission_{ts}_{safe_subject}.json"
        
        self._start_sending_from(start_idx=start_idx)

    def _start_sending_from(self, start_idx=0):
        """Snapshot all UI vars on main thread, then spawn send thread."""
        # --- Pre-thread snapshot (Gaps 3, 13, 19, 21) ---
        self._snap = {
            'body':        self.get_body_content(),
            'subject':     self.subject_var.get(),
            'personalize': self.personalize_var.get(),
            'cc_enabled':  self.cc_var.get(),
            'delay':       self.delay_var.get(),
            'batch_size':  self.batch_size_var.get(),
            'sender':      self.from_email_combo.get().strip(),
            'batch_pause': max(60.0, self.delay_var.get() * 10),
        }
        self._disable_launch()
        self.stop_btn.config(state='normal')
        self.resume_btn.config(state='disabled')
        self.retry_btn.config(state='disabled')
        
        # Create a separate log file for this mission launch (Gap: Launch isolation)
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.log_file = self.dirs['logs'] / f"Launch_{ts}.txt"
        self.log_message(f"📁 Mission log created: {self.log_file.name}")
        
        self.is_sending = True
        self.send_thread = threading.Thread(
            target=self.send_emails_thread, args=(start_idx,), daemon=True)
        self.send_thread.start()

    def _disable_launch(self):
        """Dim the RoundedButton and clear its command (Gap 1, 30 fix)."""
        # Only backup if button currently has a live command (Gap 30)
        if self.send_btn.command is not None:
            self._launch_cmd_bak = self.send_btn.command
        self.send_btn.command = None
        self.send_btn.bg      = '#888888'
        self.send_btn.draw_button()

    def _enable_launch(self):
        """Restore the RoundedButton to active state (Gap 30: never restore None)."""
        if self._launch_cmd_bak is not None:
            self.send_btn.command = self._launch_cmd_bak
        self.send_btn.bg = '#FFD700'
        self.send_btn.draw_button()

    def stop_sending(self):
        """Stop sending emails"""
        self.is_sending = False
        self.log_message("⏹ Stopping email sending...")

    
    # ------------------------------------------------------------------ #
    #  SMTP HELPERS                                                        #
    # ------------------------------------------------------------------ #
    def _smtp_host_for(self, email):
        """Infer SMTP host/port from sender domain (Gap 5, 34: uses explicit map)."""
        domain = email.split('@')[1].lower() if '@' in email else ''
        provider = _DOMAIN_TO_PROVIDER.get(domain)
        if provider and provider in SMTP_PROVIDERS:
            cfg = SMTP_PROVIDERS[provider]
            return cfg['host'], cfg['port']
        return self.current_smtp_host, self.current_smtp_port  # fallback

    def _smtp_connect(self, email, password):
        """Single SMTP factory: SSL or STARTTLS based on port (Gap 5, reuse everywhere)."""
        host, port = self._smtp_host_for(email)
        self.log_message(f"📡 Connecting {email} → {host}:{port}")
        if port == 465:
            server = smtplib.SMTP_SSL(host, port, timeout=20)
        else:
            server = smtplib.SMTP(host, port, timeout=20)
            server.ehlo()
            server.starttls()
            server.ehlo()
        server.login(email, password)
        self.log_message(f"✅ Authenticated: {email}")
        return server

    def _build_account_cycle(self, primary_email):
        """Build itertools.cycle starting from primary sender (Gaps 2, D)."""
        keys = [k for k in self.accounts]
        # Put primary first
        primary = next((k for k in keys if k.lower() == primary_email.lower()), None)
        if primary:
            keys.remove(primary)
            keys.insert(0, primary)
        pairs = [(e, self.accounts[e]) for e in keys if self.accounts.get(e)]
        self._account_cycle = itertools.cycle(pairs) if pairs else itertools.cycle([(primary_email, '')])

    def _smtp_send_with_retry(self, server, msg, account_pair, max_retries=3):
        """Send with up to max_retries auto-reconnects on connection loss (Gap 11, 29)."""
        for attempt in range(max_retries):
            try:
                if server is None:
                    raise smtplib.SMTPServerDisconnected("No live server")
                server.send_message(msg)
                return server
            except (smtplib.SMTPServerDisconnected, smtplib.SMTPConnectionReset, OSError) as exc:
                self.log_message(f"🔄 Reconnecting (attempt {attempt + 1}/{max_retries})... [{exc}]")
                server = None   # mark dead so next iteration doesn't retry broken socket (Gap 29)
                try:
                    server = self._smtp_connect(*account_pair)
                except smtplib.SMTPAuthenticationError:
                    raise   # Gap 43: propagate up — outer except shows proper auth dialog
                except Exception as re_exc:
                    self.log_message(f"⚠️ Reconnect failed: {re_exc}")
        raise smtplib.SMTPException("Max retries exceeded — could not send")

    # ------------------------------------------------------------------ #
    #  PROGRESS / STATE PERSISTENCE                                        #
    # ------------------------------------------------------------------ #
    def _save_progress(self, idx, sent, failed_list):
        """Persist send state to JSON so resume works (Gaps 19, 20)."""
        data = {
            "recipient_file": getattr(self, 'current_filename', ''),
            "sender_email":   self._snap.get('sender', ''),
            "subject":        self._snap.get('subject', ''),
            "body":           self._snap.get('body', ''),
            "attachments":    list(self.attachments), # Snapshot current attachments (paths)
            "last_sent_idx":  idx,
            "sent_count":     sent,
            "failed":         failed_list,
            "timestamp":      datetime.now().isoformat()
        }
        try:
            with open(self.progress_file, 'w') as pf:
                json.dump(data, pf, indent=2)
        except Exception as e:
            self.log_message(f"⚠️ Could not save progress: {e}")

    # ------------------------------------------------------------------ #
    #  PERSISTENCE LAYER — L4 (post-send side-effects, isolated)          #
    # ------------------------------------------------------------------ #
    def _post_send_ops(self, recipient, idx, sent, log_fh, failed_list):
        """Isolated persistence layer — Gap 40: errors here NEVER affect sent/failed counts."""
        # CSV status update (own guard)
        try:
            if recipient.get('row_idx', -1) >= 0 and hasattr(self, 'current_filename'):
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                EmailChecker.update_status(
                    self.current_filename, recipient['row_idx'], f"Sent {ts}", 
                    use_cache=True, defer_write=True)
        except Exception as e:
            self.log_message(f"⚠️ CSV status update failed for {recipient['email']}: {e}")

        # Log file write (own guard)
        try:
            log_fh.write(f"[{datetime.now()}] SUCCESS - {recipient['email']}\n")
            log_fh.flush()
        except Exception as e:
            self.log_message(f"⚠️ Log write error: {e}")

        # Progress checkpoint every 10 successes (Gap 37)
        if sent % 10 == 0:
            self._save_progress(idx, sent, failed_list)
            # PERFORMANCE GAP: Flush CSV cache to disk periodically
            if hasattr(self, 'current_filename'):
                EmailChecker.flush_cache(self.current_filename)

    def _export_failed_csv(self, failed_list):
        """Write failed emails to a dated CSV and enable the Retry button (Gap 7)."""
        ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = self._failed_dir / f"failed_{ts}.csv"
        try:
            with open(path, 'w', newline='', encoding='utf-8') as cf:
                writer = csv.writer(cf)
                writer.writerow(['email', 'name', 'error'])
                for item in failed_list:
                    writer.writerow([item['email'], item['name'], item['error']])
            self._last_failed_csv = path
            self.log_message(f"📤 Failed list → {path.name}  ({len(failed_list)} addresses)")
            self.root.after(0, lambda: self.retry_btn.config(state='normal'))
        except Exception as e:
            self.log_message(f"⚠️ Could not export failed CSV: {e}")

    def _discover_checkpoints(self):
        """Find all available mission checkpoints for resume."""
        self._active_checkpoints = list(self._checkpoints_dir.glob("Mission_*.json"))
        # Also check the legacy/main progress file
        main_p = self.dirs['config'] / "send_progress.json"
        if main_p.exists():
            self._active_checkpoints.append(main_p)
            
    def _check_resume_available(self):
        """Enable/disable Resume button and offer multi-mission selection."""
        self._discover_checkpoints()
        if hasattr(self, 'resume_btn'):
            if self._active_checkpoints:
                self.resume_btn.config(state='normal')
                self.root.after(500, self._auto_resume_prompt)
            else:
                self.resume_btn.config(state='disabled')

    def _auto_resume_prompt(self):
        """Offer to resume missions if any are found."""
        if not self._active_checkpoints: return
        
        if len(self._active_checkpoints) == 1:
            if messagebox.askyesno("Tactical Operations: Resume", 
                                   "An interrupted mission was detected.\n\n"
                                   "Would you like to resume from the last checkpoint?"):
                self.resume_sending(self._active_checkpoints[0])
        else:
            if messagebox.askyesno("Tactical Operations: Resume", 
                                   f"Multiple ({len(self._active_checkpoints)}) interrupted missions detected!\n\n"
                                   "Would you like to view the list and select one to resume?"):
                self._show_mission_selector()

    def _show_mission_selector(self):
        """Popup window to select which mission to resume."""
        sel_win = tk.Toplevel(self.root)
        sel_win.title("Mission Recovery Center")
        sel_win.geometry("600x400")
        sel_win.grab_set()
        
        theme = self.themes.get(self.current_theme_name, {})
        sel_win.configure(bg=theme.get('bg', '#808080'))
        
        container = ttk.Frame(sel_win, padding="20")
        container.pack(fill="both", expand=True)
        
        ttk.Label(container, text="📂 Select Mission to Restore", font=('Segoe UI', 12, 'bold')).pack(pady=(0, 10))
        
        tree = ttk.Treeview(container, columns=('date', 'subject', 'recipients'), show='headings', height=10)
        tree.heading('date', text='Date/Time')
        tree.heading('subject', text='Subject Preview')
        tree.heading('recipients', text='Original File')
        tree.column('date', width=150); tree.column('subject', width=200); tree.column('recipients', width=200)
        tree.pack(fill="both", expand=True)
        
        missions_data = {}
        for cp in self._active_checkpoints:
            try:
                with open(cp, 'r') as f:
                    d = json.load(f)
                    ts = d.get('timestamp', 'Unknown').replace('T', ' ')[:19]
                    subj = d.get('subject', 'No Subject')
                    rf = Path(d.get('recipient_file', 'Unknown')).name
                    iid = tree.insert('', tk.END, values=(ts, subj, rf))
                    missions_data[iid] = cp
            except: pass
            
        def on_select():
            selected = tree.selection()
            if not selected: return
            cp_path = missions_data[selected[0]]
            sel_win.destroy()
            self.resume_sending(cp_path)
            
        btn_f = ttk.Frame(container)
        btn_f.pack(fill="x", pady=10)
        ttk.Button(btn_f, text="🚀 RESTORE SELECTED", command=on_select, style='Accent.TButton').pack(side="left", padx=5)
        ttk.Button(btn_f, text="🗑️ DELETE", command=lambda: [Path(missions_data[tree.selection()[0]]).unlink(), tree.delete(tree.selection()[0])]).pack(side="left", padx=5)
        ttk.Button(btn_f, text="CLOSE", command=sel_win.destroy).pack(side="right")

    # ------------------------------------------------------------------ #
    #  THREAD-SAFE UI TEARDOWN                                             #
    # ------------------------------------------------------------------ #
    def _on_send_complete(self, sent, failed_count, total, halted=False):
        """Teardown UI state on main thread after send thread finished (Gaps 4, 15, 45)."""
        self._enable_launch()
        self.stop_btn.config(state='disabled')
        self.is_sending = False
        self._check_resume_available()
        self.progress_bar['value'] = 100
        # Restore recipients if retry was active (Gap 42 structural closure)
        if getattr(self, '_recipients_bak', None) is not None:
            self.recipients = self._recipients_bak
            self._recipients_bak = None

        # Ensure stop state is reset (Gap 57)
        self.stop_btn.config(state='disabled')
        
        # Clear CSV cache (Gap: Consistency)
        EmailChecker.clear_cache()

        prefix = "Halted." if halted else "Done!"
        final = f"{prefix} Sent:{sent} Failed:{failed_count} Total:{total}"
        self.status_var.set(final)
        self.hud_status_var.set(final)
        self.root.title("jBulkEmailSender - Tactical Operations")
        self.log_message(f"🏁 Mission Finished — Total:{total}  Sent:{sent}  Failed:{failed_count}")
        if sent > 0:
            messagebox.showinfo("Complete",
                                f"Email sending complete!\n\nSent: {sent}\nFailed: {failed_count}")

    # ------------------------------------------------------------------ #
    #  CORE SEND THREAD                                                    #
    # ------------------------------------------------------------------ #
    def send_emails_thread(self, start_idx=0):
        """Background thread — all Tkinter access via self._snap or root.after(0)."""
        total       = len(self.recipients)
        sent        = 0
        failed_list = []               # [{email, name, error}]  (Gap 7)
        server      = None             # pre-init so finally never NameErrors (Gap 17)

        try:
            # Gap 27: moved inside try so a crash here still triggers finally
            account_pair = next(self._account_cycle)
            batch_limit  = max(1, self._snap.get('batch_size', 50))   # Gap 36: never 0
            batch_pause  = self._snap.get('batch_pause', 60.0)
            
            # --- PERFORMANCE BOOST: Pre-read and encode all attachments ONCE (Gap: High Overload) ---
            pre_processed_attachments = []
            for file_path in self.attachments:
                try:
                    p = Path(file_path).absolute()
                    # We create the skeleton MIME object once
                    part = MIMEBase('application', 'octet-stream')
                    with open(p, 'rb') as fh:
                        part.set_payload(fh.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename="{p.name}"')
                    pre_processed_attachments.append(part)
                except Exception as ae:
                    self.log_message(f"⚠️ Attachment pre-read error {file_path}: {ae}")

            # --- PERFORMANCE BOOST: Cache regex patterns (Gap: Loop efficiency) ---
            r_name  = re.compile(re.escape('{name}'), re.IGNORECASE)
            r_email = re.compile(re.escape('{email}'), re.IGNORECASE)

            server = self._smtp_connect(*account_pair)

            # Open log file once for the entire run (Gap 16)
            idx_last = start_idx - 1
            is_halted = False
            with open(self.log_file, 'a', encoding='utf-8') as log_fh:
                for idx in range(start_idx, total):
                    if not self.is_sending:
                        is_halted = True
                        self.log_message("⚠️ Sending halted by user")
                        break

                    # --- Batch boundary: rotate account + fresh connection (Gap 39: Isolated) ---
                    steps = idx - start_idx
                    if steps > 0 and steps % batch_limit == 0:
                        try: server.quit()
                        except: pass
                        
                        account_pair = next(self._account_cycle)
                        self.log_message(f"⏸️ Batch boundary — pausing {batch_pause:.0f}s, rotating → {account_pair[0]}")
                        
                        # Sync all progress to disk at batch boundary
                        if hasattr(self, 'current_filename'):
                            EmailChecker.flush_cache(self.current_filename)
                        
                        time.sleep(batch_pause)
                        
                        try:
                            server = self._smtp_connect(*account_pair)
                        except Exception as stop_e:
                            self.log_message(f"⚠️ Batch rotate failed ({stop_e}) — trying next candidate")
                            account_pair = next(self._account_cycle)
                            try:
                                server = self._smtp_connect(*account_pair)
                            except Exception as stop_e2:
                                self.log_message(f"❌ Cannot reconnect any account: {stop_e2}. Aborting.")
                                break

                    # --- Thread-safe progress update (Gap 14) ---
                    progress    = int(((idx - start_idx + 1) / (total - start_idx)) * 100)  # Gap 21
                    status_text = f"Sending {idx + 1}/{total}..."
                    self.root.after(0, lambda p=progress, s=status_text: (
                        self.progress_bar.__setitem__('value', p),
                        self.status_var.set(s),
                        self.hud_status_var.set(s),
                        self.root.title(f"{s} - jBulkEmailSender")
                    ))

                    recipient = self.recipients[idx]
                    success   = False
                    try:
                        # --- Build message using pre-snapped values (Gaps 3, 13) ---
                        msg         = MIMEMultipart()
                        msg['From'] = self._snap['sender']
                        msg['To']   = recipient['email'].replace(';', ',')
                        if self._snap['cc_enabled'] and recipient.get('cc_emails'):
                            msg['Cc'] = recipient['cc_emails'].replace(';', ',')

                        subject      = self._snap['subject']
                        body_content = self._snap['body']

                        if self._snap['personalize']:
                            name       = recipient.get('name', 'Customer')
                            email_addr = recipient.get('email', '')
                            # Faster case-insensitive replacement (compiled regex)
                            subject = r_name.sub(name, subject)
                            subject = r_email.sub(email_addr, subject)
                            body_content = r_name.sub(name, body_content)
                            body_content = r_email.sub(email_addr, body_content)

                        msg['Subject'] = subject

                        is_html = any(tag in body_content.lower() for tag in ('<html>', '<body>', '<p>'))
                        if is_html:
                            # Phase 11.11: Tactical Mission Branding (Watermark & Floating Shadow)
                            styled_body = f"""
                            <div style="background-image: url('cid:mission_icon'); 
                                         background-repeat: no-repeat; 
                                         background-position: center center; 
                                         background-size: 100% 100%; 
                                         background-attachment: fixed;
                                         min-height: 500px; padding: 30px;
                                         ">
                                <div style="text-shadow: 4px 4px 8px rgba(0,0,0,0.5); 
                                            font-family: 'Segoe UI', Arial, sans-serif;
                                            font-size: 12pt; color: #000000;
                                            line-height: 1.6;
                                            ">
                                    {body_content}
                                </div>
                            </div>
                            """
                            msg.attach(MIMEText(styled_body, 'html'))
                            
                            # Embed the mission icon as the watermark source
                            icon_p = BASE_DIR / "assets" / "mission_icon.png"
                            if icon_p.exists():
                                try:
                                    with open(icon_p, 'rb') as f_ico:
                                        img_ico = MIMEImage(f_ico.read())
                                        img_ico.add_header('Content-ID', '<mission_icon>')
                                        img_ico.add_header('Content-Disposition', 'inline', filename='branding.png')
                                        msg.attach(img_ico)
                                except Exception as e_ico:
                                    self.log_message(f"⚠️ Branding Error: {e_ico}")
                        else:
                            msg.attach(MIMEText(body_content, 'plain'))

                        # Attachments (Use pre-processed objects)
                        for part in pre_processed_attachments:
                            msg.attach(part)

                        # --- Send with auto-reconnect (Gap 11) ---
                        s_send = time.time()
                        server = self._smtp_send_with_retry(server, msg, account_pair)
                        t_send = time.time() - s_send
                        
                        sent  += 1
                        success = True
                        self.log_message(f"✉️ Sent {idx+1}/{total} → {recipient['email']} (Send time: {t_send:.2f}s)")

                        # Waterfall Layer 4 — Isolated post-send persistence (Gap 40)
                        s_post = time.time()
                        self._post_send_ops(recipient, idx, sent, log_fh, failed_list)
                        t_post = time.time() - s_post
                        if t_post > 1.0:
                             self.log_message(f"⚠️ Slow background ops: {t_post:.2f}s")
                        
                        # Gap 44: Only update index after we've passed the attempt (success or accounting for failure)
                        idx_last = idx

                    except Exception as e:
                        err_msg = str(e)
                        failed_list.append({'email': recipient['email'], 'name': recipient.get('name', ''), 'error': err_msg})
                        self.log_message(f"❌ Failed → {recipient['email']}: {err_msg}")
                        log_fh.write(f"[{datetime.now()}] FAILED - {recipient['email']} - {err_msg}\n")
                        log_fh.flush()
                        idx_last = idx  # Account for this row in progress even if send failed

                    # Delay only after successes, and not after last email (Gaps 18, 26)
                    if success and idx < total - 1:
                        time.sleep(self._snap['delay'])

        except smtplib.SMTPAuthenticationError:
            self.log_message("❌ Authentication failed — check App Password")
            self.root.after(0, lambda: messagebox.showerror(
                "Auth Error",
                "SMTP login rejected.\n\n"
                "1. Use an App Password (not your regular password)\n"
                "2. Enable 2-Step Verification first\n"
                "3. Generate at: myaccount.google.com/apppasswords"))

        except Exception as e:
            self.log_message(f"❌ Connection error: {e}")
            self.root.after(0, lambda msg=str(e): messagebox.showerror("Error", f"SMTP error:\n{msg}"))

        finally:
            # Sync final results to disk regardless of HALT or Completion
            if hasattr(self, 'current_filename'):
                EmailChecker.flush_cache(self.current_filename)
            
            # Safe quit (Gap 12, 17)
            if server:
                try: server.quit()
                except: pass

            # Save final checkpoint before deciding whether to clean up (Gap 37 closure)
            if (sent > 0 or failed_list) and 'idx_last' in locals():
                self._save_progress(idx_last, sent, failed_list)

            # Clean up progress file (Gap 24):
            # Delete only when: no failures AND user didn't halt
            if not failed_list and self.is_sending:
                if self.progress_file.exists():
                    self.progress_file.unlink()

            # Export failed list if any (Gap 7)
            if failed_list:
                self._export_failed_csv(failed_list)

            # All UI teardown on main thread (Gaps 4, 14, 15, 45)
            self.root.after(0, self._on_send_complete, sent, len(failed_list), total, is_halted)

    # ------------------------------------------------------------------ #
    #  RESUME / RETRY                                                      #
    # ------------------------------------------------------------------ #
    def resume_sending(self, specific_path=None):
        """Resume an interrupted send from saved progress."""
        if self.is_sending: return
        
        target_path = specific_path if specific_path else self.progress_file
        if not target_path or not Path(target_path).exists():
            # If no specific path, try finding the most recent one
            self._discover_checkpoints()
            if self._active_checkpoints:
                target_path = Path(self._active_checkpoints[0])
            else:
                messagebox.showinfo("Resume", "No interrupted session found.")
                return

        target_path = Path(target_path)

        try:
            # CHECK FOR CORRUPTION: If file is empty or just whitespace, it will fail JSON decode
            if not target_path.exists() or target_path.stat().st_size < 2:
                 raise ValueError("File is empty or too small to be valid JSON")

            with open(target_path, 'r') as f:
                data = json.load(f)
            # Track this as the active progress file for this session
            self.progress_file = Path(target_path)
        except (json.JSONDecodeError, ValueError, Exception) as e:
            self.log_message(f"⚠️ Corruption detected in checkpoint: {target_path.name}")
            if messagebox.askyesno("Corruption Detected", 
                                   f"The checkpoint file '{target_path.name}' is corrupted or empty.\n\n"
                                   f"Error: {str(e)}\n\n"
                                   "Would you like to delete this corrupted file and start fresh?"):
                try:
                    target_path.unlink()
                    self._check_resume_available()
                except: pass
            return

        sender = data.get("sender_email")
        matched = next((k for k in self.accounts if k.lower() == sender.lower()), None)
        if not matched:
            messagebox.showerror("Resume Error", f"Credentials for '{sender}' no longer found.")
            return
        
        filepath = data.get("recipient_file", '')
        if not filepath or not Path(filepath).exists():
            messagebox.showerror("Resume Error", "Original recipient file not found.")
            return

        # 1. Subject/Body Sync
        self.subject_var.set(data.get('subject', ''))
        body_content = data.get('body', '')
        if body_content:
            self.set_body_content(body_content)
        
        # 2. Recipient File Sync
        self.current_filename = filepath
        self.recipient_file_var.set(Path(filepath).name)
        
        # 3. Sender Sync
        self.from_email_combo.set(sender)
        
        # 4. Attachments Sync
        restored_attachments = data.get('attachments', [])
        valid_attachments = []
        missing_attachments = []
        for att in restored_attachments:
            if Path(att).exists():
                valid_attachments.append(att)
            else:
                missing_attachments.append(att)
        
        self.attachments = valid_attachments
        self.update_attachment_list()

        # Reload recipients
        self.log_message("📥 Restoring mission data and email list...")
        _, self.recipients, err = EmailChecker.process_csv_file(filepath, include_cc=self.cc_var.get())
        if err:
            messagebox.showerror("Error", f"Failed to reload recipients: {err}")
            return
            
        start = data.get('last_sent_idx', 0) + 1
        sent_so_far = data.get('sent_count', 0)
        
        if start >= len(self.recipients):
            messagebox.showinfo("Resume", "All emails in this mission were already sent!")
            self.progress_file.unlink()
            self._check_resume_available()
            return

        # Verification Checklist Alert
        checklist_msg = "📋 MISSION RECOVERY CHECKLIST:\n\n"
        checklist_msg += f"✅ Subject: Loaded\n"
        checklist_msg += f"✅ Body: Loaded\n"
        checklist_msg += f"✅ File: {Path(filepath).name}\n"
        
        if missing_attachments:
            checklist_msg += f"⚠️ ATTACHMENTS: {len(missing_attachments)} file(s) are MISSING from disk!\n"
            for m in missing_attachments:
                checklist_msg += f"   - {Path(m).name}\n"
        elif valid_attachments:
            checklist_msg += f"✅ Attachments: {len(valid_attachments)} files restored\n"
        else:
            checklist_msg += "ℹ️ No attachments in this mission\n"

        checklist_msg += f"\nRESUME from email #{start + 1}?\n(Previously sent: {sent_so_far})"

        if not messagebox.askyesno("Resume Mission Checklist", checklist_msg):
            self.log_message("⚠️ Mission resume canceled by user for manual content check.")
            return

        # Setup the system to use this index on the next LAUNCH click
        self._pending_resume_idx = start
        self._build_account_cycle(matched)
        
        self.log_text.delete('1.0', tk.END)
        self.log_message(f"✅ Mission Content Restored Successfully.")
        self.log_message(f"👉 RESUME POINT: Ready to continue from Email #{start + 1}")
        self.log_message(f"📢 ACTION REQUIRED: Please review the Subject, Body, and Attachments.")
        self.log_message(f"🚀 Click the 'LAUNCH' button when you are satisfied and ready to send.")
        
        messagebox.showinfo("Mission Ready", 
                            "Mission content has been restored to the editor!\n\n"
                            "1. Review/Update your email body or attachments now.\n"
                            "2. When ready, click the '🚀 LAUNCH' button to start sending.")

    def retry_failed(self):
        """Reload the last failed CSV and resend those addresses only (Gap 23)."""
        if self.is_sending: return  # Gap 76: Double-click protection
        if not getattr(self, '_last_failed_csv', None) or not Path(self._last_failed_csv).exists():
            messagebox.showinfo("Retry", "No failed email list found.\nRun a send first.")
            return
        if not self.subject_var.get().strip():
            messagebox.showwarning("Missing", "Please enter a Subject before retrying.")
            return
        if not self.body_text.get('1.0', tk.END).strip():
            messagebox.showwarning("Missing", "Email body is empty. Fill it before retrying.")
            return
        try:
            with open(self._last_failed_csv, encoding='utf-8') as fh:   # Gap 28: close file
                rows = list(csv.DictReader(fh))
        except Exception as e:
            messagebox.showerror("Error", f"Could not read failed CSV: {e}")
            return
        if not rows:
            messagebox.showinfo("Retry", "Failed list is empty.")
            return

        # Gap 42: backup original recipients before overwriting with failed subset
        self._recipients_bak = self.recipients[:]
        self.recipients = [{'email': r['email'], 'name': r.get('name', ''), 'row_idx': -1}
                           for r in rows if r.get('email')]
        if not self.recipients:
            messagebox.showinfo("Retry", "No valid email addresses in failed list.")
            return

        # Gap 32: validate sender is in accounts before building cycle
        sender = self.from_email_combo.get().strip()
        matched = next((k for k in self.accounts if k.lower() == sender.lower()), None)
        if not matched:
            messagebox.showerror("Retry Error",
                                  f"No saved credentials for '{sender}'.\n"
                                  "Please select a valid sender account.")
            return

        # Gap 38: clear FIRST (synchronous), then schedule the insert via log_message
        self.log_text.delete('1.0', tk.END)
        self.log_message(f"🔄 Retrying {len(self.recipients)} failed addresses...")
        self._build_account_cycle(matched)
        self._start_sending_from(start_idx=0)

    
    def log_message(self, message):
        """Add message to log — thread-safe: routes widget writes through root.after(0)."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        msg_line  = f"[{timestamp}] {message}\n"

        def _insert():
            self.log_text.insert(tk.END, msg_line)
            self.log_text.see(tk.END)
            # Gap 54: Buffer capping for massive missions (keep last 1000)
            try:
                if int(float(self.log_text.index('end-1c'))) > 1000:
                    self.log_text.delete('1.0', '2.0')
            except: pass

        # Schedule on main thread regardless of caller thread
        self.root.after(0, _insert)

    def on_cc_toggle(self):
        """Show information popup and update UI status when CC is toggled"""
        state = "ENABLED (Col E)" if self.cc_var.get() else "DISABLED (Global)"
        self.cc_info_var.set(f"CC: {state}")
        
        if self.cc_var.get():
            messagebox.showinfo("CC Information", 
                                "Mission Control Alert:\n\n"
                                "1. CC email addresses must be stored in Column 'E'.\n"
                                "2. Use ';' (semicolon) as the delimiter for multiple email entries in both Column A and Column E.\n\n"
                                "The system will automatically parse and include these recipients.")

    def attach_files(self):
        """Allow user to select multiple files with a 25MB total limit"""
        files = filedialog.askopenfilenames(title="Select Attachments")
        if not files:
            return

        MAX_SIZE_MB = 25
        MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024
        
        # Calculate current total size
        current_total = sum(os.path.getsize(f) for f in self.attachments)
        
        new_valid_files = []
        for f in files:
            f_size = os.path.getsize(f)
            if current_total + f_size > MAX_SIZE_BYTES:
                messagebox.showwarning("Size Limit", f"Total attachments size exceeds {MAX_SIZE_MB}MB limit. Skipping remaining files.")
                break
            
            if f not in self.attachments:
                new_valid_files.append(f)
                current_total += f_size
        
        if new_valid_files:
            self.attachments.extend(new_valid_files)
            self.update_attachment_list()
            self.log_message(f"📎 Attached {len(new_valid_files)} files (Total: {current_total/(1024*1024):.1f} MB)")

    def remove_attachment(self):
        """Remove selected attachments from the list based on checkbox states"""
        indices_to_remove = []
        for i, (var, path) in enumerate(self.attachment_checkbox_vars):
            if var.get():
                indices_to_remove.append(i)
                
        if not indices_to_remove:
            return
            
        # Reverse to avoid index shifting
        for idx in sorted(indices_to_remove, reverse=True):
            del self.attachments[idx]
            
        self.update_attachment_list()
        self.log_message(f"🗑️ Removed {len(indices_to_remove)} attachment(s)")

    def remove_single_attachment(self, f_path):
        """Remove a specific file from the attachment list"""
        if f_path in self.attachments:
            self.attachments.remove(f_path)
            self.update_attachment_list()
            self.log_message(f"🗑️ Removed attachment: {os.path.basename(f_path)}")

    def update_attachment_list(self):
        """Update the status label and refresh the popup if open"""
        # 1. Update Global Label
        total_bytes = sum(os.path.getsize(f) for f in self.attachments)
        formatted_total = self.get_formatted_size(total_bytes)
        count = len(self.attachments)
        self.attach_status_var.set(f"📎 {count} files ({formatted_total})")
        
        # 2. Refresh Popup View (Only if the scroll frame exists/is visible)
        if hasattr(self, 'attach_scroll_frame') and self.attach_scroll_frame.winfo_exists():
            for widget in self.attach_scroll_frame.winfo_children():
                widget.destroy()
            self.attachment_checkbox_vars = []
            
            for i, f_path in enumerate(self.attachments):
                row_frame = ttk.Frame(self.attach_scroll_frame)
                row_frame.pack(fill="x", pady=2)
                row_frame.columnconfigure(1, weight=1)
                
                var = tk.BooleanVar()
                self.attachment_checkbox_vars.append((var, f_path))
                
                tk.Checkbutton(row_frame, variable=var, bg='#D3D3D3').grid(row=0, column=0)
                
                name = os.path.basename(f_path)
                size_str = self.get_formatted_size(os.path.getsize(f_path))
                ttk.Label(row_frame, text=f"{name} ({size_str})", font=('Segoe UI', 8)).grid(row=0, column=1, sticky="w", padx=5)
                
                # Per-row Trash Button
                ttk.Button(row_frame, text="🗑️", width=3, 
                           command=lambda p=f_path: self.remove_single_attachment(p)).grid(row=0, column=2, padx=5)
                
                ttk.Separator(self.attach_scroll_frame, orient="horizontal").pack(fill="x", padx=5, pady=2)

    def show_attachment_manager(self):
        """Open a popup window to manage/remove attachments"""
        if not self.attachments:
            messagebox.showinfo("Attachments", "No files attached yet. Use the 📁 button in the editor toolbar.")
            return

        mgr_win = tk.Toplevel(self.root)
        mgr_win.title("Manage Attachments")
        mgr_win.geometry("400x450")
        
        theme = self.themes.get(self.current_theme_name, {})
        bg_color = theme.get('bg', '#0B132B')
        entry_bg = theme.get('entry_bg', '#D3D3D3')

        mgr_win.configure(bg=bg_color)

        container = ttk.Frame(mgr_win, padding="15")
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="📎 Current Attachments", font=('Segoe UI', 10, 'bold')).pack(pady=(0,10))

        # Re-use scroll logic in a popup
        canvas = tk.Canvas(container, bg=entry_bg, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.attach_scroll_frame = ttk.Frame(canvas)
        
        self.attach_scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.attach_scroll_frame, anchor="nw", width=350)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill="x", pady=10)
        
        ttk.Button(btn_frame, text="🗑️ REMOVE SELECTED", command=self.remove_attachment).pack(side="left", expand=True)
        ttk.Button(btn_frame, text="CLOSE", command=mgr_win.destroy).pack(side="left", expand=True)

        self.update_attachment_list()

    def get_formatted_size(self, size_bytes):
        """Convert bytes to KB or MB string"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes/1024:.1f} KB"
        else:
            return f"{size_bytes/(1024*1024):.2f} MB"

    def view_logs(self):
        """Open the latest mission log file"""
        if hasattr(self, 'log_file') and self.log_file.exists():
            os.startfile(self.log_file) if sys.platform == 'win32' else webbrowser.open(self.log_file.as_uri())
        elif self.master_log_file.exists():
            os.startfile(self.master_log_file) if sys.platform == 'win32' else webbrowser.open(self.master_log_file.as_uri())
        else:
            # Fallback: open logs directory
            if self.dirs['logs'].exists():
                os.startfile(self.dirs['logs'])
            else:
                messagebox.showinfo("No Logs", "No logs found yet. Send some emails first!")

    def view_failed_folder(self):
        """Open the failed missions directory (Gap 55)"""
        if self._failed_dir.exists():
            os.startfile(self._failed_dir) if sys.platform == 'win32' else webbrowser.open(self._failed_dir.as_uri())

    def toggle_password(self, entry_widget, button_widget):
        """Toggle password visibility between masked (*) and plain text"""
        if entry_widget.cget('show') == '*':
            entry_widget.config(show='')
            button_widget.config(text='🙈')
        else:
            entry_widget.config(show='*')
            button_widget.config(text='👁')

    def restart_application(self):
        """Restarts the current python process to apply code changes (Refresh)."""
        if self.is_sending:
            if not messagebox.askyesno("Confirm Restart", 
                                     "🚀 MISSION IN PROGRESS\n\n"
                                     "An email mission is currently active. Restarting will halt the mission.\n"
                                     "You can resume it later from the Progress Checkpoint.\n\n"
                                     "Proceed with Refresh?"):
                return
        
        self.log_message("🔄 Initiating Tactical Refresh: Restarting application...")
        
        # Save config and Tactical State before reload
        try:
            self.save_config()
            self.save_reload_state()
        except Exception as e:
            print(f"State save failed: {e}")
            
        # Execute restart
        python = sys.executable
        
        # Determine launch arguments
        if hasattr(sys, 'frozen'):
            # If running as a compiled .exe, sys.executable is the app itself
            args = [python] + sys.argv[1:]
        else:
            # If running as a script, we need the python executable + script path + args
            args = [python] + sys.argv
        
        try:
            # On Windows, os.execl can be erratic in some IDE/Virtual environments.
            # Using subprocess.Popen ensures a clean detached launch of the new version.
            if sys.platform == 'win32':
                # Use DETACHED_PROCESS so the new process is not a child of the current one
                subprocess.Popen(args, creationflags=0x00000008, close_fds=True)
            else:
                subprocess.Popen(args, close_fds=True)
            
            # Close the current instance cleanly and immediately
            self.root.destroy()
            os._exit(0) 
        except Exception as e:
            messagebox.showerror("Refresh Error", f"Failed to restart application: {e}")
            self.log_message(f"❌ Refresh failed: {e}")

    def _show_help_mission(self):
        """Displays the tactical mission handbook with operational steps."""
        help_win = tk.Toplevel(self.root)
        help_win.title("TACTICAL INTELLIGENCE: MISSION HANDBOOK")
        help_win.geometry("750x650")
        help_win.configure(bg=self.colors['bg'])
        help_win.grab_set()

        # Header
        hdr = tk.Frame(help_win, bg=self.colors['panel'], height=50)
        hdr.pack(fill="x")
        tk.Label(hdr, text="📖 MISSION OPERATIONAL PROCEDURES", bg=self.colors['panel'], 
                 fg=self.colors['text'], font=('Segoe UI', 14, 'bold')).pack(pady=10)

        # Content Area
        f = tk.Frame(help_win, bg=self.colors['bg'], padx=20, pady=10)
        f.pack(fill="both", expand=True)

        txt = scrolledtext.ScrolledText(f, wrap=tk.WORD, bg='#1E1E2E', fg='#FFFFFF', 
                                         font=('Segoe UI', 10), padx=15, pady=15, bd=0)
        txt.pack(fill="both", expand=True)

        steps = [
            ("1. AUTHENTICATION (IDENTITY SETUP)", self.colors['aqua']),
            ("   • Add your email in the 'Security' sidebar.\n   • MISSION CRITICAL: Use an 'App Password' (16 digits), not your regular password.\n   • Click 'SAVE' to store locally. Click 'TEST' to verify connection.", "#FFFFFF"),
            ("\n2. RECIPIENT DEPLOYMENT", self.colors['aqua']),
            ("   • Click 'LOAD' (paperclip) to select your CSV or Excel list.\n   • Use 'LIST' to verify addresses and specific CC fields.", "#FFFFFF"),
            ("\n3. CONTENT STRATEGY & PERSONALIZATION", self.colors['aqua']),
            ("   • Placeholders: Use {name} or {email} in subject/body for auto-injection.\n   • HTML Mode: Toggle this to enable Rich Text, Colors, and Watermarking.\n   • Attachments: Use the toolbar clip 📎 to manage multiple files.", "#FFFFFF"),
            ("\n4. TRANSMISSION CONFIGURATION", self.colors['aqua']),
            ("   • Delay(s): Tactical pause between transmissions (Recommended: 1-5s).\n   • Batch Size: How many emails per session (Recommended: 50).", "#FFFFFF"),
            ("\n5. MISSION LAUNCH & MONITORING", self.colors['aqua']),
            ("   • Click the 'LAUNCH' rocket to start. Monitor real-time status in the Log.\n   • The 'HUD' at the top shows current atmospheric status (SENDING/IDLE).", "#FFFFFF"),
            ("\n6. RECOVERY & RETRY OPS", self.colors['aqua']),
            ("   • HALT: Stop transmission safely at any point.\n   • RESUME: Found an interrupted mission? Click Resume to pick up where you left off.\n   • RETRY: Targeted failure manifest processing for failed IDs.", "#FFFFFF"),
            ("\n7. AUTOMATED BRANDING", self.colors['aqua']),
            ("   • Your mission icon is automatically embedded as a CID background watermark in HTML emails to ensure sender authority.", "#FFFFFF"),
            ("\n8. PORTABILITY & DISTRIBUTION", self.colors['aqua']),
            ("   • The 'dist/' folder contains the 'jBulkEmailSender.exe' which runs without Python.\n   • Simply zip the entire BulkEmailSender folder to move to another laptop.", "#FFFFFF"),
        ]

        for title, color in steps:
            tag = f"tag_{color.replace('#','')}"
            txt.tag_configure(tag, foreground=color)
            if any(s in title for s in ["1.", "2.", "3.", "4.", "5.", "6.", "7.", "8."]):
                 txt.tag_configure(tag, font=('Segoe UI', 11, 'bold'))
            txt.insert(tk.END, title + "\n", tag)

        txt.config(state='disabled')
        
        # Checkbox & Close
        btn_f = tk.Frame(help_win, bg=self.colors['bg'])
        btn_f.pack(fill="x", pady=10)
        
        self.show_help_var = tk.BooleanVar(value=not self.show_help_on_start)
        tk.Checkbutton(btn_f, text="Don't show this again at startup", variable=self.show_help_var,
                       bg=self.colors['bg'], fg=self.colors['white'], selectcolor=self.colors['panel'],
                       activebackground=self.colors['bg'], activeforeground=self.colors['aqua'],
                       font=('Segoe UI', 9)).pack(side="left", padx=20)
        
        def close_help():
            self.show_help_on_start = not self.show_help_var.get()
            # Save to config
            self.config['show_help_on_start'] = self.show_help_on_start
            self.save_config()
            help_win.destroy()

        ttk.Button(btn_f, text="CONFIRM & CLOSE", command=close_help, style='Accent.TButton').pack(side="right", padx=20)

def main():
    root = tk.Tk()
    app = BulkEmailSender(root)
    root.mainloop()

if __name__ == "__main__":
    main()
