#!/usr/bin/env python3
import re

with open('labs/common/tools/fault_utils.py', 'r') as f:
    content = f.read()

# Pattern for the _read_until_prompt method
# We'll replace the broken split line
# Find the line containing "lines = data.split(b'" and the next line starting with "'"
# Use regex with DOTALL to capture across lines
pattern = r'(\s*lines = data\.split\(b\'\n\s*\'\s*\))'
# Actually simpler: replace the two lines
new_content = re.sub(r"lines = data\.split\(b'\n\s*'\)", "lines = data.split(b'\\n')", content, flags=re.MULTILINE)
if new_content != content:
    with open('labs/common/tools/fault_utils.py', 'w') as f:
        f.write(new_content)
    print('Fixed split line')
else:
    # Try alternative pattern where newline is literal
    # Look for lines = data.split(b' followed by newline then any whitespace then ')
    # Use DOTALL
    pattern2 = r"(lines = data\.split\(b')(?:\n|\r\n)\s*('\))"
    new_content = re.sub(pattern2, r"\1\\n\2", content, flags=re.MULTILINE)
    if new_content != content:
        with open('labs/common/tools/fault_utils.py', 'w') as f:
            f.write(new_content)
        print('Fixed split line (alternative)')
    else:
        print('Could not fix')