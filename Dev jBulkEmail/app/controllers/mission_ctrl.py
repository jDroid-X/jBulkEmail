import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path
from app.utils.themes import ThemeManager
from app.utils.previewer import HtmlPreviewer

class MissionController:
    """
    Controller Layer for jBulkEmailSender.
    Orchestrates logic between UI, Services, and Models.
    """
    def __init__(self, model, service, repo, root):
        self.model = model
        self.service = service
        self.repo = repo
        self.root = root # For root.after() UI thread safety
        self.theme_mgr = ThemeManager(self.repo.dirs['assets'] if hasattr(self.repo, 'dirs') else "assets")
        self.previewer = HtmlPreviewer(root)
        
        # Link service callbacks to model and disk via controller (Bridge Gap 2)
        self.service.callback_progress = self._on_service_progress
        self.service.callback_log = self._on_service_log
        self.service.callback_status = self._on_service_status

    def start_mission(self, sender_email, password, attachments=None, start_idx=0):
        """Prepare and start mission in background (Gap 2: Threading)."""
        if self.model.is_sending: return "Mission already in flight."
        
        # Gap 15: Single Source of Truth Validation
        if not self.model.recipients or not self.model.subject or not self.model.body:
            return "Incomplete Data: Please load recipients and compose your message."
            
        # Update Model State
        self.model.is_sending = True
        self.model.sender_email = sender_email
        self.model.attachments = attachments if attachments else []
        self.model.sent_count = start_idx
        self.model.failed_list = []

        # Launch Service In Thread (Gap 2)
        self.service.run_mission_thread(
            sender_email=sender_email, 
            password=password, 
            recipients=self.model.recipients, 
            subject=self.model.subject, 
            body_template=self.model.body, 
            delay=self.model.delay,
            batch_size=self.model.batch_size,
            is_html=self.model.is_html,
            personalize=self.model.is_personalize,
            attachments=self.model.attachments,
            cc_mode=self.model.cc_mode,
            start_idx=start_idx
        )
        return None # Success

    def halt_mission(self):
        """Request the service to stop (Gap 13: Chosen Choice Path)."""
        self.service.halt()
        self.model.is_sending = False
        self.model.hud_status = "ABORT_PENDING"

    def change_theme(self, theme_name):
        """Action handler for Theme Sync (Gap 35)."""
        if theme_name in self.theme_mgr.themes:
            self.model.current_theme_name = theme_name
            self.theme_mgr.apply_to_root(self.root, theme_name)
            
            # Persist back to config
            config = self.repo.load_config()
            if config:
                config['current_theme'] = theme_name
                self.repo.save_config(config)
            self._on_service_log(f"🎨 Theme switched to: {theme_name}")

    def get_available_themes(self):
        """Retrieve discovery list for UI."""
        return list(self.theme_mgr.themes.keys())

    # --- GAP FILLERS: Thread-Safe Bridge (root.after) ---

    def load_recipients(self, filename):
        """Bridge between UI and Disk for recipient data."""
        if not filename: return
        try:
            recipients = self.repo.load_recipients_file(filename)
            self.model.recipients = recipients
            self.model.recipient_file = Path(filename).name
            self.model.last_rec_path = Path(filename).resolve()
            self.model.total_recipients = len(recipients)
            self._on_service_log(f"✅ Loaded {len(recipients)} recipients from {self.model.recipient_file}")
            return True
        except Exception as e:
            self._on_service_log(f"❌ Failed to load recipients: {e}")
            return False

    def save_template(self, name, subject, body, is_html):
        """Capture current draft as a persistent template."""
        if not name: return
        template = {
            'subject': subject.strip(),
            'body': body.strip(),
            'html': is_html
        }
        template_dir = self.repo.dirs['exports'] / "templates"
        template_dir.mkdir(exist_ok=True)
        file_path = template_dir / f"{name}.json"
        
        try:
            import json
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2)
            self._on_service_log(f"💾 Template '{name}' saved.")
            return str(template_dir) # So View can open explorer
        except Exception as e:
            self._on_service_log(f"❌ Template Save Error: {e}")
            return None

    def load_template(self, filename):
        """Restore a saved template into the model."""
        if not filename: return
        try:
            import json
            with open(filename, 'r', encoding='utf-8') as f:
                template = json.load(f)
            self.model.subject = template.get('subject', '')
            self.model.body = template.get('body', '')
            self.model.is_html = template.get('html', False)
            self._on_service_log(f"✅ Loaded template: {Path(filename).name}")
            return template
        except Exception as e:
            self._on_service_log(f"❌ Template Load Error: {e}")
            return None

    def save_account(self, email, password):
        """Add credential to the secure repository."""
        if not email or not password: return False
        try:
            self.model.accounts = self.repo.save_account(email, password)
            self._on_service_log(f"🔐 Security credentials saved for {email}")
            return True
        except: return False

    def test_login(self, email, password):
        """Standardized Login Test (Gap 3: Security)."""
        if not email or not password: return False, "Missing Credentials"
        self._on_service_log(f"🧪 TESTING: Connection to {email}...")
        success, msg = self.service.test_connection(email, password)
        if success:
           self._on_service_log(f"✅ SUCCESS: {msg}")
        else:
           self._on_service_log(f"❌ FAILED: {msg}")
        return success, msg

    def view_logs(self):
        """Open the tactical mission log (User Req: Open Folder/File)."""
        log_file = self.repo.master_logs
        if log_file.exists() and sys.platform == 'win32':
             os.startfile(log_file)
             return True
        return False

    def view_failed_folder(self):
        """Open the failed recipient directory (User Req: Open Folder)."""
        fail_dir = self.repo.dirs['logs'] / "failed"
        fail_dir.mkdir(exist_ok=True)
        if sys.platform == 'win32':
             os.startfile(fail_dir)
             return True
        return False

    def retry_failed(self, file_path):
        """Reload failures into current mission model (Gap 41)."""
        if not file_path: return False
        recipients = self.repo.load_failed_recipients(file_path)
        if recipients:
            self.model.recipients = recipients
            self.model.recipient_file = f"RETRY: {Path(file_path).name}"
            self.model.total_recipients = len(recipients)
            self._on_service_log(f"🔄 RELOADED {len(recipients)} failures for re-mission.")
            return True
        return False

    def show_preview(self, subject, body):
        """Trigger tactical HTML preview."""
        self.previewer.show_preview(body, subject)

    def on_cc_toggle(self, enabled):
        """Handle CC bridge logic (Gap 14: CC Rules)."""
        self._on_service_log(f"⚙️ CC MODE: {'ACTIVE' if enabled else 'DISABLED'}")
        self.model.cc_mode = enabled

    def _on_service_progress(self, sent, total):
        """Callback from SmtpService (Bridge Gap 2)."""
        def update():
            self.model.sent_count = sent
            self.model.progress_val = int((sent / total) * 100) if total > 0 else 0

        self.root.after(0, update)

    def _on_service_log(self, message):
        """Centralized logging for View/Disk (Bridge Gap 2)."""
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        def update():
            # In actual implementation, we inform the view to append log
            if hasattr(self, 'view_callback_log'):
                self.view_callback_log(f"{timestamp} {message}")
            
        self.root.after(0, update)
        # Disk log doesn't need thread safety if file handles are handled properly
        os.environ['MASTER_LOG_TS'] = timestamp
        self.repo.append_master_log(message)

    def _on_service_status(self, status):
        """Update the HUB/Status in the model (Bridge Gap 2)."""
        def update():
            self.model.hud_status = status
            self._on_service_log(f"📡 System Status Change: {status}")
        self.root.after(0, update)
