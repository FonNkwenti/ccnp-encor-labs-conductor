import unittest
import os


class TestBGPLab07Structure(unittest.TestCase):
    LAB_PATH = "labs/bgp/lab-07-multihoming-te"

    def test_directory_exists(self):
        """Check if the lab directory exists."""
        self.assertTrue(os.path.exists(self.LAB_PATH),
                        f"Directory {self.LAB_PATH} does not exist")

    def test_subdirectories_exist(self):
        """Check if required subdirectories exist."""
        subdirs = ["initial-configs", "solutions", "scripts/fault-injection"]
        for subdir in subdirs:
            path = os.path.join(self.LAB_PATH, subdir)
            self.assertTrue(os.path.exists(path),
                            f"Subdirectory {path} does not exist")

    def test_files_exist(self):
        """Check if all required files exist."""
        files = [
            "workbook.md",
            "challenges.md",
            "setup_lab.py",
            "topology.drawio",
            "initial-configs/R1.cfg",
            "initial-configs/R2.cfg",
            "initial-configs/R3.cfg",
            "initial-configs/R4.cfg",
            "initial-configs/R5.cfg",
            "solutions/R1.cfg",
            "solutions/R2.cfg",
            "solutions/R3.cfg",
            "solutions/R4.cfg",
            "solutions/R5.cfg",
            "scripts/fault-injection/inject_scenario_01.py",
            "scripts/fault-injection/inject_scenario_02.py",
            "scripts/fault-injection/inject_scenario_03.py",
            "scripts/fault-injection/apply_solution.py",
            "scripts/fault-injection/README.md",
        ]
        for file in files:
            path = os.path.join(self.LAB_PATH, file)
            self.assertTrue(os.path.exists(path),
                            f"File {path} does not exist")

    def test_workbook_has_all_10_sections(self):
        """Check workbook.md contains all 10 required sections."""
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

    def test_workbook_has_three_tickets(self):
        """Check workbook.md has at least 3 troubleshooting tickets."""
        path = os.path.join(self.LAB_PATH, "workbook.md")
        with open(path, "r") as f:
            content = f.read()
        self.assertIn("### Ticket 1", content)
        self.assertIn("### Ticket 2", content)
        self.assertIn("### Ticket 3", content)

    def test_workbook_has_at_least_6_details_blocks(self):
        """Check workbook.md has at least 6 <details> spoiler blocks."""
        path = os.path.join(self.LAB_PATH, "workbook.md")
        with open(path, "r") as f:
            content = f.read()
        count = content.count("<details>")
        self.assertGreaterEqual(count, 6,
                                f"Expected at least 6 <details> blocks, found {count}")

    def test_workbook_has_console_access_table(self):
        """Check workbook.md has console port entries for all 5 devices."""
        path = os.path.join(self.LAB_PATH, "workbook.md")
        with open(path, "r") as f:
            content = f.read()
        self.assertIn("| R1 | 5001 |", content)
        self.assertIn("| R2 | 5002 |", content)
        self.assertIn("| R3 | 5003 |", content)
        self.assertIn("| R4 | 5004 |", content)
        self.assertIn("| R5 | 5005 |", content)

    def test_hardware_table(self):
        """Check workbook.md hardware table has all 5 devices with correct roles and platforms."""
        path = os.path.join(self.LAB_PATH, "workbook.md")
        with open(path, "r") as f:
            content = f.read()
        self.assertIn("| R1 | Enterprise Edge | c7200 |", content)
        self.assertIn("| R2 | ISP-A | c7200 |", content)
        self.assertIn("| R3 | ISP-B | c7200 |", content)
        self.assertIn("| R4 | Enterprise Internal | c3725 |", content)
        self.assertIn("| R5 | Downstream Customer | c3725 |", content)

    def test_initial_configs_have_lab06_bgp(self):
        """Check that initial configs carry forward Lab 06 BGP configuration."""
        r1_path = os.path.join(self.LAB_PATH, "initial-configs/R1.cfg")
        with open(r1_path, "r") as f:
            r1_content = f.read()
        self.assertIn("router bgp 65001", r1_content,
                      "R1 initial config must contain 'router bgp 65001'")
        self.assertIn("SET-LP-200-ISP-A", r1_content,
                      "R1 initial config must contain Lab 06 route-map 'SET-LP-200-ISP-A'")

        r5_path = os.path.join(self.LAB_PATH, "initial-configs/R5.cfg")
        with open(r5_path, "r") as f:
            r5_content = f.read()
        self.assertIn("router bgp 65004", r5_content,
                      "R5 initial config must contain 'router bgp 65004'")

    def test_solution_r1_has_te_route_maps(self):
        """Check solutions/R1.cfg has all required TE route-maps."""
        path = os.path.join(self.LAB_PATH, "solutions/R1.cfg")
        with open(path, "r") as f:
            content = f.read()
        self.assertIn("LP-FROM-ISP-A", content)
        self.assertIn("LP-FROM-ISP-B", content)
        self.assertIn("TE-TO-ISP-A", content)
        self.assertIn("TE-TO-ISP-B", content)
        self.assertIn("COND-DEFAULT", content)
        self.assertIn("default-originate", content)

    def test_solution_r1_has_null0_route(self):
        """Check solutions/R1.cfg has the static Null0 route for conditional default."""
        path = os.path.join(self.LAB_PATH, "solutions/R1.cfg")
        with open(path, "r") as f:
            content = f.read()
        self.assertIn("ip route 0.0.0.0 0.0.0.0 Null0", content)

    def test_solution_r1_has_med_values(self):
        """Check solutions/R1.cfg has MED (metric) configuration."""
        path = os.path.join(self.LAB_PATH, "solutions/R1.cfg")
        with open(path, "r") as f:
            content = f.read()
        self.assertIn("set metric", content,
                      "R1 solution must contain MED configuration via 'set metric'")

    def test_solution_r1_has_aspath_prepend(self):
        """Check solutions/R1.cfg has AS-path prepending configured."""
        path = os.path.join(self.LAB_PATH, "solutions/R1.cfg")
        with open(path, "r") as f:
            content = f.read()
        self.assertIn("set as-path prepend 65001 65001 65001", content)

    def test_solution_r2_unchanged(self):
        """Check solutions/R2.cfg has BGP but no enterprise TE route-maps (unchanged from initial)."""
        path = os.path.join(self.LAB_PATH, "solutions/R2.cfg")
        with open(path, "r") as f:
            content = f.read()
        self.assertIn("router bgp 65002", content,
                      "R2 solution must contain 'router bgp 65002'")
        self.assertNotIn("LP-FROM-ISP-A", content,
                         "R2 solution should not contain enterprise TE route-map 'LP-FROM-ISP-A'")

    def test_solution_r5_has_bgp(self):
        """Check solutions/R5.cfg has BGP configuration."""
        path = os.path.join(self.LAB_PATH, "solutions/R5.cfg")
        with open(path, "r") as f:
            content = f.read()
        self.assertIn("router bgp 65004", content)

    def test_topology_drawio_has_cisco_shapes(self):
        """Check topology.drawio uses Cisco router shapes."""
        path = os.path.join(self.LAB_PATH, "topology.drawio")
        with open(path, "r") as f:
            content = f.read()
        self.assertIn("mxgraph.cisco.routers.router", content,
                      "Must use Cisco router shapes")

    def test_topology_drawio_has_white_stroke(self):
        """Check topology.drawio uses white connection lines."""
        path = os.path.join(self.LAB_PATH, "topology.drawio")
        with open(path, "r") as f:
            content = f.read()
        self.assertIn("strokeColor=#FFFFFF", content,
                      "Connection lines must be white (strokeColor=#FFFFFF)")

    def test_topology_drawio_has_black_fill_legend(self):
        """Check topology.drawio has a black-fill legend box."""
        path = os.path.join(self.LAB_PATH, "topology.drawio")
        with open(path, "r") as f:
            content = f.read()
        self.assertIn("fillColor=#000000", content,
                      "Legend must have black fill (fillColor=#000000)")

    def test_topology_drawio_has_all_as_numbers(self):
        """Check topology.drawio legend contains all AS numbers."""
        path = os.path.join(self.LAB_PATH, "topology.drawio")
        with open(path, "r") as f:
            content = f.read()
        self.assertIn("AS 65001", content)
        self.assertIn("AS 65002", content)
        self.assertIn("AS 65003", content)

    def test_setup_lab_has_all_devices(self):
        """Check setup_lab.py configures all 5 devices with correct console ports."""
        path = os.path.join(self.LAB_PATH, "setup_lab.py")
        with open(path, "r") as f:
            content = f.read()
        for device in ["R1", "R2", "R3", "R4", "R5"]:
            self.assertIn(device, content,
                          f"setup_lab.py must reference device {device}")
        for port in [5001, 5002, 5003, 5004, 5005]:
            self.assertIn(str(port), content,
                          f"setup_lab.py must reference console port {port}")

    def test_fault_injection_scripts_use_telnet(self):
        """Check that each fault injection script uses Netmiko telnet and localhost."""
        scripts = [
            "inject_scenario_01.py",
            "inject_scenario_02.py",
            "inject_scenario_03.py",
        ]
        for script in scripts:
            path = os.path.join(self.LAB_PATH, "scripts/fault-injection", script)
            with open(path, "r") as f:
                content = f.read()
            self.assertIn("cisco_ios_telnet", content,
                          f"{script} must use 'cisco_ios_telnet' device type")
            self.assertIn("127.0.0.1", content,
                          f"{script} must target '127.0.0.1'")


if __name__ == "__main__":
    unittest.main()
