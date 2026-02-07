# Documentation

This project uses **Antigravity Agent Skills** for lab development. All skill definitions are in `.agent/skills/`.

## Available Skills

| Skill | Description |
|-------|-------------|
| [chapter-topics-creator](file:///.agent/skills/chapter-topics-creator/SKILL.md) | Generate lab topic blueprints for chapters |
| [lab-workbook-creator](file:///.agent/skills/lab-workbook-creator/SKILL.md) | Create detailed lab workbooks ("DeepSeek Standard") |
| [gns3](file:///.agent/skills/gns3/SKILL.md) | GNS3 hardware constraints for Apple M1 |
| [drawio](file:///.agent/skills/drawio/SKILL.md) | Draw.io diagram standards |

## Usage

Invoke skills via Antigravity by referencing the skill name, e.g.:
- "Use the `lab-workbook-creator` skill to create EIGRP Lab 07"
- "Use `chapter-topics-creator` to plan the OSPF chapter"

## Verification Cheatsheets

Quick command references are in `verification-cheatsheets/`.
