import unittest
import os

class TestOSPFLab02Structure(unittest.TestCase):
    LAB_PATH = "labs/ospf/lab-02-network-types"

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
            "solutions/R1.cfg"
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
        """Check if solution configs contain network type and priority commands."""
        path_r1 = os.path.join(self.LAB_PATH, "solutions/R1.cfg")
        with open(path_r1, "r") as f:
            content = f.read()
            self.assertIn("ip ospf network point-to-point", content)
            
        path_r2 = os.path.join(self.LAB_PATH, "solutions/R2.cfg")
        with open(path_r2, "r") as f:
            content = f.read()
            self.assertIn("ip ospf priority", content)

if __name__ == "__main__":
    unittest.main()
