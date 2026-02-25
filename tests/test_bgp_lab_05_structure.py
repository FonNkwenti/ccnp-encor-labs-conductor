import unittest
import os

class TestBGPLab05Structure(unittest.TestCase):
    LAB_PATH = "labs/bgp/lab-05-aspath-routemaps"

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

    def test_workbook_covers_key_concepts(self):
        path = os.path.join(self.LAB_PATH, "workbook.md")
        with open(path) as f:
            content = f.read()
        for keyword in ["as-path access-list", "route-map", "local-preference",
                        "as-path prepend", "set local-preference"]:
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

    def test_initial_configs_chained_from_lab04(self):
        """Initial configs must have prefix-lists from Lab 04 (chaining)."""
        path = os.path.join(self.LAB_PATH, "initial-configs/R1.cfg")
        with open(path) as f:
            content = f.read()
        self.assertIn("ip prefix-list FROM-ISP-A", content,
            "Initial config must carry forward Lab 04 prefix-lists")
        self.assertIn("soft-reconfiguration inbound", content)
        self.assertIn("next-hop-self", content)

    def test_initial_configs_no_route_maps(self):
        """Initial configs must NOT contain route-maps (student configures those)."""
        path = os.path.join(self.LAB_PATH, "initial-configs/R1.cfg")
        with open(path) as f:
            content = f.read()
        self.assertNotIn("route-map", content,
            "Initial config should not have route-maps")
        self.assertNotIn("ip as-path access-list", content,
            "Initial config should not have AS-path ACLs")

    def test_solution_r1_has_as_path_acls(self):
        """R1 solution must define AS-path access-lists."""
        path = os.path.join(self.LAB_PATH, "solutions/R1.cfg")
        with open(path) as f:
            content = f.read()
        self.assertIn("ip as-path access-list 1 permit ^65002$", content)
        self.assertIn("ip as-path access-list 2 permit ^65003$", content)

    def test_solution_r1_has_route_maps(self):
        """R1 solution must define all three route-maps."""
        path = os.path.join(self.LAB_PATH, "solutions/R1.cfg")
        with open(path) as f:
            content = f.read()
        self.assertIn("route-map SET-LP-200-ISP-A", content)
        self.assertIn("route-map POLICY-ISP-B-IN", content)
        self.assertIn("route-map PREPEND-TO-ISP-B", content)

    def test_solution_r1_uses_local_preference_not_weight(self):
        """R1 solution must use set local-preference, not set weight."""
        path = os.path.join(self.LAB_PATH, "solutions/R1.cfg")
        with open(path) as f:
            content = f.read()
        self.assertIn("set local-preference 200", content,
            "Must use local-preference for AS-wide policy")
        self.assertIn("set local-preference 150", content)
        self.assertNotIn("set weight", content,
            "Weight does not propagate via iBGP — use local-preference")

    def test_solution_r1_has_as_path_prepend(self):
        """R1 solution must configure AS-path prepending."""
        path = os.path.join(self.LAB_PATH, "solutions/R1.cfg")
        with open(path) as f:
            content = f.read()
        self.assertIn("set as-path prepend 65001 65001 65001", content)

    def test_solution_r1_applies_route_maps_to_neighbors(self):
        """R1 solution must apply route-maps to the correct neighbors."""
        path = os.path.join(self.LAB_PATH, "solutions/R1.cfg")
        with open(path) as f:
            content = f.read()
        self.assertIn("neighbor 10.1.12.2 route-map SET-LP-200-ISP-A in", content)
        self.assertIn("neighbor 10.1.13.2 route-map POLICY-ISP-B-IN in", content)
        self.assertIn("neighbor 10.1.13.2 route-map PREPEND-TO-ISP-B out", content)

    def test_solution_r1_has_pass_through_sequences(self):
        """Route-maps must have final permit pass-through sequences."""
        path = os.path.join(self.LAB_PATH, "solutions/R1.cfg")
        with open(path) as f:
            content = f.read()
        # Each route-map should have a permit sequence with no match clause (pass-through)
        self.assertIn("route-map SET-LP-200-ISP-A permit 20", content)
        self.assertIn("route-map PREPEND-TO-ISP-B permit 20", content)
        self.assertIn("route-map POLICY-ISP-B-IN permit 20", content)

    def test_topology_drawio_standards(self):
        path = os.path.join(self.LAB_PATH, "topology.drawio")
        with open(path) as f:
            content = f.read()
        self.assertIn("mxgraph.cisco.routers.router", content)
        self.assertIn("strokeColor=#FFFFFF", content)
        self.assertIn("fillColor=#000000", content)
        self.assertIn("AS 65001", content)
        self.assertIn("AS 65002", content)
        self.assertIn("AS 65003", content)
        self.assertIn("PREPEND-TO-ISP-B", content,
            "Topology must annotate route-maps on links")


if __name__ == "__main__":
    unittest.main()
