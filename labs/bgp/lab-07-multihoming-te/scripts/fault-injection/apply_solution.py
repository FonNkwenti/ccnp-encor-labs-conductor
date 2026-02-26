"""
Restore Solution — BGP Lab 07
Pushes the full solution configurations to all devices, restoring the lab
to the known-good state after fault injection.
"""
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../common/tools')))
from lab_utils import LabSetup

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    solutions_dir = os.path.abspath(os.path.join(script_dir, "../../solutions"))

    devices = [
        ("R1", 5001, os.path.join(solutions_dir, "R1.cfg")),
        ("R2", 5002, os.path.join(solutions_dir, "R2.cfg")),
        ("R3", 5003, os.path.join(solutions_dir, "R3.cfg")),
        ("R4", 5004, os.path.join(solutions_dir, "R4.cfg")),
        ("R5", 5005, os.path.join(solutions_dir, "R5.cfg")),
    ]
    setup = LabSetup(devices)
    setup.run()
    print("\nBGP Lab 07 solution restored.")
