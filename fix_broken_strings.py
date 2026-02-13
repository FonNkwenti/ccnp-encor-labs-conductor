#!/usr/bin/env python3
"""
Fix broken byte string literals in Python files caused by incorrect newline replacement.
"""
import os
import sys

def fix_file(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    new_lines = []
    i = 0
    changed = False
    while i < len(lines):
        line = lines[i]
        stripped = line.rstrip()
        # Check if line ends with b" or b' (not closed)
        if stripped.endswith('b"') or stripped.endswith("b'"):
            quote_char = '"' if stripped.endswith('b"') else "'"
            # Look ahead for closing quote line
            if i + 1 < len(lines) and lines[i+1].lstrip().startswith(quote_char):
                # Merge the two lines
                prefix = line[:line.rfind('b' + quote_char)]
                # Extract content after b" (could be empty)
                content = line[line.rfind('b' + quote_char) + 2:].rstrip()
                # The next line starts with quote char, maybe with spaces before it
                next_line = lines[i+1]
                # Remove leading spaces and the quote char
                next_stripped = next_line.lstrip()
                if next_stripped.startswith(quote_char):
                    # There may be characters after the quote (like )) etc.
                    suffix = next_stripped[1:]  # after the quote
                    # Determine what the original string should be
                    # If content is empty and suffix is just newline, it's b"
" or b"\r\n"
                    # We'll assume it's supposed to be b"\r\n" (since we want that)
                    # But we need to infer from context: if the line is tn.sendall(b"
") etc.
                    # For simplicity, replace with b"\r\n"
                    # However, we need to preserve any suffix (like ))
                    # The suffix may contain closing parenthesis, newline, etc.
                    # We'll reconstruct: prefix + b"<content>\r\n" + suffix
                    # If content is empty, just b"\r\n"
                    # If content already ends with \r or \n, avoid doubling
                    # Let's just replace with b"\r\n"
                    new_line = f'{prefix}b{quote_char}{content}\\r\\n{quote_char}{suffix}'
                    new_lines.append(new_line)
                    changed = True
                    i += 2
                    continue
        new_lines.append(line)
        i += 1
    
    if changed:
        with open(filepath, 'w') as f:
            f.writelines(new_lines)
        print(f'Fixed {filepath}')
        return True
    return False

def main():
    root = os.getcwd()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        for filename in filenames:
            if filename.endswith('.py'):
                filepath = os.path.join(dirpath, filename)
                try:
                    fix_file(filepath)
                except Exception as e:
                    print(f'Error processing {filepath}: {e}')

if __name__ == '__main__':
    main()