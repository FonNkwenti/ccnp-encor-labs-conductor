"""
Apply Solution — BGP Lab 09
Restores all routers to the Lab 09 solution state.
Loads the full solution configs via the lab setup script.
"""
import subprocess
import sys
import os

if __name__ == "__main__":
    setup_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../setup_lab.py")
    setup_script = os.path.normpath(setup_script)

    print("[*] Restoring BGP Lab 09 to solution state...")
    print(f"    Running: python3 {setup_script}")
    result = subprocess.run([sys.executable, setup_script], check=True)
    print("[+] Lab 09 solution state restored.")
