#!/usr/bin/env python3
import re

with open('labs/common/tools/fault_utils.py', 'r') as f:
    content = f.read()

# Pattern for the entire method (from def to return data)
# Use re.DOTALL to match across lines
pattern = r'(\s*def _read_until_prompt\(self, sock, timeout=2\):\s*"""[^"]*"""\s*sock\.settimeout\(timeout\)\s*data = b""\s*try:\s*while True:\s*chunk = sock\.recv\(4096\)\s*if not chunk:\s*break\s*data \+= chunk\s*# Look for IOS prompt patterns\s*lines = data\.split\(b\'\n\s*\'\)\s*for line in lines:\s*line = line\.strip\(\)\s*if line\.endswith\(b\'#\'\) or line\.endswith\(b\'>\'\):\s*return data\s*except socket\.timeout:\s*pass\s*return data)'
# Simpler: replace the broken split line only using a more specific pattern
# We'll replace the two lines containing the split with b'\n'
new_content = re.sub(r"lines = data\.split\(b'\n\s*'\)", "lines = data.split(b'\\n')", content, flags=re.MULTILINE)
if new_content != content:
    with open('labs/common/tools/fault_utils.py', 'w') as f:
        f.write(new_content)
    print('Fixed using regex')
else:
    # Try alternative pattern where newline is literal and there is whitespace between lines
    # Replace lines = data.split(b' + newline + any whitespace + ')
    new_content = re.sub(r"lines = data\.split\(b'(\n|\r\n)\s*'\)", "lines = data.split(b'\\\\n')", content, flags=re.MULTILINE)
    if new_content != content:
        with open('labs/common/tools/fault_utils.py', 'w') as f:
            f.write(new_content)
        print('Fixed using alternative regex')
    else:
        print('Could not fix')
        # Output the problematic lines
        lines = content.splitlines()
        for i, line in enumerate(lines):
            if 'lines = data.split' in line:
                print(f'Line {i+1}: {line}')