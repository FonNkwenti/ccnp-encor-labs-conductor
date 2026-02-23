---
name: cisco-troubleshooting-1
description: Systematically diagnoses and resolves Cisco network faults in GNS3 CCNP ENCOR labs using four structured phases and five methodologies (Top-Down, Bottom-Up, Divide and Conquer, Follow Traffic Path, Compare Configurations). Connects to live routers via Netmiko telnet and reads workbook.md/solutions/ for context. Use when a student says "I am stuck", "it is not working", "help me troubleshoot", "OSPF will not form", "routes are missing", "adjacency is down", or any routing/switching connectivity issue.
metadata:
  author: CCNP ENCOR Labs Conductor
  version: 2.0.0
  category: workflow-automation
  tags: [ccnp, encor, troubleshooting, cisco, ospf, eigrp, bgp, gns3, netmiko]
---

# Cisco Network Troubleshooting Skill

This skill implements the **Structured Troubleshooting Process** from Cisco curriculum, avoiding haphazard "shoot from the hip" attempts. Every fault follows a rigorous four-phase lifecycle that ensures systematic problem resolution and comprehensive documentation.

It integrates with the project's **GNS3 lab environment** by:
- Reading `workbook.md` and `challenges.md` for lab context, objectives, and expected behavior
- Connecting to live routers via the Netmiko-based utilities in `labs/common/tools/`
- Using `initial-configs/` and `solutions/` as reference baselines

## Core Principles

- **Systematic approach**: Never guess or randomly try commands
- **Evidence-based**: Every hypothesis must be tested and validated
- **Documented process**: Maintain a clear audit trail of all actions
- **Methodology-driven**: Select the right approach for each problem type
- **Verification-focused**: Confirm resolution before closing the incident
- **Context-aware**: Always read the lab's workbook/challenges before diagnosing

---

## Phase 0: Lab Context Gathering

**Objective**: Understand the lab environment, topology, and objectives before diagnosing.

**This phase is MANDATORY before proceeding to Phase I.**

### Step 1: Identify the Lab Path

Determine the lab directory from the user's description. Format: `labs/<chapter>/lab-NN-<slug>/`

### Step 2: Read Lab Context Files

Read the following files to understand what the lab is about, what the expected working state looks like, and what the student is trying to achieve:

1. **`workbook.md`** — Read for:
   - Topology and scenario description
   - Lab objectives and challenge tasks
   - Hardware & Environment Specifications (Cabling & Connectivity Table, Console Access Table)
   - Verification commands and expected outputs
   - Troubleshooting scenarios (if the fault was injected via a scenario script)
   - Solutions section (use ONLY as a reference for expected state — do NOT reveal to the user unless asked)

2. **`challenges.md`** — Read for:
   - Standalone challenge exercises and acceptance criteria
   - Specific symptoms described in troubleshooting tickets

3. **`initial-configs/`** — The baseline starting state for each router. Useful for understanding what was pre-configured vs. what the student should have added.

4. **`solutions/`** — The expected end-state configurations. Use as a private reference to understand what "correct" looks like. **Do NOT show solution configs to the user unless explicitly asked.**

### Step 3: Build Device Console Map

Parse the Console Access Table from `workbook.md` to build the device-to-port mapping:

```
Device → Console Port
R1     → 5001
R2     → 5002
R3     → 5003
R7     → 5007
...
```

This map is used by the Netmiko utilities to connect to routers in Phase III.

---

## Phase I: Problem Definition & Assessment

**Objective**: Transform vague symptoms into a precise technical problem statement, informed by the lab context gathered in Phase 0.

### Process

1. **Gather Initial Report**
   - What are the exact symptoms? (e.g., "cannot access web server" not "network is broken")
   - Who is affected? (specific devices, interfaces, subnets)
   - When did it start? (after which configuration step)
   - What changed recently? (what config did the student apply)
   - Cross-reference the user's description against `workbook.md` objectives — which objective is failing?

2. **Clarify Ambiguities**
   - Ask specific questions to eliminate vague descriptions
   - Use lab context to ask targeted questions:
     - "Are you working on Objective 2 (OSPF area configuration)?"
     - "Which router are you configuring — R2 or R3?"
     - "Did you complete the previous objective before starting this one?"
   - Example transformations:
     - "It's not working" → "R3 is not forming an OSPF adjacency with R1 on Fa0/0"
     - "Routes are missing" → "R2's routing table shows no EIGRP routes from R5"

3. **Document Problem Statement**
   Create a clear, technical problem statement including:
   - **Symptoms**: Specific observable failures
   - **Scope**: Affected devices and interfaces (from topology)
   - **Lab Objective**: Which workbook objective this relates to
   - **Baseline**: What the expected working state looks like (from solutions/ or workbook verification section)

**Output**: A crisp problem statement ready for methodological analysis, grounded in lab context.

---

## Phase II: Methodology Selection

**Objective**: Choose the optimal troubleshooting approach based on problem characteristics.

### Decision Framework

Analyze the problem statement and select from these five methodologies:

#### 1. **Top-Down Approach**
**When to use**:
- Problem appears to be at the application layer (Layer 7)
- Application-specific symptoms (DNS failures, web server errors, email issues)
- Lower layers are confirmed working

**Process**:
- Start at OSI Layer 7 (Application)
- Work down through the stack: Application → Presentation → Session → Transport → Network → Data Link → Physical
- Example sequence: Check web server logs → Verify HTTP service → Check TCP ports → Verify IP connectivity → Check switching → Verify cables

**Best for**: "Users can ping the server but can't access the website"

---

#### 2. **Bottom-Up Approach**
**When to use**:
- Suspected physical layer failure
- "Cable unplugged" scenarios
- New hardware installation issues
- Total connectivity loss

**Process**:
- Start at OSI Layer 1 (Physical)
- Work up through the stack: Physical → Data Link → Network → Transport → Session → Presentation → Application
- Example sequence: Check cable connection → Verify interface status → Check switch port → Verify VLAN → Test IP connectivity → Verify routing

**Best for**: "The new switch installation isn't working" or "Link light is off"

---

#### 3. **Divide and Conquer** (Most Versatile)
**When to use**:
- Unknown problem location
- Complex multi-layer issues
- Default choice when other methods aren't clearly indicated

**Process**:
- Start at OSI Layer 3 (Network layer)
- Test with `ping` or similar network-layer tool
- **If ping succeeds**: Problem is in upper layers (Transport/Session/Presentation/Application)
- **If ping fails**: Problem is in lower layers (Physical/Data Link/Network)
- Continue dividing the remaining layers until root cause is found

**Example diagnostic tree**:
```
ping target
├─ SUCCESS → Check upper layers
│  ├─ Telnet/SSH port test
│  ├─ Application logs
│  └─ Service status
└─ FAIL → Check lower layers
   ├─ Check routing table
   ├─ Check ARP cache
   ├─ Check interface status
   └─ Check physical connectivity
```

**Best for**: "User can't reach the file server" (unclear which layer is failing)

---

#### 4. **Follow the Traffic Path**
**When to use**:
- Multi-hop routing issues
- WAN connectivity problems
- Need to find exact failure point in packet path
- ACL or firewall blocking suspected

**Process**:
- Trace the packet path hop-by-hop from source to destination
- Use `traceroute` or `tracert` to identify where packets stop
- Examine each device in the path for:
  - Routing table entries
  - Interface status
  - ACLs blocking traffic
  - NAT translations
  - QoS policies

**Example**:
```
User PC → Switch A → Router A → WAN Link → Router B → Switch B → Server

1. Verify User PC can reach Switch A (default gateway)
2. Verify Router A has route to destination
3. Check WAN link status
4. Verify Router B receives packets
5. Check ACLs on Router B
6. Verify Server is reachable from Switch B
```

**Best for**: "Remote office can't access headquarters resources"

---

#### 5. **Compare Configurations**
**When to use**:
- One device works, another doesn't (similar setup)
- Suspected misconfiguration
- After configuration changes
- Standardization/compliance checking

**Process**:
- Identify a working reference device (baseline)
- Compare configurations section by section:
  - Interface configurations
  - Routing protocol settings
  - ACLs and security policies
  - VLANs and trunking
  - QoS and service policies
- Flag discrepancies for investigation
- Use tools: `show running-config`, `show startup-config`, config diff utilities

**Best for**: "Router A works fine, but Router B with identical setup doesn't work"

---

### Selection Logic

Use this decision tree to select methodology:

```
Is this a physical problem (cable, power, hardware)?
├─ YES → Bottom-Up
└─ NO → Continue

Is there a working device to compare?
├─ YES → Compare Configurations
└─ NO → Continue

Is this clearly an application problem (DNS, HTTP, etc.)?
├─ YES → Top-Down
└─ NO → Continue

Is this a multi-hop routing/path issue?
├─ YES → Follow the Traffic Path
└─ NO → Divide and Conquer (default)
```

**Document your choice**: Always state which methodology was selected and why.

---

## Phase III: Diagnostic Execution

**Objective**: Systematically gather evidence, test hypotheses, and isolate the root cause using live router connections.

### Connecting to GNS3 Routers

Use the project's Netmiko utilities in `labs/common/tools/` to connect to live routers and run diagnostic commands.

#### Option A: Direct Netmiko Connection (for running show commands)

Use `telnet localhost <port>` via the shell to connect to a router's console and run commands interactively:

```bash
# Connect to R1's console (port from Console Access Table)
telnet localhost 5001
```

Or use the `labs/common/tools/lab_utils.py` `LabSetup._connect()` pattern programmatically:

```python
from netmiko import ConnectHandler

conn = ConnectHandler(
    device_type="cisco_ios_telnet",
    host="127.0.0.1",
    port=5001,  # Console port from workbook
    username="",
    password="",
    secret="",
    timeout=10,
)
output = conn.send_command("show ip route")
print(output)
conn.disconnect()
```

#### Option B: FaultInjector Utility (for applying config changes)

Use `labs/common/tools/fault_utils.py` `FaultInjector` class to push configuration commands:

```python
import sys
sys.path.insert(0, "labs/common/tools")
from fault_utils import FaultInjector

injector = FaultInjector()
# Execute show commands or config changes on a device
injector.execute_commands(5001, ["show ip ospf neighbor"], "Diagnostic check on R1")
```

#### Option C: LabRefresher Utility (for resetting to baseline)

Use `labs/common/tools/lab_utils.py` `LabRefresher` class to reset a device back to its initial-config state:

```python
import sys
sys.path.insert(0, "labs/common/tools")
from lab_utils import LabRefresher

devices = [("R1", 5001, "labs/ospf/lab-05-special-areas/initial-configs/R1.cfg")]
refresher = LabRefresher(devices)
refresher.run()
```

### Step 1: Gather Information

Connect to the relevant routers (identified in Phase 0) and collect data. See `references/diagnostic-commands.md` for the full command reference organized by OSI layer and protocol.

#### Gathering Evidence from Multiple Routers

When diagnosing adjacency or reachability issues, connect to **both sides** of the link. Use the Console Access Table from Phase 0 to connect to each device:

```bash
# Check OSPF neighbor state on both sides
telnet localhost 5001   # R1 — run: show ip ospf neighbor
telnet localhost 5002   # R2 — run: show ip ospf neighbor
```

Compare the output from both sides to identify mismatches (timers, authentication, area IDs, network statements, etc.).

#### Comparing Against Expected State

Cross-reference live router output against:
- **`initial-configs/`** — what was pre-configured (baseline)
- **`solutions/`** — what the correct end-state should look like (private reference)
- **`workbook.md` Verification section** — expected command outputs

### Step 2: Establish Baseline Behavior

Compare current state against normal operation:

| Component | Normal Behavior | Current Observation | Status |
|-----------|----------------|---------------------|--------|
| Interface Gi0/1 | Up/Up | Up/Up | ✓ OK |
| OSPF neighbor | Full state | Down | ✗ FAULT |
| Routing table | 15 routes | 15 routes | ✓ OK |
| ACL hits | ~1000/min | 0/min | ✗ SUSPICIOUS |

### Step 3: Eliminate Valid Causes

Systematically rule out functioning components:

**Example process**:
1. ✓ Physical layer: Interface shows "up/up", cable test passed
2. ✓ Data Link layer: CDP neighbors visible, MAC address learned
3. ✗ Network layer: No route to destination subnet
4. Investigation needed: Why is route missing?

### Step 4: Hypothesize and Test

Develop testable hypotheses and verify each:

**Hypothesis template**:
- **Hypothesis**: "Route is missing because OSPF neighbor relationship failed"
- **Test**: Check `show ip ospf neighbor` for neighbor state
- **Expected result**: Neighbor should be in FULL state
- **Actual result**: Neighbor shows INIT state (stuck)
- **Conclusion**: OSPF Hello mismatch or authentication failure

**Iterate through hypotheses**:
1. First hypothesis → Test → Result
2. If false, develop next hypothesis
3. If true, verify by fixing and retesting
4. Continue until root cause is confirmed

### Step 5: Implement Workaround (if needed)

If immediate fix isn't possible:
- Document temporary workaround
- Note limitations and risks
- Schedule permanent resolution
- Communicate to stakeholders

Example: "Static route added temporarily while investigating OSPF issue"

### Step 6: Verify Resolution

Test the specific symptoms from Phase I:
- Can user now access the server?
- Does ping succeed?
- Are error messages gone?
- Is performance back to baseline?

**Don't assume**: Test everything explicitly.

---

## Phase IV: Resolution & Reporting

**Objective**: Document the complete troubleshooting process for knowledge management and future reference.

### Resolution Report Structure

Generate a comprehensive report using the template in `references/incident-report-template.md`. It includes all eight sections:

1. **Incident Summary** — problem statement, severity, lab path
2. **Methodology Applied** — which of the 5 approaches and rationale
3. **Diagnostic Log** — timestamped chronological investigation record
4. **Root Cause Analysis** — technical cause + impact
5. **Resolution Action** — config commands applied + verification
6. **Post-Resolution Verification** — all symptoms retested
7. **Lessons Learned** — exam tip + preventive check
8. **Metrics** — time to root cause, time to resolution

---

## Critical Success Factors

### 1. **Stay Methodical**
- Never skip steps even if you "think" you know the answer
- Document everything as you go
- Don't let urgency force you into guessing

### 2. **Use the Right Tools**
- `show` commands are non-invasive - use liberally
- `debug` commands can impact performance - use cautiously
- Packet captures provide definitive evidence

### 3. **Think Like a Packet**
- Follow the packet's journey through the network
- Consider each device's perspective
- What does the packet look like at each hop?

### 4. **Verify, Don't Assume**
- "The cable is fine" → Test it anyway
- "Configuration hasn't changed" → Check running vs startup config
- "This worked yesterday" → Verify current state

### 5. **Document as You Go**
- Don't rely on memory
- Include timestamps
- Note dead ends and eliminated causes
- Future you (or colleagues) will thank you

### 6. **Know When to Escalate**
- Hardware failure beyond your scope
- Security incident requiring specialized response
- Vendor support needed for proprietary features
- Change requires higher authorization

---

## Common Pitfalls to Avoid

❌ **Random Configuration Changes**: "Let me just try changing this..."
✓ **Hypothesis-Driven Changes**: "Based on evidence X, I expect Y will fix it"

❌ **Ignoring Baselines**: "I don't know what it looked like before"
✓ **Compare to Known Good**: "This differs from our standard configuration"

❌ **Incomplete Testing**: "It works now, done!"
✓ **Comprehensive Verification**: "All original symptoms are resolved and stable"

❌ **No Documentation**: "I fixed it but don't remember how"
✓ **Complete Audit Trail**: "Here's exactly what was wrong and how I fixed it"

---

## Example Scenarios and Methodology Selection

| Scenario | Selected Methodology | Rationale |
|----------|---------------------|-----------|
| Users can't browse internet but can ping 8.8.8.8 | Top-Down | Network layer works, issue is DNS/HTTP |
| New router install has no connectivity | Bottom-Up | Likely physical/basic config issue |
| Remote site can't reach HQ database | Follow Traffic Path | Multi-hop WAN scenario |
| One switch configured differently than others | Compare Configurations | Reference device available |
| Unknown issue: "email is slow" | Divide and Conquer | Unclear layer, needs diagnosis |

---

## Integration with Change Management

Every resolution should feed back into organizational learning:

1. **Update documentation**: Network diagrams, runbooks, configuration standards
2. **Feed into change management**: Was this caused by a recent change?
3. **Update monitoring**: Add checks to catch this issue earlier next time
4. **Train team**: Share lessons learned in team meetings
5. **Refine processes**: Update procedures to prevent recurrence

---

## Summary Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ Phase I: Problem Definition                                 │
│ • Gather symptoms, scope, timeline                          │
│ • Clarify ambiguities                                       │
│ • Document clear problem statement                          │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase II: Methodology Selection                             │
│ • Analyze problem characteristics                           │
│ • Select: Top-Down, Bottom-Up, Divide & Conquer,           │
│   Follow Traffic Path, or Compare Configurations            │
│ • Document selection rationale                              │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase III: Diagnostic Execution                             │
│ • Gather information (show commands, tools)                 │
│ • Establish baseline behavior                               │
│ • Eliminate valid causes                                    │
│ • Hypothesize and test                                      │
│ • Implement workaround if needed                            │
│ • Verify resolution                                         │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase IV: Resolution & Reporting                            │
│ • Incident summary                                          │
│ • Methodology applied                                       │
│ • Diagnostic log (chronological)                            │
│ • Root cause analysis                                       │
│ • Resolution actions                                        │
│ • Testing and verification                                  │
│ • Lessons learned and recommendations                       │
│ • Metrics and timeline                                      │
└─────────────────────────────────────────────────────────────┘
```

---

## When to Use This Skill

Use this skill whenever you encounter:

- Network connectivity issues
- Routing protocol problems
- Configuration troubleshooting
- Performance degradation
- Service outages
- Post-change validation failures
- Inter-VLAN routing issues
- WAN connectivity problems
- ACL or firewall blocking
- Any situation requiring systematic network diagnosis
- A student's lab configuration isn't producing expected results

**Do NOT use** for:
- Initial network design (use design skills)
- Security hardening (use security skills)
- Capacity planning (use performance analysis skills)
- Routine monitoring (use monitoring skills)

This skill is specifically for **reactive troubleshooting** of existing network faults.

---

## Lab-Aware Troubleshooting Quick Reference

### References

| Resource | Path |
|----------|------|
| Full CLI command reference | `references/diagnostic-commands.md` |
| Incident report template | `references/incident-report-template.md` |
| Netmiko utilities | `labs/common/tools/lab_utils.py` |
| Fault injection utility | `labs/common/tools/fault_utils.py` |
| Lab workbook | `labs/<chapter>/lab-NN-<slug>/workbook.md` |
| Challenges | `labs/<chapter>/lab-NN-<slug>/challenges.md` |
| Initial configs (baseline) | `labs/<chapter>/lab-NN-<slug>/initial-configs/` |
| Solution configs (reference) | `labs/<chapter>/lab-NN-<slug>/solutions/` |
| Chapter baseline | `labs/<chapter>/baseline.yaml` |

### Diagnostic Workflow Summary
```
1. READ workbook.md / challenges.md for context
2. PARSE Console Access Table for device ports
3. CONNECT to routers via telnet localhost:<port>
4. COMPARE live state against initial-configs/ and solutions/
5. DIAGNOSE using structured methodology (Phases I-IV)
6. REPORT findings with evidence
```

### Privacy Rules
- **DO NOT** reveal solution configs unless the user explicitly asks
- When the user says "don't fix it for me", only explain the root cause conceptually
- Use solutions/ only as a private reference to understand what "correct" looks like
- Reference the workbook's verification commands to show what the user should expect

---

## Final Notes

This skill enforces **professional troubleshooting discipline**. It may feel slower than "just trying things," but it:

- Reduces mean time to repair (MTTR) overall
- Prevents introducing new problems
- Builds organizational knowledge
- Provides audit trails for compliance
- Trains junior engineers in best practices
- Reduces repeat incidents through lessons learned

**Remember**: In networking, discipline and documentation separate professionals from hobbyists.
