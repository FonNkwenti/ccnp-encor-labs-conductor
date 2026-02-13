#!/usr/bin/env python3
import sys

with open('labs/common/tools/fault_utils.py', 'r') as f:
    lines = f.readlines()

# line numbers are 1-indexed, index 36 is line 37
if lines[36].rstrip() == "                lines = data.split(b'" and lines[37].strip() == "'":
    lines[36] = "                lines = data.split(b'\\n')\n"
    lines[37] = ''
    with open('labs/common/tools/fault_utils.py', 'w') as f:
        f.writelines(lines)
    print('Fixed split line')
else:
    # Maybe already fixed?
    # Check if line 37 contains correct pattern
    if "lines = data.split(b'\\n')" in lines[36]:
        print('Already fixed')
    else:
        print('Unexpected pattern')
        sys.exit(1)