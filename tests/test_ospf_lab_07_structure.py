import unittest
import os

class TestOSPFLab07Structure(unittest.TestCase):
    LAB_PATH = "labs/ospf/lab-07-auth-redistribution"

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
            "initial-configs/R5.cfg",
            "solutions/R1.cfg",
            "solutions/R2.cfg",
            "solutions/R3.cfg"
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
            self.assertIn("### Verification Cheatsheet", content)

    def test_hardware_standard(self):
        """Check if workbook mentions c7200 for R1-R3, R5."""
        path = os.path.join(self.LAB_PATH, "workbook.md")
        with open(path, "r") as f:
            content = f.read()
            self.assertIn("| R1 | Hub/ABR | c7200 |", content)
            self.assertIn("| R5 | External Partner| c7200 |", content)

    def test_config_content(self):
        """Check if solution configs contain Auth and Redistribution commands."""
        path_r1 = os.path.join(self.LAB_PATH, "solutions/R1.cfg")
        with open(path_r1, "r") as f:
            content = f.read()
            self.assertIn("cryptographic-algorithm hmac-sha-256", content)
            
        path_r2 = os.path.join(self.LAB_PATH, "solutions/R2.cfg")
        with open(path_r2, "r") as f:
            content = f.read()
            self.assertIn("redistribute eigrp 100", content)
            self.assertIn("metric-type type-1", content)

if __name__ == "__main__":
    unittest.main()
