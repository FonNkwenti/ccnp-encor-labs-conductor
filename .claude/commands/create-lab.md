Create a detailed lab workbook and all supporting artifacts for: $ARGUMENTS

## Workflow

1. **Read context first:**
   - Read `conductor/product-guidelines.md` for workbook standards
   - Read the chapter's `baseline.yaml` for topology, devices, IPs, and console ports
   - If this is Lab N > 1, read Lab (N-1)'s `solutions/` directory — those become this lab's `initial-configs/`
   - Read the track spec if a conductor track exists for this lab

2. **Generate the lab directory** at `labs/<chapter>/lab-NN-<slug>/` with:
   - `workbook.md` — full lab guide following the Required Sections in CLAUDE.md
   - `challenges.md` — standalone challenge exercises
   - `initial-configs/` — starting `.cfg` files per router (from baseline or previous lab solutions)
   - `solutions/` — complete solution `.cfg` files + `verification_commands.txt`
   - `setup_lab.py` — Python automation script using `labs/common/tools/lab_utils.py` patterns to push initial configs via Netmiko (`cisco_ios_telnet`)
   - `topology.drawio` — visual diagram following `.agent/skills/drawio/SKILL.md` Section 4

3. **Topology diagram** must follow the Draw.io Standards in CLAUDE.md:
   - White connection lines, Cisco device icons, labels on empty side
   - IP last-octet labels, legend box, no link crossthrough
   - Use `generate_topo.py` when possible

4. **Workbook must include at minimum 3 troubleshooting scenarios** with:
   - Problem statement, mission, success criteria
   - Solutions in collapsible `<details>` blocks
   - Each targeting common misconfigurations (parameter mismatches, interface issues, authentication, etc.)

5. **After workbook generation**, automatically create fault injection scripts:
   - Parse the troubleshooting scenarios from the workbook
   - Generate `scripts/fault-injection/inject_scenario_01.py`, `02.py`, `03.py`
   - Generate `scripts/fault-injection/apply_solution.py`
   - Generate `scripts/fault-injection/README.md`
   - All scripts use Netmiko with `device_type="cisco_ios_telnet"` connecting to `localhost:<console_port>`

6. **Export topology PNG:**
   - Run `python3 labs/common/tools/export_diagrams.py --file <path_to_drawio>`

7. **Write tests** in `tests/` following existing test naming conventions.

8. **If a conductor track exists**, update `plan.md` per the workflow in CLAUDE.md.
