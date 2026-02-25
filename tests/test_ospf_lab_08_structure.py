import unittest
import os

class TestOSPFLab08Structure(unittest.TestCase):
    LAB_PATH = "labs/ospf/lab-08-ospfv3-integration"

    def test_directory_exists(self):
        """Check if the lab directory exists."""
        self.assertTrue(os.path.exists(self.LAB_PATH), f"Directory {self.LAB_PATH} does not exist")

    def test_subdirectories_exist(self):
        """Check if required subdirectories exist."""
        subdirs = ["initial-configs", "solutions"]
        for subdir in subdirs:
            path = os.path.join(self.LAB_PATH, subdir)
            self.assertTrue(os.path.exists(path), f"Subdirectory {path} does not exist")

    def test_files_exist(self):
        """Check if required files exist."""
        files = [
            "topology.drawio",
            "workbook.md",
            "challenges.md",
            "setup_lab.py",
            "initial-configs/R1.cfg",
            "initial-configs/R2.cfg",
            "initial-configs/R3.cfg",
            "initial-configs/R6.cfg",
            "solutions/R1.cfg",
            "solutions/R2.cfg",
            "solutions/R3.cfg",
            "solutions/R6.cfg"
        ]
        for file in files:
            path = os.path.join(self.LAB_PATH, file)
            self.assertTrue(os.path.exists(path), f"File {path} does not exist")

    def test_workbook_content(self):
        """Check if workbook has required sections."""
        path = os.path.join(self.LAB_PATH, "workbook.md")
        with open(path, "r") as f:
            content = f.read()
            self.assertIn("### Scenario", content)
            self.assertIn("### Objectives", content)
            self.assertIn("### Challenge Tasks", content)
            self.assertIn("OSPFv3", content)
            self.assertIn("Address Families", content)

    def test_hardware_standard(self):
        """Check if workbook mentions c7200 for R1-R3, R6."""
        path = os.path.join(self.LAB_PATH, "workbook.md")
        with open(path, "r") as f:
            content = f.read()
            self.assertIn("| R1 | Hub/ABR | c7200 |", content)
            self.assertIn("| R6 | Dual-Stack Border | c7200 |", content)

    def test_config_content(self):
        """Check if solution configs contain OSPFv3 Address Family commands."""
        path_r1 = os.path.join(self.LAB_PATH, "solutions/R1.cfg")
        with open(path_r1, "r") as f:
            content = f.read()
            self.assertIn("router ospfv3 1", content)
            self.assertIn("address-family ipv4 unicast", content)
            self.assertIn("address-family ipv6 unicast", content)
            self.assertIn("ospfv3 1 ipv4 area 0", content)
            self.assertIn("ospfv3 1 ipv6 area 0", content)

if __name__ == "__main__":
    unittest.main()
