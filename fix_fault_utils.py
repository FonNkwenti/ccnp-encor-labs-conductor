#!/usr/bin/env python3
import re
import sys

with open('labs/common/tools/fault_utils.py', 'r') as f:
    content = f.read()

# Fix the broken split line
# Pattern for the method _read_until_prompt
pattern = r'(    def _read_until_prompt\(self, sock, timeout=2\):\s*"""[^"]*"""\s*sock\.settimeout\(timeout\)\s*data = b""\s*try:\s*while True:\s*chunk = sock\.recv\(4096\)\s*if not chunk:\s*break\s*data \+= chunk\s*# Look for IOS prompt patterns\s*lines = data\.split\(b\'\n\s*\'\)\s*for line in lines:\s*line = line\.strip\(\)\s*if line\.endswith\(b\'#\'\) or line\.endswith\(b\'>\'\):\s*return data\s*except socket\.timeout:\s*pass\s*return data)'
# This regex is too complex; simpler: replace the specific broken line
# Let's just replace the two lines with correct one
lines = content.splitlines(keepends=True)
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    if line.rstrip().startswith('lines = data.split(b\'') and i+1 < len(lines) and lines[i+1].strip() == "'):
        # Fix this pair
        indent = line[:len(line) - len(line.lstrip())]
        new_lines.append(f'{indent}lines = data.split(b\'\\n\')\n')
        i += 2
    else:
        new_lines.append(line)
        i += 1
new_content = ''.join(new_lines)
if new_content != content:
    with open('labs/common/tools/fault_utils.py', 'w') as f:
        f.write(new_content)
    print('Fixed fault_utils.py')
else:
    print('No change needed')