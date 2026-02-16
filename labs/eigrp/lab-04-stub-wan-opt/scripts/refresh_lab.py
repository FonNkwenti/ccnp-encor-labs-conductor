import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from lab_utils import LabRefresher

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    lab_dir = os.path.join(script_dir, "..")
    devices = [
        ("R1", 5001, os.path.join(lab_dir, "initial-configs/R1.cfg")),
        ("R2", 5002, os.path.join(lab_dir, "initial-configs/R2.cfg")),
        ("R3", 5003, os.path.join(lab_dir, "initial-configs/R3.cfg")),
        ("R5", 5005, os.path.join(lab_dir, "initial-configs/R5.cfg")),
    ]
    refresher = LabRefresher(devices)
    refresher.run()
    print("\nLab 04 has been refreshed.")
