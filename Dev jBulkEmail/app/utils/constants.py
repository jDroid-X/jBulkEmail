"""
Constants and Shared Mappings for jBulkEmailSender.
Centralized repository for UI strings, colors, and SMTP settings.
"""

# --- Mission Aesthetics (Dynamic Design tokens) ---
MISSION_COLORS = {
    'bg': '#808080',       # Mission Control Grey
    'panel': '#4D4D4D',    # Card Grey
    'aqua': '#00E5FF',     # Electric Aqua
    'glow': '#00B8D4',     # Deep Aqua
    'text': '#FFD700',     # Command Gold
    'white': '#FFFFFF',
    'border': '#94D2BD',
    'dark_blue': '#0B132B' # Foundation Theme
}

# --- Transmission Constants ---
SMTP_PROVIDERS = {
    "Gmail":   {"host": "smtp.gmail.com",      "port": 587, "url": "https://myaccount.google.com/apppasswords"},
    "Outlook": {"host": "smtp.office365.com",  "port": 587, "url": "https://account.microsoft.com/security"},
    "Yahoo":   {"host": "smtp.mail.yahoo.com", "port": 587, "url": "https://login.yahoo.com/account/security"},
    "Zoho":    {"host": "smtp.zoho.com",        "port": 465, "url": "https://accounts.zoho.com/u/h#setting/clientapps"},
    "iCloud":  {"host": "smtp.mail.me.com",    "port": 587, "url": "https://appleid.apple.com/account/manage"},
    "Hotmail": {"host": "smtp.live.com",       "port": 587, "url": "https://account.microsoft.com/security"},
}

DOMAIN_TO_PROVIDER = {
    'gmail.com': 'Gmail',     'googlemail.com': 'Gmail',
    'outlook.com': 'Outlook', 'hotmail.com': 'Outlook',
    'live.com': 'Outlook',    'msn.com': 'Outlook',
    'yahoo.com': 'Yahoo',     'ymail.com': 'Yahoo',
    'zoho.com': 'Zoho',
    'icloud.com': 'iCloud',   'me.com': 'iCloud', 'mac.com': 'iCloud',
}

# --- UI Strings & HUD Status ---
HUD_STATUS_IDLE = "IDLE"
HUD_STATUS_READY = "READY_TO_LAUNCH"
HUD_STATUS_RECOVERY = "RECOVERY_ARMED"
HUD_STATUS_SENDING = "IN_FLIGHT"
HUD_STATUS_HALTED = "MISSION_ABORTED"
HUD_STATUS_COMPLETE = "MISSION_COMPLETE"

# --- Default Config ---
DEFAULT_CONFIG = {
    'delay': 1.0,
    'batch_size': 50,
    'current_theme': "Neural Void (Future)"
}
