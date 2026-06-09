import tkinter as tk
import sys
import os
from pathlib import Path

# --- TACTICAL ENTRY POINT UNIFICATION (Gap 45) ---
# Project shifted from Distributed MVC to Stable Monolith per Mission Command.
# main.py now acts as a high-level wrapper for bulk_email_sender.py

# 1. Environment Preparation
BASE_DIR = Path(__file__).parent
CORE_DIR = BASE_DIR / "core"
sys.path.append(str(BASE_DIR))
sys.path.append(str(CORE_DIR))

# 2. Redirect to Orchestrator
try:
    from bulk_email_sender import BulkEmailSender
except ImportError as e:
    print(f"❌ ARCHITECTURAL ERROR: Could not find monolith ({e})")
    print("Ensure 'bulk_email_sender.py' is in the root directory.")
    sys.exit(1)

def launch_mission():
    """Hierarchy Layer 1: Mission Orchestration"""
    print("[INFO] jBulkEmailSender: Initiating Entry Point Waterfall...")
    
    # Ensure necessary project structure
    dirs = ['config', 'logs', 'exports', 'assets']
    for d in dirs:
        (BASE_DIR / d).mkdir(exist_ok=True)
    
    # Launch GUI
    root = tk.Tk()
    app = BulkEmailSender(root)
    root.mainloop()

if __name__ == "__main__":
    launch_mission()
