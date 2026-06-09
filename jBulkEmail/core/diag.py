import time
import smtplib
from pathlib import Path
import sys
import os

# --- PATH HIERARCHY CORRECTION (Gap 44) ---
# diag.py is in 'core/', so its parent is the project root.
CORE_DIR = Path(__file__).parent
PROJECT_ROOT = CORE_DIR.parent
sys.path.append(str(CORE_DIR))

# Now we can import reliably
from email_check import EmailChecker

def run_speed_audit():
    """Perform a comprehensive speed audit on tactical components."""
    print("🚀 INITIALIZING TACTICAL SPEED AUDIT (v6.1-MISSION)")
    print("-" * 50)
    
    start_total = time.time()
    
    # 1. Test SMTP Connection
    print("[1/3] 📡 Testing SMTP Latency (Gmail Target)...")
    s_connect = time.time()
    try:
        # Assuming Gmail for baseline
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
        server.ehlo()
        server.starttls()
        server.ehlo()
        latency = time.time() - s_connect
        print(f"✅ SMTP Handshake + STARTTLS: {latency:.2f}s")
        server.quit()
    except Exception as e:
        print(f"❌ SMTP Connection failed: {e}")
    
    # 2. Test CSV Update (Cold vs Warm Cache)
    csv_path = PROJECT_ROOT / "assets" / "sample_recipients.csv"
    if csv_path.exists():
        print(f"\n[2/3] 💾 Testing CSV Disk I/O (Target: {csv_path.name})...")
        
        # Test 1: Cold Cache (Direct Read/Write)
        # Note: update_status uses cache if told, but we simulate a clean slate
        s_csv_cold = time.time()
        # No 'use_cache' arg = manual read/write cycle
        EmailChecker.update_status(str(csv_path), 1, f"Audit-Cold {time.time()}")
        print(f"🔴 COLD Disk Write (Manual I/O): {time.time() - s_csv_cold:.2f}s")
        
        # Test 2: Warm Cache (Deferred Write)
        s_csv_warm = time.time()
        EmailChecker.update_status(str(csv_path), 1, f"Audit-Warm {time.time()}", 
                                   use_cache=True, defer_write=True)
        print(f"🟢 WARM Memory Update (Deferred): {time.time() - s_csv_warm:.4f}s")
    else:
        print(f"\n⚠️ Missing asset: {csv_path}")
    
    # 3. Test Module Integration
    print("\n[3/3] 🛠️ Verifying Sub-System Integration...")
    try:
        import RichContentManager as rcm
        print("✅ RichContentManager: Integration Healthy")
    except ImportError as e:
        print(f"❌ RichContentManager: Broken Dependency ({e})")

    print("-" * 50)
    print(f"🏁 AUDIT COMPLETE: {time.time() - start_total:.2f}s total latency.")

if __name__ == "__main__":
    run_speed_audit()
