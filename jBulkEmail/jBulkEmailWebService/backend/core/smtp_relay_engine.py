import time
import os
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from datetime import datetime
import asyncio
from typing import List, Dict, Callable

from .zip_manager import ZipManager
from .api_relay_engine import APIRelayEngine
from .email_check import EmailChecker

SMTP_PROVIDERS = {
    "Gmail":   {"host": "smtp.gmail.com",      "port": 587},
    "Outlook": {"host": "smtp.office365.com",  "port": 587},
    "Yahoo":   {"host": "smtp.mail.yahoo.com", "port": 587},
    "Zoho":    {"host": "smtp.zoho.com",        "port": 465},
    "iCloud":  {"host": "smtp.mail.me.com",    "port": 587},
}

class WebRelayEngine:
    def __init__(self, log_callback: Callable[[str], None], progress_callback: Callable[[int, str], None]):
        self.log_callback = log_callback
        self.progress_callback = progress_callback
        self.is_sending = False
        self.current_filename = "web_session"

    def _smtp_connect(self, email, password):
        # Auto resolve provider
        domain = email.split('@')[-1].lower()
        provider = "Gmail" # Default fallback
        
        # Simple domain mapping
        mapping = {
            'gmail.com': 'Gmail', 'googlemail.com': 'Gmail',
            'outlook.com': 'Outlook', 'hotmail.com': 'Outlook',
            'yahoo.com': 'Yahoo', 'zoho.com': 'Zoho', 'icloud.com': 'iCloud'
        }
        for k, v in mapping.items():
            if k in domain:
                provider = v
                break
                
        config = SMTP_PROVIDERS.get(provider, SMTP_PROVIDERS["Gmail"])
        host, port = config["host"], config["port"]
        
        self.log_callback(f"Connecting to SMTP {host}:{port} for {email}...")
        
        if port == 465:
            server = smtplib.SMTP_SSL(host, port, timeout=15)
        else:
            server = smtplib.SMTP(host, port, timeout=15)
            server.starttls()
            
        server.login(email, password)
        self.log_callback(f"Authenticated SMTP connection established.")
        return server

    def _smtp_send_with_retry(self, server, msg, account_pair, max_retries=2):
        for attempt in range(max_retries + 1):
            try:
                server.send_message(msg)
                return server
            except Exception as e:
                self.log_callback(f"⚠️ SMTP Send attempt {attempt+1} failed: {e}")
                if attempt < max_retries:
                    try: server.quit()
                    except: pass
                    time.sleep(2)
                    server = self._smtp_connect(*account_pair)
                else:
                    raise e
        return server

    async def execute_mission(
        self,
        recipients: List[Dict],
        sender_email: str,
        app_password: str,
        sendgrid_key: str,
        subject_template: str,
        body_template: str,
        attachments: List[str], # Local temporary paths
        delay: float = 1.0,
        batch_size: int = 50,
        batch_pause: float = 60.0,
        personalize: bool = True,
        html_mode: bool = True
    ):
        self.is_sending = True
        total = len(recipients)
        sent = 0
        failed_list = []
        server = None
        account_pair = (sender_email, app_password)

        try:
            # Pre-process attachments
            pre_processed_attachments = []
            api_attachments = []
            for file_path in attachments:
                try:
                    p = Path(file_path).absolute()
                    # In-memory compression
                    zip_name, file_data, is_zipped = ZipManager.compress_to_memory(str(p), threshold_mb=1.0)
                    api_attachments.append({'filename': zip_name, 'data': file_data})

                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(file_data)
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename="{zip_name}"')
                    pre_processed_attachments.append(part)
                    
                    comp_msg = " [ZIPPED]" if is_zipped else ""
                    self.log_callback(f"📦 Pre-encoded: {zip_name} ({len(file_data)/1024:.0f} KB){comp_msg}")
                except Exception as ae:
                    self.log_callback(f"⚠️ Attachment error {file_path}: {ae}")

            r_name = re.compile(re.escape('{name}'), re.IGNORECASE)
            r_email = re.compile(re.escape('{email}'), re.IGNORECASE)

            # Establish initial connection if not using API Relay exclusively
            if not sendgrid_key:
                server = self._smtp_connect(*account_pair)

            for idx in range(total):
                if not self.is_sending:
                    self.log_callback("⚠️ Sending halted by user.")
                    break

                steps = idx
                # Connection refresh boundary
                if not sendgrid_key and steps > 0 and steps % 10 == 0:
                    try: server.quit()
                    except: pass
                    self.log_callback(f"🔄 Connection Refresh — Rotating SMTP connector.")
                    try:
                        server = self._smtp_connect(*account_pair)
                    except Exception as stop_e:
                        self.log_callback(f"⚠️ Connection refresh failed ({stop_e}) — retrying")
                        try:
                            server = self._smtp_connect(*account_pair)
                        except Exception as stop_e2:
                            self.log_callback(f"❌ Aborting mission: {stop_e2}")
                            break

                # Batch Pause
                if steps > 0 and steps % batch_size == 0:
                    self.log_callback(f"⏸️ Batch safety pause ({batch_pause:.0f}s)...")
                    await asyncio.sleep(batch_pause)

                # Stream progress
                progress = int(((idx + 1) / total) * 100)
                self.progress_callback(progress, f"Sending {idx+1}/{total}...")

                recipient = recipients[idx]
                success = False
                t_build = 0.0
                t_send = 0.0

                try:
                    s_build = time.time()
                    msg = MIMEMultipart()
                    msg['From'] = sender_email
                    msg['To'] = recipient['email'].replace(';', ',')
                    if recipient.get('cc_emails'):
                        msg['Cc'] = recipient['cc_emails'].replace(';', ',')

                    subject = subject_template
                    body_content = body_template

                    if personalize:
                        name = recipient.get('name', 'Customer')
                        email_addr = recipient.get('email', '')
                        subject = r_name.sub(name, subject)
                        subject = r_email.sub(email_addr, subject)
                        body_content = r_name.sub(name, body_content)
                        body_content = r_email.sub(email_addr, body_content)

                    msg['Subject'] = subject

                    is_html = html_mode or any(tag in body_content.lower() for tag in ('<html>', '<body>', '<p>'))
                    if is_html:
                        styled_body = f"""
                        <div style="font-family: 'Segoe UI', Arial, sans-serif;
                                     font-size: 12pt; color: #000000;
                                     line-height: 1.6; padding: 20px;">
                            {body_content}
                        </div>
                        """
                        msg.attach(MIMEText(styled_body, 'html'))
                    else:
                        msg.attach(MIMEText(body_content, 'plain'))

                    for part in pre_processed_attachments:
                        msg.attach(part)
                    t_build = time.time() - s_build

                    # Transmission phase
                    s_send = time.time()
                    api_sent = False

                    if sendgrid_key:
                        try:
                            engine = APIRelayEngine(api_key=sendgrid_key)
                            engine.send_via_sendgrid(
                                sender_email=sender_email,
                                to_email=recipient['email'].replace(';', ','),
                                subject=subject,
                                body=styled_body if is_html else body_content,
                                attachments=api_attachments,
                                is_html=is_html
                            )
                            api_sent = True
                            t_send = time.time() - s_send
                            self.log_callback(f"✉️ [API RELAY] Sent {idx+1}/{total} → {recipient['email']} [Build:{t_build:.2f}s | Data:{t_send:.2f}s]")
                        except Exception as api_err:
                            self.log_callback(f"⚠️ API Relay failed: {api_err}. Falling back to SMTP.")

                    if not api_sent:
                        server = self._smtp_send_with_retry(server, msg, account_pair)
                        t_send = time.time() - s_send
                        self.log_callback(f"✉️ [SMTP] Sent {idx+1}/{total} → {recipient['email']} [Build:{t_build:.2f}s | Data:{t_send:.2f}s]")

                    success = True
                    sent += 1

                except Exception as e:
                    err_msg = str(e)
                    failed_list.append({'email': recipient['email'], 'name': recipient.get('name', ''), 'error': err_msg})
                    self.log_callback(f"❌ Failed → {recipient['email']}: {err_msg}")

                if success and idx < total - 1:
                    await asyncio.sleep(delay)

        finally:
            if server:
                try: server.quit()
                except: pass
            self.is_sending = False
            self.progress_callback(100, "Mission Concluded.")
            return sent, failed_list
