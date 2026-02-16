import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../common/tools')))
from lab_utils import LabSetup

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    devices = [
        ("R1", 5001, os.path.join(script_dir, "initial-configs/R1.cfg")),
        ("R2", 5002, os.path.join(script_dir, "initial-configs/R2.cfg")),
        ("R3", 5003, os.path.join(script_dir, "initial-configs/R3.cfg")),
    ]
    setup = LabSetup(devices)
    setup.run()
    print("\nLab 03 setup complete.")
