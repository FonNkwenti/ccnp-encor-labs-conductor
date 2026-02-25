import unittest
import os

class TestBGPLab04Structure(unittest.TestCase):
    LAB_PATH = "labs/bgp/lab-04-route-filtering"

    def test_directory_exists(self):
        self.assertTrue(os.path.exists(self.LAB_PATH))

    def test_subdirectories_exist(self):
        for subdir in ["initial-configs", "solutions", "scripts/fault-injection"]:
            self.assertTrue(os.path.exists(os.path.join(self.LAB_PATH, subdir)),
                            f"Missing subdirectory: {subdir}")

    def test_files_exist(self):
        files = [
            "topology.drawio", "workbook.md", "challenges.md", "setup_lab.py",
            "initial-configs/R1.cfg", "initial-configs/R2.cfg",
            "initial-configs/R3.cfg", "initial-configs/R4.cfg",
            "solutions/R1.cfg", "solutions/R2.cfg",
            "solutions/R3.cfg", "solutions/R4.cfg",
            "solutions/verification_commands.txt",
            "scripts/fault-injection/inject_scenario_01.py",
            "scripts/fault-injection/inject_scenario_02.py",
            "scripts/fault-injection/inject_scenario_03.py",
            "scripts/fault-injection/apply_solution.py",
            "scripts/fault-injection/README.md",
        ]
        for f in files:
            self.assertTrue(os.path.exists(os.path.join(self.LAB_PATH, f)),
                            f"Missing file: {f}")

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

    def test_workbook_covers_prefix_list_concepts(self):
        path = os.path.join(self.LAB_PATH, "workbook.md")
        with open(path) as f:
            content = f.read()
        for keyword in ["prefix-list", "soft-reconfiguration", "distribute-list",
                        "received-routes", "advertised-routes"]:
            self.assertIn(keyword, content, f"Missing concept: {keyword}")

    def test_workbook_has_details_spoilers(self):
        path = os.path.join(self.LAB_PATH, "workbook.md")
        with open(path) as f:
            content = f.read()
        self.assertGreaterEqual(content.count("<details>"), 6,
            "Should have at least 6 <details> blocks (solutions + troubleshooting)")

    def test_workbook_hardware_table(self):
        path = os.path.join(self.LAB_PATH, "workbook.md")
        with open(path) as f:
            content = f.read()
        self.assertIn("| R1 | Enterprise Edge | c7200 |", content)
        self.assertIn("| R2 | ISP-A (Primary) | c7200 |", content)
        self.assertIn("| R3 | ISP-B (Backup) | c7200 |", content)
        self.assertIn("| R4 | Enterprise Internal | c3725 |", content)

    def test_console_access_table(self):
        path = os.path.join(self.LAB_PATH, "workbook.md")
        with open(path) as f:
            content = f.read()
        self.assertIn("| R1 | 5001 |", content)
        self.assertIn("| R2 | 5002 |", content)
        self.assertIn("| R3 | 5003 |", content)
        self.assertIn("| R4 | 5004 |", content)

    def test_initial_configs_chained_from_lab03(self):
        """Initial configs must have iBGP and next-hop-self from Lab 03."""
        path = os.path.join(self.LAB_PATH, "initial-configs/R1.cfg")
        with open(path) as f:
            content = f.read()
        self.assertIn("router bgp 65001", content)
        self.assertIn("next-hop-self", content)
        self.assertIn("update-source Loopback0", content)

    def test_initial_configs_no_prefix_lists(self):
        """Initial configs must NOT contain prefix-list filtering (not yet configured)."""
        path = os.path.join(self.LAB_PATH, "initial-configs/R1.cfg")
        with open(path) as f:
            content = f.read()
        self.assertNotIn("ip prefix-list", content,
            "Initial config should not have prefix-lists — student configures those")
        self.assertNotIn("soft-reconfiguration inbound", content,
            "Initial config should not have soft-reconfiguration — student configures that")

    def test_solution_r1_has_prefix_lists(self):
        """R1 solution must have all three prefix-lists configured."""
        path = os.path.join(self.LAB_PATH, "solutions/R1.cfg")
        with open(path) as f:
            content = f.read()
        self.assertIn("ip prefix-list FROM-ISP-A", content)
        self.assertIn("ip prefix-list FROM-ISP-B", content)
        self.assertIn("ip prefix-list TO-ISP-B", content)

    def test_solution_r1_has_soft_reconfiguration(self):
        """R1 solution must enable soft-reconfiguration for both eBGP peers."""
        path = os.path.join(self.LAB_PATH, "solutions/R1.cfg")
        with open(path) as f:
            content = f.read()
        self.assertIn("soft-reconfiguration inbound", content)

    def test_solution_r1_applies_filters_correctly(self):
        """R1 solution must apply prefix-lists to the correct neighbors."""
        path = os.path.join(self.LAB_PATH, "solutions/R1.cfg")
        with open(path) as f:
            content = f.read()
        self.assertIn("neighbor 10.1.12.2 prefix-list FROM-ISP-A in", content)
        self.assertIn("neighbor 10.1.13.2 prefix-list FROM-ISP-B in", content)
        self.assertIn("neighbor 10.1.13.2 prefix-list TO-ISP-B out", content)

    def test_solution_r4_has_distribute_list(self):
        """R4 solution must use a distribute-list for outbound filtering."""
        path = os.path.join(self.LAB_PATH, "solutions/R4.cfg")
        with open(path) as f:
            content = f.read()
        self.assertIn("ip access-list standard ENTERPRISE-INTERNAL", content)
        self.assertIn("distribute-list ENTERPRISE-INTERNAL out", content)
        self.assertIn("permit 10.4.1.0 0.0.0.255", content)
        self.assertIn("permit 10.4.2.0 0.0.0.255", content)

    def test_topology_drawio_standards(self):
        path = os.path.join(self.LAB_PATH, "topology.drawio")
        with open(path) as f:
            content = f.read()
        self.assertIn("mxgraph.cisco.routers.router", content,
            "Must use Cisco router shapes")
        self.assertIn("strokeColor=#FFFFFF", content,
            "Connection lines must be white")
        self.assertIn("fillColor=#000000", content,
            "Legend must have black fill")
        self.assertIn("AS 65001", content)
        self.assertIn("AS 65002", content)
        self.assertIn("AS 65003", content)
        self.assertIn("FROM-ISP-A", content,
            "Topology must annotate active filters on links")


if __name__ == "__main__":
    unittest.main()
