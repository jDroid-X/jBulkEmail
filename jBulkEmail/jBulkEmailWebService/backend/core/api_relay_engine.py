try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

import json
import base64
class APIRelayEngine:
    """
    Phase 1 HTTP Relay Engine
    Bypasses port 25/587 blocking by routing outbound email traffic
    through REST APIs (SendGrid).
    """

    def __init__(self, provider="SendGrid", api_key=""):
        self.provider = provider
        self.api_key = api_key
        
    def send_via_sendgrid(self, sender_email, to_email, subject, body, attachments=None, is_html=False):
        """
        Constructs and dispatches the SendGrid v3 JSON payload.
        Returns True if successful, raises Exceptions on failure (including 429).
        """
        if not self.api_key:
            raise ValueError("SendGrid API Key is empty.")
            
        if not HAS_REQUESTS:
            raise RuntimeError("MISSING_DEPENDENCY: 'requests' module not installed.")

        url = "https://api.sendgrid.com/v3/mail/send"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        content_type = "text/html" if is_html else "text/plain"
        
        payload = {
            "personalizations": [
                {
                    "to": [{"email": to_email}]
                }
            ],
            "from": {"email": sender_email},
            "subject": subject,
            "content": [
                {"type": content_type, "value": body}
            ]
        }
        
        if attachments:
            payload["attachments"] = []
            # attachments should be list of dicts: {'filename': str, 'data': bytes, 'mime': str}
            for att in attachments:
                encoded_data = base64.b64encode(att['data']).decode('utf-8')
                payload["attachments"].append({
                    "content": encoded_data,
                    "filename": att['filename'],
                    "type": att.get('mime', 'application/octet-stream'),
                    "disposition": "attachment"
                })
                
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 429:
            raise RuntimeError("HTTP_429_RATE_LIMIT")
        elif response.status_code >= 400:
            raise RuntimeError(f"API Relay Error {response.status_code}: {response.text}")
            
        return True
