import unittest
import os

LAB_PATH = "labs/bgp/lab-06-communities-policy"


class TestBGPLab06Structure(unittest.TestCase):

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
        """Workbook must contain exactly Ticket 1, Ticket 2, Ticket 3."""
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

    # ── Initial Configs ──────────────────────────────────────────────────────

    def test_initial_configs_r1_inherits_lab05(self):
        """R1 initial config must carry forward Lab 05 route-maps and AS-path ACLs."""
        path = os.path.join(LAB_PATH, "initial-configs/R1.cfg")
        with open(path) as f:
            content = f.read()
        self.assertIn("router bgp 65001", content)
        self.assertIn("ip as-path access-list 1 permit ^65002$", content)
        self.assertIn("route-map SET-LP-200-ISP-A", content)
        self.assertIn("route-map POLICY-ISP-B-IN", content)
        self.assertIn("route-map PREPEND-TO-ISP-B", content)

    def test_initial_configs_r3_has_fa1_1_for_r5(self):
        """R3 initial config must include Fa1/1 interface for R5 link."""
        path = os.path.join(LAB_PATH, "initial-configs/R3.cfg")
        with open(path) as f:
            content = f.read()
        self.assertIn("FastEthernet1/1", content)
        self.assertIn("10.1.35.1", content)

    def test_initial_configs_r3_no_r5_bgp(self):
        """R3 initial config must NOT include R5 as a BGP neighbor (student task)."""
        path = os.path.join(LAB_PATH, "initial-configs/R3.cfg")
        with open(path) as f:
            content = f.read()
        self.assertNotIn("10.1.35.2", content,
            "R3 initial config must not have R5 BGP peer — student configures it")

    def test_initial_configs_r5_no_bgp(self):
        """R5 initial config must NOT contain BGP (student task)."""
        path = os.path.join(LAB_PATH, "initial-configs/R5.cfg")
        with open(path) as f:
            content = f.read()
        self.assertNotIn("router bgp", content,
            "R5 initial config must not have BGP — student configures it")

    def test_initial_configs_no_send_community(self):
        """Initial configs must NOT contain send-community (student task)."""
        for device in ["R1", "R2", "R3", "R4"]:
            path = os.path.join(LAB_PATH, f"initial-configs/{device}.cfg")
            with open(path) as f:
                content = f.read()
            self.assertNotIn("send-community", content,
                f"{device} initial config must not have send-community")

    # ── Solution Configs — send-community ────────────────────────────────────

    def test_solution_r1_has_send_community_on_all_neighbors(self):
        """R1 solution must have send-community on all 3 BGP neighbors."""
        path = os.path.join(LAB_PATH, "solutions/R1.cfg")
        with open(path) as f:
            content = f.read()
        self.assertIn("send-community", content)
        # All three neighbors must have it
        self.assertIn("neighbor 10.1.12.2 send-community", content)
        self.assertIn("neighbor 10.1.13.2 send-community", content)
        self.assertIn("neighbor 172.16.4.4 send-community", content)

    def test_solution_r2_has_send_community(self):
        """R2 solution must have send-community on both neighbors."""
        path = os.path.join(LAB_PATH, "solutions/R2.cfg")
        with open(path) as f:
            content = f.read()
        self.assertIn("neighbor 10.1.12.1 send-community", content)
        self.assertIn("neighbor 10.1.23.2 send-community", content)

    def test_solution_r3_has_send_community_and_r5_peer(self):
        """R3 solution must have send-community on all neighbors and R5 eBGP peer."""
        path = os.path.join(LAB_PATH, "solutions/R3.cfg")
        with open(path) as f:
            content = f.read()
        self.assertIn("neighbor 10.1.13.1 send-community", content)
        self.assertIn("neighbor 10.1.23.1 send-community", content)
        self.assertIn("neighbor 10.1.35.2 remote-as 65004", content)
        self.assertIn("neighbor 10.1.35.2 send-community", content)

    def test_solution_r3_has_tag_customer_in_route_map(self):
        """R3 solution must have TAG-CUSTOMER-IN route-map setting 65003:500."""
        path = os.path.join(LAB_PATH, "solutions/R3.cfg")
        with open(path) as f:
            content = f.read()
        self.assertIn("route-map TAG-CUSTOMER-IN", content)
        self.assertIn("set community 65003:500 additive", content)
        self.assertIn("neighbor 10.1.35.2 route-map TAG-CUSTOMER-IN in", content)

    def test_solution_r4_has_send_community_and_no_export(self):
        """R4 solution must have send-community and SET-NO-EXPORT route-map."""
        path = os.path.join(LAB_PATH, "solutions/R4.cfg")
        with open(path) as f:
            content = f.read()
        self.assertIn("neighbor 172.16.1.1 send-community", content)
        self.assertIn("route-map SET-NO-EXPORT", content)
        self.assertIn("set community no-export additive", content)
        self.assertIn("neighbor 172.16.1.1 route-map SET-NO-EXPORT out", content)

    def test_solution_r4_removes_distribute_list(self):
        """R4 solution must use route-map instead of distribute-list."""
        path = os.path.join(LAB_PATH, "solutions/R4.cfg")
        with open(path) as f:
            content = f.read()
        self.assertNotIn("distribute-list ENTERPRISE-INTERNAL out", content,
            "R4 solution must replace distribute-list with route-map SET-NO-EXPORT")

    def test_solution_r5_has_bgp_65004(self):
        """R5 solution must configure BGP AS 65004."""
        path = os.path.join(LAB_PATH, "solutions/R5.cfg")
        with open(path) as f:
            content = f.read()
        self.assertIn("router bgp 65004", content)
        self.assertIn("bgp router-id 172.16.5.5", content)
        self.assertIn("neighbor 10.1.35.1 remote-as 65003", content)
        self.assertIn("neighbor 10.1.35.1 send-community", content)

    def test_solution_r5_has_network_statements(self):
        """R5 solution must advertise all 3 prefixes via network statements."""
        path = os.path.join(LAB_PATH, "solutions/R5.cfg")
        with open(path) as f:
            content = f.read()
        self.assertIn("network 172.16.5.5 mask 255.255.255.255", content)
        self.assertIn("network 10.5.1.0 mask 255.255.255.0", content)
        self.assertIn("network 10.5.2.0 mask 255.255.255.0", content)

    # ── Solution R1 — Community Policy ───────────────────────────────────────

    def test_solution_r1_has_community_list(self):
        """R1 solution must define the CUSTOMER-ROUTES community-list."""
        path = os.path.join(LAB_PATH, "solutions/R1.cfg")
        with open(path) as f:
            content = f.read()
        self.assertIn("ip community-list standard CUSTOMER-ROUTES permit 65003:500", content)

    def test_solution_r1_has_policy_ispb_in_with_seq8(self):
        """R1 POLICY-ISP-B-IN must include sequence 8 matching CUSTOMER-ROUTES."""
        path = os.path.join(LAB_PATH, "solutions/R1.cfg")
        with open(path) as f:
            content = f.read()
        self.assertIn("route-map POLICY-ISP-B-IN permit 8", content)
        self.assertIn("match community CUSTOMER-ROUTES", content)
        self.assertIn("set local-preference 120", content)

    def test_solution_r1_has_set_community_out_route_map(self):
        """R1 solution must have SET-COMMUNITY-OUT route-map tagging 65001:100."""
        path = os.path.join(LAB_PATH, "solutions/R1.cfg")
        with open(path) as f:
            content = f.read()
        self.assertIn("route-map SET-COMMUNITY-OUT", content)
        self.assertIn("set community 65001:100 additive", content)

    def test_solution_r1_preserves_lab05_local_preference_policy(self):
        """R1 solution must retain LP 200 (ISP-A) and LP 150 (ISP-B) from Lab 05."""
        path = os.path.join(LAB_PATH, "solutions/R1.cfg")
        with open(path) as f:
            content = f.read()
        self.assertIn("set local-preference 200", content)
        self.assertIn("set local-preference 150", content)

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
        self.assertIn("AS 65004", content)

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

    def test_inject_01_targets_send_community(self):
        """Scenario 01 fault script must remove send-community."""
        path = os.path.join(LAB_PATH, "scripts/fault-injection/inject_scenario_01.py")
        with open(path) as f:
            content = f.read()
        self.assertIn("send-community", content)
        self.assertIn("5001", content, "Scenario 01 targets R1 on port 5001")

    def test_inject_02_targets_community_list(self):
        """Scenario 02 fault script must misconfigure the community-list."""
        path = os.path.join(LAB_PATH, "scripts/fault-injection/inject_scenario_02.py")
        with open(path) as f:
            content = f.read()
        self.assertIn("CUSTOMER-ROUTES", content)
        self.assertIn("5001", content, "Scenario 02 targets R1 on port 5001")

    def test_inject_03_targets_r5_network_statements(self):
        """Scenario 03 fault script must remove R5 network statements."""
        path = os.path.join(LAB_PATH, "scripts/fault-injection/inject_scenario_03.py")
        with open(path) as f:
            content = f.read()
        self.assertIn("network", content)
        self.assertIn("5005", content, "Scenario 03 targets R5 on port 5005")

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
