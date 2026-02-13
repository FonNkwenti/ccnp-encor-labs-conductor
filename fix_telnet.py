#!/usr/bin/env python3
"""
Fix telnetlib usage in Python files for Python 3.14+ where telnetlib is removed.
Replaces telnetlib with socket and fixes string literals.
"""
import os
import sys
import re

def fix_file(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Replace import telnetlib with import socket
        if line.strip() == 'import telnetlib':
            new_lines.append('import socket\n')
            i += 1
            continue
        # Replace from telnetlib import ... (unlikely)
        if line.startswith('from telnetlib'):
            # Not present in codebase, skip
            new_lines.append(line)
            i += 1
            continue
        tn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tn.settimeout(5)
        tn.connect((...))
        tn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tn.settimeout(5)
        tn.connect((host, port))
        if 'telnetlib.Telnet' in line:
            # Extract the part inside parentheses
            match = re.search(r'telnetlib\.Telnet\(([^)]+)\)', line)
            if match:
                args = match.group(1)
                # Keep only host, port (ignore timeout=5)
                parts = [p.strip() for p in args.split(',')]
                if len(parts) >= 2:
                    connect_args = ', '.join(parts[:2])
                else:
                    connect_args = args  # fallback
                indent = line[:len(line) - len(line.lstrip())]
                new_lines.append(f'{indent}tn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\n')
                new_lines.append(f'{indent}tn.settimeout(5)\n')
                new_lines.append(f'{indent}tn.connect(({connect_args}))\n')
                i += 1
                continue
        # Fix multiline string literals: b"<newline>" and b"text<newline>"
        # Pattern: line ends with b" or b"text, next line starts with " (maybe with spaces)
        stripped = line.rstrip()
        if 'b"' in stripped:
            # Look ahead to see if next line is just a closing quote/parenthesis
            if i + 1 < len(lines) and (lines[i+1].strip().startswith('"') or lines[i+1].strip().startswith('")')):
                # Merge the two lines into a single line with \n escape
                # Extract prefix before b"
                prefix = line[:line.rfind('b"')]
                # Extract text after b" (could be empty)
                text = line[line.rfind('b"')+2:].rstrip()
                # The closing quote line may have spaces before it; we need to capture any characters after quote
                closing_line = lines[i+1].strip()
                # Determine suffix after quote (e.g., ')' )
                suffix = ''
                if closing_line.startswith('"'):
                    suffix = closing_line[1:]  # could be ')', '', or maybe ') ' etc.
                # Build new line: prefix + b"text\n" + suffix
                new_line = f'{prefix}b"{text}\\n"{suffix}\n'
                # Replace tn.sendall with tn.sendall in the new line
                new_line = new_line.replace('tn.sendall', 'tn.sendall')
                new_lines.append(new_line)
                i += 2
                continue
        # Replace tn.sendall with tn.sendall
        if 'tn.sendall' in line:
            line = line.replace('tn.sendall', 'tn.sendall')
        new_lines.append(line)
        i += 1
    
    # Final pass: ensure socket is imported if not already
    content = ''.join(new_lines)
    if 'import socket' not in content and 'socket.socket' in content:
        # Add import socket at top after any shebang
        lines2 = content.splitlines(keepends=True)
        final_lines = []
        added = False
        for line in lines2:
            if line.startswith('#!/'):
                final_lines.append(line)
                continue
            if not added and line.strip() and not line.startswith('import ') and not line.startswith('from '):
                final_lines.append('import socket\n')
                added = True
            final_lines.append(line)
        if not added:
            final_lines.insert(0, 'import socket\n')
        content = ''.join(final_lines)
    
    with open(filepath, 'w') as f:
        f.write(content)
    print(f'Fixed {filepath}')

def main():
    root = os.getcwd()
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip hidden directories
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        for filename in filenames:
            if filename.endswith('.py'):
                filepath = os.path.join(dirpath, filename)
                try:
                    with open(filepath, 'r') as f:
                        if 'telnetlib' in f.read():
                            fix_file(filepath)
                except Exception as e:
                    print(f'Error processing {filepath}: {e}')

if __name__ == '__main__':
    main()