import unittest
import os

class TestBGPLab02Structure(unittest.TestCase):
    LAB_PATH = "labs/bgp/lab-02-path-selection"

    def test_directory_exists(self):
        self.assertTrue(os.path.exists(self.LAB_PATH))

    def test_subdirectories_exist(self):
        for subdir in ["initial-configs", "solutions", "scripts/fault-injection"]:
            self.assertTrue(os.path.exists(os.path.join(self.LAB_PATH, subdir)))

    def test_files_exist(self):
        files = [
            "topology.drawio", "workbook.md", "challenges.md", "setup_lab.py",
            "initial-configs/R1.cfg", "initial-configs/R2.cfg", "initial-configs/R3.cfg",
            "solutions/R1.cfg", "solutions/R2.cfg", "solutions/R3.cfg",
            "scripts/fault-injection/inject_scenario_01.py",
            "scripts/fault-injection/inject_scenario_02.py",
            "scripts/fault-injection/inject_scenario_03.py",
            "scripts/fault-injection/apply_solution.py",
            "scripts/fault-injection/README.md",
        ]
        for f in files:
            self.assertTrue(os.path.exists(os.path.join(self.LAB_PATH, f)), f"Missing: {f}")

    def test_workbook_sections(self):
        path = os.path.join(self.LAB_PATH, "workbook.md")
        with open(path) as f:
            content = f.read()
        for section in ["## 1. Concepts", "## 2. Topology", "## 3. Hardware",
                        "## 4. Base Configuration", "## 5. Lab Challenge",
                        "## 6. Verification", "## 7. Verification Cheatsheet",
                        "## 8. Solutions", "## 9. Troubleshooting Scenarios",
                        "## 10. Lab Completion Checklist"]:
            self.assertIn(section, content, f"Missing section: {section}")

    def test_workbook_has_three_tickets(self):
        path = os.path.join(self.LAB_PATH, "workbook.md")
        with open(path) as f:
            content = f.read()
        self.assertIn("### Ticket 1", content)
        self.assertIn("### Ticket 2", content)
        self.assertIn("### Ticket 3", content)

    def test_workbook_covers_all_four_attributes(self):
        path = os.path.join(self.LAB_PATH, "workbook.md")
        with open(path) as f:
            content = f.read()
        for keyword in ["Weight", "Local Preference", "AS-Path", "MED"]:
            self.assertIn(keyword, content, f"Missing attribute: {keyword}")

    def test_workbook_has_details_spoilers(self):
        path = os.path.join(self.LAB_PATH, "workbook.md")
        with open(path) as f:
            content = f.read()
        self.assertGreaterEqual(content.count("<details>"), 6)

    def test_workbook_hardware_table(self):
        path = os.path.join(self.LAB_PATH, "workbook.md")
        with open(path) as f:
            content = f.read()
        self.assertIn("| R1 | Enterprise Edge | c7200 |", content)
        self.assertIn("| R2 | ISP-A", content)
        self.assertIn("| R3 | ISP-B", content)

    def test_initial_configs_chained_from_lab01(self):
        """Initial configs must have BGP from Lab 01 (chaining)."""
        for device in ["R1", "R2", "R3"]:
            path = os.path.join(self.LAB_PATH, f"initial-configs/{device}.cfg")
            with open(path) as f:
                content = f.read()
            self.assertIn("router bgp", content,
                f"Initial config for {device} must have BGP (chained from Lab 01)")

    def test_solution_r1_has_weight(self):
        """R1 solution must have neighbor weight configured."""
        path = os.path.join(self.LAB_PATH, "solutions/R1.cfg")
        with open(path) as f:
            content = f.read()
        self.assertIn("weight 100", content, "R1 solution must set weight 100 on R2 neighbor")

    def test_topology_drawio_standards(self):
        path = os.path.join(self.LAB_PATH, "topology.drawio")
        with open(path) as f:
            content = f.read()
        self.assertIn("mxgraph.cisco.routers.router", content)
        self.assertIn("strokeColor=#FFFFFF", content)
        self.assertIn("fillColor=#000000", content)
        self.assertIn("65001", content)
        self.assertIn("65002", content)
        self.assertIn("65003", content)


if __name__ == "__main__":
    unittest.main()
