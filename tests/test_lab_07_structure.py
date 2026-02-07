import unittest
import os

class TestLab07Structure(unittest.TestCase):
    LAB_PATH = "labs/eigrp/lab-07-redistribution"

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
            "initial-configs/R1.cfg",
            "solutions/R1.cfg",
            "solutions/R4.cfg"
        ]
        for file in files:
            path = os.path.join(self.LAB_PATH, file)
            self.assertTrue(os.path.exists(path), f"File {path} does not exist")

    def test_workbook_content(self):
        """Check if workbook has required sections."""
        path = os.path.join(self.LAB_PATH, "workbook.md")
        with open(path, "r") as f:
            content = f.read()
            self.assertIn("## 1. Concepts & Skills Covered", content)
            self.assertIn("## 2. Topology & Scenario", content)
            self.assertIn("## 9. Solutions", content)

    def test_config_content(self):
        """Check if solution configs contain redistribution commands."""
        path = os.path.join(self.LAB_PATH, "solutions/R1.cfg")
        with open(path, "r") as f:
            content = f.read()
            self.assertIn("redistribute ospf", content)
            self.assertIn("redistribute eigrp", content)

if __name__ == "__main__":
    unittest.main()
