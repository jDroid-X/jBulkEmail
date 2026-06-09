import smtplib
import threading
import time
import re
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders

class SmtpService:
    """
    Service Layer for SMTP Operations.
    Handles email transmission, provider selection, and threading logic.
    """
    
    SMTP_PROVIDERS = {
        "Gmail":   {"host": "smtp.gmail.com",      "port": 587, "url": "https://myaccount.google.com/apppasswords"},
        "Outlook": {"host": "smtp.office365.com",  "port": 587, "url": "https://account.microsoft.com/security"},
        "Yahoo":   {"host": "smtp.mail.yahoo.com", "port": 587, "url": "https://login.yahoo.com/account/security"},
        "Zoho":    {"host": "smtp.zoho.com",        "port": 465, "url": "https://accounts.zoho.com/u/h#setting/clientapps"},
        "iCloud":  {"host": "smtp.mail.me.com",    "port": 587, "url": "https://appleid.apple.com/account/manage"},
        "Hotmail": {"host": "smtp.live.com",       "port": 587, "url": "https://account.microsoft.com/security"},
        "Custom":  {"host": None, "port": None, "url": None}
    }

    DOMAIN_MAP = {
        'gmail.com': 'Gmail',     'googlemail.com': 'Gmail',
        'outlook.com': 'Outlook', 'hotmail.com': 'Outlook',
        'live.com': 'Outlook',    'msn.com': 'Outlook',
        'yahoo.com': 'Yahoo',     'ymail.com': 'Yahoo',
        'zoho.com': 'Zoho',
        'icloud.com': 'iCloud',   'me.com': 'iCloud', 'mac.com': 'iCloud',
    }

    def __init__(self, callback_log=None, callback_progress=None, callback_status=None):
        self.callback_log = callback_log
        self.callback_progress = callback_progress
        self.callback_status = callback_status
        self.is_sending = False
        self._stop_event = threading.Event()

    def halt(self):
        self._stop_event.set()
        self.is_sending = False
        self._log("🛑 MISSION HALT SIGNAL SENT.")

    def run_mission_thread(self, sender_email, password, recipients, subject, body_template, 
                          delay=1.0, batch_size=50, is_html=False, personalize=True, 
                          attachments=None, cc_mode=False, start_idx=0):
        """Wrapper to run mission in a background thread."""
        thread = threading.Thread(
            target=self.send_mission, 
            args=(sender_email, password, recipients, subject, body_template, 
                  delay, batch_size, is_html, personalize, attachments, cc_mode, start_idx),
            daemon=True
        )
        thread.start()
        return thread

    def send_mission(self, sender_email, password, recipients, subject, body_template, 
                     delay=1.0, batch_size=50, is_html=False, personalize=True, 
                     attachments=None, cc_mode=False, start_idx=0):
        """Main mission loop for sending bulk emails."""
        self._stop_event.clear()
        self.is_sending = True
        self._update_status("LAUNCHING")
        
        sent = start_idx
        failed = []
        total = len(recipients)
        
        provider_name = self._detect_provider(sender_email)
        provider_info = self.SMTP_PROVIDERS.get(provider_name, self.SMTP_PROVIDERS['Custom'])
        host = provider_info['host']
        port = provider_info['port']
        
        if not host:
            self._log(f"❌ ERROR: SMTP Host not detected for {sender_email}")
            self._update_status("FAILED_HOST")
            return

        try:
            self._log(f"🔗 Establishing Secure Connection to {host}...")
            server = smtplib.SMTP(host, port)
            server.starttls()
            server.login(sender_email, password)
            self._log(f"🔐 Authentication Successful as {sender_email}")
            self._update_status("IN_FLIGHT")

            for i in range(start_idx, total):
                if self._stop_event.is_set():
                    break
                
                recipient = recipients[i]
                email_addr = recipient.get('email', '')
                try:
                    msg = self._craft_message(sender_email, recipient, subject, body_template, 
                                             is_html, personalize, attachments, cc_mode)
                    
                    server.send_message(msg)
                    sent += 1
                    self._log(f"✅ [{sent}/{total}] Transmission Success: {email_addr}")
                    
                    if self.callback_progress:
                        self.callback_progress(sent, total)
                    
                    # Tactical delay
                    if delay > 0:
                        time.sleep(delay)
                        
                except Exception as e:
                    failed.append((recipient, str(e)))
                    self._log(f"❌ Transmission Error {email_addr}: {e}")
                    
            server.quit()
        except Exception as e:
            self._log(f"🚨 ENGINE FAILURE: {e}")
            self._update_status("CRITICAL_ERROR")
            return
        finally:
            self.is_sending = False
            self._update_status("MISSION_COMPLETE" if sent == total else "HALTED")
        
        return {'sent': sent, 'failed': failed, 'total': total}

    def test_connection(self, sender_email, password):
        """Standardized Login Test (Gap 3: Security)."""
        provider_name = self._detect_provider(sender_email)
        provider_info = self.SMTP_PROVIDERS.get(provider_name, self.SMTP_PROVIDERS['Custom'])
        
        try:
            server = smtplib.SMTP(provider_info['host'], provider_info['port'])
            server.starttls()
            server.login(sender_email, password)
            server.quit()
            return True, "Login Successful"
        except Exception as e:
            return False, str(e)

    def _detect_provider(self, email):
        domain = email.split('@')[-1].lower()
        return self.DOMAIN_MAP.get(domain, 'Custom')

    def _craft_message(self, sender, recipient, subject, body, is_html, personalize, attachments, cc_mode):
        name = recipient.get('name', 'Customer')
        email_addr = recipient.get('email', '')
        
        if personalize:
            subject = re.sub(r'\{name\}', name, subject, flags=re.IGNORECASE)
            subject = re.sub(r'\{email\}', email_addr, subject, flags=re.IGNORECASE)
            body = re.sub(r'\{name\}', name, body, flags=re.IGNORECASE)
            body = re.sub(r'\{email\}', email_addr, body, flags=re.IGNORECASE)
            
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = email_addr
        msg['Subject'] = subject
        
        if cc_mode:
            # Handle CC logic if recipient has cc_emails field
            cc_emails = recipient.get('cc_emails', '')
            if cc_emails:
                msg['Cc'] = cc_emails

        subtype = 'html' if is_html else 'plain'
        
        # Phase 11.7: Tactical Mission Branding (Watermark & Floating Shadow)
        if is_html:
            # Wrap the body in a mission-branded container
            styled_body = f"""
            <div style="background-image: url('cid:mission_icon'); 
                         background-repeat: no-repeat; 
                         background-position: center center; 
                         background-size: contain; 
                         background-attachment: fixed;
                         min-height: 400px; padding: 20px;
                         ">
                <div style="text-shadow: 2px 2px 4px rgba(0,0,0,0.3); 
                            font-family: 'Segoe UI', Arial, sans-serif;
                            font-size: 11pt; color: #000000;
                            ">
                    {body}
                </div>
            </div>
            """
            msg.attach(MIMEText(styled_body, subtype))
            
            # Embed the mission icon as the watermark source
            icon_path = os.path.join("assets", "mission_icon.png")
            if os.path.exists(icon_path):
                try:
                    with open(icon_path, 'rb') as f:
                        img = MIMEImage(f.read())
                        img.add_header('Content-ID', '<mission_icon>')
                        img.add_header('Content-Disposition', 'inline', filename='branding.png')
                        msg.attach(img)
                except Exception as e:
                    self._log(f"⚠️ Branding Attachment Error: {e}")
        else:
            msg.attach(MIMEText(body, subtype))
        
        if attachments:
            for path in attachments:
                if not os.path.exists(path): continue
                if os.path.basename(path) == "mission_icon.png": continue # Skip redundant icon
                try:
                    with open(path, "rb") as f:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(path)}")
                    msg.attach(part)
                except Exception as e:
                    self._log(f"⚠️ Attachment Error ({os.path.basename(path)}): {e}")
                
        return msg

    def _log(self, msg):
        if self.callback_log:
            self.callback_log(msg)

    def _update_status(self, status):
        if self.callback_status:
            self.callback_status(status)
