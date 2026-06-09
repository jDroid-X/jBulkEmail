import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox, simpledialog
import sys
import os
from pathlib import Path
from app.utils.constants import MISSION_COLORS, SMTP_PROVIDERS, HUD_STATUS_IDLE
from app.utils.widgets import RoundedButton

BASE_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(BASE_DIR / "core"))

try:
    # We expect these to be in the core folder of the monolith's project
    from RichContentManager import RichTextEditor, ToolTip, RichToolTip
    RICH_TEXT_AVAILABLE = True
except ImportError:
    RICH_TEXT_AVAILABLE = False
    print("Warning: RichContentManager dependencies missing.")

class MainDashboardView:
    """
    View Layer for jBulkEmailSender.
    Handles UI layout, widgets, and aesthetics.
    Decomposes the monolith UI into modular sections.
    """
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.model = controller.model
        self.colors = MISSION_COLORS
        
        # Link controller callbacks for logging
        self.controller.view_callback_log = self.append_to_log
        
        # UI Variables (Synced with Model)
        self._init_ui_variables()
        
        # Primary Structure
        self._setup_mission_styles()
        self._setup_containers()
        self._setup_hud()
        self._setup_sidebar()        # Left ~15% (Reduced by 50%)
        self._setup_composition_area() # Right ~85%
        
        # Post-Init
        self._sync_ui_to_model()

    def _init_ui_variables(self):
        self.subject_var = tk.StringVar()
        self.hud_status_var = tk.StringVar(value=HUD_STATUS_IDLE)
        self.status_var = tk.StringVar(value="Ready")
        self.account_email_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.delay_var = tk.DoubleVar(value=1.0)
        self.batch_size_var = tk.IntVar(value=50)
        self.personalize_var = tk.BooleanVar(value=True)
        self.html_var = tk.BooleanVar(value=False)
        self.recipient_file_var = tk.StringVar(value="No file")
        self.cc_var = tk.BooleanVar(value=False)
        self.cc_info_var = tk.StringVar(value="[Disabled]")
        self.attach_status_var = tk.StringVar(value="📎 0 files")
        self.theme_var = tk.StringVar(value=self.model.current_theme_name)

    def _setup_mission_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        bg = self.colors['bg']
        panel = self.colors['panel']
        aqua = self.colors['aqua']
        white = self.colors['white']
        glow = self.colors['glow']
        text_gold = self.colors['text']

        style.configure('TFrame', background=bg)
        style.configure('TLabel', background=bg, foreground=white, font=('Segoe UI', 9))
        style.configure('TLabelFrame', background=panel, foreground=aqua, 
                        font=('Segoe UI', 9, 'bold'), borderwidth=4, relief='groove')
        style.configure('TLabelFrame.Label', background=panel, foreground=aqua)
        style.configure('TButton', font=('Segoe UI', 8, 'bold'), borderwidth=2, relief='raised', padding=(8, 4))
        style.configure('Accent.TButton', background=aqua, foreground='#000000', borderwidth=2, relief='raised')
        style.map('Accent.TButton', background=[('active', glow), ('pressed', '#00838F')])
        style.configure('Gold.TButton', background=text_gold, foreground='#000000', padding=(8, 4), borderwidth=2, relief='raised')
        
        self.root.configure(bg=bg)

    def _setup_containers(self):
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1); self.root.rowconfigure(0, weight=1)
        
        # Phase 11.12: Fixed-width Ultra-Compact Sidebar (150px - 50% reduction)
        self.main_frame.columnconfigure(0, weight=0, minsize=150) # Fixed Sidebar
        self.main_frame.columnconfigure(1, weight=1) # Fluid Main View
        self.main_frame.rowconfigure(1, weight=1)

    def _setup_hud(self):
        hud_frame = tk.Frame(self.main_frame, bg=self.colors['panel'], height=60)
        hud_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        hud_frame.grid_propagate(False)
        
        tk.Label(hud_frame, text="🚀 jBulkEmailSender", bg=self.colors['panel'], fg=self.colors['text'], 
                 font=('Segoe UI', 18, 'bold')).pack(side="left", padx=20)
        
        tk.Label(hud_frame, textvariable=self.hud_status_var, bg=self.colors['panel'], fg=self.colors['aqua'], 
                 font=('Segoe UI', 12, 'bold')).pack(side="left", expand=True)

        version_label = tk.Label(hud_frame, text="MISSION CONTROL • v6.1-MISSION", bg=self.colors['panel'], 
                                 fg=self.colors['aqua'], font=('Segoe UI', 8, 'bold'))
        version_label.pack(side="right", padx=20)
        
        if RICH_TEXT_AVAILABLE:
            RichToolTip(version_label, [
                ("TACTICAL EVALUATION: v6.0-PORTABLE", self.colors['aqua'], ("Segoe UI", 10, "bold")),
                ("-" * 55, "#444444", ("Segoe UI", 8)),
                ("PORTABILITY: Zero-Python executable build ready.", "#FFFFFF", ("Segoe UI", 9)),
                ("AESTHETICS: Watermark branding + Floating shadow enabled.", "#FFFFFF", ("Segoe UI", 9)),
                ("SAFETY: Waterfall uninitialized state protection.", self.colors['text'], ("Segoe UI", 9, "bold")),
                ("IO: Close-one-step-back file management.", self.colors['text'], ("Segoe UI", 9, "bold")),
                ("RECOVERY: Mission state logic enabled.", self.colors['glow'], ("Segoe UI", 9, "bold"))
            ])

    def _setup_sidebar(self):
        left_panel = ttk.Frame(self.main_frame)
        left_panel.grid(row=1, column=0, sticky="nsew", padx=(0, 15))
        left_panel.columnconfigure(0, weight=1)
        
        # 1. Security
        sec_f = ttk.LabelFrame(left_panel, text="🔑 Security", padding="5")
        sec_f.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        sec_f.columnconfigure(1, weight=1)
        
        ttk.Label(sec_f, text="ID:").grid(row=0, column=0, sticky="w")
        self.account_email_combo = ttk.Combobox(sec_f, textvariable=self.account_email_var)
        self.account_email_combo.grid(row=0, column=1, pady=2, sticky="ew")
        self.account_email_combo.bind("<<ComboboxSelected>>", self._on_account_selected)
        
        ttk.Label(sec_f, text="PW:").grid(row=1, column=0, sticky="w")
        self.password_entry = ttk.Entry(sec_f, textvariable=self.password_var, show="*")
        self.password_entry.grid(row=1, column=1, pady=2, sticky="ew")
        
        btn_f = ttk.Frame(sec_f)
        btn_f.grid(row=2, column=0, columnspan=2, pady=5, sticky="ew")
        btn_f.columnconfigure((0,1), weight=1)
        ttk.Button(btn_f, text="🟢 SAVE", command=self.trigger_save_account, style='Accent.TButton').grid(row=0, column=0, padx=1, sticky="ew")
        ttk.Button(btn_f, text="🧪 TEST", command=self.trigger_test_login, style='Accent.TButton').grid(row=0, column=1, padx=1, sticky="ew")

        # 2. Config
        opt_f = ttk.LabelFrame(left_panel, text="⚙️ Config", padding="5")
        opt_f.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        opt_f.columnconfigure(1, weight=1)
        
        ttk.Label(opt_f, text="Delay(s):").grid(row=0, column=0, sticky="w")
        ttk.Spinbox(opt_f, from_=0, to=60, increment=0.5, textvariable=self.delay_var, width=5).grid(row=0, column=1, sticky="ew")
        
        ttk.Label(opt_f, text="Batch:").grid(row=1, column=0, sticky="w")
        ttk.Spinbox(opt_f, from_=1, to=500, textvariable=self.batch_size_var, width=5).grid(row=1, column=1, sticky="ew")

        ttk.Checkbutton(opt_f, text="Personalize", variable=self.personalize_var).grid(row=2, column=0, sticky="w")
        ttk.Checkbutton(opt_f, text="HTML Mode", variable=self.html_var).grid(row=2, column=1, sticky="w")
        
        # Removed REFRESH button to match baseline

        # 3. Actions & Status
        mon_f = ttk.LabelFrame(left_panel, text="📊 Monitor", padding="5")
        mon_f.grid(row=2, column=0, sticky="ew", pady=(0, 5))
        mon_f.columnconfigure((0,1), weight=1)
        
        ttk.Label(mon_f, textvariable=self.status_var, font=('Segoe UI', 8, 'bold')).grid(row=0, column=0, columnspan=2, sticky="w")
        self.progress_bar = ttk.Progressbar(mon_f, mode='determinate')
        self.progress_bar.grid(row=1, column=0, columnspan=2, sticky="ew", pady=2)
        
        bt = [("📂 T-LOAD", self.trigger_load_template, 2, 0), ("💾 T-SAVE", self.trigger_save_template, 2, 1),
              ("🛑 HALT", self.controller.halt_mission, 3, 0), ("▶️ RESUME", self.trigger_resume, 3, 1),
              ("📋 LOGS", self.trigger_view_logs, 4, 0), ("📁 FAILED", self.trigger_view_failed, 4, 1),
              ("❓ HELP", self._show_help_mission, 5, 0)]
        for text, cmd, r, c in bt:
            ttk.Button(mon_f, text=text, command=cmd, style='Accent.TButton').grid(row=r, column=c, pady=1, padx=1, sticky="ew")

        # 4. Mission Aesthetics (Theme)
        theme_f = ttk.LabelFrame(left_panel, text="🎨 Aesthetics", padding="5")
        theme_f.grid(row=4, column=0, sticky="ew", pady=5)
        
        theme_cb = ttk.Combobox(theme_f, textvariable=self.theme_var, state="readonly")
        theme_cb['values'] = self.controller.get_available_themes()
        theme_cb.pack(fill="x", pady=2)
        theme_cb.bind("<<ComboboxSelected>>", lambda e: self.controller.change_theme(self.theme_var.get()))

        # 4. Activity Log
        l_f = ttk.LabelFrame(left_panel, text="📜 Activity Log", padding="5")
        l_f.grid(row=3, column=0, sticky="nsew")
        l_f.columnconfigure(0, weight=1); l_f.rowconfigure(0, weight=1); left_panel.rowconfigure(3, weight=1)
        self.log_text = scrolledtext.ScrolledText(l_f, wrap=tk.WORD, font=('Consolas', 8), bg='#D3D3D3', height=8)
        self.log_text.grid(row=0, column=0, sticky="nsew")

    def _setup_composition_area(self):
        right_panel = ttk.Frame(self.main_frame, padding="3")
        right_panel.grid(row=1, column=1, sticky="nsew")
        right_panel.columnconfigure(0, weight=10); right_panel.rowconfigure(2, weight=1)
        
        # 1. Strip
        tx_f = ttk.LabelFrame(right_panel, text="📡 Transmission Control", padding="3")
        tx_f.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 3))
        tx_f.columnconfigure((1,3,6), weight=1)
        
        ttk.Label(tx_f, text="From:").grid(row=0, column=0, padx=2)
        self.from_email_combo = ttk.Combobox(tx_f)
        self.from_email_combo.grid(row=0, column=1, sticky="ew")
        
        ttk.Label(tx_f, text="To:").grid(row=0, column=2, padx=2)
        ttk.Label(tx_f, textvariable=self.recipient_file_var, font=('Segoe UI', 8, 'italic')).grid(row=0, column=3, sticky="ew")
        ttk.Button(tx_f, text="📎 LOAD", command=self.trigger_load_recipients, style='Accent.TButton').grid(row=0, column=4, padx=2)
        
        ttk.Checkbutton(tx_f, text="CC", variable=self.cc_var, command=self.on_cc_toggle).grid(row=0, column=5, padx=5)
        ttk.Label(tx_f, textvariable=self.cc_info_var).grid(row=0, column=6, sticky="ew")
        ttk.Button(tx_f, text="📑 LIST", command=self.trigger_show_participant_list, style='Accent.TButton').grid(row=0, column=7, padx=2)
        ttk.Button(tx_f, textvariable=self.attach_status_var, command=self.trigger_add_attachments, style='Accent.TButton').grid(row=0, column=8, padx=2)
        ttk.Button(tx_f, text="🗑️", command=self.trigger_clear_attachments, width=3).grid(row=0, column=9, padx=2)

        # 2. Subject & Launch
        sub_f = ttk.LabelFrame(right_panel, text="📌 Subject", padding="3")
        sub_f.grid(row=1, column=0, sticky="ew", pady=(0, 3))
        sub_f.columnconfigure(0, weight=1)
        
        bt_f = ttk.Frame(sub_f)
        bt_f.pack(side="right", fill="y", padx=5)
        ttk.Button(bt_f, text="🔍 PREVIEW", command=self.trigger_preview, style='Accent.TButton').pack(fill="x", expand=True)

        ttk.Entry(sub_f, textvariable=self.subject_var, font=('Segoe UI', 11)).pack(fill="x", expand=True)
        
        l_cont = tk.Frame(right_panel, bg='#FF0000', width=118, bd=0)
        l_cont.grid(row=1, column=1, sticky="nsew", padx=(3, 0), pady=(0, 3))
        l_cont.grid_propagate(False)
        l_inner = tk.Frame(l_cont, bg=self.colors['bg'], bd=0)
        l_inner.pack(fill="both", expand=True, padx=4, pady=4)
        
        self.send_btn = RoundedButton(l_inner, text="🚀 LAUNCH", command=self.trigger_launch, bg=self.colors['text'], 
                                      fg='#000000', width=110, height=50, corner_radius=12)
        self.send_btn.pack(fill="both", expand=True)

        # 3. Editor
        body_frame = ttk.LabelFrame(right_panel, text="✉️ Email Body (HTML Enabled)", padding="3")
        body_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(0, 3))
        body_frame.columnconfigure(0, weight=1); body_frame.rowconfigure(1, weight=1)
        
        # Create the actual Text widget
        self.editor = scrolledtext.ScrolledText(body_frame, wrap=tk.WORD, font=('Segoe UI', 11))
        self.editor.grid(row=1, column=0, sticky="nsew")
        
        # Bridge with Rich Logic if available
        if RICH_TEXT_AVAILABLE:
            try:
                self.rich_editor = RichTextEditor(
                    self.root, 
                    self.editor, 
                    update_html_mode_callback=lambda: self.html_var.set(True),
                    log_callback=self.append_to_log,
                    attach_callback=self.trigger_add_attachments,
                    attach_mgr_callback=self.trigger_view_attachments, # Dummy for now
                    attach_status_var=self.attach_status_var,
                    theme_callback=lambda t: self.controller.change_theme(t)
                )
                # Add toolbar to UI
                self.rich_editor.create_toolbar(body_frame).grid(row=0, column=0, sticky="ew", pady=(0, 5))
            except Exception as e:
                print(f"Rich editor integration failed: {e}")
                self.rich_editor = None
        else:
            self.rich_editor = None

    def trigger_show_participant_list(self):
        """Hierarchy level 4: Tactical Participant Review Popup."""
        if not self.model.recipients:
            messagebox.showwarning("No Data", "No participants loaded.")
            return

        list_win = tk.Toplevel(self.root)
        list_win.title("Tactical Participant Manifest")
        list_win.geometry("600x400")
        list_win.configure(bg=self.colors['bg'])

        container = ttk.Frame(list_win, padding="15")
        container.pack(fill="both", expand=True)

        list_frame = ttk.Frame(container)
        list_frame.pack(fill="both", expand=True)

        cols = ('index', 'email', 'name')
        tree = ttk.Treeview(list_frame, columns=cols, show='headings', height=10)
        tree.heading('index', text='#')
        tree.heading('email', text='Email Address')
        tree.heading('name', text='Target Name')
        
        tree.column('index', width=40); tree.column('email', width=250); tree.column('name', width=200)
        
        sb = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side='left', fill='both', expand=True)
        sb.pack(side='right', fill='y')

        for i, r in enumerate(self.model.recipients):
            tree.insert('', 'end', values=(i+1, r.get('email', 'N/A'), r.get('name', 'Customer')))

    def append_to_log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def trigger_resume(self, path=None):
        """Action handler for Mission Resume."""
        if not path:
             # Manual selection if path not provided by auto-recovery
             checkpoints = self.controller.check_for_checkpoints()
             if not checkpoints:
                 messagebox.showinfo("System", "No active recovery points found.")
                 return
             # Logic to show selector would go here, for now use latest
             path = max(checkpoints, key=lambda p: p.stat().st_mtime)
             
        if self.controller.resume_mission_from_file(path):
            self._sync_ui_to_model()
            messagebox.showinfo("Recovery", f"Mission primed at Email #{self.model.resume_index + 1}")
            # Automatically trigger launch if user confirms
            if messagebox.askyesno("Launch", "Resume transmission now?"):
                self.trigger_launch(start_idx=self.model.resume_index)

    def trigger_launch(self, start_idx=0):
        # Update model before handoff
        self.model.subject = self.subject_var.get().strip()
        if self.rich_editor and hasattr(self.rich_editor, 'generate_html'):
            self.model.body = self.rich_editor.generate_html().strip()
        else:
            self.model.body = self.editor.get('1.0', tk.END).strip()
            
        err = self.controller.start_mission(
            sender_email=self.from_email_combo.get(), 
            password=self.password_var.get(),
            attachments=self.model.attachments,
            start_idx=start_idx
        )
        if err: messagebox.showwarning("System Check", err)

    def trigger_add_attachments(self):
        """Action handler for adding files."""
        files = filedialog.askopenfilenames(title="Attach Tactical Assets")
        if files:
            self.model.attachments.extend(files)
            self.attach_status_var.set(f"📎 {len(self.model.attachments)} files")
            self.append_to_log(f"📎 Added {len(files)} asset(s) to transmission manifest.")

    def trigger_clear_attachments(self):
        """Standardized cleanup."""
        self.model.attachments = []
        self.attach_status_var.set("📎 0 files")
        self.append_to_log("🗑️ Attachment manifest cleared.")

    def trigger_save_template(self):
        """Action handler for Template Save (User Requirement: Open Path)."""
        name = simpledialog.askstring("Save Template", "Enter mission template name:")
        if not name: return
        
        subject = self.subject_var.get()
        if self.rich_editor and hasattr(self.rich_editor, 'generate_html'):
            body = self.rich_editor.generate_html()
        else:
            body = self.editor.get('1.0', tk.END)
            
        path = self.controller.save_template(name, subject, body, self.html_var.get())
        if path and sys.platform == 'win32':
             os.startfile(path)
             messagebox.showinfo("Tactical Success", f"Template '{name}' archived.")

    def trigger_load_template(self):
        """Action handler for Template Load (User Requirement: Open Path)."""
        template_dir = self.controller.repo.dirs['exports'] / "templates"
        if template_dir.exists() and sys.platform == 'win32':
             os.startfile(template_dir)
             
        filename = filedialog.askopenfilename(
            initialdir=template_dir,
            title="Load Tactical Template",
            filetypes=[("JSON Mission", "*.json"), ("All Files", "*.*")]
        )
        if not filename: return
        
        template = self.controller.load_template(filename)
        if template:
            self.subject_var.set(template.get('subject', ''))
            self.html_var.set(template.get('html', False))
            body = template.get('body', '')
            if self.rich_editor:
                # Assuming RichTextEditor has a set_body method or similar
                # From monolith, set_body_content was used on self.rich_editor
                if hasattr(self.rich_editor, 'set_body_content'):
                    self.rich_editor.set_body_content(body)
                else:
                    self.editor.delete('1.0', tk.END)
                    self.editor.insert('1.0', body)
            else:
                self.editor.delete('1.0', tk.END)
                self.editor.insert('1.0', body)

    def trigger_load_recipients(self):
        """Action handler for Recipient Loading."""
        filename = filedialog.askopenfilename(
            title="Select Recipients File",
            filetypes=[("CSV Tables", "*.csv"), ("TXT Targets", "*.txt"), ("All Files", "*.*")]
        )
        if filename:
            if self.controller.load_recipients(filename):
                self.recipient_file_var.set(self.model.recipient_file)

    def trigger_save_account(self):
        """Delegate security storage to controller."""
        email = self.account_email_var.get()
        password = self.password_var.get()
        if self.controller.save_account(email, password):
            messagebox.showinfo("Security", "Tactical credentials saved.")
            self._update_account_combos()

    def trigger_test_login(self):
        """Standardized Login Test Launcher (Gap 3)."""
        email = self.account_email_var.get()
        password = self.password_var.get()
        success, msg = self.controller.test_login(email, password)
        if success:
            messagebox.showinfo("Tactical Success", "Authentication parameters verified.")
        else:
            messagebox.showerror("Auth Failure", msg)

    def trigger_view_logs(self):
        """Action handler for View Logs."""
        if not self.controller.view_logs():
            messagebox.showwarning("System", "Log file not yet initialized.")

    def trigger_view_failed(self):
        """Action handler for Failed Manifest management."""
        fail_dir = self.repo.dirs['logs'] / "failed"
        fail_dir.mkdir(exist_ok=True)
        
        if messagebox.askyesno("Tactical Failed Manifest", "Would you like to open the FAILED folder?\n\n(Choose 'No' to select a manifest for RETRY ONLY FAILED)"):
             self.controller.view_failed_folder()
        else:
             filename = filedialog.askopenfilename(
                 initialdir=fail_dir,
                 title="Select Failure Manifest for Retry",
                 filetypes=[("CSV Tables", "*.csv"), ("All Files", "*.*")]
             )
             if filename:
                 if self.controller.retry_failed(filename):
                     self.recipient_file_var.set(self.model.recipient_file)

    def trigger_preview(self):
        """Action handler for Mission Preview."""
        subject = self.subject_var.get()
        if self.rich_editor and hasattr(self.rich_editor, 'generate_html'):
            body = self.rich_editor.generate_html()
        else:
            body = self.editor.get('1.0', tk.END)
        self.controller.show_preview(subject, body)

    def on_cc_toggle(self):
        """Sync UI CC toggle with mission model."""
        self.controller.on_cc_toggle(self.cc_var.get())

    def _on_account_selected(self, event=None):
        email = self.account_email_var.get()
        if email in self.model.accounts:
            self.password_var.set(self.model.accounts[email])

    def _update_account_combos(self):
        emails = list(self.model.accounts.keys())
        self.account_email_combo['values'] = emails
        self.from_email_combo['values'] = emails

    def _sync_ui_to_model(self):
        self.subject_var.set(self.model.subject)
        self.hud_status_var.set(self.model.hud_status)
        self.from_email_combo.set(self.model.sender_email)
        self.theme_var.set(self.model.current_theme_name)
        self._update_account_combos()
        # Restore editor content
        if self.model.body:
            if self.rich_editor and hasattr(self.rich_editor, 'set_body_content'):
                self.rich_editor.set_body_content(self.model.body)
            else:
                self.editor.delete('1.0', tk.END)
                self.editor.insert('1.0', self.model.body)

    def _show_help_mission(self):
        """Displays the tactical mission handbook with operational steps."""
        help_win = tk.Toplevel(self.root)
        help_win.title("TACTICAL INTELLIGENCE: MISSION HANDBOOK")
        help_win.geometry("750x600")
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
        ]

        for title, color in steps:
            tag = f"tag_{color.replace('#','')}"
            txt.tag_configure(tag, foreground=color)
            if "AUTHENTICATION" in title or "2." in title or "3." in title or "4." in title or "5." in title or "6." in title or "7." in title:
                 txt.tag_configure(tag, font=('Segoe UI', 11, 'bold'))
            txt.insert(tk.END, title + "\n", tag)

        txt.config(state='disabled')
        ttk.Button(help_win, text="CONFIRM & CLOSE", command=help_win.destroy, style='Accent.TButton').pack(pady=10)
                
    def trigger_view_attachments(self):
        """Dummy for now, will implement attachment manager view later if needed."""
        messagebox.showinfo("Attachments", f"Manifest contains {len(self.model.attachments)} files.")
