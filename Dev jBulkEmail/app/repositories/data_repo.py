import json
import csv
import os
from pathlib import Path

class DataRepository:
  """
  Repository Layer for jBulkEmailSender.
  Handles all file persistence logic for config, accounts, and recipients.
  """
  def __init__(self, dirs):
    self.dirs = dirs
    self.config_file   = dirs['config']  / "config.json"
    self.login_file    = dirs['config']  / "login.txt"
    self.reload_state  = dirs['config']  / "reload_state.json"
    self.master_logs   = dirs['logs']    / "send_logs.txt"
    
  def load_config(self):
    if self.config_file.exists():
      try:
        with open(self.config_file, 'r', encoding='utf-8') as f:
          return json.load(f)
      except Exception:
        return {}
    return {}

  def save_config(self, config_data):
    try:
      with open(self.config_file, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=2)
    except Exception as e:
      print(f"Config Persistence Error: {e}")

  def load_accounts(self):
    accounts = {}
    if self.login_file.exists():
      with open(self.login_file, 'r', encoding='utf-8') as f:
        for line in f:
          if ':' in line:
            parts = line.strip().split(':', 1)
            if len(parts) == 2:
              accounts[parts[0]] = parts[1]
    return accounts

  def save_account(self, email, password):
    """Saves a new account and returns the updated account map."""
    accounts = self.load_accounts()
    accounts[email] = password
    try:
      with open(self.login_file, 'w', encoding='utf-8') as f:
        for em, pw in accounts.items():
          f.write(f"{em}:{pw}\n")
    except Exception as e:
      print(f"Account Save Error: {e}")
    return accounts

  def load_recipients_file(self, filename):
    """Load and validate recipients from disk."""
    recipients = []
    path = Path(filename)
    if not path.exists(): return []
      
    try:
      if path.suffix.lower() == '.csv':
        with open(path, mode='r', encoding='utf-8') as f:
          reader = csv.DictReader(f)
          for row in reader:
            if 'email' in row:
              recipients.append(row)
      else:
        with open(path, mode='r', encoding='utf-8') as f:
          for line in f:
            email = line.strip()
            if email:
              recipients.append({'email': email, 'name': 'Customer'})
    except Exception as e:
      print(f"Recipient Load Error: {e}")
    return recipients

  def save_reload_snapshot(self, state):
    try:
      with open(self.reload_state, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2)
    except Exception as e:
      print(f"Reload Persistence Error: {e}")

  def load_reload_snapshot(self):
    if self.reload_state.exists():
      try:
        with open(self.reload_state, 'r', encoding='utf-8') as f:
          state = json.load(f)
          # self.reload_state.unlink() # Cleanup handled by controller
          return state
      except:
        return None
    return None

  def discover_checkpoints(self):
    """Find all available mission checkpoints in the config/checkpoints folder."""
    checkpoint_dir = self.dirs['config'] / "checkpoints"
    checkpoint_dir.mkdir(exist_ok=True)
    return list(checkpoint_dir.glob("Mission_*.json"))

  def load_checkpoint(self, path):
    """Read mission state from a specific checkpoint file."""
    if not path.exists(): return None
    try:
      with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)
    except Exception:
      return None

  def save_mission_progress(self, checkpoint_path, state):
    """Persist current mission progress (Gap 19/20)."""
    try:
      with open(checkpoint_path, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2)
      return True
    except:
      return False

  def export_failed_recipients(self, failed_list):
    """Write failed transmissions to a uniquely dated CSV (Gap 7)."""
    from datetime import datetime
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = self.dirs['logs'] / f"failed_{ts}.csv"
    try:
      with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['email', 'name', 'error'])
        for item in failed_list:
          writer.writerow([item['email'], item['name'], item['error']])
      return path
    except:
      return None

  def load_failed_recipients(self, file_path):
    """Reload a previously exported failure manifest (Gap 7)."""
    return self.load_recipients_file(file_path)

  def append_master_log(self, message):
      """Maintain the master log file."""
      try:
          with open(self.master_logs, "a", encoding="utf-8") as f:
              timestamp = os.environ.get('MASTER_LOG_TS', "") # Injected by controller
              f.write(f"{timestamp} {message}\n")
      except: pass
