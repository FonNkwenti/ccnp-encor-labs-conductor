import unittest
import os

LAB_PATH = "labs/bgp/lab-07-multihoming-te"


class TestBGPLab07Structure(unittest.TestCase):

    # ── Directory & File Existence ───────────────────────────────────────────

    def test_directory_exists(self):
        """Lab directory must exist."""
        self.assertTrue(os.path.exists(LAB_PATH),
                        f"Directory {LAB_PATH} does not exist")

    def test_subdirectories_exist(self):
        """Required subdirectories must exist."""
        for subdir in ["initial-configs", "solutions", "scripts/fault-injection"]:
            path = os.path.join(LAB_PATH, subdir)
            self.assertTrue(os.path.exists(path),
                            f"Missing subdirectory: {path}")

    def test_required_files_exist(self):
        """All required lab files must be present."""
        files = [
            "topology.drawio",
            "workbook.md",
            "challenges.md",
            "setup_lab.py",
            # Initial configs — R1 through R5
            "initial-configs/R1.cfg",
            "initial-configs/R2.cfg",
            "initial-configs/R3.cfg",
            "initial-configs/R4.cfg",
            "initial-configs/R5.cfg",
            # Solution configs — R1 through R5
            "solutions/R1.cfg",
            "solutions/R2.cfg",
            "solutions/R3.cfg",
            "solutions/R4.cfg",
            "solutions/R5.cfg",
            # Fault injection scripts
            "scripts/fault-injection/inject_scenario_01.py",
            "scripts/fault-injection/inject_scenario_02.py",
            "scripts/fault-injection/inject_scenario_03.py",
            "scripts/fault-injection/apply_solution.py",
            "scripts/fault-injection/README.md",
        ]
        for f in files:
            path = os.path.join(LAB_PATH, f)
            self.assertTrue(os.path.exists(path), f"Missing file: {path}")

    # ── Workbook Sections ────────────────────────────────────────────────────

    def test_workbook_has_all_10_sections(self):
        """Workbook must contain all 10 required sections."""
        path = os.path.join(LAB_PATH, "workbook.md")
        with open(path) as f:
            content = f.read()
        sections = [
            "## 1. Concepts & Skills Covered",
            "## 2. Topology & Scenario",
            "## 3. Hardware & Environment Specifications",
            "## 4. Base Configuration",
            "## 5. Lab Challenge",
            "## 6. Verification & Analysis",
            "## 7. Verification Cheatsheet",
            "## 8. Solutions",
            "## 9. Troubleshooting Scenarios",
            "## 10. Lab Completion Checklist",
        ]
        for section in sections:
            self.assertIn(section, content, f"Missing section: {section}")

    def test_workbook_has_three_tickets(self):
        """Workbook must contain Ticket 1, Ticket 2, and Ticket 3."""
        path = os.path.join(LAB_PATH, "workbook.md")
        with open(path) as f:
            content = f.read()
        self.assertIn("### Ticket 1", content)
        self.assertIn("### Ticket 2", content)
        self.assertIn("### Ticket 3", content)

    def test_workbook_has_at_least_6_details_blocks(self):
        """Solutions and troubleshooting must use at least 6 collapsible blocks."""
        path = os.path.join(LAB_PATH, "workbook.md")
        with open(path) as f:
            content = f.read()
        count = content.count("<details>")
        self.assertGreaterEqual(count, 6,
            f"Expected at least 6 <details> blocks, found {count}")

    # ── Console Access Table ─────────────────────────────────────────────────

    def test_console_access_table_has_r1_through_r5(self):
        """Workbook console table must list all 5 routers with correct ports."""
        path = os.path.join(LAB_PATH, "workbook.md")
        with open(path) as f:
            content = f.read()
        self.assertIn("| R1 | 5001 |", content)
        self.assertIn("| R2 | 5002 |", content)
        self.assertIn("| R3 | 5003 |", content)
        self.assertIn("| R4 | 5004 |", content)
        self.assertIn("| R5 | 5005 |", content)

    # ── Hardware Table ───────────────────────────────────────────────────────

    def test_hardware_table_has_all_5_routers(self):
        """Workbook hardware table must list all 5 routers with correct platforms."""
        path = os.path.join(LAB_PATH, "workbook.md")
        with open(path) as f:
            content = f.read()
        self.assertIn("| R1 | Enterprise Edge | c7200 |", content)
        self.assertIn("| R2 | ISP-A | c7200 |", content)
        self.assertIn("| R3 | ISP-B | c7200 |", content)
        self.assertIn("| R4 | Enterprise Internal | c3725 |", content)
        self.assertIn("| R5 | Downstream Customer | c3725 |", content)

    # ── R1 Solution Config — Lab 07 TE Features ──────────────────────────────

    def test_solution_r1_has_lp_from_isp_a(self):
        """R1 solution must contain LP-FROM-ISP-A route-map."""
        path = os.path.join(LAB_PATH, "solutions/R1.cfg")
        with open(path) as f:
            content = f.read()
        self.assertIn("LP-FROM-ISP-A", content,
            "R1 solution must define LP-FROM-ISP-A route-map")

    def test_solution_r1_has_te_to_isp_a(self):
        """R1 solution must contain TE-TO-ISP-A route-map."""
        path = os.path.join(LAB_PATH, "solutions/R1.cfg")
        with open(path) as f:
            content = f.read()
        self.assertIn("TE-TO-ISP-A", content,
            "R1 solution must define TE-TO-ISP-A route-map")

    def test_solution_r1_has_te_to_isp_b(self):
        """R1 solution must contain TE-TO-ISP-B route-map."""
        path = os.path.join(LAB_PATH, "solutions/R1.cfg")
        with open(path) as f:
            content = f.read()
        self.assertIn("TE-TO-ISP-B", content,
            "R1 solution must define TE-TO-ISP-B route-map")

    def test_solution_r1_has_cond_default(self):
        """R1 solution must contain COND-DEFAULT route-map."""
        path = os.path.join(LAB_PATH, "solutions/R1.cfg")
        with open(path) as f:
            content = f.read()
        self.assertIn("COND-DEFAULT", content,
            "R1 solution must define COND-DEFAULT route-map")

    def test_solution_r1_has_default_originate(self):
        """R1 solution must use default-originate on R4 neighbor."""
        path = os.path.join(LAB_PATH, "solutions/R1.cfg")
        with open(path) as f:
            content = f.read()
        self.assertIn("default-originate", content,
            "R1 solution must include neighbor default-originate statement")

    def test_solution_r1_has_null0_static_route(self):
        """R1 solution must include ip route 0.0.0.0 0.0.0.0 Null0."""
        path = os.path.join(LAB_PATH, "solutions/R1.cfg")
        with open(path) as f:
            content = f.read()
        self.assertIn("ip route 0.0.0.0 0.0.0.0 Null0", content,
            "R1 solution must have static default to Null0 for conditional default-originate")

    def test_solution_r1_has_med_metric(self):
        """R1 solution must contain metric (MED) settings in outbound route-maps."""
        path = os.path.join(LAB_PATH, "solutions/R1.cfg")
        with open(path) as f:
            content = f.read()
        self.assertIn("set metric", content,
            "R1 solution must set MED metric values in outbound TE route-maps")

    def test_solution_r1_has_as_path_prepend(self):
        """R1 solution must contain AS-path prepend statements."""
        path = os.path.join(LAB_PATH, "solutions/R1.cfg")
        with open(path) as f:
            content = f.read()
        self.assertIn("set as-path prepend", content,
            "R1 solution must include AS-path prepend for inbound TE")

    def test_solution_r1_retains_community_infrastructure(self):
        """R1 solution must retain community-list from Lab 06."""
        path = os.path.join(LAB_PATH, "solutions/R1.cfg")
        with open(path) as f:
            content = f.read()
        self.assertIn("ip community-list standard CUSTOMER-ROUTES permit 65003:500", content)
        self.assertIn("send-community", content)

    # ── R2/R3/R4/R5 Solution Configs — Unchanged ─────────────────────────────

    def test_solution_r2_has_bgp_65002(self):
        """R2 solution must have BGP AS 65002."""
        path = os.path.join(LAB_PATH, "solutions/R2.cfg")
        with open(path) as f:
            content = f.read()
        self.assertIn("router bgp 65002", content)
        self.assertIn("neighbor 10.1.12.1 send-community", content)
        self.assertIn("neighbor 10.1.23.2 send-community", content)

    def test_solution_r3_has_bgp_65003_and_r5_peer(self):
        """R3 solution must have BGP AS 65003 with R5 neighbor."""
        path = os.path.join(LAB_PATH, "solutions/R3.cfg")
        with open(path) as f:
            content = f.read()
        self.assertIn("router bgp 65003", content)
        self.assertIn("neighbor 10.1.35.2 remote-as 65004", content)
        self.assertIn("neighbor 10.1.35.2 send-community", content)

    def test_solution_r4_has_no_export(self):
        """R4 solution must have SET-NO-EXPORT route-map."""
        path = os.path.join(LAB_PATH, "solutions/R4.cfg")
        with open(path) as f:
            content = f.read()
        self.assertIn("route-map SET-NO-EXPORT", content)
        self.assertIn("set community no-export additive", content)

    def test_solution_r5_has_bgp_65004(self):
        """R5 solution must configure BGP AS 65004."""
        path = os.path.join(LAB_PATH, "solutions/R5.cfg")
        with open(path) as f:
            content = f.read()
        self.assertIn("router bgp 65004", content)
        self.assertIn("neighbor 10.1.35.1 remote-as 65003", content)

    # ── Initial Configs — Lab 06 Solutions ───────────────────────────────────

    def test_initial_config_r1_has_lab06_route_maps(self):
        """R1 initial config must carry Lab 06 route-maps as starting point."""
        path = os.path.join(LAB_PATH, "initial-configs/R1.cfg")
        with open(path) as f:
            content = f.read()
        self.assertIn("router bgp 65001", content)
        self.assertIn("ip as-path access-list 1 permit ^65002$", content)
        self.assertIn("route-map SET-LP-200-ISP-A", content)
        self.assertIn("route-map POLICY-ISP-B-IN", content)
        self.assertIn("route-map PREPEND-TO-ISP-B", content)

    # ── Topology Drawio ──────────────────────────────────────────────────────

    def test_topology_drawio_has_cisco_router_shapes(self):
        """topology.drawio must use Cisco router shapes."""
        path = os.path.join(LAB_PATH, "topology.drawio")
        with open(path) as f:
            content = f.read()
        self.assertIn("mxgraph.cisco.routers.router", content,
            "Must use mxgraph.cisco.routers.router shape")

    def test_topology_drawio_has_white_stroke_lines(self):
        """topology.drawio connection lines must be white."""
        path = os.path.join(LAB_PATH, "topology.drawio")
        with open(path) as f:
            content = f.read()
        self.assertIn("strokeColor=#FFFFFF", content,
            "Connection lines must use strokeColor=#FFFFFF")

    def test_topology_drawio_has_black_fill_legend(self):
        """topology.drawio legend must have black fill."""
        path = os.path.join(LAB_PATH, "topology.drawio")
        with open(path) as f:
            content = f.read()
        self.assertIn("fillColor=#000000", content,
            "Legend must have fillColor=#000000")

    def test_topology_drawio_has_all_as_numbers(self):
        """topology.drawio legend must list all 4 AS numbers."""
        path = os.path.join(LAB_PATH, "topology.drawio")
        with open(path) as f:
            content = f.read()
        self.assertIn("AS 65001", content)
        self.assertIn("AS 65002", content)
        self.assertIn("AS 65003", content)

    # ── setup_lab.py ─────────────────────────────────────────────────────────

    def test_setup_lab_references_all_5_devices(self):
        """setup_lab.py must reference all 5 devices with correct ports."""
        path = os.path.join(LAB_PATH, "setup_lab.py")
        with open(path) as f:
            content = f.read()
        self.assertIn("5001", content)
        self.assertIn("5002", content)
        self.assertIn("5003", content)
        self.assertIn("5004", content)
        self.assertIn("5005", content)
        self.assertIn("R5", content)

    # ── Fault Injection Scripts ───────────────────────────────────────────────

    def test_fault_scripts_use_telnet_device_type(self):
        """All fault injection scripts must use cisco_ios_telnet."""
        scripts = [
            "scripts/fault-injection/inject_scenario_01.py",
            "scripts/fault-injection/inject_scenario_02.py",
            "scripts/fault-injection/inject_scenario_03.py",
            "scripts/fault-injection/apply_solution.py",
        ]
        for script in scripts:
            path = os.path.join(LAB_PATH, script)
            with open(path) as f:
                content = f.read()
            self.assertIn("cisco_ios_telnet", content,
                f"{script} must use device_type=cisco_ios_telnet")
            self.assertIn("127.0.0.1", content,
                f"{script} must connect to 127.0.0.1 (GNS3 localhost)")

    def test_inject_01_targets_conditional_default(self):
        """Scenario 01 fault script must break the conditional default route."""
        path = os.path.join(LAB_PATH, "scripts/fault-injection/inject_scenario_01.py")
        with open(path) as f:
            content = f.read()
        self.assertIn("Null0", content,
            "Scenario 01 must remove the ip route 0.0.0.0 0.0.0.0 Null0")
        self.assertIn("5001", content,
            "Scenario 01 targets R1 on port 5001")
        self.assertIn("COND-DEFAULT", content,
            "Scenario 01 must reference COND-DEFAULT route-map")

    def test_inject_02_targets_med_values(self):
        """Scenario 02 fault script must inject incorrect MED values."""
        path = os.path.join(LAB_PATH, "scripts/fault-injection/inject_scenario_02.py")
        with open(path) as f:
            content = f.read()
        self.assertIn("metric", content,
            "Scenario 02 must set metric (MED) values")
        self.assertIn("5001", content,
            "Scenario 02 targets R1 on port 5001")
        self.assertIn("TE-TO-ISP-A", content,
            "Scenario 02 must modify TE-TO-ISP-A route-map")

    def test_inject_03_targets_as_path_prepend(self):
        """Scenario 03 fault script must break AS-path prepend sequencing."""
        path = os.path.join(LAB_PATH, "scripts/fault-injection/inject_scenario_03.py")
        with open(path) as f:
            content = f.read()
        self.assertIn("as-path prepend", content,
            "Scenario 03 must involve AS-path prepend")
        self.assertIn("5001", content,
            "Scenario 03 targets R1 on port 5001")
        self.assertIn("TE-TO-ISP-A", content,
            "Scenario 03 must modify TE-TO-ISP-A route-map")

    def test_apply_solution_targets_all_5_routers(self):
        """apply_solution.py must connect to all 5 routers."""
        path = os.path.join(LAB_PATH, "scripts/fault-injection/apply_solution.py")
        with open(path) as f:
            content = f.read()
        for port in ["5001", "5002", "5003", "5004", "5005"]:
            self.assertIn(port, content,
                f"apply_solution.py must connect to port {port}")


if __name__ == "__main__":
    unittest.main()
