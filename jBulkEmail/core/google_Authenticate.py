import smtplib
import sys
import json
import logging
import traceback
from datetime import datetime
from pathlib import Path

# Setup Debug Logging
LOG_FILE = Path(__file__).parent.parent / "logs" / "smtp_debug.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Popular SMTP Provider Settings
SMTP_PROVIDERS = {
    "Gmail": {"host": "smtp.gmail.com", "port": 587, "use_tls": True},
    "Outlook": {"host": "smtp.office365.com", "port": 587, "use_tls": True},
    "Yahoo": {"host": "smtp.mail.yahoo.com", "port": 587, "use_tls": True},
    "Zoho": {"host": "smtp.zoho.com", "port": 465, "use_tls": False},
    "iCloud": {"host": "smtp.mail.me.com", "port": 587, "use_tls": True},
}

def check_smtp(provider_name, email, password):
    logging.info(f"--- Starting SMTP Check for {provider_name} ({email}) ---")
    
    if provider_name not in SMTP_PROVIDERS:
        err = f"Unknown provider: {provider_name}"
        logging.error(err)
        return {"success": False, "message": err}
    
    config = SMTP_PROVIDERS[provider_name]
    host = config["host"]
    port = config["port"]
    
    try:
        logging.debug(f"Connecting to {host}:{port}...")
        if port == 465:
            server = smtplib.SMTP_SSL(host, port, timeout=15)
        else:
            server = smtplib.SMTP(host, port, timeout=15)
            if config["use_tls"]:
                logging.debug("Starting TLS...")
                server.starttls()
        
        logging.debug(f"Attempting login for {email}...")
        server.login(email, password)
        server.quit()
        
        logging.info(f"✅ SUCCESS: Authenticated with {provider_name}")
        return {"success": True, "message": f"Successfully authenticated with {provider_name}"}
        
    except smtplib.SMTPAuthenticationError as e:
        msg = "Authentication failed: Likely incorrect App Password or 2FA not enabled."
        logging.warning(f"❌ {msg} Details: {str(e)}")
        return {"success": False, "message": msg, "error_code": "AUTH_FAIL"}
        
    except Exception as e:
        detailed_err = traceback.format_exc()
        logging.error(f"💥 CRITICAL ERROR during SMTP check:\n{detailed_err}")
        return {
            "success": False, 
            "message": f"Connection Error: {str(e)}", 
            "details": detailed_err.splitlines()[-1] # Pass last line of error
        }

if __name__ == "__main__":
    try:
        if len(sys.argv) > 3:
            p = sys.argv[1]
            e = sys.argv[2]
            pw = sys.argv[3]
            result = check_smtp(p, e, pw)
            print(json.dumps(result))
        else:
            logging.error("Insufficient arguments provided to script")
            print(json.dumps({"success": False, "message": "Missing arguments"}))
    except Exception as e:
        logging.error(f"Script crash: {str(e)}")
        print(json.dumps({"success": False, "message": f"Script Error: {str(e)}"}))
