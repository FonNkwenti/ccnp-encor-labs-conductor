import unittest
import os

class TestBGPLab01Structure(unittest.TestCase):
    LAB_PATH = "labs/bgp/lab-01-basic-ebgp-peering"

    def test_directory_exists(self):
        """Check if the lab directory exists."""
        self.assertTrue(os.path.exists(self.LAB_PATH), f"Directory {self.LAB_PATH} does not exist")

    def test_subdirectories_exist(self):
        """Check if required subdirectories exist."""
        subdirs = ["initial-configs", "solutions", "scripts/fault-injection"]
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
            "solutions/R1.cfg",
            "solutions/R2.cfg",
            "solutions/R3.cfg",
            "scripts/fault-injection/inject_scenario_01.py",
            "scripts/fault-injection/inject_scenario_02.py",
            "scripts/fault-injection/inject_scenario_03.py",
            "scripts/fault-injection/apply_solution.py",
            "scripts/fault-injection/README.md",
        ]
        for file in files:
            path = os.path.join(self.LAB_PATH, file)
            self.assertTrue(os.path.exists(path), f"File {path} does not exist")

    def test_workbook_sections(self):
        """Check if workbook has all 10 required sections."""
        path = os.path.join(self.LAB_PATH, "workbook.md")
        with open(path, "r") as f:
            content = f.read()
            self.assertIn("## 1. Concepts & Skills Covered", content)
            self.assertIn("## 2. Topology & Scenario", content)
            self.assertIn("## 3. Hardware & Environment Specifications", content)
            self.assertIn("## 4. Base Configuration", content)
            self.assertIn("## 5. Lab Challenge", content)
            self.assertIn("## 6. Verification & Analysis", content)
            self.assertIn("## 7. Verification Cheatsheet", content)
            self.assertIn("## 8. Solutions", content)
            self.assertIn("## 9. Troubleshooting Scenarios", content)
            self.assertIn("## 10. Lab Completion Checklist", content)

    def test_workbook_has_troubleshooting_tickets(self):
        """Check that workbook has at least 3 troubleshooting tickets."""
        path = os.path.join(self.LAB_PATH, "workbook.md")
        with open(path, "r") as f:
            content = f.read()
            self.assertIn("### Ticket 1", content)
            self.assertIn("### Ticket 2", content)
            self.assertIn("### Ticket 3", content)

    def test_workbook_has_details_spoilers(self):
        """Check that solutions use collapsible details blocks."""
        path = os.path.join(self.LAB_PATH, "workbook.md")
        with open(path, "r") as f:
            content = f.read()
            self.assertGreaterEqual(content.count("<details>"), 6,
                "Should have at least 6 <details> blocks (solutions + troubleshooting)")

    def test_workbook_has_console_access_table(self):
        """Check that workbook has console port references."""
        path = os.path.join(self.LAB_PATH, "workbook.md")
        with open(path, "r") as f:
            content = f.read()
            self.assertIn("| R1 | 5001 |", content)
            self.assertIn("| R2 | 5002 |", content)
            self.assertIn("| R3 | 5003 |", content)

    def test_hardware_standard(self):
        """Check that workbook mentions c7200 for all three routers."""
        path = os.path.join(self.LAB_PATH, "workbook.md")
        with open(path, "r") as f:
            content = f.read()
            self.assertIn("| R1 | Enterprise Edge | c7200 |", content)
            self.assertIn("| R2 | ISP-A | c7200 |", content)
            self.assertIn("| R3 | ISP-B | c7200 |", content)

    def test_initial_configs_no_bgp(self):
        """Check that initial configs do NOT contain BGP configuration."""
        for device in ["R1", "R2", "R3"]:
            path = os.path.join(self.LAB_PATH, f"initial-configs/{device}.cfg")
            with open(path, "r") as f:
                content = f.read()
                self.assertNotIn("router bgp", content,
                    f"Initial config for {device} should not contain BGP")

    def test_solution_configs_have_bgp(self):
        """Check that solution configs contain BGP configuration."""
        expected = {
            "R1": ("router bgp 65001", "neighbor 10.1.12.2 remote-as 65002"),
            "R2": ("router bgp 65002", "neighbor 10.1.12.1 remote-as 65001"),
            "R3": ("router bgp 65003", "neighbor 10.1.13.1 remote-as 65001"),
        }
        for device, (bgp_proc, neighbor) in expected.items():
            path = os.path.join(self.LAB_PATH, f"solutions/{device}.cfg")
            with open(path, "r") as f:
                content = f.read()
                self.assertIn(bgp_proc, content,
                    f"Solution for {device} must contain {bgp_proc}")
                self.assertIn(neighbor, content,
                    f"Solution for {device} must contain {neighbor}")

    def test_topology_drawio_valid(self):
        """Check that topology.drawio follows diagram standards."""
        path = os.path.join(self.LAB_PATH, "topology.drawio")
        with open(path, "r") as f:
            content = f.read()
            self.assertIn("mxgraph.cisco.routers.router", content,
                "Must use Cisco router shapes")
            self.assertIn("strokeColor=#FFFFFF", content,
                "Connection lines must be white")
            self.assertIn("fillColor=#000000", content,
                "Legend must have black fill")
            self.assertIn("AS 65001", content, "Legend must list AS numbers")
            self.assertIn("AS 65002", content)
            self.assertIn("AS 65003", content)


if __name__ == "__main__":
    unittest.main()
