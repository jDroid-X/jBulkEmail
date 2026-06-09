from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class MissionModel:
    """
    Model Layer for jBulkEmailSender.
    Represents the active state of an email mission.
    """
    # UI Variables
    subject: str = ""
    body: str = ""
    sender_email: str = ""
    recipient_file: str = "No file"
    hud_status: str = "IDLE"
    progress_val: int = 0
    total_recipients: int = 0
    
    # Core Data
    recipients: List[Dict] = field(default_factory=list)
    delay: float = 1.0
    batch_size: int = 50
    is_html: bool = False
    is_personalize: bool = True
    attachments: List[str] = field(default_factory=list)
    cc_mode: bool = False
    
    # Persistence
    config_data: Dict = field(default_factory=dict)
    accounts: Dict = field(default_factory=dict)
    
    # Runtime State
    is_sending: bool = False
    sent_count: int = 0
    failed_list: List[Dict] = field(default_factory=list)
    current_theme_name: str = "Neural Void (Future)"

    def to_dict(self):
        """Convert model to dictionary for persistence/reloading."""
        return {
            'subject': self.subject,
            'body': self.body,
            'sender': self.sender_email,
            'recipient_file': self.recipient_file,
            'recipients': self.recipients,
            'delay': self.delay,
            'batch_size': self.batch_size,
            'html_mode': self.is_html,
            'personalize': self.is_personalize,
            'attachments': self.attachments,
            'cc_mode': self.cc_mode,
            'current_theme': self.current_theme_name
        }

    def update_from_dict(self, data):
        """Populate model from dictionary (e.g., from reload_state)."""
        self.subject = data.get('subject', self.subject)
        self.body = data.get('body', self.body)
        self.sender_email = data.get('sender', self.sender_email)
        self.recipient_file = data.get('recipient_file', self.recipient_file)
        self.recipients = data.get('recipients', self.recipients)
        self.delay = data.get('delay', self.delay)
        self.batch_size = data.get('batch_size', self.batch_size)
        self.is_html = data.get('html_mode', self.is_html)
        self.is_personalize = data.get('personalize', self.is_personalize)
        self.attachments = data.get('attachments', self.attachments)
        self.cc_mode = data.get('cc_mode', self.cc_mode)
        self.current_theme_name = data.get('current_theme', self.current_theme_name)
